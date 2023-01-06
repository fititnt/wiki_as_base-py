#!/bin/bash

# run with
#    ./tests/test_cli.sh

set -e
set -x

err_report() {
    echo "errexit on line $(caller)" >&2
}

trap err_report ERR

wiki_as_base --help

echo "SUCCESS"
