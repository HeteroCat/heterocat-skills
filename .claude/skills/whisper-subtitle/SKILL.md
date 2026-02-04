---
name: whisper-subtitle
description: |
  使用 OpenAI Whisper API 将音频文件转换为 SRT 字幕文件。
  当用户需要：
  1. 从音频/视频生成字幕文件
  2. 使用 Whisper 进行语音转文字
  3. 生成 SRT 格式的字幕文件
  4. 批量处理音频文件生成字幕
  时使用此 skill。
  支持的音频格式：mp3, mp4, mpeg, mpga, m4a, wav, webm 等。
---

# Whisper 字幕生成

此 skill 用于使用 OpenAI Whisper API 将音频文件转换为 SRT 字幕文件。

## 快速开始

### 1. 环境准备

确保已安装依赖：

```bash
pip install openai
```

设置 OpenAI API 密钥（二选一）：

**方式一：环境变量（推荐）**
```bash
export OPENAI_API_KEY="your-api-key"
```

**方式二：命令行参数**
```bash
python whisper_subtitle.py audio.mp3 --api-key "your-api-key"
```

### 2. 使用脚本生成字幕

脚本位于 `scripts/whisper_subtitle.py`。

**基本用法：**
```bash
python scripts/whisper_subtitle.py audio.mp3
```

**指定输出文件：**
```bash
python scripts/whisper_subtitle.py audio.mp3 -o output.srt
```

**使用特定 API 密钥：**
```bash
python scripts/whisper_subtitle.py audio.mp3 --api-key sk-xxx
```

## 作为 Python 模块使用

```python
from scripts.whisper_subtitle import transcribe_audio

# 使用环境变量中的 API 密钥
result = transcribe_audio("audio.mp3")

# 或指定输出路径
result = transcribe_audio("audio.mp3", output_path="subtitle.srt")

# 或指定 API 密钥
result = transcribe_audio("audio.mp3", api_key="your-api-key")
```

## 支持的音频格式

- MP3 (.mp3)
- MP4 (.mp4)
- MPEG (.mpeg)
- MPGA (.mpga)
- M4A (.m4a)
- WAV (.wav)
- WebM (.webm)

## 输出格式

生成的 SRT 文件格式：

```
1
00:00:00,000 --> 00:00:05,000
这是第一句话

2
00:00:05,000 --> 00:00:10,000
这是第二句话
```

## 注意事项

1. **API 密钥安全**：不要将 API 密钥硬编码在代码中，优先使用环境变量
2. **文件大小限制**：OpenAI API 对文件大小有限制（通常为 25MB）
3. **网络连接**：需要能够访问 OpenAI API 的网络环境
4. **费用**：使用 Whisper API 会产生费用，请参考 OpenAI 官方定价

## 故障排除

**错误：找不到音频文件**
- 检查文件路径是否正确
- 确保文件存在于指定路径

**错误：未提供 API 密钥**
- 设置 `OPENAI_API_KEY` 环境变量
- 或通过 `--api-key` 参数提供

**转录失败**
- 检查网络连接
- 确认 API 密钥有效且有足够余额
- 检查音频文件是否损坏
