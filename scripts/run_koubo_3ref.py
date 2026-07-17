# -*- coding: utf-8 -*-
"""3-ref compose (person+bg+product) then LTX talking I2V."""
import json
import shutil
import time
import uuid
import urllib.request
from pathlib import Path
from PIL import Image

BASE = "http://127.0.0.1:8188"
ROOT = Path(r"d:\mycode\cursor_comfyui")
OUT_DIR = Path(r"D:\Comfy-Desktop\ComfyUI-Shared\output")
INPUT_DIR = Path(r"D:\Comfy-Desktop\ComfyUI-Shared\input")


def free_vram():
    req = urllib.request.Request(
        f"{BASE}/free",
        data=json.dumps({"unload_models": True, "free_memory": True}).encode(),
        headers={"Content-Type": "application/json"},
    )
    urllib.request.urlopen(req, timeout=60)


def post_prompt(workflow: dict) -> str:
    payload = json.dumps({"prompt": workflow, "client_id": str(uuid.uuid4())}).encode("utf-8")
    req = urllib.request.Request(
        f"{BASE}/prompt", data=payload, headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode())
    except Exception as e:
        body = e.read().decode() if hasattr(e, "read") else str(e)
        raise RuntimeError(body) from e
    if data.get("node_errors"):
        raise RuntimeError(json.dumps(data["node_errors"], ensure_ascii=False, indent=2))
    return data["prompt_id"]


def wait(prompt_id: str, timeout: int = 1200) -> dict:
    t0 = time.time()
    while time.time() - t0 < timeout:
        hist = json.load(urllib.request.urlopen(f"{BASE}/history/{prompt_id}"))
        if prompt_id in hist:
            return hist[prompt_id]
        time.sleep(3)
    raise TimeoutError(prompt_id)


def normalize_refs(size=(576, 1024)):
    mapping = {
        "koubo_person.png": "koubo_person_norm.png",
        "koubo_bg_park.png": "koubo_bg_park_norm.png",
        "koubo_product_mochi.png": "koubo_product_mochi_norm.png",
    }
    tw, th = size
    for src, dst in mapping.items():
        im = Image.open(INPUT_DIR / src).convert("RGB")
        im.thumbnail((tw, th), Image.Resampling.LANCZOS)
        canvas = Image.new("RGB", (tw, th), (255, 255, 255))
        canvas.paste(im, ((tw - im.width) // 2, (th - im.height) // 2))
        canvas.save(INPUT_DIR / dst)
        print("norm", dst, canvas.size)
    return mapping


def latest_output_image(hist: dict, prefix: str) -> str:
    for node_out in hist.get("outputs", {}).values():
        for img in node_out.get("images", []):
            if img.get("filename", "").startswith(prefix):
                return img["filename"], img.get("subfolder", "")
    raise RuntimeError(f"no output starting with {prefix}: {hist.get('outputs')}")


def build_i2v(image_name: str) -> dict:
    api = json.load(open(ROOT / "workflows" / "ecommerce_koubo_i2v_api.json", encoding="utf-8"))
    api["6"]["inputs"]["image"] = image_name
    api["9"]["inputs"]["text"] = (
        "The same young East Asian woman stands on the sunny green park lawn, "
        "wearing a white asymmetrical off-shoulder blouse and black flared trousers with a brown belt. "
        "She holds a plate of cocoa-dusted chocolate xue mei niang mochi and one cut-open piece "
        "showing rich dark chocolate filling. Soft tree bokeh behind her. "
        "She faces the camera like a live-commerce host, smiles warmly, gently presents the product, "
        'and speaks clearly: "\u5b9d\u5b9d\u4eec\u770b\u8fc7\u6765\uff0c\u8fd9\u6b3e\u5de7\u514b\u529b\u96ea\u5a9a\u5a18'
        "\u5916\u76ae\u8f6f\u7cef\uff0c\u4e00\u53e3\u54ac\u4e0b\u53bb\u662f\u6d53\u90c1\u5de7\u514b\u529b\u9985\uff0c"
        "\u73b0\u5728\u4e0b\u5355\u8d85\u5212\u7b97\uff01\" "
        "Light breeze in hair and clothes, vertical smartphone framing, subtle handheld motion, product stays clear."
    )
    api["25"]["inputs"]["filename_prefix"] = "video/ecommerce_koubo_3ref"
    return api


def main():
    normalize_refs()
    free_vram()

    stage1 = json.load(open(ROOT / "workflows" / "ecommerce_koubo_stage1_compose_api.json", encoding="utf-8"))
    stage1["6"]["inputs"]["image"] = "koubo_person_norm.png"
    stage1["7"]["inputs"]["image"] = "koubo_bg_park_norm.png"
    stage1["8"]["inputs"]["image"] = "koubo_product_mochi_norm.png"
    stage1["9"]["inputs"]["auto_resize_images"] = False

    print("queue stage1 compose...")
    pid1 = post_prompt(stage1)
    print("prompt_id", pid1)
    hist1 = wait(pid1)
    status = hist1.get("status", {})
    print("stage1", status.get("status_str"))
    if status.get("status_str") != "success":
        print(json.dumps(status, ensure_ascii=False)[:2000])
        raise SystemExit(1)

    fname, sub = latest_output_image(hist1, "koubo_composed_still")
    src = OUT_DIR / sub / fname if sub else OUT_DIR / fname
    dst = INPUT_DIR / fname
    shutil.copy2(src, dst)
    print("composed:", src)

    free_vram()
    print("queue stage2 i2v...")
    pid2 = post_prompt(build_i2v(fname))
    print("prompt_id", pid2)
    hist2 = wait(pid2)
    status2 = hist2.get("status", {})
    print("stage2", status2.get("status_str"))
    print("outputs", json.dumps(hist2.get("outputs", {}), ensure_ascii=False)[:1200])
    if status2.get("status_str") != "success":
        raise SystemExit(2)
    print("DONE")


if __name__ == "__main__":
    main()
