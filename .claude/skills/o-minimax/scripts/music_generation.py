#!/usr/bin/env python3
"""
MiniMax 音乐生成 API 客户端
支持根据歌词和风格描述生成音乐
API: POST /v1/music_generation
"""

import os
import json
import base64
import requests
from typing import Optional, Dict, Any
from pathlib import Path


def _get_default_output_dir() -> Path:
    """获取默认音频输出目录"""
    return Path.cwd() / "assets" / "audios"


class MiniMaxMusicGenerator:
    """MiniMax 音乐生成客户端"""

    BASE_URL = "https://api.minimaxi.com/v1/music_generation"

    # 支持的模型
    MODELS = ["music-2.5"]

    # 支持的音频格式
    FORMATS = ["mp3", "wav", "pcm"]

    # 支持的采样率
    SAMPLE_RATES = [16000, 24000, 32000, 44100]

    # 支持的比特率
    BITRATES = [32000, 64000, 128000, 256000]

    def __init__(self, api_key: Optional[str] = None, group_id: Optional[str] = None):
        """
        初始化音乐生成客户端

        Args:
            api_key: MiniMax API Key
            group_id: MiniMax Group ID
        """
        raw_key = api_key or os.getenv("MINIMAX_API_KEY")
        self.group_id = group_id or os.getenv("MINIMAX_GROUP_ID")

        if not raw_key:
            raise ValueError(
                "API key is required.\n"
                "Please set MINIMAX_API_KEY environment variable:\n"
                "  export MINIMAX_API_KEY='Bearer sk-api-xxxxx'\n"
                "Or pass api_key parameter to MiniMaxMusicGenerator()."
            )

        # 自动添加 Bearer 前缀（如果没有的话）
        self.api_key = raw_key if raw_key.startswith("Bearer ") else f"Bearer {raw_key}"

    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": self.api_key
        }
        if self.group_id:
            headers["X-Minimax-Group-Id"] = self.group_id
        return headers

    def generate(
        self,
        lyrics: str,
        prompt: Optional[str] = None,
        model: str = "music-2.5",
        stream: bool = False,
        output_format: str = "hex",
        sample_rate: int = 44100,
        bitrate: int = 256000,
        format: str = "mp3",
        aigc_watermark: bool = False,
    ) -> Dict[str, Any]:
        """
        生成音乐

        Args:
            lyrics: 歌词内容，使用 \\n 分隔每行，支持 [Verse], [Chorus] 等结构标签
            prompt: 音乐风格描述（music-2.5 可选，其他模型必填）
            model: 模型版本，默认 music-2.5
            stream: 是否流式传输，默认 False
            output_format: 输出格式，hex 或 url，默认 hex
            sample_rate: 采样率，默认 44100
            bitrate: 比特率，默认 256000
            format: 音频格式，默认 mp3
            aigc_watermark: 是否添加水印，默认 False

        Returns:
            包含音频数据和元信息的字典
        """
        if model not in self.MODELS:
            raise ValueError(f"Unsupported model: {model}. Choose from {self.MODELS}")

        if len(lyrics) < 1 or len(lyrics) > 3500:
            raise ValueError("Lyrics length must be between 1 and 3500 characters")

        if prompt and len(prompt) > 2000:
            raise ValueError("Prompt length must be <= 2000 characters")

        if stream and output_format != "hex":
            raise ValueError("Streaming mode only supports hex output format")

        payload: Dict[str, Any] = {
            "model": model,
            "lyrics": lyrics,
            "stream": stream,
            "output_format": output_format,
            "audio_setting": {
                "sample_rate": sample_rate,
                "bitrate": bitrate,
                "format": format,
            },
            "aigc_watermark": aigc_watermark,
        }

        if prompt:
            payload["prompt"] = prompt

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
        保存生成的音乐到文件

        Args:
            result: API 返回的结果字典
            filename: 文件名（不含路径），默认使用 music_{timestamp}.mp3
            output_dir: 输出目录，默认使用 ./assets/audios

        Returns:
            保存的文件完整路径
        """
        if "data" not in result or "audio" not in result["data"]:
            raise ValueError("Invalid result: missing audio data")

        # 确定输出目录
        if output_dir is None:
            output_dir = _get_default_output_dir()
        else:
            output_dir = Path(output_dir)

        # 确保目录存在
        output_dir.mkdir(parents=True, exist_ok=True)

        # 确定文件名
        if filename is None:
            import time
            ext = result.get("extra_info", {}).get("audio_format", "mp3")
            filename = f"music_{int(time.time())}.{ext}"

        output_path = output_dir / filename

        audio_hex = result["data"]["audio"]
        audio_bytes = bytes.fromhex(audio_hex)

        with open(output_path, "wb") as f:
            f.write(audio_bytes)

        extra_info = result.get("extra_info", {})
        print(f"Music saved to: {output_path}")
        print(f"  Duration: {extra_info.get('music_duration', 'N/A')} ms")
        print(f"  Sample rate: {extra_info.get('music_sample_rate', 'N/A')} Hz")
        print(f"  Size: {extra_info.get('music_size', 'N/A')} bytes")
        return str(output_path)

    def generate_with_structure(
        self,
        verses: list[str],
        choruses: list[str],
        prompt: str,
        bridge: Optional[str] = None,
        outro: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        使用结构化歌词生成音乐

        Args:
            verses: 主歌歌词列表
            choruses: 副歌歌词列表
            prompt: 音乐风格描述
            bridge: 桥段歌词（可选）
            outro: 尾奏歌词（可选）
            **kwargs: 其他 generate 参数

        Returns:
            API 响应结果
        """
        lyrics_parts = []

        # 构建结构化歌词
        for i, verse in enumerate(verses):
            lyrics_parts.append(f"[Verse {i+1}]")
            lyrics_parts.append(verse)

        for i, chorus in enumerate(choruses):
            lyrics_parts.append(f"[Chorus {i+1}]")
            lyrics_parts.append(chorus)

        if bridge:
            lyrics_parts.append("[Bridge]")
            lyrics_parts.append(bridge)

        if outro:
            lyrics_parts.append("[Outro]")
            lyrics_parts.append(outro)

        lyrics = "\n".join(lyrics_parts)

        return self.generate(lyrics=lyrics, prompt=prompt, **kwargs)


class APIError(Exception):
    """API 错误异常"""
    pass


def main():
    """命令行使用示例"""
    import argparse

    parser = argparse.ArgumentParser(description="MiniMax Music Generation")
    parser.add_argument("--lyrics", "-l", required=True, help="Lyrics file path or text")
    parser.add_argument("--prompt", "-p", help="Music style prompt")
    parser.add_argument("--model", "-m", default="music-2.5", help="Model name")
    parser.add_argument("--output", "-o", default="music.mp3", help="Output file")

    args = parser.parse_args()

    # 读取歌词
    if os.path.isfile(args.lyrics):
        with open(args.lyrics, "r", encoding="utf-8") as f:
            lyrics = f.read()
    else:
        lyrics = args.lyrics

    generator = MiniMaxMusicGenerator()

    print("Generating music...")
    result = generator.generate(
        lyrics=lyrics,
        prompt=args.prompt,
        model=args.model
    )

    generator.save_audio(result, args.output)
    print("Done!")


if __name__ == "__main__":
    main()
