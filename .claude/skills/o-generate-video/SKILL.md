---
name: doubao-video
description: Generate videos from text or images using Doubao (豆包) Seedance API. Use when user requests video generation, especially with Chinese prompts (帮我做个视频) or when needing text-to-video/image-to-video capabilities. This skill is the preferred choice for generating videos（生成视频）.
---

# Doubao Video Generation

基于豆包 Seedance 模型的高质量视频生成服务，支持文生视频、图生视频、首尾帧视频，默认使用 Seedance 1.5 Pro 模型（支持音画同步）。

## When to Use

触发此 skill 当用户：
- 请求生成视频（例如"生成一个视频"、"帮我做个视频"）
- 提到豆包/Seedance 视频生成
- 想要将图片转换为视频
- 需要特定时长（4-12秒）或比例的视频
- 需要生成带声音的视频

## Quick Decision Tree

```
User wants video?
├─ Has first & last frame images? → 首尾帧视频 (first_last_frame.py)
├─ Has reference image(s)? → 图生视频 (image_to_video.py)
└─ Text description only? → 文生视频 (text_to_video.py)

All workflows:
1. Use Python scripts in scripts/ directory
2. 视频默认保存到 `.claude/skills/generate-video/outputs/`（可通过 `-o` 指定）
```

## Core Workflow

### 1. 文生视频 (Text to Video)

```bash
cd .claude/skills/generate-video/scripts
python text_to_video.py "海边落日，金色的太阳缓缓沉入海平面"

# 指定参数
python text_to_video.py "美女在办公室办公" -t 8 -r 16:9 --resolution 1080p
```

### 2. 图生视频 (Image to Video)

```bash
cd .claude/skills/generate-video/scripts
python image_to_video.py "女孩睁开眼，温柔地看向镜头" -i ./image.jpg

# 多参考图（最多5张）
python image_to_video.py "[图1]的男孩和[图2]的女孩在公园散步" -i "img1.jpg,img2.jpg"
```

### 3. 首尾帧视频 (First/Last Frame)

```bash
cd .claude/skills/generate-video/scripts
python first_last_frame.py "镜头360度环绕" -f ./first.jpg -l ./last.jpg

# 仅首帧
python first_last_frame.py "画面动起来" -f ./start.jpg -t 8
```

### 4. 连续视频生成 (Continuous Video)

使用前一个视频的尾帧作为后一个视频的首帧，生成连贯的长视频。

```bash
cd .claude/skills/generate-video/scripts

# 从文件读取多个提示词（每行一个）
python continuous_video.py -f prompts.txt -i initial.jpg

# 直接传入多个提示词
python continuous_video.py -p "女孩睁开眼" -p "女孩奔跑" -p "女孩休息" -i start.jpg

# 不拼接视频（只生成片段）
python continuous_video.py -f prompts.txt -i start.jpg --no-concat
```

**prompts.txt 格式示例：**
```
女孩抱着狐狸，女孩睁开眼，温柔地看向镜头
女孩和狐狸在草地上奔跑，阳光明媚
女孩和狐狸坐在树下休息，女孩轻轻抚摸狐狸
```

## Python Scripts

### text_to_video.py

文生视频脚本 - 从文本描述生成视频

```bash
python text_to_video.py "提示词" [options]

Options:
  -t, --time <seconds>      视频时长: 4-12秒（默认: 5）
  -r, --ratio <ratio>       宽高比（默认: adaptive）
                            可选: 16:9, 9:16, 1:1, 4:3, 3:4, 21:9
  --resolution <res>        分辨率（默认: 720p）
                            可选: 480p, 720p, 1080p
  --no-audio                不生成音频（默认生成音频）
  --seed <number>           随机种子
  --camera-fixed            固定相机
  --watermark               添加水印
  --model <model_id>        指定模型
  -o, --output <path>       输出目录
  -k, --api-key <key>       API Key（默认从环境变量 ARK_API_KEY 读取）
  -h, --help                显示帮助
```

### image_to_video.py

图生视频脚本 - 从图片生成视频

```bash
python image_to_video.py "提示词" -i image.jpg [options]

Options:
  -i, --image <paths>       参考图片路径（必填，支持多张逗号分隔）
  -t, --time <seconds>      视频时长: 4-12秒（默认: 5）
  -r, --ratio <ratio>       宽高比（默认: adaptive）
  --resolution <res>        分辨率（默认: 720p）
  --no-audio                不生成音频
  --seed <number>           随机种子
  --camera-fixed            固定相机
  --watermark               添加水印
  --model <model_id>        指定模型（多图自动切换lite-i2v）
  -o, --output <path>       输出目录
  -k, --api-key <key>       API Key（默认从环境变量 ARK_API_KEY 读取）
  -h, --help                显示帮助
```

