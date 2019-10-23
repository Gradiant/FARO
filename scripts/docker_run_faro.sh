#!/bin/bash
echo "Analyzing documents..."
INPUT_PATH=$(cd $1; pwd)
mkdir -p output
docker run -v $INPUT_PATH:/opt/faro/input -v $PWD/output:/opt/faro/output faro input \"$INPUT_PATH\"
