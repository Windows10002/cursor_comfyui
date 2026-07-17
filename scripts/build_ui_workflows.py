# -*- coding: utf-8 -*-
"""Build openable UI workflows for 3-ref koubo pipeline."""
import json
import copy
import os
from pathlib import Path

TPL_DIR = Path(
    r"D:\Comfy-Desktop\ComfyUI-Installs\1\ComfyUI\.venv\Lib\site-packages\comfyui_workflow_templates_json\templates"
)
OUT_DIRS = [
    Path(r"d:\mycode\cursor_comfyui\workflows"),
    Path(r"D:\Comfy-Desktop\ComfyUI-Shared\user\default\workflows"),
    Path(r"D:\Comfy-Desktop\ComfyUI-Installs\1\ComfyUI\user\default\workflows"),
]

COMPOSE_PROMPT = (
    "Using Image 1 as the ONLY identity reference, keep this exact same young East Asian woman "
    "(same face, same facial features, same long straight black hair, same body proportions, "
    "same white asymmetrical off-shoulder blouse, black high-waisted flared trousers, brown belt, black heels). "
    "Do NOT change her identity or face. "
    "Replace ONLY the background with the sunny green park lawn and soft tree bokeh from Image 2, "
    "matching Image 2 lighting and atmosphere as closely as possible. "
    "Replace ONLY the desserts in her hands with the exact chocolate xue mei niang from Image 3: "
    "round cocoa-powder-dusted mochi with soft white skin and glossy dark chocolate filling, "
    "one piece cut open, plus a white plate stacked with the same desserts. "
    "Keep her pose as a live-commerce host presenting the product to camera. "
    "Photorealistic vertical full-body shot, no watermark, no text, no logo."
)

NEG_PROMPT = (
    "different person, face change, identity change, age change, different hairstyle, "
    "different clothes, deformed hands, extra fingers, wrong dessert, melted food, "
    "blurry, low quality, watermark, text, logo, cartoon, illustration"
)

VIDEO_PROMPT = (
    "Keep the exact same young East Asian woman, face and outfit unchanged. "
    "She stands on the sunny green park lawn with soft tree bokeh, holding a white plate of "
    "cocoa-dusted chocolate xue mei niang and one cut-open piece showing rich dark chocolate filling. "
    "She is a live-commerce host speaking to camera with natural mouth movement, warm smile, "
    "small hand gestures presenting the product. She says clearly in Mandarin Chinese: "
    '"\u5b9d\u5b9d\u4eec\u770b\u8fc7\u6765\uff01\u8fd9\u6b3e\u5de7\u514b\u529b\u96ea\u5a9a\u5a18\uff0c'
    "\u5916\u76ae\u8f6f\u7cef\u6709\u54ac\u52b2\uff0c\u4e00\u53e3\u54ac\u4e0b\u53bb\u662f\u6d53\u90c1\u5de7\u514b\u529b\u9985\uff0c"
    "\u751c\u800c\u4e0d\u817b\uff0c\u51b7\u85cf\u66f4\u597d\u5403\u3002\u73b0\u5728\u4e0b\u5355\u8d85\u5212\u7b97\uff0c"
    '\u5bb6\u4eba\u670b\u53cb\u90fd\u7231\u5403\uff0c\u5feb\u70b9\u4e0b\u5355\u5427\uff01" '
    "Gentle breeze moves hair and clothes. Camera mostly locked with subtle handheld micro-motion. "
    "Product stays sharp and appetizing. Vertical smartphone framing, natural daylight, no watermark."
)

NOTE_COMPOSE = """# \u4e09\u56fe\u5408\u6210\u9759\u56fe\uff08\u53ef\u6253\u5f00\u7684 UI \u5de5\u4f5c\u6d41\uff09

## \u8f93\u5165
- Image1 \u4eba\u7269\uff1a`koubo_person.png`
- Image2 \u80cc\u666f\uff1a`koubo_bg_park.png`
- Image3 \u4ea7\u54c1\uff1a`koubo_product_mochi.png`

## \u76ee\u6807
\u4eba\u7269\u5f62\u8c61\u4e0d\u53d8\uff1b\u80cc\u666f\u7528\u56fe\u4e8c\uff1b\u624b\u4e2d\u98df\u7269\u7528\u56fe\u4e00\u5de7\u514b\u529b\u96ea\u5a9a\u5a18\u3002

## \u9700\u8981\u6a21\u578b\uff08D \u76d8\uff09
- diffusion_models/`qwen_image_edit_2509_fp8_e4m3fn.safetensors`
- vae/`qwen_image_vae.safetensors`
- text_encoders/`qwen_2.5_vl_7b_fp8_scaled.safetensors`
- loras/`Qwen-Image-Edit-2509-Lightning-4steps-V1.0-bf16.safetensors`
- loras/`Qwen-Image-Edit-2509-Light-Migration.safetensors`\uff08\u53ef\u9009\uff09
"""

