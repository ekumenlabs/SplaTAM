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
    sysctl -w net.core.rmem_max=2147483647
fi

if sysctl -a | grep -q "net.core.wmem_max = 2147483647"; then
    echo "wmem_max already set to 2147483647"
else
    echo "Setting wmem_max to 2147483647"
    sysctl -w net.core.wmem_max=2147483647
fi

base_dir=$(dirname $2)
scene="$(basename $2)_nerfcapture"
echo $base_dir $scene

# Convert Spectacular AI dataset to NeRF Capture.
python3 spectacularAI-sdk/python/mapping/replay_to_nerf.py $2 \
    --format=nerfcapture --fast \
    --image_format=png \
    --device_preset=ios-tof \
    --key_frame_distance=0.0001 \
    $base_dir/$scene

frames=$(ls -l ${base_dir}/${scene}/rgb | wc -l)
if [ -z $frames ] || [ $frames -eq 0 ]; then
    echo "Not enough frames at $base_dir/$scene/rgb!"
    exit
fi

python3 scripts/nerfcapture2dataset.py --config $1 --base_dir $base_dir --scene $scene --frames $frames

# Run SplaTAM
python3 scripts/splatam.py $1 --base_dir $base_dir --scene $scene --frames $frames

exit 0

# Visualize SplaTAM Output
python3 viz_scripts/final_recon.py $1
