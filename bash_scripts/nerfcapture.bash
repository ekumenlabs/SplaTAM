#!/bin/bash

# check rmem_max and wmem_max, and increase size if necessary
if [ "$#" -ne 2 ]; then
    echo "Usage: bash_scripts/nerfcapture.bash <config_file> <input_dataset>"
    exit
fi

if [ ! -f $1 ]; then
    echo "Config file not found!"
    exit
fi

if sysctl -a | grep -q "net.core.rmem_max = 2147483647"; then
    echo "rmem_max already set to 2147483647"
else
    echo "Setting rmem_max to 2147483647"
    sudo sysctl -w net.core.rmem_max=2147483647
fi

if sysctl -a | grep -q "net.core.wmem_max = 2147483647"; then
    echo "wmem_max already set to 2147483647"
else
    echo "Setting wmem_max to 2147483647"
    sudo sysctl -w net.core.wmem_max=2147483647
fi

nerfcapture_dir=$(dirname $2)/nerfcapture
# Convert Spectacular AI dataset to NeRF Capture.
python3 spectacularAI-sdk/python/mapping/replay_to_nerf.py $2 \
    --format=nerfcapture --fast \
    --image_format=png \
    --device_preset=ios-tof \
    --key_frame_distance=0.0001 \
    $nerfcapture_dir

FRAMES=$(ls -l $nerfcapture_dir/rgb | wc -l)
if [ -z FRAMES ] || [ FRAMES -eq 0 ]; then
    echo "Not enough frames at $nerfcapture_dir/rgb!"
    exit
fi

# 
python3 scripts/nerfcapture2dataset.py --config $1 --dataset $nerfcapture_dir --frames $FRAMES
# Capture Dataset
python3 scripts/nerfcapture2dataset.py --config $1

# Run SplaTAM
python3 scripts/splatam.py $1

# Visualize SplaTAM Output
python3 viz_scripts/final_recon.py $1