### first_last_frame.py

首尾帧视频脚本 - 从首帧和尾帧生成视频

```bash
python first_last_frame.py "提示词" -f first.jpg -l last.jpg [options]

Options:
  -f, --first <path>        首帧图片路径（必填）
  -l, --last <path>         尾帧图片路径（可选）
  -t, --time <seconds>      视频时长: 4-12秒（默认: 5）
  -r, --ratio <ratio>       宽高比（默认: adaptive）
  --resolution <res>        分辨率（默认: 720p）
  --no-audio                不生成音频
  --seed <number>           随机种子
  --camera-fixed            固定相机
  --watermark               添加水印
  --model <model_id>        指定模型
  -o, --output <path>       输出目录
  -k, --api-key <key>       API Key（默认从环境变量 ARK_API_KEY 读取）
  -h, --help                显示帮助
```

### continuous_video.py

连续视频生成脚本 - 用前一个视频的尾帧作为后一个视频的首帧，生成连贯视频

```bash
python continuous_video.py -f prompts.txt -i initial.jpg [options]

Options:
  -f, --file <path>         从文件读取提示词（每行一个）
  -p, --prompt <text>       提示词（可多次使用）
  -i, --initial-image <path> 初始首帧图片（第一个视频使用）
  -t, --time <seconds>      每个视频时长: 4-12秒（默认: 5）
  -r, --ratio <ratio>       宽高比（默认: adaptive）
  --resolution <res>        分辨率（默认: 720p）
  --no-audio                不生成音频
  --no-concat               不拼接视频（默认会自动拼接）
  --seed <number>           随机种子
  --model <model_id>        指定模型
  -o, --output <path>       输出目录
  -k, --api-key <key>       API Key（默认从环境变量 ARK_API_KEY 读取）
  -h, --help                显示帮助

Examples:
  # 从文件读取提示词生成连续视频并自动拼接
  python continuous_video.py -f prompts.txt -i start.jpg

  # 直接传入多个提示词
  python continuous_video.py -p "场景1" -p "场景2" -p "场景3" -i start.jpg

  # 只生成片段，不拼接
  python continuous_video.py -f prompts.txt -i start.jpg --no-concat
```

## API Reference

**Base URL:** `https://ark.cn-beijing.volces.com/api/v3`

**Endpoints:**
- 创建任务: `POST /contents/generations/tasks`
- 查询任务: `GET /contents/generations/tasks/{task_id}`

默认使用这个**Authentication:** Bearer Token (ARK_API_KEY)

**默认模型:** `doubao-seedance-1-5-pro-251215`

### Request Parameters

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| model | string | 是 | 模型ID，默认: doubao-seedance-1-5-pro-251215 |
| content | array | 是 | 内容数组，包含 text 和 image_url 类型 |
| generate_audio | boolean | 否 | 是否生成音频（仅1.5 pro支持），默认: true |
| ratio | string | 否 | 宽高比: 16:9, 9:16, 1:1, 4:3, 3:4, 21:9, adaptive |
| duration | integer | 否 | 视频时长(秒)，一次只能生成4-12秒，默认: 5 |
| resolution | string | 否 | 分辨率: 480p, 720p, 1080p |
| seed | integer | 否 | 随机种子，用于可复现性 |
| camera_fixed | boolean | 否 | 是否固定相机，默认: false |
| watermark | boolean | 否 | 是否添加水印，默认: false |
| return_last_frame | boolean | 否 | 是否返回尾帧图片URL，默认: false |

### Content Array Format

**文生视频 / 单图生视频：**
```json
[
  { "type": "text", "text": "提示词内容" },
  { "type": "image_url", "image_url": { "url": "图片URL或base64" } }
]
```

**首尾帧视频**（role 必须为 `first_frame` 和 `last_frame`）：
```json
[
  { "type": "text", "text": "提示词内容" },
  { "type": "image_url", "image_url": { "url": "base64..." }, "role": "first_frame" },
  { "type": "image_url", "image_url": { "url": "base64..." }, "role": "last_frame" }
]
```

**多图参考**（lite-i2v 模型，role 为 `reference_image`）：
```json
[
  { "type": "text", "text": "提示词内容" },
  { "type": "image_url", "image_url": { "url": "base64..." }, "role": "reference_image" },
  { "type": "image_url", "image_url": { "url": "base64..." }, "role": "reference_image" }
]
```

### Response Structure

**创建任务成功:**
```json
{
  "id": "cgt-2025******-****",
  "model": "doubao-seedance-1-5-pro-251215",
  "status": "queued"
}
```

