---
name: nano-banana2
description: 使用 OpenRouter 的 Google Gemini 图像生成模型生成和编辑图片。当用户需要通过文本描述生成图片、基于已有图片进行修改编辑、AI 绘图、图像创作时使用此 skill。支持文生图和图生图两种模式，支持中英文提示词，自动保存生成的图片到本地。
---

# Nano-Banana2 图像生成与编辑

使用 OpenRouter 提供的 Google Gemini 3.1 Flash Image Preview 模型，支持：
1. **文生图 (Text-to-Image)**: 根据文本描述生成图片
2. **图生图 (Image-to-Image)**: 基于已有图片进行编辑修改

## 前置要求

设置 OpenRouter API 密钥：

```bash
export OPENROUTER_API_KEY="你的 OpenRouter API 密钥"
```

获取 API 密钥：https://openrouter.ai/keys

## 使用方法

### 1. 文生图 (Text-to-Image)

根据文本描述生成全新图片：

```bash
# 基本用法
python scripts/generate_image.py "Generate a beautiful sunset over mountains"

# 指定输出路径
python scripts/generate_image.py "一只可爱的猫咪" --output ./cat.png

# 直接传入 API 密钥
python scripts/generate_image.py "futuristic city" --api-key "your-key"
```

### 2. 图生图 (Image-to-Image)

基于已有图片进行修改编辑：

```bash
# 基本用法 - 上传图片并修改
python scripts/generate_image.py --image ./input.png "Change the style to cyberpunk"

# 修改人物穿着
python scripts/generate_image.py --image ./portrait.jpg "Change the person to wear a red jacket" --output ./edited.png

# 调整场景
python scripts/generate_image.py --image ./photo.png "Change the background to a beach at sunset" --output ./beach_version.png
```

### Python 调用

```python
from scripts.generate_image import generate_image, save_image

# 文生图
result = generate_image("a serene lake with mountains in the background")

# 图生图
result = generate_image(
    "Change the person to look younger",
    image_path="./input.png"
)

if result and result.get("images"):
    # 保存第一张图片
    save_image(result["images"][0], "output.png")
```

## 提示词技巧
图片生成提示词撰写时，首先必须明确你要画的是什么，用一句话在脑中形成清晰画面，如果你自己都说不清楚模型一定画不好；提示词开头必须先写唯一的核心主体，主体可以是人物、动物、物体或场景，但只能有一个主角，其他只能作为陪衬；主体描述要遵循从大到小的顺序，先写身份或类型，再写外观，然后是动作或姿态，最后补充情绪或状态，不要一上来就写颜色和零碎细节；任何画面都必须交代清楚场景，包括在哪里、是什么时间或氛围以及空间是开阔还是封闭，否则画面会显得空洞或混乱；光线和色彩必须明确，至少说明光源方向、光线强弱或整体色调中的一项，否则模型会随机发挥导致不可控；风格一定要具体明确，只使用清晰、常见、模型能理解的风格或媒介描述，避免使用高级感、好看之类的模糊词；构图要主动说明，例如近景中景远景、特写半身全身、居中或三分法构图，这一步能显著提升专业感；细节只选择能强化主题的关键内容，如衣物材质、环境质感或标志性道具，避免堆砌大量无关细节；所有抽象词必须转化为可被看见的具体画面描述，模型无法理解主观感受；不要使用否定句、愿望句或模糊指令，只描述你要看到的画面本身

* 图片提示词示例：
一个年轻的东方女性，短发，穿着简洁的深色风衣，双手插兜安静地站在城市街头，表情平静略带思考感，夜晚的现代都市环境，街道空旷，远处有模糊的高楼与路灯，雨后地面微微反光，整体空间开阔，柔和的侧逆光从路灯方向照亮人物轮廓，冷色调为主略带蓝灰色氛围，写实摄影风格，电影感画面，中景构图，人物居中，背景轻微虚化，细节清晰，衣物材质真实，画面干净克制。

## 输出

生成的图片自动保存到指定目录，文件名格式：
`{提示词摘要}_{时间戳}.jpg`

### 图生图
- 明确描述要修改的内容
- 可以保持主体不变，只改变风格/背景/服装等
- 支持多轮迭代编辑

**示例修改指令：**
- "Change the style to cyberpunk" (改变风格为赛博朋克)
- "Change the person to wear a red jacket" (改变人物穿着)
- "Change the background to a beach at sunset" (改变背景)
- "Make the person look younger, like a Gen Z" (让人物看起来更年轻)
- "Add a coffee cup in their hand" (添加物品)

## 脚本文件

| 脚本 | 功能 |
|------|------|
| `scripts/generate_image.py` | 生成/编辑图片并保存到本地 |

## 模型信息

- **模型**: `google/gemini-3.1-flash-image-preview`
- **提供商**: OpenRouter
- **支持模式**: 文生图、图生图
- **输出格式**: Base64 编码的图片数据
- **支持格式**: PNG, JPEG, WebP

## 图生图支持的功能

- **风格转换**: 将图片转换为不同艺术风格（赛博朋克、油画、吉卜力等）
- **人物编辑**: 修改年龄、性别、服装、表情等
- **场景调整**: 改变背景、光线、季节、环境
- **对象替换**: 替换图片中的特定对象
- **多轮迭代**: 基于生成结果继续编辑
