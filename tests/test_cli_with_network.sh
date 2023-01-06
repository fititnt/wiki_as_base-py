#!/bin/bash

# run with
#    ./tests/test_cli_with_network.sh

set -e
set -x

err_report() {
    echo "errexit on line $(caller)" >&2
}

trap err_report ERR

wiki_as_base --titles 'User:EmericusPetro/sandbox/Wiki-as-base' | jq --exit-status .data[1]

echo "ok"
