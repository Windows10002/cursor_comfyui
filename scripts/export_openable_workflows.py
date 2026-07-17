# -*- coding: utf-8 -*-
"""Export openable workflows with exact names from user's ComfyUI list."""
import copy
import json
from pathlib import Path

from PIL import Image, ImageDraw, PngImagePlugin

TPL = Path(
    r"D:\Comfy-Desktop\ComfyUI-Installs\1\ComfyUI\.venv\Lib\site-packages\comfyui_workflow_templates_json\templates"
)
OPENABLE_LTX = Path(r"d:\mycode\cursor_comfyui\workflows\ecommerce_koubo_chocolate_mochi_LTX23_I2V.json")
OUTS = [
    Path(r"d:\mycode\cursor_comfyui\workflows"),
    Path(r"D:\Comfy-Desktop\ComfyUI-Shared\user\default\workflows"),
    Path(r"D:\Comfy-Desktop\ComfyUI-Installs\1\ComfyUI\user\default\workflows"),
]

VIDEO_POS = (
    "Photorealistic vertical live-commerce video matching the first frame. "
    "Keep the same young East Asian woman, stable natural face, no face morph. "
    "She stands on a sunny park lawn holding chocolate xue mei niang desserts, "
    "smiles warmly, presents the product, and speaks clearly in Mandarin Chinese with natural lip sync: "
    '"\u5b9d\u5b9d\u4eec\u770b\u8fc7\u6765\uff01\u8fd9\u6b3e\u5de7\u514b\u529b\u96ea\u5a9a\u5a18\u5916\u76ae\u8f6f\u7cef\uff0c'
    "\u4e00\u53e3\u54ac\u4e0b\u53bb\u662f\u6d53\u90c1\u5de7\u514b\u529b\u9985\uff0c\u73b0\u5728\u4e0b\u5355\u8d85\u5212\u7b97\uff01\" "
    "Clear spoken audio only. "
    "Do not render any subtitles, captions, lyrics, lower-thirds, or on-screen text. "
    "No watermark, no logo. Soft daylight, clean low-noise image, subtle handheld motion."
)
VIDEO_NEG = (
    "subtitles, captions, on-screen text, karaoke text, lower third, title text, lyrics, "
    "watermark, logo, burned-in text, closed captions, "
    "face morph, distorted face, weird face, heavy noise, grain, flicker, still frame"
)
COMPOSE_POS = (
    "Keep the exact same woman from Image 1. Do not change her face or identity. "
    "Replace only the background with Image 2 park lawn. "
    "Replace only desserts with Image 3 chocolate xue mei niang. "
    "Photorealistic vertical photo. No watermark, no logo, no text, no subtitles."
)
COMPOSE_NEG = (
    "different face, face morph, weird face, subtitles, captions, text, watermark, logo, noise, grain"
)


def save_all(name, data):
    for d in OUTS:
        d.mkdir(parents=True, exist_ok=True)
        path = d / name
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("wrote", path, "nodes", len(data.get("nodes", [])), "defs", "definitions" in data)


def save_png(stem, workflow, title):
    img = Image.new("RGB", (1280, 720), (28, 32, 40))
    draw = ImageDraw.Draw(img)
    draw.rectangle([40, 40, 1240, 680], outline=(90, 160, 255), width=3)
    draw.text((70, 80), title, fill=(240, 240, 240))
    draw.text((70, 140), "Drag into ComfyUI canvas", fill=(180, 200, 220))
    draw.text((70, 190), stem + ".json", fill=(140, 180, 140))
    meta = PngImagePlugin.PngInfo()
    meta.add_text("workflow", json.dumps(workflow, ensure_ascii=False))
    for d in OUTS:
        img.save(d / f"{stem}.png", pnginfo=meta)


