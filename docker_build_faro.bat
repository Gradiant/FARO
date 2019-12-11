@ECHO off

ECHO Building gradiant/faro docker image...
docker build -t gradiant/faro:1.1.0 .

git lfs pull
IF %ERRORLEVEL% NEQ 0 (
   ECHO Warning: You should either have git lfs installed on your host machine or manually download the models to get a successful build. Check README for details. 1>&2
   EXIT /B 1
)
