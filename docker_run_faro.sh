#!/bin/bash
echo "Analyzing documents..."
INPUT_PATH=$(cd "$1"; pwd)
mkdir -p output

if [ -z "$2" ]
then
	docker run --rm -v "$INPUT_PATH":/opt/faro/input -v "$PWD"/output:/opt/faro/output gradiant/faro:1.1.1 input "$INPUT_PATH"
else
   	docker run --env-file "$2" --rm -v "$INPUT_PATH":/opt/faro/input -v "$PWD"/output:/opt/faro/output gradiant/faro:1.1.1 input "$INPUT_PATH"
fi

