#!/bin/bash
rm -r test/ui/result/
python -m pytest --alluredir=test/ui/result/ ./test/ui/
