# -*- coding: utf-8 -*-
"""Download model files with curl resume directly to D drive."""
import subprocess
import sys
from pathlib import Path

MODELS = Path(r"D:\Comfy-Desktop\ComfyUI-Shared\models")
MIRROR = "https://hf-mirror.com"

jobs = [
    (
        f"{MIRROR}/Comfy-Org/Qwen-Image_ComfyUI/resolve/main/split_files/vae/qwen_image_vae.safetensors",
        MODELS / "vae" / "qwen_image_vae.safetensors",
        250_000_000,
    ),
    (
        f"{MIRROR}/lightx2v/Qwen-Image-Lightning/resolve/main/Qwen-Image-Edit-2509/Qwen-Image-Edit-2509-Lightning-4steps-V1.0-bf16.safetensors",
        MODELS / "loras" / "Qwen-Image-Edit-2509-Lightning-4steps-V1.0-bf16.safetensors",
        800_000_000,
    ),
    (
        f"{MIRROR}/Comfy-Org/Qwen-Image-Edit_ComfyUI/resolve/main/split_files/loras/Qwen-Image-Edit-2509-Light-Migration.safetensors",
        MODELS / "loras" / "Qwen-Image-Edit-2509-Light-Migration.safetensors",
        200_000_000,
    ),
    (
        f"{MIRROR}/Comfy-Org/Qwen-Image-Edit_ComfyUI/resolve/main/split_files/diffusion_models/qwen_image_edit_2509_fp8_e4m3fn.safetensors",
        MODELS / "diffusion_models" / "qwen_image_edit_2509_fp8_e4m3fn.safetensors",
        20_000_000_000,
    ),
]


def download(url: str, dest: Path, min_size: int):
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size >= min_size:
        print("SKIP", dest.name, f"{dest.stat().st_size/1e9:.2f}GB", flush=True)
        return
    print("DOWNLOAD", dest.name, flush=True)
    print("URL", url, flush=True)
    # curl resume (-C -), follow redirects (-L), fail on HTTP errors (-f), show progress
    cmd = [
        "curl.exe",
        "-L",
        "-C",
        "-",
        "--retry",
        "5",
        "--retry-delay",
        "3",
        "-o",
        str(dest),
        url,
    ]
    rc = subprocess.call(cmd)
    if rc != 0:
        raise SystemExit(f"curl failed rc={rc} for {dest.name}")
    size = dest.stat().st_size
    print("OK", dest.name, f"{size/1e9:.2f}GB", flush=True)
    if size < min_size * 0.9:
        raise SystemExit(f"file too small: {dest} size={size}")


def main():
    for url, dest, min_size in jobs:
        download(url, dest, min_size)
    print("ALL DONE", flush=True)


if __name__ == "__main__":
    main()
