@ECHO off
ECHO Analyzing documents...
PUSHD %1
SET INPUT_PATH=%CD%
POPD
IF NOT EXIST output MKDIR output
docker run --rm --name "gradiant-faro" -v "%INPUT_PATH%":/opt/faro/input -v "%cd%"\output:/opt/faro/output gradiant/faro:1.0.1 input "%INPUT_PATH%" win
