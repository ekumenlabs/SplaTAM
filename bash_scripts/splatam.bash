#!/bin/bash

# check rmem_max and wmem_max, and increase size if necessary
if [ "$#" -ne 2 ]; then
    echo "Usage: bash_scripts/splatam.bash <config_file> <dataset_dir>"
    exit
fi

if [ ! -f $1 ]; then
    echo "Config file not found!"
    exit
fi
if [ ! -d $2]; then
    echo "Dataset directory not found!"
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

FRAMES=$(ls -l $2/rgb | wc -l)
if [ -z FRAMES ] || [ FRAMES -eq 0 ]; then
    echo "Not enough frames at $2/rgb!"
    exit
fi

python3 scripts/splatam.py --config $1 --dataset $2 --frames $FRAMES
