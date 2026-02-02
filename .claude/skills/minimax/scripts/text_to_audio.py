#!/usr/bin/env python3
"""
MiniMax 同步语音合成 API 客户端
API: POST /v1/t2a_v2

字符限制: 最多 10000 字符，超过请使用异步语音合成 (text_to_audio_async.py)
"""

import os
import json
import base64
import requests
from typing import Optional, Dict, Any
from pathlib import Path


class MiniMaxTTS:
    """MiniMax 文本转语音客户端"""

    BASE_URL = "https://api.minimaxi.com/v1/t2a_v2"
    BACKUP_URL = "https://api-bj.minimaxi.com/v1/t2a_v2"

    # 支持的模型
    MODELS = [
        "speech-2.8-hd",
        "speech-2.8-turbo",
        "speech-2.6-hd",
        "speech-2.6-turbo",
        "speech-02-hd",
        "speech-02-turbo",
        "speech-01-hd",
        "speech-01-turbo",
    ]

    # 支持的情绪
    EMOTIONS = [
        "happy", "sad", "angry", "fearful",
        "disgusted", "surprised", "calm", "fluent", "whisper"
    ]

    # 支持的音频格式
    FORMATS = ["mp3", "pcm", "flac", "wav"]

    # 支持的采样率
    SAMPLE_RATES = [8000, 16000, 22050, 24000, 32000, 44100]

    # 支持的比特率
    BITRATES = [32000, 64000, 128000, 256000]

    def __init__(self, api_key: Optional[str] = None, group_id: Optional[str] = None):
        """
        初始化 TTS 客户端

        Args:
            api_key: MiniMax API Key，默认从环境变量 MINIMAX_API_KEY 读取
            group_id: MiniMax Group ID，默认从环境变量 MINIMAX_GROUP_ID 读取
        """
        self.api_key = api_key or os.getenv("MINIMAX_API_KEY")
        self.group_id = group_id or os.getenv("MINIMAX_GROUP_ID")

        if not self.api_key:
            raise ValueError("API key is required. Set MINIMAX_API_KEY env var or pass api_key parameter.")

    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        if self.group_id:
            headers["X-Minimax-Group-Id"] = self.group_id
        return headers

    def synthesize(
        self,
        text: str,
        voice_id: str,
        model: str = "speech-2.8-hd",
        speed: float = 1.0,
        vol: float = 1.0,
        pitch: int = 0,
        emotion: Optional[str] = None,
        sample_rate: int = 32000,
        bitrate: int = 128000,
        format: str = "mp3",
        channel: int = 1,
        pronunciation_dict: Optional[Dict] = None,
        subtitle_enable: bool = False,
        continuous_sound: bool = False,
        output_format: str = "hex",
        language_boost: Optional[str] = None,
        voice_modify: Optional[Dict] = None,
        aigc_watermark: bool = False,
    ) -> Dict[str, Any]:
        """
        同步语音合成（非流式）

        Args:
            text: 待合成文本，长度限制 < 10000 字符
            voice_id: 音色 ID
            model: 模型版本，默认 speech-2.8-hd
            speed: 语速，范围 [0.5, 2]，默认 1.0
            vol: 音量，范围 (0, 10]，默认 1.0
            pitch: 语调，范围 [-12, 12]，默认 0
            emotion: 情绪，可选 happy/sad/angry/fearful/disgusted/surprised/calm/fluent/whisper
            sample_rate: 采样率，默认 32000
            bitrate: 比特率，默认 128000
            format: 音频格式，默认 mp3
            channel: 声道数，1=单声道，2=双声道，默认 1
            pronunciation_dict: 发音词典，如 {"tone": ["处理/(chu3)(li3)"]}
            subtitle_enable: 是否开启字幕，默认 False
            continuous_sound: 连续声音优化，仅 speech-2.8 模型支持，默认 False
            output_format: 输出格式，hex 或 url，默认 hex
            language_boost: 语言增强，如 Chinese/English/auto
            voice_modify: 声音效果器设置
            aigc_watermark: 是否添加水印，默认 False

        Returns:
            包含音频数据和元信息的字典
        """
        if model not in self.MODELS:
            raise ValueError(f"Unsupported model: {model}. Choose from {self.MODELS}")

        if len(text) > 10000:
            raise ValueError("Text length must be < 10000 characters. Use async API for longer text.")

        payload = {
            "model": model,
            "text": text,
            "stream": False,
            "voice_setting": {
                "voice_id": voice_id,
                "speed": speed,
                "vol": vol,
                "pitch": pitch,
            },
            "audio_setting": {
                "sample_rate": sample_rate,
                "bitrate": bitrate,
                "format": format,
                "channel": channel,
            },
            "subtitle_enable": subtitle_enable,
            "continuous_sound": continuous_sound,
            "output_format": output_format,
            "aigc_watermark": aigc_watermark,
        }

        if emotion and emotion in self.EMOTIONS:
            payload["voice_setting"]["emotion"] = emotion

        if pronunciation_dict:
            payload["pronunciation_dict"] = pronunciation_dict

        if language_boost:
            payload["language_boost"] = language_boost

        if voice_modify:
            payload["voice_modify"] = voice_modify

        response = requests.post(
            self.BASE_URL,
            headers=self._get_headers(),
            json=payload
        )
        response.raise_for_status()

        result = response.json()

        if result.get("base_resp", {}).get("status_code") != 0:
            raise APIError(
                f"API Error: {result['base_resp']['status_msg']} "
                f"(code: {result['base_resp']['status_code']})"
            )

        return result

    def save_audio(
        self,
        result: Dict[str, Any],
        filename: Optional[str] = None,
        output_dir: Optional[str] = None
    ) -> str:
        """
        保存音频数据到文件

        Args:
            result: API 返回的结果字典
            filename: 文件名（不含路径），默认使用 tts_{timestamp}.mp3
            output_dir: 输出目录，默认使用 ./assets/audios

        Returns:
            保存的文件完整路径
        """
        if "data" not in result or "audio" not in result["data"]:
            raise ValueError("Invalid result: missing audio data")

        # 确定输出路径
        if output_dir is None:
            output_dir = Path.cwd() / "assets" / "audios"
        else:
            output_dir = Path(output_dir)

        # 确保目录存在
        output_dir.mkdir(parents=True, exist_ok=True)

        # 确定文件名
        if filename is None:
            import time
            ext = result.get("extra_info", {}).get("audio_format", "mp3")
            filename = f"tts_{int(time.time())}.{ext}"

        output_path = output_dir / filename

        audio_hex = result["data"]["audio"]
        audio_bytes = bytes.fromhex(audio_hex)

        with open(output_path, "wb") as f:
            f.write(audio_bytes)

        extra_info = result.get("extra_info", {})
        print(f"Audio saved to: {output_path}")
        print(f"  Duration: {extra_info.get('audio_length', 'N/A')} ms")
        print(f"  Sample rate: {extra_info.get('audio_sample_rate', 'N/A')} Hz")
        print(f"  Size: {extra_info.get('audio_size', 'N/A')} bytes")
        print(f"  Usage characters: {extra_info.get('usage_characters', 'N/A')}")

        return str(output_path)


class APIError(Exception):
    """API 错误异常"""
    pass


def main():
    """命令行使用示例"""
    import argparse

    parser = argparse.ArgumentParser(description="MiniMax Text-to-Speech")
    parser.add_argument("--text", "-t", required=True, help="Text to synthesize")
    parser.add_argument("--voice", "-v", default="male-qn-qingse", help="Voice ID")
    parser.add_argument("--model", "-m", default="speech-2.8-hd", help="Model name")
    parser.add_argument("--output", "-o", default="output.mp3", help="Output file")
    parser.add_argument("--speed", type=float, default=1.0, help="Speech speed")
    parser.add_argument("--emotion", help="Emotion (happy/sad/angry/etc.)")

    args = parser.parse_args()

    client = MiniMaxTTS()

    result = client.synthesize(
        text=args.text,
        voice_id=args.voice,
        model=args.model,
        speed=args.speed,
        emotion=args.emotion
    )
    client.save_audio(result, args.output)
    print("Done!")


if __name__ == "__main__":
    main()
