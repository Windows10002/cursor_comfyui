# -*- coding: utf-8 -*-
import json
import os
import urllib.request

data = json.load(urllib.request.urlopen("http://127.0.0.1:8188/object_info", timeout=60))
for n in [
    "TextEncodeZImageOmni",
    "RemoveBackground",
    "UNETLoader",
    "CLIPLoader",
    "VAELoader",
    "ModelSamplingAuraFlow",
    "CFGNorm",
    "EmptyLatentImage",
    "FluxKontextImageScale",
    "FluxKontextMultiReferenceLatentMethod",
    "ReferenceLatent",
    "ImageCompositeMasked",
    "ImageBlend",
]:
    print("====", n, "YES" if n in data else "NO")
    if n in data:
        print(json.dumps(data[n]["input"], ensure_ascii=False)[:1000])
        print("out", data[n].get("output"))

tpl = r"D:\Comfy-Desktop\ComfyUI-Installs\1\ComfyUI\.venv\Lib\site-packages\comfyui_workflow_templates_json\templates"
for f in os.listdir(tpl):
    fl = f.lower()
    if any(x in fl for x in ("qwen", "z_image", "zimage", "edit", "ic_lora")):
        print("tpl", f)
