#!/bin/bash
set -e

BIN=/usr/local/bin/

# Check type annotations
# mypy -p magneticalc --disallow-untyped-defs

# Check code style
"$BIN"/pycodestyle \
  --max-line-length=120 \
  --ignore=E203,E226,W504 \
  magneticalc/

# Check for unused code (some names explicitly excluded)
"$BIN"/vulture \
  --ignore-names run,set_get_bool,set_get_str,closeEvent,keyPressEvent,focusOutEvent,add_constraint,bgcolor,parent,Constraint,focusInEvent \
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

# Copy images for docs
cp images_for_docs/*.png docs