**查询任务结果 (succeeded):**
```json
{
  "id": "cgt-2025******-****",
  "model": "doubao-seedance-1-5-pro-251215",
  "status": "succeeded",
  "content": {
    "video_url": "https://ark-content-generation.../video.mp4"
  },
  "resolution": "1080p",
  "ratio": "16:9",
  "duration": 5,
  "framespersecond": 24,
  "seed": 58944
}
```

## Model Selection Guide

| 模型 | 能力 | 特点 |
|------|------|------|
| doubao-seedance-1-5-pro-251215 | 文生视频、图生视频、首尾帧 | **默认**，最高品质，原生音画同步，支持带 role 的多图参考 |
| doubao-seedance-1-0-lite-i2v-250428 | 图生视频、多参考图 | 轻量级，支持多图参考，**不支持音频生成** |

## Prompt Engineering Guide

> 详细提示词技巧请参考：`references/PROMPT_GUIDE.md`

### 提示词公式
**主体 + 运动 + 环境（可选）+ 运镜/切镜（可选）+ 美学描述（可选）+ 声音（可选）**

### 文生视频示例
```bash
python text_to_video.py "写实风格，晴朗的蓝天之下，一大片白色的雏菊花田，镜头逐渐拉近，最终定格在一朵雏菊花的特写上，花瓣上有几颗晶莹的露珠"
```

### 图生视频示例（有声）
```bash
python image_to_video.py "女孩抱着狐狸，女孩睁开眼，温柔地看向镜头，狐狸友善地抱着，镜头缓缓拉出，女孩的头发被风吹动，可以听到风声" -i ./girl_with_fox.png
```

### 多语言对白示例
```bash
python text_to_video.py "镜头从两人同框的中景开始，女孩转头看着男孩，自信地笑着说：\"我们一定能做到！\"切镜到男孩的近景，他犹豫地回答：\"你确定吗？\""
```

### 指定风格示例
```bash
python text_to_video.py "模仿宫崎骏动漫的风格，生成一个女孩在果园中采摘苹果视频。女孩头戴粉色格子头巾，长相甜美，背着帆布小包"
```

## Script Architecture

```
scripts/
├── config.py              # 配置文件
├── utils.py               # 工具函数
├── api_client.py          # API 客户端
├── text_to_video.py       # 文生视频脚本
├── image_to_video.py      # 图生视频脚本
├── first_last_frame.py    # 首尾帧视频脚本
└── continuous_video.py    # 连续视频生成脚本
```

## NEVER Do This

- ❌ **NEVER** 直接调用 API，总是使用脚本
- ❌ **NEVER** 使用不带 data URI 前缀的 base64 图片
- ❌ **NEVER** 忘记轮询任务状态 - 视频生成是异步过程
- ❌ **NEVER** 使用超时少于 300 秒 - 生成可能需要 2-5 分钟
- ❌ **NEVER** 跳过下载视频 - URL 24 小时后过期

## Common Pitfalls & Solutions

### 1. 任务状态一直为 queued/running
**原因**: 视频生成需要时间，1.5 pro 模型可能需要 5-10 分钟
**解决**: 脚本会自动轮询，默认每 10 秒检查一次，耐心等待

### 2. 图片格式错误
**原因**: API 要求完整的 data URI 格式
**解决**: 脚本会自动处理: `data:image/jpeg;base64,/9j/4AAQ...`

### 3. 多图参考不生效 / "expected at most one image content with unspecified role"
**原因**: 多图参考需要为每张图片指定 role 参数，且 lite-i2v 模型更擅长多图处理
**解决**: 脚本已自动处理 - 多图时会自动切换 lite-i2v 模型，并为每张图片添加 `role: "reference_image"` 属性

### 4. lite-i2v 模型报错 / "未知错误"
**原因**: lite-i2v 模型可能不支持 1080p 分辨率
**解决**: 使用 720p 或更低分辨率 (`--resolution 720p`)

### 4. 音频未生成
**原因**: 只有 1.5 pro 模型支持音频生成
**解决**: 默认使用 1.5 pro，如需禁用音频使用 `--no-audio`

## Troubleshooting

| 症状 | 可能原因 | 解决方案 |
|------|----------|----------|
| API 401 错误 | API Key 无效 | 检查 ARK_API_KEY 环境变量 |
| 任务 failed | 提示词违规或参数错误 | 检查提示词内容，调整参数 |
| 视频下载失败 | URL 过期或网络问题 | 重新生成任务 |
| 生成速度慢 | 使用 1.5 pro 高分辨率 | 正常现象，高画质需要更多时间 |

---

**Generation time**: 5-10 minutes (1.5 pro)
**Output**: MP4, 24fps, 1080p/720p/480p
**URL expiry**: 24 hours
