#!/bin/bash
SCRIPT_FILE=`python -c 'import os,sys;print os.path.realpath(sys.argv[1])' "$BASH_SOURCE"`
SCRIPT_DIR=$(dirname $SCRIPT_FILE)

cd $SCRIPT_DIR/../twinkle-client
python client.py "$@"
