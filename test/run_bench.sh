#!/usr/bin/env bash
DIR=$(dirname ${BASH_SOURCE[0]})
pushd $DIR > /dev/null
REPORT_DIR=$(realpath ./bench/result) bench/bench.sh
popd > /dev/null