NOTE_VIDEO = """# \u7535\u5546\u53e3\u64ad\u56fe\u751f\u89c6\u9891\uff08\u53ef\u6253\u5f00\u7684 UI \u5de5\u4f5c\u6d41\uff09

1. Load Image \u8bf7\u7528 Stage1 \u5408\u6210\u56fe `koubo_composed_still_XXXX_.png`
2. Prompt \u91cc\u5f15\u53f7\u4e2d\u6587\u5373\u53e3\u64ad\u53f0\u8bcd
3. length \u5df2\u52a0\u957f\uff08\u7ea6 7\u20138 \u79d2 @25fps\uff09
"""


def save_all(name: str, data: dict):
    for d in OUT_DIRS:
        d.mkdir(parents=True, exist_ok=True)
        path = d / name
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("wrote", path)


def next_ids(j):
    return j.get("last_node_id", 1000) + 1, j.get("last_link_id", 1000) + 1


def build_compose_ui():
    src = TPL_DIR / "image_qwen_image_edit_2509.json"
    j = json.load(open(src, encoding="utf-8"))
    nid, lid = next_ids(j)

    # find subgraph node
    sub = None
    for n in j["nodes"]:
        if n.get("type") == "eba40a3a-f6c5-48ac-b58e-55525d06b373" or (
            isinstance(n.get("type"), str) and n["type"].count("-") == 4 and len(n.get("inputs", [])) >= 10
        ):
            # prefer the big subgraph by inputs
            if any(i.get("name") == "image2" for i in n.get("inputs", [])):
                sub = n
                break
    if sub is None:
        for n in j["nodes"]:
            if any(i.get("name") == "image2" for i in n.get("inputs", [])):
                sub = n
                break
    assert sub is not None, "subgraph not found"

    # update existing load image (person)
    for n in j["nodes"]:
        if n.get("type") == "LoadImage":
            n["widgets_values"] = ["koubo_person.png", "image"]
            n["title"] = "Image1 \u4eba\u7269"
        if n.get("type") == "MarkdownNote" and n.get("id") == 99:
            n["title"] = "\u4e09\u56fe\u5408\u6210\u8bf4\u660e"
            n["widgets_values"] = [NOTE_COMPOSE]
        if n.get("type") == "SaveImageAdvanced":
            n["widgets_values"] = ["koubo_composed_qwen", "png", "8-bit", "sRGB"]

    # create bg + product loaders
    person_node = next(n for n in j["nodes"] if n.get("type") == "LoadImage")
    base_pos = person_node.get("pos", [0, 0])

    bg = {
        "id": nid,
        "type": "LoadImage",
        "pos": [base_pos[0], base_pos[1] + 420],
        "size": [320, 314],
        "flags": {},
        "order": 20,
        "mode": 0,
        "inputs": [],
        "outputs": [
            {"name": "IMAGE", "type": "IMAGE", "links": []},
            {"name": "MASK", "type": "MASK", "links": None},
        ],
        "title": "Image2 \u80cc\u666f",
        "properties": {"Node name for S&R": "LoadImage"},
        "widgets_values": ["koubo_bg_park.png", "image"],
    }
    nid += 1
    prod = {
        "id": nid,
        "type": "LoadImage",
        "pos": [base_pos[0], base_pos[1] + 840],
        "size": [320, 314],
        "flags": {},
        "order": 21,
        "mode": 0,
        "inputs": [],
        "outputs": [
            {"name": "IMAGE", "type": "IMAGE", "links": []},
            {"name": "MASK", "type": "MASK", "links": None},
        ],
        "title": "Image3 \u4ea7\u54c1",
        "properties": {"Node name for S&R": "LoadImage"},
        "widgets_values": ["koubo_product_mochi.png", "image"],
    }
    nid += 1

    # wire image2 / image3 into subgraph
    # find input slots
    in_image2 = next(i for i in sub["inputs"] if i.get("name") == "image2")
    in_image3 = next(i for i in sub["inputs"] if i.get("name") == "image3")

    link_bg = lid
    lid += 1
    link_prod = lid
    lid += 1

    # slot indices
    slot_image2 = sub["inputs"].index(in_image2)
    slot_image3 = sub["inputs"].index(in_image3)

    in_image2["link"] = link_bg
    in_image3["link"] = link_prod
    bg["outputs"][0]["links"] = [link_bg]
    prod["outputs"][0]["links"] = [link_prod]

    # links format in modern comfy: [id, src_id, src_slot, dst_id, dst_slot, type]
    # older: objects. Detect existing
    links = j.get("links", [])
    if links and isinstance(links[0], dict):
        links.append(
            {
                "id": link_bg,
                "origin_id": bg["id"],
                "origin_slot": 0,
                "target_id": sub["id"],
                "target_slot": slot_image2,
                "type": "IMAGE",
            }
        )
        links.append(
            {
                "id": link_prod,
                "origin_id": prod["id"],
                "origin_slot": 0,
                "target_id": sub["id"],
                "target_slot": slot_image3,
                "type": "IMAGE",
            }
        )
    else:
        links.append([link_bg, bg["id"], 0, sub["id"], slot_image2, "IMAGE"])
        links.append([link_prod, prod["id"], 0, sub["id"], slot_image3, "IMAGE"])
    j["links"] = links

    # set subgraph widget values: positive/negative prompts and models
    # widgets_values order follows proxyWidgets / inputs with widgets
    # From inspect: proxyWidgets prompt, prompt(neg), seed, unet, clip, vae, turbo bool, lightning lora...
    # Safer: patch nested TextEncode and loaders inside definitions
    def walk(o):
        if isinstance(o, dict):
            t = o.get("type")
            if t == "TextEncodeQwenImageEditPlus":
                wv = o.get("widgets_values")
                if isinstance(wv, list) and wv:
                    # positive usually non-empty template prompt
                    if "Replace the cat" in str(wv[0]) or (wv[0] and "dalmatian" in str(wv[0])):
                        o["widgets_values"] = [COMPOSE_PROMPT]
                    elif wv[0] == "" or wv[0] is None:
                        # keep empty as negative unless titled
                        pass
            if t == "UNETLoader":
                o["widgets_values"] = ["qwen_image_edit_2509_fp8_e4m3fn.safetensors", "default"]
            if t == "CLIPLoader":
                o["widgets_values"] = ["qwen_2.5_vl_7b_fp8_scaled.safetensors", "qwen_image", "default"]
            if t == "VAELoader":
                o["widgets_values"] = ["qwen_image_vae.safetensors"]
            if t == "LoraLoaderModelOnly":
                name = str((o.get("widgets_values") or [""])[0])
                if "Lightning" in name or "lightning" in name.lower():
                    o["widgets_values"] = [
                        "Qwen-Image-Edit-2509-Lightning-4steps-V1.0-bf16.safetensors",
                        1.0,
                    ]
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)

    walk(j)

    # also set negative encode if we can find empty one and fill
    def set_neg(o):
        if isinstance(o, dict):
            if o.get("type") == "TextEncodeQwenImageEditPlus":
                wv = o.get("widgets_values")
                if isinstance(wv, list) and (wv[0] == "" or wv[0] is None):
                    o["widgets_values"] = [NEG_PROMPT]
            for v in o.values():
                set_neg(v)
        elif isinstance(o, list):
            for v in o:
                set_neg(v)

    set_neg(j)

    # subgraph widgets_values often stores exposed prompt fields
    wv = sub.get("widgets_values")
    if isinstance(wv, list) and len(wv) >= 2:
        # try map known positions from template: often [pos_prompt, neg_prompt, ...]
        # Update any string fields that look like prompts
        for i, val in enumerate(wv):
            if isinstance(val, str) and "dalmatian" in val:
                wv[i] = COMPOSE_PROMPT
            if isinstance(val, str) and val == "":
                # first empty may be negative; set once
                pass
        # brute: if first is prompt-like
        if wv and isinstance(wv[0], str):
            wv[0] = COMPOSE_PROMPT
        if len(wv) > 1 and isinstance(wv[1], str):
            wv[1] = NEG_PROMPT
        sub["widgets_values"] = wv

    j["nodes"].extend([bg, prod])
    j["last_node_id"] = nid
    j["last_link_id"] = lid
    j["id"] = "ecommerce-koubo-3ref-compose-qwen-ui"
    j.setdefault("extra", {})["workflow_name"] = "\u7535\u5546\u53e3\u64ad_Stage1_\u4e09\u56fe\u5408\u6210_QwenEdit"
    save_all("\u7535\u5546\u53e3\u64ad_Stage1_\u4e09\u56fe\u5408\u6210.json", j)


