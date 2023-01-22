#!/usr/bin/env bash

set -e

# 1. Install the runme with `cargo install --force runme`
# 2. Grab shell completion from: https://github.com/sigoden/runme/tree/main/completions
# 3. Run `runme` to see the list of existing tasks

exec 3>&1
exec 4>&2

log() {
  echo "$@" >&3
}
readonly -f log

err() {
  echo "$@" >&4
}
readonly -f err

catch() {
  if ! output=$("$@" 2>&1); then
    err
    err "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    err "There was an error while executing '$@':"
    err "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    err
    err "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    err "$(echo \"$output\" | tail -n 5)"
    err "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    err
    exit 1
  fi
}

# @cmd Install development dependencies
deps() {
  catch python -m pip install --upgrade pip
  catch pip install -r requirements_dev.txt
  catch pip install -e .
}

# @cmd Run tests
test() {
  pytest
}

# Install Java (meant for Github Actions)
jython.ensure_java() {
  if loc=$(command -v java 2>&1); then
    log "Java present in system PATH: $loc"
    return
  elif [[ $GITHUB_ACTIONS == true ]] && python -m platform | grep -qi Ubuntu; then
    log "Github Actions detected, installing Java"
    catch sudo apt update -y
    catch sudo apt install default-jre -y
  else
    err "Java missing, install it and make sure it is present in PATH"
    exit 1
  fi
}

# @cmd Install Jython to jython/
jython.install() {
  jython.ensure_java
  if [[ -e jython ]]; then
    err "Can't create jython directory. If you want to reinstall Jython, run 'run -rf jython/' first."
    err "Otherwise, just run jython.test directly."
    exit 1
  fi

  catch wget https://repo1.maven.org/maven2/org/python/jython-installer/2.7.3/jython-installer-2.7.3.jar
  catch java -jar jython-installer-2.7.3.jar -s -i mod ensurepip -e demo doc src -d jython
  rm -f jython-installer-2.7.3.jar
}

# FIXME: echo prints to stderr here, as only jython path should go to stdout, this can be handled better
jython.get_path() {
  if location=$(command -v jython 2>/dev/null); then
    log "Found Jython in the system PATH"
    echo $location
  elif [[ -x jython/bin/jython ]]; then
    log "Found Jython in jython/bin/jython"
    readlink -f jython/bin/jython
  else
    log "Jython not present, about to install to jython/"
    catch jython.install
    readlink -f jython/bin/jython
  fi
}

jython.prepare_version() {
  catch python3 -m pip install setuptools_scm
  catch python3 -c "import setuptools_scm; setuptools_scm.get_version(write_to='_version.py')"
}

jython.install_deps() {
  jython=$1
  log "Making sure pip is available in Jython"
  catch $jython -m ensurepip
  log "Installing dependencies from requirements_dev.txt"
  catch $jython -m pip install -r requirements_dev.txt
  log "Installing GQLSpection"
  catch jython.prepare_version
  catch $jython -m pip install -e .
}

# @cmd Cleanup after Jython
jython.clean() {
  catch find . -name '*$py.class' -exec rm '{}' +
  rm -rf .jython_cache
}

# @cmd Run tests to check Jython compatibility
# @alias jython
jython.test() {
  jython=$(jython.get_path)
  catch jython.install_deps $jython
  $jython -m pytest tests/
}

# @cmd Run linters
lint() {
  log "Running flake8"
  flake8 src/

  log "Running bandit"
  bandit -r src/
}

# @cmd Cleanup bytecode and cache files
clean() {
  catch find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete
  rm -rf dist .eggs .pytest_cache .coverage coverage.xml
}

configure_git() {
  if [[ $GITHUB_ACTIONS == true ]]; then
    log "GITHUB ACTIONS DETECTED"
    if ! git config --global user.email >/dev/null; then
      log "SETTING GITHUB ACTIONS EMAIL"
      git config --global user.email "41898282+github-actions[bot]@users.noreply.github.com"
    fi
    log "The email now is: $(git config user.email)"

    if ! git config --global user.name >/dev/null; then
      log "SETTING GITHUB ACTIONS USER"
      git config --global user.name "github-actions[bot]"
    fi
    log "The user now is: $(git config user.name)"
  else
    log "I DON'T THINK WE'RE RUNNING WITHIN THE GITHUB ACTIONS"
  fi
}

# @cmd Run pytest with coverage calculation
# @alias coverage
coverage.calculate() {
  catch pip install -e .
  catch command coverage run -m pytest
  catch command coverage xml
  command coverage report
}

# @cmd Generate comment body with coverage for Github Action
coverage.github_action() {
  echo 'Coverage report:'
  echo
  command coverage report --format=markdown
}

# @cmd Update coverage badge
# @arg path Path to the github repo that should be used for adding coverage badge info.
coverage.update_badge() {
  # Coverage badge is defined in an endpoint.json file, which is located in
  # 'coverage-badge' branch.
  #
  # An example format:
  # {"schemaVersion": 1, "label": "Coverage", "message": "68%", "color": "red"}
  branch="coverage-badge"
  configure_git

  if [[ $argc_path ]]; then
    pushd $argc_path
  else
    tempdir=$(mktemp -d); pushd "$tempdir"

    # Get fresh copy of the repo
    origin="git@github.com:doyensec/GQLSpection.git"
    git clone "$origin" repo; cd repo
  fi

  if ! percentage=$(command coverage report --format=total); then
    err "There was a problem during coverage calculation! Got '$percentage'%."
    exit 1
  fi

  if   (( percentage > 95 )); then
    color=brightgreen
  elif (( percentage > 90 )); then
    color=green
  elif (( percentage > 85 )); then
    color=yellow
  elif (( percentage > 80 )); then
    color=orange
  else
    color=red
  fi

  log "Updating badge with new coverage stat: ${percentage}% which corresponds to $color color."

  git fetch
  git checkout $branch

  if [[ -f coverage.json ]]; then
    log "Found the file coverage.json with the following contents: $(echo; cat coverage.json)"
  else
    err "Couldn't find the coverage.json file!"
    exit 1
  fi

  # Generate the new coverage.json
  rm -f coverage.json
  printf '{"schemaVersion": 1, "label": "Coverage", "message": "%d%%", "color": "%s"}' $percentage $color > coverage.json

  # Commit and push changes
  git add coverage.json
  # Be cautious, as the file created above could have been the same, so there are no changes and git will cause an error.
  git diff-index --cached --quiet HEAD || git commit -m 'Update coverage stats for the badge'

  git push origin

  popd
  if [[ ! $argc_path ]]; then
    rm -rf "$tempdir"
  fi
}

# @cmd Build the python release (files go to dist/)
build() {
  catch pip install build
  catch python -m build
}

# @cmd Publish release to PyPI
publish.pypi() {
  catch pip install twine

  if [[ $TWINE_PASSWORD ]]; then
    # Config parameters provided as env variables. Set the default username if not provided:
    if [[ ! $TWINE_USERNAME ]]; then
      TWINE_USERNAME="__token__"
    fi
  fi
  catch twine upload --non-interactive dist/*
}

# @cmd Publish release to Github
# @arg tag! Git tag for release (should exist already, and should have been pushed to GitHub)
publish.github() {
  catch gh release create $argc_tag --verify-tag --generate-notes --latest
}

bump_version() {
  mode=$1
  current_version=$(git describe --abbrev=0)

  IFS=. read -r major minor patch <<<"$current_version"

  re='^[0-9]+$'
  if ! [[ $major =~ $re && $minor =~ $re && $patch =~ $re ]]; then
    err "Couldn't determine previous version, '$current_version' doesn't seem like a valid semver."
    exit 1
  fi

  case $mode in
    major)
      new_tag="$((major + 1)).0.0"
      ;;
    minor)
      new_tag="$major.$((minor + 1)).0"
      ;;
    patch)
      new_tag="$major.$minor.$((patch + 1))"
      ;;
    *)
      err "Couldn't increment version, because '$mode' is unexpected (valid values are: 'major', 'minor' or 'patch')."
      exit 1
      ;;
  esac

  configure_git

  git tag -a -m "Release $new_tag" "$new_tag"
  git push origin "$new_tag"
}

# @cmd Make a new release
# @arg mode! A semver release mode: 'major', 'minor' or 'patch'
release() {
  bump_version "$argc_mode"
  build
  publish.pypi
  publish.github
}

# @cmd Make new release

eval $(runme --runme-eval "$0" "$@")
