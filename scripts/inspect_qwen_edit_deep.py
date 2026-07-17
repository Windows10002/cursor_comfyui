# -*- coding: utf-8 -*-
import json
from collections import Counter

p = r"D:\Comfy-Desktop\ComfyUI-Installs\1\ComfyUI\.venv\Lib\site-packages\comfyui_workflow_templates_json\templates\image_qwen_image_edit_2509.json"
j = json.load(open(p, encoding="utf-8"))

# top nodes
print("TOP NODES:")
for n in j["nodes"]:
    print(n["id"], n["type"], n.get("title"), str(n.get("widgets_values"))[:120])

# count types in whole tree
types = Counter()


def walk(o):
    if isinstance(o, dict):
        if "type" in o and ("widgets_values" in o or "inputs" in o):
            types[o["type"]] += 1
            if o["type"] == "LoadImage":
                print("LoadImage", o.get("id"), o.get("widgets_values"), "title", o.get("title"))
            if o["type"] == "TextEncodeQwenImageEditPlus":
                print("Encode", o.get("id"), "title", o.get("title"), "wv", str(o.get("widgets_values"))[:200])
            if o["type"] == "PrimitiveStringMultiline":
                print("PromptPrim", o.get("id"), o.get("title"), str(o.get("widgets_values"))[:200])
        for v in o.values():
            walk(v)
    elif isinstance(o, list):
        for v in o:
            walk(v)


walk(j)
print("type counts", types.most_common(30))