def build_stage1():
    # Pristine official template = maximum openability (same class as working workflows)
    j = json.load(open(TPL / "image_qwen_image_edit_2509.json", encoding="utf-8"))
    for n in j["nodes"]:
        if n.get("type") == "LoadImage":
            n["widgets_values"] = ["koubo_person_clean.png", "image"]
            n["title"] = "Image1 Person"
        if n.get("type") == "MarkdownNote" and n.get("id") == 99:
            n["title"] = "Stage1 compose"
            n["widgets_values"] = [
                "# ecommerce_koubo_3ref_stage1_compose\n\n"
                "Official Qwen Edit template format (openable).\n"
                "Connect Image2=background, Image3=product on the center subgraph inputs.\n"
                "Or run: python scripts/run_koubo_clean.py\n"
            ]
        if n.get("type") == "SaveImageAdvanced":
            n["widgets_values"] = ["koubo_composed_clean", "png", "8-bit", "sRGB"]

    def walk(o):
        if isinstance(o, dict):
            t = o.get("type")
            if t == "TextEncodeQwenImageEditPlus":
                wv = o.get("widgets_values")
                if isinstance(wv, list) and wv:
                    if "dalmatian" in str(wv[0]) or "Replace the cat" in str(wv[0]):
                        o["widgets_values"] = [COMPOSE_POS]
                    elif wv[0] in ("", None):
                        o["widgets_values"] = [COMPOSE_NEG]
            if t == "UNETLoader":
                o["widgets_values"] = ["qwen_image_edit_2509_fp8_e4m3fn.safetensors", "default"]
            if t == "CLIPLoader":
                o["widgets_values"] = ["qwen_2.5_vl_7b_fp8_scaled.safetensors", "qwen_image", "default"]
            if t == "VAELoader":
                o["widgets_values"] = ["qwen_image_vae.safetensors"]
            if t == "LoraLoaderModelOnly":
                o["widgets_values"] = ["Qwen-Image-Edit-2509-Lightning-4steps-V1.0-bf16.safetensors", 1.0]
            if t == "KSampler":
                wv = o.get("widgets_values")
                if isinstance(wv, list) and len(wv) >= 7:
                    wv[6] = 0.62
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)

    walk(j)
    j["id"] = "ecommerce-koubo-3ref-stage1-compose"
    j.setdefault("extra", {})["workflow_name"] = "ecommerce_koubo_3ref_stage1_compose"
    return j


def build_stage2():
    # Exact clone of the workflow user CAN open
    j = json.load(open(OPENABLE_LTX, encoding="utf-8"))

    def walk(o):
        if isinstance(o, dict):
            t = o.get("type")
            if t == "LoadImage":
                o["widgets_values"] = ["koubo_composed_clean_00002_.png", "image"]
                o["title"] = "Composed still"
            if t == "PrimitiveStringMultiline":
                o["widgets_values"] = [VIDEO_POS]
            if t == "CLIPTextEncode":
                wv = o.get("widgets_values")
                if isinstance(wv, list) and wv:
                    s = str(wv[0])
                    if "blurry" in s or "watermark" in s.lower() or "subtitle" in s.lower():
                        o["widgets_values"] = [VIDEO_NEG]
            if t == "SaveVideo":
                wv = o.get("widgets_values") or []
                if wv:
                    wv[0] = "video/ecommerce_koubo_3ref_voice_nosub"
            if t == "PrimitiveInt":
                wv = o.get("widgets_values")
                if isinstance(wv, list) and wv and wv[0] in (97, 105, 121, 161, 193):
                    o["widgets_values"] = [161, wv[1] if len(wv) > 1 else "fixed"]
            if t in ("EmptyLTXVLatentVideo", "LTXVImgToVideo", "LTXVEmptyLatentAudio"):
                wv = o.get("widgets_values")
                if isinstance(wv, list):
                    if t == "EmptyLTXVLatentVideo" and len(wv) >= 3:
                        wv[2] = 161
                    if t == "LTXVImgToVideo" and len(wv) >= 3:
                        wv[2] = 161
                    if t == "LTXVEmptyLatentAudio" and wv:
                        wv[0] = 161
            if t == "LoraLoaderModelOnly":
                wv = o.get("widgets_values")
                if isinstance(wv, list) and wv and "talkvid" in str(wv[0]).lower():
                    if len(wv) >= 2:
                        wv[1] = 0.85
                    else:
                        o["widgets_values"] = [wv[0], 0.85]
            if t == "MarkdownNote" and o.get("id") == 103:
                o["title"] = "Stage2 voice no subtitles"
                o["widgets_values"] = [
                    "# ecommerce_koubo_3ref_stage2_i2v\n\n"
                    "Same openable format as chocolate_mochi_LTX23_I2V.\n"
                    "Has Mandarin voice + lipsync. No burned-in subtitles.\n"
                ]
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)

    walk(j)
    j["id"] = "ecommerce-koubo-3ref-stage2-i2v"
    j.setdefault("extra", {})["workflow_name"] = "ecommerce_koubo_3ref_stage2_i2v"
    return j


def main():
    s1, s2 = build_stage1(), build_stage2()
    save_all("ecommerce_koubo_3ref_stage1_compose.json", s1)
    save_all("ecommerce_koubo_3ref_stage2_i2v.json", s2)
    save_png("ecommerce_koubo_3ref_stage1_compose", s1, "Stage1 Compose")
    save_png("ecommerce_koubo_3ref_stage2_i2v", s2, "Stage2 I2V with voice")
    # keep aliases
    save_all("Koubo_Stage1_Compose.json", s1)
    save_all("Koubo_Stage2_Video.json", s2)
    print("DONE")


if __name__ == "__main__":
    main()
