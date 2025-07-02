#!/bin/bash

# ----------------------------------------------------------------------------------------------------------------------
# Upload-to-PyPI
# Prerequisites:
#     python3 -m pip install --upgrade --user setuptools wheel twine
#     ~/.pypirc:  See: https://packaging.python.org/en/latest/specifications/pypirc/
# ----------------------------------------------------------------------------------------------------------------------
cd ..
# set -e
clear

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Package
python3 setup.py sdist bdist_wheel

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Upload
twine upload --verbose -r pypi dist/*

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Clean
rm -rf build/
rm -rf dist/
rm -rf MagnetiCalc.egg-info/

# ----------------------------------------------------------------------------------------------------------------------
cd dev/
