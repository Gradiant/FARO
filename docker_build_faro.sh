#!/bin/bash

echo "Building gradiant/faro docker image..."
docker build -t gradiant/faro:1.1.0 .

git lfs pull
if [ $? -ne 0 ]
then
  echo "Warning: You should either have git lfs installed on your host machine or manually download the models to get a successful build. Check README for details." >&2
  exit 1
fi
