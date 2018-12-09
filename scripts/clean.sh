#!/usr/bin/env bash

set -e

SCRIPTS_DIR="$(dirname "$(readlink -f "$0")")"


remove(){
    if [[ -d "$1" ]]; then
        rm -r "$1" && echo rm -r "$1"
    fi

}

pushd "$SCRIPTS_DIR/.." &> /dev/null
remove build
remove dist
remove libvirt_vm_optimizer.egg-info
popd  &> /dev/null
