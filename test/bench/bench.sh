#!/usr/bin/env bash
# env: REPORT_DIR

# Set target url
if [ -z "$TARGET" ]; then
    export TARGET="http://127.0.0.1:5000"
fi

# Set bench parameters
export CONNECTIONS=32
export THREADS=2
export DURATION=30

# move to the script dir
pushd $(dirname ${BASH_SOURCE[0]}) > /dev/null

mkdir -p $REPORT_DIR

for script in wrk_scripts/*; do
    SCRIPT=$script ./wrk_wrapper.sh > $REPORT_DIR/$(basename $script | sed 's/\.lua//').wrk
done

# move back
popd > /dev/null

# Unset env
unset TARGET
unset CONNECTIONS
unset THREADS
unset DURATION
unset SCRIPT
