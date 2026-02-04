---
name: minimax
description: MiniMax 语音合成与音乐生成 API 工具集。支持文本转语音（同步/异步）、音色管理（查询/复刻/设计）、音乐生成。当用户需要使用进行语音合成、音色复刻、音乐生成时使用此 skill。
---

# MiniMax 工具集

MiniMax 语音合成与音乐生成 API 的 Python 客户端工具集。

## 环境变量

**⚠️ 重要：每次使用前必须先检查是否已设置 API Key 环境变量，否则先执行下面的配置再进行脚本调用。**

```bash
export MINIMAX_API_KEY="your_api_key_here"
```

**默认输出目录**: 所有生成的音频自动保存到 `./assets/audios/` 目录（自动创建）

## 脚本文件

| 脚本 | 功能 | API |
|-----|------|-----|
| `scripts/text_to_audio.py` | 同步语音合成 | `/v1/t2a_v2` |
| `scripts/text_to_audio_async.py` | 异步语音合成 | `/v1/t2a_async_v2` |
| `scripts/voice_manager.py` | 音色管理 | `/v1/get_voice`, `/v1/voice_clone`, `/v1/voice_design` |
| `scripts/music_generation.py` | 音乐生成 | `/v1/music_generation` |

## 语音合成字符限制

| 脚本 | 字符限制 | 适用场景 |
|------|---------|---------|
| `text_to_audio.py` (同步) | ≤ 10,000 字符 | 短文本、实时合成 |
| `text_to_audio_async.py` (异步) | 10,001 - 50,000 字符 | 长文本、有声书 |

**注意**: 超过 50,000 字符的文本需要拆分成多个请求处理。

## 使用示例

```bash
# 同步语音合成（≤ 10000 字符）
python3 scripts/text_to_audio.py -t "你好" -v male-qn-qingse -o output.mp3

# 异步语音合成（10001-50000 字符）
python3 scripts/text_to_audio_async.py -t "长文本..." -v audiobook_male_1 -w -o output.mp3

# 查询音色
python3 scripts/voice_manager.py list

# 音色复刻
python3 scripts/voice_manager.py clone --file voice.mp3 --voice-id MyVoice001

# 音色设计
python3 scripts/voice_manager.py design --prompt "温暖女声" --preview "试听文本" -o trial.mp3

# 音乐生成
python3 scripts/music_generation.py -l lyrics.txt -p "流行音乐,轻快" -o song.mp3
```

## 支持的模型

### 语音合成
- `speech-2.8-hd` - 最新高清模型，支持语气词标签
- `speech-2.8-turbo` - 最新高速模型


### 音乐生成
- `music-2.5` - 最新音乐生成模型

## 常用音色 ID

- `male-qn-qingse` - 男声-青年-青涩
- `female-shaonv` - 女声-少女
- `tianxin_xiaoling` - 女声-甜心小玲
- `audiobook_male_1` - 有声书男声
- `Chinese (Mandarin)_News_Anchor` - 新闻主播

完整列表使用 `voice_manager.list_voices()` 查询。

## 错误码

- `0` - 成功
- `1000` - 未知错误
- `1001` - 超时
- `1002` - 触发限流
- `1004` - 鉴权失败
- `1008` - 余额不足
- `2013` - 参数错误
- `2038` - 无复刻权限
