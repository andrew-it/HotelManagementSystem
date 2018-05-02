#!/bin/bash

py.test --alluredir=test/result/ --cov=app --cov-report xml:test/result/coverage.xml ./test/unit

