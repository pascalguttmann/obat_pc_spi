#!/bin/bash

# Check if a file path is provided
if [ -z "$1" ]; then
  echo "Usage: $0 path/to/python_file.py"
  exit 1
fi

source go_venv.sh
source export_pythonpath.sh
sudo -E env PATH="$PATH" PYTHONPATH="$PYTHONPATH" python3 "$1"
