# -*- coding: utf-8 -*-
import json
import os
import shutil
from pathlib import Path

paths = [
    r"d:\mycode\cursor_comfyui\workflows\ecommerce_koubo_stage1_compose_api.json",
    r"d:\mycode\cursor_comfyui\workflows\ecommerce_koubo_i2v_api.json",
    r"d:\mycode\cursor_comfyui\workflows\ecommerce_koubo_chocolate_mochi_LTX23_I2V.json",
    r"D:\Comfy-Desktop\ComfyUI-Shared\user\default\workflows\ecommerce_koubo_3ref_stage1_compose.json",
    r"D:\Comfy-Desktop\ComfyUI-Shared\user\default\workflows\ecommerce_koubo_3ref_stage2_i2v.json",
    r"D:\Comfy-Desktop\ComfyUI-Shared\user\default\workflows\ecommerce_koubo_chocolate_mochi_LTX23_I2V.json",
]
for p in paths:
    if not os.path.exists(p):
        print("MISSING", p)
        continue
    j = json.load(open(p, encoding="utf-8"))
    has_nodes = isinstance(j, dict) and "nodes" in j
    sample_key = next(iter(j)) if isinstance(j, dict) else None
    api_like = False
    if isinstance(j, dict) and sample_key and isinstance(j.get(sample_key), dict):
        api_like = "class_type" in j[sample_key]
    print(Path(p).name, "UI_nodes=" + str(has_nodes), "API=" + str(api_like), "bytes", os.path.getsize(p))

print("D free GB", round(shutil.disk_usage("D:\\").free / 1e9, 1))

import urllib.request

for t in ["checkpoints", "diffusion_models", "loras", "text_encoders", "vae", "clip_vision", "latent_upscale_models"]:
    m = json.load(urllib.request.urlopen(f"http://127.0.0.1:8188/models/{t}"))
    print(t, m)
