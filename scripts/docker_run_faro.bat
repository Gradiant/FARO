@echo off
echo Analyzing documents...
pushd %1
set INPUT_PATH=%CD%
popd
mkdir output
docker run -v %INPUT_PATH%:/opt/faro/input -v %cd%\output:/opt/faro/output faro input %INPUT_PATH% win
