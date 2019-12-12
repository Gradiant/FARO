@ECHO off
ECHO Analyzing documents...
PUSHD %1
SET INPUT_PATH=%CD%
POPD
IF NOT EXIST output MKDIR output
IF "%2" == "--no-ocr" (
	docker run -e FARO_DISABLE_OCR="YES" --rm --name "gradiant-faro" -v "%INPUT_PATH%":/opt/faro/input -v "%cd%"\output:/opt/faro/output gradiant/faro:1.1.0 input "%INPUT_PATH%" win
) ELSE (
	docker run --rm --name "gradiant-faro" -v "%INPUT_PATH%":/opt/faro/input -v "%cd%"\output:/opt/faro/output gradiant/faro:1.1.0 input "%INPUT_PATH%" win
)
