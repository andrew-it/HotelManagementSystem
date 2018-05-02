#!/bin/bash
python -m pytest --alluredir=test/result/  --allure-features=API, ./test/api/
