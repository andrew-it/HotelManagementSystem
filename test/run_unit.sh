#!/bin/bash
python -m pytest --alluredir=test/unit/result/ --cov=app --cov-report xml:test/unit/result/coverage.xml ./test/unit/

