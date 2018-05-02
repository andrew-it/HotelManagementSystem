#!/bin/bash
python -m nose --with-allure --logdir=test/result/ ./test/api
