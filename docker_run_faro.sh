#!/bin/bash
echo "Analyzing documents..."
INPUT_PATH=$(cd "$1"; pwd)
mkdir -p output
docker run --rm --name "gradiant/faro:1.0.1" -v "$INPUT_PATH":/opt/faro/input -v "$PWD"/output:/opt/faro/output gradiant/faro:1.0.1 input "$INPUT_PATH"