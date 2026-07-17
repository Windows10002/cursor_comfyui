# -*- coding: utf-8 -*-
import json
import urllib.request
from PIL import Image
from pathlib import Path

INPUT = Path(r"D:\Comfy-Desktop\ComfyUI-Shared\input")

# normalize all refs to same portrait size
for name in ["koubo_person.png", "koubo_bg_park.png", "koubo_product_mochi.png"]:
    im = Image.open(INPUT / name).convert("RGB")
    # contain into 576x1024 canvas
    tw, th = 576, 1024
    im.thumbnail((tw, th), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (tw, th), (255, 255, 255))
    x = (tw - im.width) // 2
    y = (th - im.height) // 2
    canvas.paste(im, (x, y))
    out = INPUT / name.replace(".png", "_norm.png")
    canvas.save(out)
    print("saved", out, canvas.size)

# free memory
req = urllib.request.Request(
    "http://127.0.0.1:8188/free",
    data=json.dumps({"unload_models": True, "free_memory": True}).encode(),
    headers={"Content-Type": "application/json"},
)
urllib.request.urlopen(req)
print("freed")

# patch workflow to use normalized images, empty latent 576x1024
wf = json.load(open(r"d:\mycode\cursor_comfyui\workflows\ecommerce_koubo_stage1_compose_api.json", encoding="utf-8"))
wf["6"]["inputs"]["image"] = "koubo_person_norm.png"
wf["7"]["inputs"]["image"] = "koubo_bg_park_norm.png"
wf["8"]["inputs"]["image"] = "koubo_product_mochi_norm.png"
# try without auto resize
wf["9"]["inputs"]["auto_resize_images"] = False

payload = json.dumps({"prompt": wf, "client_id": "test"}).encode()
req = urllib.request.Request("http://127.0.0.1:8188/prompt", data=payload, headers={"Content-Type": "application/json"})
try:
    print(urllib.request.urlopen(req).read().decode())
except Exception as e:
    print(e.read().decode() if hasattr(e, "read") else e)
