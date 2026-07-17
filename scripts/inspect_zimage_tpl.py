# -*- coding: utf-8 -*-
import json
import os

tpl_dir = r"D:\Comfy-Desktop\ComfyUI-Installs\1\ComfyUI\.venv\Lib\site-packages\comfyui_workflow_templates_json\templates"
for name in ["image_z_image_turbo.json", "image_z_image.json", "template_ltx2_3_ic_lora_ingredients.json"]:
    path = os.path.join(tpl_dir, name)
    if not os.path.exists(path):
        print("missing", name)
        continue
    j = json.load(open(path, encoding="utf-8"))
    print("====", name)

    def walk(o, depth=0):
        if isinstance(o, dict):
            t = o.get("type") or o.get("class_type")
            if t in (
                "UNETLoader",
                "CLIPLoader",
                "VAELoader",
                "TextEncodeZImageOmni",
                "CLIPTextEncode",
                "KSampler",
                "ModelSamplingAuraFlow",
                "LoadImage",
                "CLIPVisionLoader",
                "SaveImage",
                "EmptyLatentImage",
            ):
                print(" ", t, "wv=", str(o.get("widgets_values"))[:200], "title=", o.get("title"))
                if o.get("inputs") and isinstance(o.get("inputs"), dict):
                    print("   inputs", {k: v for k, v in list(o["inputs"].items())[:12]})
            for v in o.values():
                walk(v, depth + 1)
        elif isinstance(o, list):
            for v in o:
                walk(v, depth + 1)

    walk(j)
    # also check extra.prompt API
    extra = j.get("extra", {})
    prompt = extra.get("prompt")
    if prompt:
        print(" API nodes:")
        for k, v in prompt.items():
            print(" ", k, v.get("class_type"), str(v.get("inputs"))[:180])
