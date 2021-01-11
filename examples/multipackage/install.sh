#!/bin/bash

set -e

if [ -d .venv ]; then
  echo "already installed; remove the venv to reinstall"
  echo "  e.g. 'rm -r .venv'"
  exit 0
fi

virtualenv --python=python3 .venv
.venv/bin/pip install -U pip setuptools
.venv/bin/pip install -e ./together-sample -e ./together-subsample
