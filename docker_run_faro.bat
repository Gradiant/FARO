@ECHO off
ECHO Analyzing documents...
PUSHD %1
SET INPUT_PATH=%CD%
POPD
IF NOT EXIST output MKDIR output
IF [%2]==[] (
	docker run --rm --name "gradiant-faro" -v "%INPUT_PATH%":/opt/faro/input -v "%cd%"\output:/opt/faro/output gradiant/faro:latest input "%INPUT_PATH%" win
) ELSE (
	docker run --env-file "%2" --rm --name "gradiant-faro" -v "%INPUT_PATH%":/opt/faro/input -v "%cd%"\output:/opt/faro/output gradiant/faro:latest input "%INPUT_PATH%" win
)
