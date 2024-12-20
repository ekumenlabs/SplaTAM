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
    parser.add_argument("--base_dir", type=str, help="Path to the dataset.")
    parser.add_argument("--scene", type=str, help="Name of the NeRFCapture dataset. Usually has a _nerfcapture suffix.")
    parser.add_argument("--frames", type=int, help="Amount of frames to process.")
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
        image = cv2.imread(f"{sample['file_path']}.png")
        cv2.imwrite(str(images_dir.joinpath(f"{total_frames}.png")), image)

        # Depth if avaiable
        depth = None
        if has_depth:
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


from pathlib import Path

if __name__ == "__main__":
    args = parse_args()

    # Load config
    experiment = SourceFileLoader(
        os.path.basename(args.config), args.config
    ).load_module()

    config = experiment.config
    config['workdir'] = args.base_dir + "/" + args.scene
    config['data']['num_frames'] = config['num_frames'] = args.frames / 3 # SplaTAM usually stars to go nuts after 1/3 of the dataset frames.
    config['data']['base_dir'] = config['base_dir'] = args.base_dir
    config['data']['sequence'] = config['scene_name'] = args.scene

    transform_file = os.path.join(config['workdir'], 'transforms.json')
    with open(transform_file, 'r') as f:
        json_data = json.load(f)

    dataset_capture_loop(json_data, Path(config['workdir']), config['overwrite'], config['num_frames'], config['depth_scale'])
