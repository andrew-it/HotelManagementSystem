#!/bin/bash
rm -r test/api/result/
python -m pytest --alluredir=test/api/result/  --allure-features=API, ./test/api/
