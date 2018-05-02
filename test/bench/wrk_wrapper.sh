#!/usr/bin/env bash

# env:
# TARGET =      http target (/)
# SCRIPT =      path to wrk lua script
# CONNECTIONS = connections to keep open
# THREADS =     number of threads to use
# DURATION =    test duration in seconds

wrk -c $CONNECTIONS -d $DURATION -t $THREADS -s $SCRIPT $TARGET
