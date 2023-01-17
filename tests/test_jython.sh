#!/bin/bash

if ! command -v jython &> /dev/null; then
  echo "Jython not available in the path!"
  exit 1
fi


echo "============================================="
echo "Run 'jython -m ensurepip'"
jython -m ensurepip
echo "============================================="
echo

echo "============================================="
echo "Run 'jython -m pip install --upgrade pip'"
jython -m pip install --upgrade pip
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
  jython -m pytest
  echo "============================================="
  echo
popd >/dev/null
