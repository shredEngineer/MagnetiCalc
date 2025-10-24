#!/bin/bash

# ----------------------------------------------------------------------------------------------------------------------
# Pre-GitHub-Workflow
# ----------------------------------------------------------------------------------------------------------------------
cd ..
set -e

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Check type annotations

# WARNING: I have disabled "reportGeneralTypeIssues" because pyright does not recognize any PyQt5 constants! (FIX THIS!)

# TODO: Fix those errors and warnings
# uv run pyright magneticalc/

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Check code style

# TODO: Fix those errors and warnings
# uv run ruff check .

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
uv run vulture \
  --ignore-names "$(echo "$IGNORE_NAMES" | tr -d " \t" | paste -sd ",")" \
  magneticalc/

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Delete documentation

rm -r docs/*

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Create documentation

uv run pydoctor \
  --make-html \
  --html-output=docs \
  --docformat=epytext \
  --project-base-dir=. \
  --project-name=MagnetiCalc \
  --project-url=https://github.com/shredEngineer/MagnetiCalc \
  magneticalc/

# ----------------------------------------------------------------------------------------------------------------------
cd dev/
