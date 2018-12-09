#!/usr/bin/env bash

set -e

SCRIPTS_DIR="$(dirname "$(readlink -f "$0")")"


pushd "$SCRIPTS_DIR/.." &> /dev/null
if [[ $1 == "-r" || $1 == "--rebuild" ]]; then
    ./scripts/clean.sh
    shift
fi
if [[ ! -d dist ]]; then
    ./scripts/build.sh
fi
twine upload dist/* $@
popd  &> /dev/null
