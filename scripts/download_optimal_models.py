# -*- coding: utf-8 -*-
"""Download optimal models for 3-ref koubo pipeline onto D: drive."""
import shutil
from pathlib import Path
from huggingface_hub import hf_hub_download

MODELS = Path(r"D:\Comfy-Desktop\ComfyUI-Shared\models")

jobs = [
    (
        "Comfy-Org/Qwen-Image-Edit_ComfyUI",
        "split_files/diffusion_models/qwen_image_edit_2509_fp8_e4m3fn.safetensors",
        MODELS / "diffusion_models" / "qwen_image_edit_2509_fp8_e4m3fn.safetensors",
    ),
    (
        "Comfy-Org/Qwen-Image_ComfyUI",
        "split_files/vae/qwen_image_vae.safetensors",
        MODELS / "vae" / "qwen_image_vae.safetensors",
    ),
    (
        "lightx2v/Qwen-Image-Lightning",
        "Qwen-Image-Edit-2509/Qwen-Image-Edit-2509-Lightning-4steps-V1.0-bf16.safetensors",
        MODELS / "loras" / "Qwen-Image-Edit-2509-Lightning-4steps-V1.0-bf16.safetensors",
    ),
    (
        "Comfy-Org/Qwen-Image-Edit_ComfyUI",
        "split_files/loras/Qwen-Image-Edit-2509-Light-Migration.safetensors",
        MODELS / "loras" / "Qwen-Image-Edit-2509-Light-Migration.safetensors",
    ),
]


def main():
    for repo, remote, dest in jobs:
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists() and dest.stat().st_size > 10_000_000:
            print("SKIP", dest.name, dest.stat().st_size)
            continue
        print("DOWNLOAD", repo, remote)
        cached = hf_hub_download(repo_id=repo, filename=remote)
        shutil.copy2(cached, dest)
        print("OK", dest, dest.stat().st_size)


if __name__ == "__main__":
    main()
