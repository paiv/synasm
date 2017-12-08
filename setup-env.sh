#!/bin/bash
set -e

if hash virtualenv 2>/dev/null
then
  VENV="virtualenv"
else
  VENV="python -m venv"
fi

$VENV -p python3 .virtualenv/sasm

. activate

pip install -U setuptools
pip install -U pip
pip install -r requirements.txt
