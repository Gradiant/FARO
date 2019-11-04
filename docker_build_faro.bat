@ECHO off
git lfs pull

REM Check exit status of git lfs pull
IF %ERRORLEVEL% EQU 0 (
   ECHO Building gradiant/faro docker image.
   docker build -t gradiant/faro:1.0.1 .
   EXIT /B 0
) ELSE (
   ECHO Failure: You should have git lfs installed in your host machine. Check README file 1>&2
   EXIT /B 1
)