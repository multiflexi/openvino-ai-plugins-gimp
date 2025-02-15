# Copyright(C) 2022-2023 Intel Corporation
# SPDX - License - Identifier: Apache - 2.0

import os
import json
import sys

plugin_loc = os.path.join(os.path.dirname(os.path.realpath(__file__)), "openvino_common")
sys.path.extend([plugin_loc])

import cv2
from stable_diffusion_run_ov import run
import torch
from gimpopenvino.tools.tools_utils import get_weight_path
import traceback
import numpy as np

def get_sb(device="CPU", prompt="northern lights", negative_prompt=None,  num_infer_steps=32, guidance_scale=7.5, init_image=None, strength=0.8, seed=None, create_gif=False, weight_path=None):
    if weight_path is None:
        weight_path = get_weight_path()
    model_path = os.path.join(weight_path, "stable-diffusion-ov")
 
    out = run(device, prompt,negative_prompt, num_infer_steps,guidance_scale, init_image, strength, seed, create_gif, model_path)
    return out


if __name__ == "__main__":
    weight_path = get_weight_path()
    with open(os.path.join(weight_path, "..", "gimp_openvino_run.json"), "r") as file:
        data_output = json.load(file)
    device = data_output["device_name"] 
    prompt = data_output["prompt"]
    negative_prompt = data_output["negative_prompt"]
    init_image = data_output["initial_image"]
    num_infer_steps = data_output["num_infer_steps"]
    guidance_scale = data_output["guidance_scale"]
    strength = data_output["strength"]
    seed = data_output["seed"]
    create_gif = data_output["create_gif"]


    #prompt = data_output["model_name"]
    #image = cv2.imread(os.path.join(weight_path, "..", "cache.png"))[:, :, ::-1]
    try:
        output = get_sb(device=device, prompt=prompt, negative_prompt=negative_prompt,num_infer_steps=num_infer_steps, guidance_scale=guidance_scale, init_image=init_image, strength=strength, seed=seed, create_gif=create_gif, weight_path=weight_path)
        cv2.imwrite(os.path.join(weight_path, "..", "cache.png"), output) #, output[:, :, ::-1])
        data_output["inference_status"] = "success"
        with open(os.path.join(weight_path, "..", "gimp_openvino_run.json"), "w") as file:
            json.dump(data_output, file)

        # Remove old temporary error files that were saved
        my_dir = os.path.join(weight_path, "..")
        for f_name in os.listdir(my_dir):
            if f_name.startswith("error_log"):
                os.remove(os.path.join(my_dir, f_name))
  

    except Exception as error:
        with open(os.path.join(weight_path, "..", "gimp_openvino_run.json"), "w") as file:
            json.dump({"inference_status": "failed"}, file)
        with open(os.path.join(weight_path, "..", "error_log.txt"), "w") as file:
            traceback.print_exception("DEBUG THE ERROR", file=file)
            # Uncoment below lines to debug            
            #e_type, e_val, e_tb = sys.exc_info()
            #traceback.print_exception(e_type, e_val, e_tb, file=file)

