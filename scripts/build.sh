#!/usr/bin/env bash

set -e

SCRIPTS_DIR="$(dirname "$(readlink -f "$0")")"


pushd "$SCRIPTS_DIR/.." &> /dev/null
/usr/bin/env python3 setup.py sdist bdist_wheel
popd  &> /dev/null
