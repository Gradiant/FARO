#!/bin/bash
echo "Analyzing documents..."
docker run -v $PWD/$1:/opt/faro/input/$1 -v $PWD/output:/opt/faro/output faro input/$1
