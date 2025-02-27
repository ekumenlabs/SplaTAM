#!/bin/bash

timestamp=$(date +%s)
CONTAINER_NAME=splatam-$timestamp
IMAGE_NAME=splatam-env

docker run -it \
    --volume ./:/ws/SplaTAM/ \
    --volume /tmp/.X11-unix:/tmp/.X11-unix \
    --env NVIDIA_VISIBLE_DEVICES=all \
    --env NVIDIA_DRIVER_CAPABILITIES=all \
    --env DISPLAY=$DISPLAY \
    --net=host \
    --privileged \
    --group-add audio \
    --group-add video \
    --ulimit memlock=-1 \
    --ulimit stack=67108864 \
    --name $CONTAINER_NAME \
    --ipc=host \
    --gpus all \
    $IMAGE_NAME \
    /bin/bash
    
# Trap workspace exits and give the user the choice to save changes.
function onexit() {
  while true; do
    read -p "Do you want to overwrite the image called '$IMAGE_NAME' with the current changes? [y/n]: " answer
    if [[ "${answer:0:1}" =~ y|Y ]]; then
      echo "Overwriting docker image..."
      docker commit $CONTAINER_NAME $IMAGE_NAME
      break
    elif [[ "${answer:0:1}" =~ n|N ]]; then
      break
    fi
  done
  docker stop $CONTAINER_NAME > /dev/null
  docker rm $CONTAINER_NAME > /dev/null
}

trap onexit EXIT

