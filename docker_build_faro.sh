#!/bin/bash
git lfs pull

## Check exit status of git lfs pull
if [ $? -eq 0 ]
then
  echo "Building gradiant/faro docker image."
  docker build -t gradiant/faro:1.0.1 .
  exit 0
else
  echo "Failure: You should have git lfs installed in your host machine. Check README file" >&2
  exit 1
fi