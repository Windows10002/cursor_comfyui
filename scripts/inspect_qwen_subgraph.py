# -*- coding: utf-8 -*-
import json

p = r"D:\Comfy-Desktop\ComfyUI-Installs\1\ComfyUI\.venv\Lib\site-packages\comfyui_workflow_templates_json\templates\image_qwen_image_edit_2509.json"
j = json.load(open(p, encoding="utf-8"))

# inspect definitions / subgraph
defs = j.get("definitions", {})
print("definitions type", type(defs), getattr(defs, "keys", lambda: None)())
if isinstance(defs, dict):
    for k, v in defs.items():
        print("def key", k, type(v))
        if isinstance(v, dict):
            print("  keys", list(v.keys())[:20])
            if "nodes" in v:
                for n in v["nodes"]:
                    if n.get("type") in ("LoadImage", "TextEncodeQwenImageEditPlus", "ComfySwitchNode") or "Image" in str(n.get("type")):
                        print(" ", n.get("id"), n.get("type"), n.get("title"), n.get("widgets_values"))

# look at subgraph node 433
for n in j["nodes"]:
    if n["id"] == 433:
        print("subgraph node keys", n.keys())
        print("properties", json.dumps(n.get("properties", {}), ensure_ascii=False)[:500])
        inputs = n.get("inputs", [])
        print("inputs count", len(inputs))
        for i in inputs:
            print(" in", i.get("name"), i.get("label"), i.get("type"), i.get("widget"))
        for o in n.get("outputs", []):
            print(" out", o.get("name"), o.get("type"))
