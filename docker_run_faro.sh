#!/bin/bash
echo "Analyzing documents..."
INPUT_PATH=$(cd "$1"; pwd)
mkdir -p output
# Generate random id to be able to cleanup after spider execution
RANDOM_NAME=$(dd bs=1 count=16 if=/dev/urandom 2> /dev/null | xxd -p)
docker run --name "faro_"$RANDOM_NAME -v "$INPUT_PATH":/opt/faro/input -v "$PWD"/output:/opt/faro/output faro input "$INPUT_PATH"
# Cleanup
docker rm "faro_"$RANDOM_NAME >/dev/null