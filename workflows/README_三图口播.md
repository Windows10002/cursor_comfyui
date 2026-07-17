# 三图电商口播工作流（人物 + 背景 + 产品 → 视频）

## 输入三张图

| 角色 | 文件名 | 说明 |
|------|--------|------|
| 图三 人物 | `koubo_person.png` | 口播主播外形/服装 |
| 图二 背景 | `koubo_bg_park.png` | 公园草地场景 |
| 图一 产品 | `koubo_product_mochi.png` | 巧克力雪媚娘特写 |

放入：`D:\Comfy-Desktop\ComfyUI-Shared\input\`

## 两阶段流程

### Stage 1 — 三图合成静图（Z-Image Turbo Omni）
工作流：`workflows/ecommerce_koubo_stage1_compose_api.json`  
输出：`koubo_composed_still_XXXX_.png`

### Stage 2 — 口播图生视频（LTX-2.3 + talkvid）
工作流：`workflows/ecommerce_koubo_i2v_api.json`（Load Image 指向合成图）  
输出：`D:\Comfy-Desktop\ComfyUI-Shared\output\video\ecommerce_koubo_3ref_XXXX_.mp4`

## 一键跑通

```bash
python scripts/run_koubo_3ref.py
```

会自动：对齐三图尺寸 → 合成 → 生成口播视频。

## 在 ComfyUI 里手动开

1. 先跑 Stage1（或直接用已生成的 `koubo_composed_still_*.png`）
2. 再加载之前的 LTX 口播工作流，把 Load Image 换成合成图
3. 改 Prompt 引号里的口播文案后 Queue

## 模型（均在 D 盘）

- Stage1：`z_image_turbo_bf16` + `qwen_3_4b` + `ae.safetensors`
- Stage2：`ltx-2.3-22b-dev-fp8` + distilled LoRA + talkvid LoRA + gemma text encoder
