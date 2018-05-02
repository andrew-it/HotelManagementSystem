#!/usr/bin/env bash
DIR=$(dirname ${BASH_SOURCE[0]})
pushd $DIR > /dev/null
REPORT_DIR=$(realpath ./result/) bench/bench.sh
popd > /dev/null
