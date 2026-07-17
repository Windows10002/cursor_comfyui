# -*- coding: utf-8 -*-
"""Preprocess -> Qwen compose -> LTX talking video WITH voice, WITHOUT burned-in subtitles."""
import json
import shutil
import time
import uuid
import urllib.request
from pathlib import Path

BASE = "http://127.0.0.1:8188"
OUT = Path(r"D:\Comfy-Desktop\ComfyUI-Shared\output")
INP = Path(r"D:\Comfy-Desktop\ComfyUI-Shared\input")

COMPOSE_POS = (
    "Keep the exact same woman from Image 1. Do not change her face or identity. "
    "Replace only the background with Image 2 park lawn. "
    "Replace only desserts with Image 3 chocolate xue mei niang. "
    "Photorealistic vertical photo. No watermark, no logo, no text, no subtitles."
)
COMPOSE_NEG = "different face, face morph, weird face, subtitles, captions, text, watermark, logo, noise, grain"

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
LENGTH = 161


def free_vram():
    urllib.request.urlopen(
        urllib.request.Request(
            f"{BASE}/free",
            data=json.dumps({"unload_models": True, "free_memory": True}).encode(),
            headers={"Content-Type": "application/json"},
        ),
        timeout=60,
    )


def post(wf):
    payload = json.dumps({"prompt": wf, "client_id": str(uuid.uuid4())}).encode()
    req = urllib.request.Request(f"{BASE}/prompt", data=payload, headers={"Content-Type": "application/json"})
    try:
        data = json.loads(urllib.request.urlopen(req, timeout=60).read().decode())
    except Exception as e:
        raise RuntimeError(e.read().decode() if hasattr(e, "read") else e) from e
    if data.get("node_errors"):
        raise RuntimeError(json.dumps(data["node_errors"], ensure_ascii=False, indent=2))
    return data["prompt_id"]


def wait(pid, timeout=1800):
    t0 = time.time()
    while time.time() - t0 < timeout:
        h = json.load(urllib.request.urlopen(f"{BASE}/history/{pid}"))
        if pid in h:
            return h[pid]
        time.sleep(3)
    raise TimeoutError(pid)


def latest(hist, prefix):
    for o in hist.get("outputs", {}).values():
        for img in o.get("images", []):
            if img.get("filename", "").startswith(prefix):
                return img["filename"], img.get("subfolder", "")
    raise RuntimeError(hist.get("outputs"))


def compose_wf():
    return {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": "qwen_image_edit_2509_fp8_e4m3fn.safetensors", "weight_dtype": "default"}},
        "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen_2.5_vl_7b_fp8_scaled.safetensors", "type": "qwen_image", "device": "default"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": "qwen_image_vae.safetensors"}},
        "4": {"class_type": "LoraLoaderModelOnly", "inputs": {"model": ["1", 0], "lora_name": "Qwen-Image-Edit-2509-Lightning-4steps-V1.0-bf16.safetensors", "strength_model": 1.0}},
        "5": {"class_type": "LoraLoaderModelOnly", "inputs": {"model": ["4", 0], "lora_name": "Qwen-Image-Edit-2509-Light-Migration.safetensors", "strength_model": 0.55}},
        "6": {"class_type": "ModelSamplingAuraFlow", "inputs": {"model": ["5", 0], "shift": 3.0}},
        "7": {"class_type": "CFGNorm", "inputs": {"model": ["6", 0], "strength": 1.0}},
        "8": {"class_type": "LoadImage", "inputs": {"image": "koubo_person_clean.png"}},
        "9": {"class_type": "LoadImage", "inputs": {"image": "koubo_bg_park_clean.png"}},
        "10": {"class_type": "LoadImage", "inputs": {"image": "koubo_product_mochi_clean.png"}},
        "11": {"class_type": "FluxKontextImageScale", "inputs": {"image": ["8", 0]}},
        "12": {"class_type": "TextEncodeQwenImageEditPlus", "inputs": {"clip": ["2", 0], "prompt": COMPOSE_POS, "vae": ["3", 0], "image1": ["11", 0], "image2": ["9", 0], "image3": ["10", 0]}},
        "13": {"class_type": "TextEncodeQwenImageEditPlus", "inputs": {"clip": ["2", 0], "prompt": COMPOSE_NEG, "vae": ["3", 0], "image1": ["11", 0], "image2": ["9", 0], "image3": ["10", 0]}},
        "14": {"class_type": "VAEEncode", "inputs": {"pixels": ["11", 0], "vae": ["3", 0]}},
        "15": {"class_type": "KSampler", "inputs": {"model": ["7", 0], "seed": 42, "steps": 4, "cfg": 1.0, "sampler_name": "euler", "scheduler": "simple", "positive": ["12", 0], "negative": ["13", 0], "latent_image": ["14", 0], "denoise": 0.62}},
        "16": {"class_type": "VAEDecode", "inputs": {"samples": ["15", 0], "vae": ["3", 0]}},
        "17": {"class_type": "SaveImage", "inputs": {"images": ["16", 0], "filename_prefix": "koubo_composed_clean"}},
    }


