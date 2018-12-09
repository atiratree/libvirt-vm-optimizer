#!/usr/bin/env bash

set -e

SCRIPTS_DIR="$(dirname "$(readlink -f "$0")")"

LEAVE_BUILD_FILES=""

if [[ $1 == "-l" || $1 == "--leave-files" ]]; then
    LEAVE_BUILD_FILES="true"
    shift
fi

pushd "$SCRIPTS_DIR/.." &> /dev/null

./scripts/clean.sh

if [[ ! -d dist ]]; then
    ./scripts/build.sh
fi

twine upload dist/* $@

if [[ -z "$LEAVE_BUILD_FILES" ]]; then
    ./scripts/clean.sh
fi

popd  &> /dev/null
