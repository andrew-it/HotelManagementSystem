#!/bin/bash
python -m pytest --alluredir=test/api/result/  --allure-features=API, ./test/api/
