#!/bin/bash
python -m nose --with-allure --logdir=test/result/  --with-xcoverage --cover-package=app --xcoverage-file=test/result/coverage.xml ./test/ui
