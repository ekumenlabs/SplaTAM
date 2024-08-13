'''
Script to capture a dataset from the NeRFCapture iOS App. Code is adapted from instant-ngp/scripts/nerfcapture2nerf.py.
https://github.com/NVlabs/instant-ngp/blob/master/scripts/nerfcapture2nerf.py
'''
#!/usr/bin/env python3

import argparse
import json
import os
import shutil
import sys
from pathlib import Path
import json
from importlib.machinery import SourceFileLoader

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.insert(0, _BASE_DIR)

import cv2
import numpy as np


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="./configs/iphone/nerfcapture.py", type=str, help="Path to config file.")
    return parser.parse_args()


def dataset_capture_loop(json_data, save_path: Path, overwrite: bool, n_frames: int, depth_scale: float):
    if save_path.exists():
        if overwrite:
            # Prompt user to confirm deletion
            if (input(f"warning! folder '{save_path}' will be deleted/replaced. continue? (Y/n)").lower().strip()+"y")[:1] != "y":
                sys.exit(1)
            shutil.rmtree(save_path)
        else:
            print(f"save_path {save_path} already exists")
            sys.exit(1)

    print("Waiting for frames...")
    # Make directory
    images_dir = save_path.joinpath("rgb")

    manifest = {
        "fl_x":  0.0,
        "fl_y":  0.0,
        "cx": 0.0,
        "cy": 0.0,
        "w": 0.0,
        "h": 0.0,
        "frames": []
    }

    total_frames = 0 # Total frames received

    for sample in json_data['frames']:
        has_depth = 'depth_path' in sample.keys()
        print(f"{total_frames + 1}/{n_frames} frames received")

        if total_frames == 0:
            save_path.mkdir(parents=True)
            images_dir.mkdir()
            manifest["w"] = sample.width
            manifest["h"] = sample.height
            manifest["cx"] = sample.cx
            manifest["cy"] = sample.cy
            manifest["fl_x"] = sample.fl_x
            manifest["fl_y"] = sample.fl_y
            manifest["integer_depth_scale"] = float(depth_scale)/65535.0
            if has_depth:
                depth_dir = save_path.joinpath("depth")
                depth_dir.mkdir()

        # RGB
        #image = np.asarray(sample.image, dtype=np.uint8).reshape((sample.height, sample.width, 3))
        image = cv2.imread(f"{sample['file_path']}.png")
        #cv2.imwrite(str(images_dir.joinpath(f"{total_frames}.png")), cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
        cv2.imwrite(str(images_dir.joinpath(f"{total_frames}.png")), image)

        # Depth if avaiable
        depth = None
        if has_depth:
            #depth = np.asarray(depth, dtype=np.uint8).view(
                #dtype=np.float32).reshape((depth.height, depth.width))
            #depth = (depth*65535/float(depth_scale)).astype(np.uint16)
            #depth = cv2.resize(depth, dsize=(
                #sample.width, sample.height), interpolation=cv2.INTER_NEAREST)
            depth=cv2.imread(sample['depth_path'])
            cv2.imwrite(str(depth_dir.joinpath(f"{total_frames}.png")), depth)

        # Transform
        X_WV = np.asarray(sample.transform_matrix,
                        dtype=np.float32).reshape((4, 4)).T

        frame = {
            "transform_matrix": X_WV.tolist(),
            "file_path": f"rgb/{total_frames}.png",
            "fl_x": sample.fl_x,
            "fl_y": sample.fl_y,
            "cx": sample.cx,
            "cy": sample.cy,
            "w": sample.width,
            "h": sample.height
        }

        if depth is not None:
            frame["depth_path"] = f"depth/{total_frames}.png"

        manifest["frames"].append(frame)

        # Update index
        if total_frames == n_frames - 1:
            print("Saving manifest...")
            # Write manifest as json
            manifest_json = json.dumps(manifest, indent=4)
            with open(save_path.joinpath("transforms.json"), "w") as f:
                f.write(manifest_json)
            print("Done")
            sys.exit(0)
        total_frames += 1



if __name__ == "__main__":
    args = parse_args()

    # Load config
    experiment = SourceFileLoader(
        os.path.basename(args.config), args.config
    ).load_module()

    transform_file = os.path.join(args.config.workdir, 'transforms.json')
    with open(transform_file, 'r') as f:
        json_data = json.load(f)


    config = experiment.config
    dataset_capture_loop(json_data, Path(config['workdir']), config['overwrite'], config['num_frames'], config['depth_scale'])
