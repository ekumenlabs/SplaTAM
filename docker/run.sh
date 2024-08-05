#!/bin/bash

timestamp=$(date +%s)

docker run -it \
    --volume ./:/ws/SplaTAM/ \
    --volume /tmp/.X11-unix:/tmp/.X11-unix \
    --rm \
    --env NVIDIA_VISIBLE_DEVICES=all \
    --env NVIDIA_DRIVER_CAPABILITIES=all \
    --env DISPLAY=$DISPLAY \
    --net=host \
    --privileged \
    --group-add audio \
    --group-add video \
    --ulimit memlock=-1 \
    --ulimit stack=67108864 \
    --name splatam-$timestamp \
    --ipc=host \
    --gpus all \
    splatam-env \
    /bin/bash
    
