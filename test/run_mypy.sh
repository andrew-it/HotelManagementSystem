#!/bin/bash
mkdir -p test/static/result/
python -m mypy app --ignore-missing-imports --junit-xml test/static/result/mypy.xml || true