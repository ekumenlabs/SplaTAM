#!/bin/bash

echo $(whoami)

docker build --build-arg UID=$(id -u) --build-arg GID=$(id -g) \
    --build-arg UNAME=$(whoami) -t splatam-env ./docker/

