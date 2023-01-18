#!/bin/bash
set -e -o pipefail

if ! command -v java &> /dev/null; then
  echo "Java not installed, can't proceed!"
  exit 1
fi

if command -v jython &> /dev/null; then
  echo "System jython will be used."
  jython=jython
else
  if [[ -f jython/bin/jython ]]; then
    echo "Local jython will be used."
  else
    echo "Jython not available in the path! It will get downloaded."
    wget https://repo1.maven.org/maven2/org/python/jython-installer/2.7.3/jython-installer-2.7.3.jar
    java -jar jython-installer-2.7.3.jar -s -d jython
    rm -f jython-installer-2.7.3.jar
  fi
  export PATH=$(readlink -f jython/bin):$PATH
fi

echo "============================================="
echo "Run 'jython -m ensurepip'"
jython -m ensurepip
echo "============================================="
echo

test_dir=$(readlink -f $(dirname "$0"))
src_dir=$(dirname "$test_dir")

pushd "$src_dir" >/dev/null || exit 1

  echo "============================================="
  echo "Run 'jython -m pip install -r requirements_dev.txt'"
  jython -m pip install -r requirements_dev.txt
  echo "============================================="
  echo

  echo "============================================="
  echo "Run 'jython -m pip install -e .'"
  jython -m pip install -e .
  echo "============================================="
  echo

  echo "============================================="
  echo "Run 'jython -m pytest'"
  jython -m pytest tests/
  echo "============================================="
  echo
popd >/dev/null
