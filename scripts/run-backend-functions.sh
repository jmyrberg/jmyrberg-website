#!/bin/bash
conda activate jmyrberg-website
set -a
source ./functions/.env.local
set +a
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
functions-framework --source ./functions/main.py --target index --host localhost --port 8000 --debug
