# 工作流打开说明

## ComfyUI 列表里请打开这两个（已按可打开格式重写）

1. `ecommerce_koubo_3ref_stage1_compose` — 三图合成（官方 Qwen 模板格式）
2. `ecommerce_koubo_3ref_stage2_i2v` — 口播图生视频（与第三个相同的 LTX 官方模板格式）

第三个 `ecommerce_koubo_chocolate_mochi_LTX23_I2V` 仍可作参考。

路径：`D:\Comfy-Desktop\ComfyUI-Shared\user\default\workflows\`

若列表仍显示旧空白版：重启 ComfyUI，或把同名 `.png` 拖进画布。

## 配音 / 字幕

- **保留配音**（中文口播 + talkvid）
- **禁止烧录字幕**（字幕请后期自己加）

## 一键生成

```bash
python d:\mycode\cursor_comfyui\scripts\run_koubo_clean.py
```

输出：`output/video/ecommerce_koubo_3ref_voice_nosub_XXXX_.mp4`
