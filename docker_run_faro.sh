#!/bin/bash
echo "Analyzing documents..."
INPUT_PATH=$(cd "$1"; pwd)
mkdir -p output
if [ "$2" == "--no-ocr" ]
then
	echo "found --no-ocr argument"
	docker run -e FARO_DISABLE_OCR="YES" --rm -v "$INPUT_PATH":/opt/faro/input -v "$PWD"/output:/opt/faro/output gradiant/faro:1.1.0 input "$INPUT_PATH"
else
	docker run --rm -v "$INPUT_PATH":/opt/faro/input -v "$PWD"/output:/opt/faro/output gradiant/faro:1.1.0 input "$INPUT_PATH"
fi

