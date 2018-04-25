python -m flake8 --output-file test/result/flake8.txt || true
flake8_junit test/result/flake8.txt test/result/flake8_junit.xml