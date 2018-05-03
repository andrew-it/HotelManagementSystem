#!/bin/bash
mkdir -p test/static/result/
rm -r test/static/result/flake8_junit.xml || true
python -m flake8 --output-file test/static/result/flake8.txt app || true
flake8_junit test/static/result/flake8.txt test/static/result/flake8_junit.xml