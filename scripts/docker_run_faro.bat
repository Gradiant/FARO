@echo off
echo Analyzing documents...
docker run -v %cd%\%1:/opt/faro/input/%1 -v %cd%\output:/opt/faro/output faro input/%1