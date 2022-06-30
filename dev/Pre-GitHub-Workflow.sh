#!/bin/bash

# ----------------------------------------------------------------------------------------------------------------------
# Pre-GitHub-Workflow
# Prerequisites:
#     python3 -m pip install --upgrade pyright pycodestyle vulture pydoctor
# ----------------------------------------------------------------------------------------------------------------------
cd ..
set -e

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Check type annotations

# WARNING: I have disabled "reportGeneralTypeIssues" because pyright does not recognize any PyQt5 constants! (FIX THIS!)

pyright magneticalc/

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Check code style (some errors and warnings explicitly ignored)

IGNORE_ERRORS=$(cat << EOF
  E203
  E221
  E226
  E241
  E722
  W504
EOF
)
pycodestyle \
  --max-line-length=120 \
  --ignore="$(echo "$IGNORE_ERRORS" | tr -d " \t" | paste -sd ",")" \
  magneticalc/

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Check for unused code (some names explicitly ignored)

IGNORE_NAMES=$(cat << EOF
  import_hdf5
  run
  set_get_str
  closeEvent
  closeEvent
  get_wire_list
  get_current
  get_axes_list
  get_a_field_list
  get_b_field_list
  showEvent
  focusInEvent
  focusOutEvent
  bgcolor
  keyPressEvent
  setData
  flags
  headerData
EOF
)
vulture \
  --ignore-names "$(echo "$IGNORE_NAMES" | tr -d " \t" | paste -sd ",")" \
  magneticalc/

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Delete documentation

rm -r docs/*

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Create documentation

pydoctor \
  --make-html \
  --html-output=docs \
  --docformat=epytext \
  --project-base-dir=. \
  --project-name=MagnetiCalc \
  --project-url=https://github.com/shredEngineer/MagnetiCalc \
  magneticalc/

# ----------------------------------------------------------------------------------------------------------------------
cd dev/
