#!/bin/bash -e

SCRIPT_DIR=$(dirname $(readlink -f "${BASH_SOURCE[0]}"))
export PYTHONPATH=$SCRIPT_DIR

export PYTHONPATH+=:$SCRIPT_DIR/python_xp_named_pipe
export PYTHONPATH+=:$SCRIPT_DIR/spi_elements
export PYTHONPATH+=:$SCRIPT_DIR/spi_master
export PYTHONPATH+=:$SCRIPT_DIR/spi_operation
export PYTHONPATH+=:$SCRIPT_DIR/device_implementation
