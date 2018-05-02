#!/bin/bash
mkdir -p test/static/result/
rm -r test/static/result/mypy.xml
python -m mypy app --ignore-missing-imports --junit-xml test/static/result/mypy.xml || true