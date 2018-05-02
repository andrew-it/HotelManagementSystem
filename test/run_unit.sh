#!/bin/bash
python -m pytest --alluredir=test/result/ --cov=app --cov-report xml:test/result/coverage.xml ./test/unit

