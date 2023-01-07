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

wiki_as_base --titles 'User:EmericusPetro/sandbox/Wiki-as-base|User:EmericusPetro/sandbox/Wiki-as-base/data-validation'

# 295916    User:EmericusPetro/sandbox/Wiki-as-base
# 296167    User:EmericusPetro/sandbox/Wiki-as-base/data-validation
wiki_as_base --pageids '295916|296167'

echo "ok"
