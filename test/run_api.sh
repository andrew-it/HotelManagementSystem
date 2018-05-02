#!/bin/bash
python -m pytest --alluredir=test/result/ --allure_features=API ./test/api/