def video_wf(image_name: str):
    """Voice + lipsync, no burned-in subtitles."""
    return {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "ltx-2.3-22b-dev-fp8.safetensors"}},
        "2": {"class_type": "LTXAVTextEncoderLoader", "inputs": {"text_encoder": "gemma_3_12B_it_fp4_mixed.safetensors", "ckpt_name": "ltx-2.3-22b-dev-fp8.safetensors", "device": "default"}},
        "3": {"class_type": "LoraLoaderModelOnly", "inputs": {"model": ["1", 0], "lora_name": "ltx_2.3_22b_distilled_1.1_lora_dynamic_fro09_avg_rank_111_bf16.safetensors", "strength_model": 1.0}},
        "4": {"class_type": "LoraLoaderModelOnly", "inputs": {"model": ["3", 0], "lora_name": "ltx-2.3-id-lora-talkvid-3k.safetensors", "strength_model": 0.85}},
        "5": {"class_type": "LoraLoader", "inputs": {"model": ["4", 0], "clip": ["2", 0], "lora_name": "gemma-3-12b-it-abliterated_lora_rank64_bf16.safetensors", "strength_model": 0.0, "strength_clip": 1.0}},
        "6": {"class_type": "LoadImage", "inputs": {"image": image_name}},
        "7": {"class_type": "ImageResizeKJ", "inputs": {"image": ["6", 0], "width": 576, "height": 1024, "upscale_method": "lanczos", "keep_proportion": True, "divisible_by": 32, "crop": "center"}},
        "8": {"class_type": "ImageBlur", "inputs": {"image": ["7", 0], "blur_radius": 1, "sigma": 0.8}},
        "9": {"class_type": "LTXVPreprocess", "inputs": {"image": ["8", 0], "img_compression": 18}},
        "10": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["5", 1], "text": VIDEO_POS}},
        "11": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["5", 1], "text": VIDEO_NEG}},
        "12": {"class_type": "LTXVConditioning", "inputs": {"positive": ["10", 0], "negative": ["11", 0], "frame_rate": 25.0}},
        "13": {
            "class_type": "LTXVImgToVideo",
            "inputs": {
                "positive": ["12", 0],
                "negative": ["12", 1],
                "vae": ["1", 2],
                "image": ["9", 0],
                "width": 576,
                "height": 1024,
                "length": LENGTH,
                "batch_size": 1,
                "strength": 1.0,
            },
        },
        "14": {"class_type": "LTXVAudioVAELoader", "inputs": {"ckpt_name": "ltx-2.3-22b-dev-fp8.safetensors"}},
        "15": {"class_type": "LTXVEmptyLatentAudio", "inputs": {"frames_number": LENGTH, "frame_rate": 25, "batch_size": 1, "audio_vae": ["14", 0]}},
        "16": {"class_type": "LTXVConcatAVLatent", "inputs": {"video_latent": ["13", 2], "audio_latent": ["15", 0]}},
        "17": {"class_type": "RandomNoise", "inputs": {"noise_seed": 77}},
        "18": {"class_type": "CFGGuider", "inputs": {"model": ["5", 0], "positive": ["13", 0], "negative": ["13", 1], "cfg": 1.0}},
        "19": {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "euler"}},
        "20": {"class_type": "ManualSigmas", "inputs": {"sigmas": "1., 0.99375, 0.9875, 0.98125, 0.975, 0.909375, 0.725, 0.421875, 0.0"}},
        "21": {"class_type": "SamplerCustomAdvanced", "inputs": {"noise": ["17", 0], "guider": ["18", 0], "sampler": ["19", 0], "sigmas": ["20", 0], "latent_image": ["16", 0]}},
        "22": {"class_type": "LTXVSeparateAVLatent", "inputs": {"av_latent": ["21", 0]}},
        "23": {"class_type": "VAEDecode", "inputs": {"samples": ["22", 0], "vae": ["1", 2]}},
        "24": {"class_type": "LTXVAudioVAEDecode", "inputs": {"samples": ["22", 1], "audio_vae": ["14", 0]}},
        "25": {"class_type": "CreateVideo", "inputs": {"images": ["23", 0], "fps": 25.0, "audio": ["24", 0]}},
        "26": {
            "class_type": "SaveVideo",
            "inputs": {
                "video": ["25", 0],
                "filename_prefix": "video/ecommerce_koubo_3ref_voice_nosub",
                "format": "mp4",
                "codec": "h264",
            },
        },
    }


def main():
    import preprocess_refs

    preprocess_refs.main()
    free_vram()
    print("compose...")
    h1 = wait(post(compose_wf()))
    print("compose", h1.get("status", {}).get("status_str"))
    if h1.get("status", {}).get("status_str") != "success":
        raise SystemExit(1)
    fname, sub = latest(h1, "koubo_composed_clean")
    src = OUT / sub / fname if sub else OUT / fname
    shutil.copy2(src, INP / fname)
    print("composed", src)

    free_vram()
    print("voice video (no subtitles)...")
    h2 = wait(post(video_wf(fname)))
    print("video", h2.get("status", {}).get("status_str"))
    print(json.dumps(h2.get("outputs", {}), ensure_ascii=False)[:800])
    if h2.get("status", {}).get("status_str") != "success":
        raise SystemExit(2)
    print("DONE")


if __name__ == "__main__":
    main()