def build_video_ui():
    src = OUT_DIRS[0] / "ecommerce_koubo_chocolate_mochi_LTX23_I2V.json"
    if not src.exists():
        src = TPL_DIR / "video_ltx2_3_i2v.json"
    j = json.load(open(src, encoding="utf-8"))

    def walk(o):
        if isinstance(o, dict):
            t = o.get("type")
            if t == "LoadImage":
                o["widgets_values"] = ["koubo_composed_still_00002_.png", "image"]
                o["title"] = "\u5408\u6210\u9759\u56fe"
            if t == "PrimitiveStringMultiline" and o.get("title") == "Prompt":
                o["widgets_values"] = [VIDEO_PROMPT]
            if t == "SaveVideo":
                wv = o.get("widgets_values") or []
                if wv:
                    wv[0] = "video/ecommerce_koubo_3ref_long"
                    o["widgets_values"] = wv
            if t == "PrimitiveInt" and o.get("title") in ("Length", "length", "Frames"):
                o["widgets_values"] = [193, "fixed"]
            # EmptyLTXVLatentVideo default length in widgets
            if t == "EmptyLTXVLatentVideo":
                wv = o.get("widgets_values")
                if isinstance(wv, list) and len(wv) >= 3:
                    wv[2] = 193
                    o["widgets_values"] = wv
            if t == "LTXVImgToVideo":
                wv = o.get("widgets_values")
                if isinstance(wv, list) and len(wv) >= 3:
                    # width,height,length,...
                    wv[2] = 193
                    o["widgets_values"] = wv
            if t == "LTXVEmptyLatentAudio":
                wv = o.get("widgets_values")
                if isinstance(wv, list) and len(wv) >= 1:
                    wv[0] = 193
                    o["widgets_values"] = wv
            if t == "MarkdownNote" and o.get("id") == 103:
                o["title"] = "\u53e3\u64ad\u89c6\u9891\u8bf4\u660e"
                o["widgets_values"] = [NOTE_VIDEO]
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)

    walk(j)
    # also bump any PrimitiveInt named length in subgraph labels via widgets with 97/121
    def bump_len(o):
        if isinstance(o, dict):
            if o.get("type") == "PrimitiveInt":
                wv = o.get("widgets_values")
                if isinstance(wv, list) and wv and wv[0] in (97, 105, 121):
                    o["widgets_values"] = [193, wv[1] if len(wv) > 1 else "fixed"]
            for v in o.values():
                bump_len(v)
        elif isinstance(o, list):
            for v in o:
                bump_len(v)

    bump_len(j)
    j["id"] = "ecommerce-koubo-3ref-video-ltx-ui"
    j.setdefault("extra", {})["workflow_name"] = "\u7535\u5546\u53e3\u64ad_Stage2_\u56fe\u751f\u89c6\u9891"
    save_all("\u7535\u5546\u53e3\u64ad_Stage2_\u56fe\u751f\u89c6\u9891.json", j)


def cleanup_blank_api_named():
    # rename confusing API files so user doesn't open blank ones
    for d in OUT_DIRS:
        for name in [
            "ecommerce_koubo_3ref_stage1_compose.json",
            "ecommerce_koubo_3ref_stage2_i2v.json",
        ]:
            p = d / name
            if p.exists():
                newp = d / (p.stem + "_API\u4e0d\u8981\u7528\u753b\u5e03\u6253\u5f00.json")
                p.replace(newp)
                print("renamed blank API", p.name, "->", newp.name)


if __name__ == "__main__":
    build_compose_ui()
    build_video_ui()
    cleanup_blank_api_named()
    print("DONE UI workflows")
