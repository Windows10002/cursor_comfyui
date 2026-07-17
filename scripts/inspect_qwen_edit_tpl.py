# -*- coding: utf-8 -*-
"""Inspect qwen edit 2509 template structure for customization."""
import json
from pathlib import Path

p = Path(r"D:\Comfy-Desktop\ComfyUI-Installs\1\ComfyUI\.venv\Lib\site-packages\comfyui_workflow_templates_json\templates\image_qwen_image_edit_2509.json")
j = json.load(open(p, encoding="utf-8"))
print("top keys", list(j.keys()))
print("nodes", len(j.get("nodes", [])))

interesting = {
    "LoadImage",
    "UNETLoader",
    "CLIPLoader",
    "VAELoader",
    "LoraLoaderModelOnly",
    "TextEncodeQwenImageEditPlus",
    "KSampler",
    "SaveImage",
    "EmptyLatentImage",
    "ModelSamplingAuraFlow",
    "CFGNorm",
    "PrimitiveStringMultiline",
}


def walk(o):
    if isinstance(o, dict):
        t = o.get("type")
        if t in interesting:
            print(
                f"id={o.get('id')} type={t} title={o.get('title')} wv={str(o.get('widgets_values'))[:220]}"
            )
        for v in o.values():
            walk(v)
    elif isinstance(o, list):
        for v in o:
            walk(v)


walk(j)
