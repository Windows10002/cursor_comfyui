# 电商口播图生视频（LTX-2.3）

用产品静图生成竖屏口播带货视频（含口型与旁白音频）。

## 文件

| 文件 | 用途 |
|------|------|
| `workflows/ecommerce_koubo_chocolate_mochi_LTX23_I2V.json` | ComfyUI 桌面端完整 UI 工作流（官方 I2V 模板定制） |
| `workflows/ecommerce_koubo_i2v_api.json` | API 精简版（已跑通） |
| `input/ecommerce_chocolate_mochi.png` | 产品参考图 |

## 在 ComfyUI 中打开

1. 打开 ComfyUI → Workflows → 加载  
   `ecommerce_koubo_chocolate_mochi_LTX23_I2V`
2. 确认 Load Image 为 `ecommerce_chocolate_mochi.png`
3. 修改 Prompt 里引号中的口播文案
4. Queue 生成

输出目录：`D:\Comfy-Desktop\ComfyUI-Shared\output\video\`

## 模型位置（均在 D 盘，不在 C 盘）

- 安装：`D:\Comfy-Desktop\`
- 权重：`D:\Comfy-Desktop\ComfyUI-Shared\models\`
- 输入/输出：`D:\Comfy-Desktop\ComfyUI-Shared\input` / `output`
- C 盘仅有路径配置文件：`C:\Users\sutai\AppData\Roaming\Comfy Desktop\shared_model_paths.yaml`（指向 D 盘）

## 参数建议

- 分辨率：竖屏 `576x1024`（可调，需为 32 倍数）
- 时长：`length=97` ≈ 3.9 秒 @25fps；加长可试 121
- talkvid LoRA：增强口播口型；有真人旁白音频时效果更好（可用官方 `video_ltx2_3_id_lora` / `ia2v`）
