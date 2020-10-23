#!/bin/bash

/home/pw/MagnetiCalc/venv/bin/pydoctor \
  --verbose \
  --make-html \
  --html-output=docs \
  --add-package=magneticalc \
  --docformat=epytext \
  --project-base-dir=. \
  --project-name=MagnetiCalc \
  --project-url=https://github.com/shredEngineer/MagnetiCalc \
