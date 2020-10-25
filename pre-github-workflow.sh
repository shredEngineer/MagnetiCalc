#!/bin/bash
set -e

BIN=$HOME/MagnetiCalc/venv/bin/

# Check code style
"$BIN"/pycodestyle \
  --max-line-length=120 \
  --ignore=E203,E226 \
  magneticalc/

# Check for unused code (some names explicitly excluded)
"$BIN"/vulture \
  --ignore-names run,set_get_bool,set_get_str,closeEvent,add_constraint,bgcolor,parent \
  magneticalc/

# Generate documentation
"$BIN"/pydoctor \
  --make-html \
  --html-output=docs \
  --add-package=magneticalc \
  --docformat=epytext \
  --project-base-dir=. \
  --project-name=MagnetiCalc \
  --project-url=https://github.com/shredEngineer/MagnetiCalc \
