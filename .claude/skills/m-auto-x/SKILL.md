---
name: auto-x
description: "自动发布推文到 X (Twitter)。支持：发布纯文本/带图片/带视频推文、多图上传、回复推文。用于：自动发推、内容发布、图文视频分享。需要 OAuth 1.0a 四件套：X_API_KEY、X_API_SECRET、X_ACCESS_TOKEN、X_ACCESS_TOKEN_SECRET。"
---

# Auto-X - X (Twitter) 自动发布工具

专注于**自动发布**的 X (Twitter) 工具，简化发推流程。

## 前置要求

配置 OAuth 1.0a 认证：

```bash
export X_API_KEY="你的 Consumer Key"
export X_API_SECRET="你的 Consumer Secret"
export X_ACCESS_TOKEN="你的 Access Token"
export X_ACCESS_TOKEN_SECRET="你的 Access Token Secret"
```

**获取凭证**：
1. 前往 [X Developer Portal](https://developer.x.com/en/portal/dashboard)
2. 进入项目/应用 → "Keys and Tokens"
3. 生成 "Access Token and Secret"（需要有 Write 权限）

## 功能

### 1. 发布推文

```bash
# 纯文本
python post.py "Hello, X!"

# 带图片（最多4张）
python post.py "看图" -m ./photo.jpg
python post.py "多图" -m ./img1.jpg -m ./img2.jpg

# 使用已上传的 media_id
python post.py "使用 media id" --media-id 1234567890

# 回复推文
python post.py "回复内容" --reply 1234567890
```

### 2. 上传媒体

```bash
# 上传图片/视频
python upload.py ./photo.jpg
python upload.py ./video.mp4
```

支持格式：JPG, PNG, GIF, WEBP, MP4, MOV
