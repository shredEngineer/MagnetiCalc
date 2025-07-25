#!/bin/bash

# ----------------------------------------------------------------------------------------------------------------------
# Upload-to-TestPyPI
# ----------------------------------------------------------------------------------------------------------------------
cd ..
# set -e
clear

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Configure TestPyPI repository
poetry config repositories.testpypi https://test.pypi.org/legacy/

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Build and upload
poetry publish --repository testpypi --build

# ----------------------------------------------------------------------------------------------------------------------
cd dev/