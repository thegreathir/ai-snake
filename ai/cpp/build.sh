#!/bin/sh

cd "$(dirname "$0")"

set -e

mkdir -p build

cd build

cmake ..
make
