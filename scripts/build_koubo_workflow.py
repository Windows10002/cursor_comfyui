# -*- coding: utf-8 -*-
import json
import os

SRC = r"D:\Comfy-Desktop\ComfyUI-Installs\1\ComfyUI\.venv\Lib\site-packages\comfyui_workflow_templates_json\templates\video_ltx2_3_i2v.json"

PROMPT = (
    "A young East Asian woman with long straight black hair stands on a sunny green lawn in a park, "
    "wearing a white asymmetrical off-shoulder blouse, black high-waisted flared trousers, a thin brown belt and black heels. "
    "Soft bokeh green trees behind her. In her left hand she holds a white plate stacked with round cocoa-dusted chocolate mochi desserts, "
    "and in her right hand a bitten chocolate mochi showing rich dark chocolate filling. "
    "She faces the camera like a live-commerce host, smiles warmly, gently presents the plate toward the lens with small natural hand gestures, "
    'and speaks clearly: "\u5b9d\u5b9d\u4eec\u770b\u8fc7\u6765\uff0c\u8fd9\u6b3e\u5de7\u514b\u529b\u96ea\u5a9a\u5a18\u5916\u76ae\u8f6f\u7cef\uff0c'
    "\u4e00\u53e3\u54ac\u4e0b\u53bb\u662f\u6d53\u90c1\u5de7\u514b\u529b\u9985\uff0c\u73b0\u5728\u4e0b\u5355\u8d85\u5212\u7b97\uff01\" "
    "A light breeze moves her hair and clothes. Vertical smartphone framing, mostly locked-off camera with subtle handheld micro-motion, "
    "natural daylight, realistic skin texture, product clearly visible."
)

NOTE = """# \u7535\u5546\u53e3\u64ad\u56fe\u751f\u89c6\u9891\uff08LTX-2.3\uff09

\u57fa\u4e8e\u4f60\u7684\u5de7\u514b\u529b\u96ea\u5a9a\u5a18\u4ea7\u54c1\u56fe\uff0c\u7528 LTX-2.3 \u505a\u7ad6\u5c4f\u53e3\u64ad\u5e26\u8d27\u89c6\u9891\u3002

## \u4f7f\u7528\u65b9\u6cd5
1. \u5de6\u4fa7 Load Image \u5df2\u6307\u5411 `ecommerce_chocolate_mochi.png`
2. \u5728 Prompt \u91cc\u6539\u53e3\u64ad\u6587\u6848\uff08\u5f15\u53f7\u5185\u4e2d\u6587\u4f1a\u9a71\u52a8\u53e3\u578b\u4e0e\u58f0\u97f3\uff09
3. \u70b9 Queue \u751f\u6210

## \u5f53\u524d\u5df2\u52a0\u8f7d\u6a21\u578b\uff08\u5747\u5728 D \u76d8\uff09
- checkpoints: `ltx-2.3-22b-dev-fp8.safetensors`
- loras: distilled + \u53ef\u5728\u5b50\u56fe\u4e2d\u52a0 talkvid
- text_encoders: `gemma_3_12B_it_fp4_mixed.safetensors`

## \u63d0\u793a
- \u53e3\u578b\u66f4\u7a33\uff1a\u53ef\u6539\u7528 ID LoRA / IA2V \u5de5\u4f5c\u6d41\uff0c\u5e76\u653e\u5165\u4e00\u6bb5\u771f\u4eba\u65c1\u767d\u97f3\u9891
- \u5206\u8fa8\u7387/\u65f6\u957f\u5728\u5b50\u56fe\u53c2\u6570\u91cc\u8c03\uff08length\u3001width\u3001height\u3001fps\uff09
"""


def walk(o, fn):
    if isinstance(o, dict):
        fn(o)
        for v in o.values():
            walk(v, fn)
    elif isinstance(o, list):
        for v in o:
            walk(v, fn)


def main():
    with open(SRC, encoding="utf-8") as f:
        j = json.load(f)

    changed = {"prompt": 0, "image": 0}

    for node in j.get("nodes", []):
        t = node.get("type")
        if t == "LoadImage":
            wv = node.get("widgets_values", [])
            if wv:
                wv[0] = "ecommerce_chocolate_mochi.png"
                changed["image"] += 1
        if t == "SaveVideo":
            wv = node.get("widgets_values", [])
            if wv:
                wv[0] = "video/ecommerce_koubo_chocolate_mochi"
        if t == "MarkdownNote" and node.get("id") == 103:
            node["title"] = "\u7535\u5546\u53e3\u64ad\u8bf4\u660e"
            node["widgets_values"] = [NOTE]

    def patch(node):
        if node.get("type") == "PrimitiveStringMultiline" and node.get("title") == "Prompt":
            node["widgets_values"] = [PROMPT]
            changed["prompt"] += 1
        if node.get("type") == "LoadImage":
            wv = node.get("widgets_values")
            if isinstance(wv, list) and wv:
                wv[0] = "ecommerce_chocolate_mochi.png"
                changed["image"] += 1

    walk(j, patch)
    print("changed", changed)

    j["id"] = "ecommerce-koubo-chocolate-mochi-ltx23"
    j.setdefault("extra", {})
    j["extra"]["workflow_name"] = "ecommerce_koubo_chocolate_mochi_LTX23_I2V"

    outs = [
        r"d:\mycode\cursor_comfyui\workflows\ecommerce_koubo_chocolate_mochi_LTX23_I2V.json",
        r"D:\Comfy-Desktop\ComfyUI-Shared\user\default\workflows\ecommerce_koubo_chocolate_mochi_LTX23_I2V.json",
        r"D:\Comfy-Desktop\ComfyUI-Installs\1\ComfyUI\user\default\workflows\ecommerce_koubo_chocolate_mochi_LTX23_I2V.json",
    ]
    for p in outs:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(j, f, ensure_ascii=False, indent=2)
        print("wrote", p)


if __name__ == "__main__":
    main()
