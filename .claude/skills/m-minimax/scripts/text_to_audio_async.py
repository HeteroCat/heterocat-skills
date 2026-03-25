#!/usr/bin/env python3
"""
MiniMax 长文本语音合成（异步）API 客户端
支持创建异步任务和查询任务状态
API: POST /v1/t2a_async_v2, GET /v1/query/t2a_async_query_v2
"""

import os
import time
import tarfile
import io
import requests
from typing import Optional, Dict, Any, Union
from pathlib import Path


def _get_default_output_dir() -> Path:
    """获取默认音频输出目录"""
    return Path.cwd() / "assets" / "audios"


class MiniMaxAsyncTTS:
    """MiniMax 异步文本转语音客户端"""

    BASE_URL = "https://api.minimaxi.com"

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

    def __init__(self, api_key: Optional[str] = None, group_id: Optional[str] = None):
        """
        初始化异步 TTS 客户端

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
                "Or pass api_key parameter to MiniMaxAsyncTTS()."
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

    def create_task(
        self,
        text: Optional[str] = None,
        text_file_id: Optional[int] = None,
        voice_id: str = "",
        model: str = "speech-2.8-hd",
        speed: float = 1.0,
        vol: float = 1.0,
        pitch: int = 0,
        emotion: Optional[str] = None,
        sample_rate: int = 32000,
        bitrate: int = 128000,
        format: str = "mp3",
        channel: int = 2,
        pronunciation_dict: Optional[Dict] = None,
        language_boost: Optional[str] = None,
        voice_modify: Optional[Dict] = None,
        continuous_sound: bool = False,
        aigc_watermark: bool = False,
    ) -> Dict[str, Any]:
        """
        创建异步语音合成任务

        Args:
            text: 待合成文本，长度限制 < 50000 字符，与 text_file_id 二选一
            text_file_id: 文本文件 ID，与 text 二选一
            voice_id: 音色 ID（必填）
            model: 模型版本
            speed: 语速 [0.5, 2]
            vol: 音量 (0, 10]
            pitch: 语调 [-12, 12]
            emotion: 情绪
            sample_rate: 采样率
            bitrate: 比特率
            format: 音频格式
            channel: 声道数
            pronunciation_dict: 发音词典
            language_boost: 语言增强
            voice_modify: 声音效果器
            continuous_sound: 连续声音优化
            aigc_watermark: 是否添加水印

        Returns:
            包含 task_id、file_id、task_token 的字典
        """
        if not text and not text_file_id:
            raise ValueError("Either text or text_file_id must be provided")

        if text and len(text) > 50000:
            raise ValueError("Text length must be < 50000 characters")

        if not voice_id:
            raise ValueError("voice_id is required")

        if model not in self.MODELS:
            raise ValueError(f"Unsupported model: {model}")

        payload: Dict[str, Any] = {
            "model": model,
            "voice_setting": {
                "voice_id": voice_id,
                "speed": speed,
                "vol": vol,
                "pitch": pitch,
            },
            "audio_setting": {
                "audio_sample_rate": sample_rate,
                "bitrate": bitrate,
                "format": format,
                "channel": channel,
            },
            "continuous_sound": continuous_sound,
            "aigc_watermark": aigc_watermark,
        }

        if text:
            payload["text"] = text
        elif text_file_id:
            payload["text_file_id"] = text_file_id

        if emotion and emotion in self.EMOTIONS:
            payload["voice_setting"]["emotion"] = emotion

        if pronunciation_dict:
            payload["pronunciation_dict"] = pronunciation_dict

        if language_boost:
            payload["language_boost"] = language_boost

        if voice_modify:
            payload["voice_modify"] = voice_modify

        response = requests.post(
            f"{self.BASE_URL}/v1/t2a_async_v2",
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

        return {
            "task_id": result.get("task_id"),
            "file_id": result.get("file_id"),
            "task_token": result.get("task_token"),
            "usage_characters": result.get("usage_characters"),
        }

    def query_task(self, task_id: Union[str, int]) -> Dict[str, Any]:
        """
        查询异步任务状态

        Args:
            task_id: 任务 ID

        Returns:
            任务状态信息，包含 status、file_id 等
        """
        response = requests.get(
            f"{self.BASE_URL}/v1/query/t2a_async_query_v2",
            headers=self._get_headers(),
            params={"task_id": str(task_id)}
        )
        response.raise_for_status()

        result = response.json()

        if result.get("base_resp", {}).get("status_code") != 0:
            raise APIError(
                f"API Error: {result['base_resp']['status_msg']} "
                f"(code: {result['base_resp']['status_code']})"
            )

        return {
            "task_id": result.get("task_id"),
            "status": result.get("status"),
            "file_id": result.get("file_id"),
        }

    def wait_for_completion(
        self,
        task_id: Union[str, int],
        poll_interval: float = 5.0,
        timeout: float = 600.0
    ) -> Dict[str, Any]:
        """
        等待任务完成

        Args:
            task_id: 任务 ID
            poll_interval: 轮询间隔（秒），默认 5 秒
            timeout: 超时时间（秒），默认 600 秒

        Returns:
            任务结果

        Raises:
            TimeoutError: 超时未完成
            APIError: 任务失败
        """
        start_time = time.time()

        while time.time() - start_time < timeout:
            result = self.query_task(task_id)
            status = result.get("status", "").lower()

            if status == "success":
                return result
            elif status == "failed":
                raise APIError(f"Task {task_id} failed")
            elif status == "expired":
                raise APIError(f"Task {task_id} expired")

            time.sleep(poll_interval)

        raise TimeoutError(f"Task {task_id} did not complete within {timeout} seconds")

    def download_result(
        self,
        file_id: Union[str, int],
        filename: Optional[str] = None,
        output_dir: Optional[str] = None,
        file_type: str = "audio"
    ) -> str:
        """
        下载任务结果文件

        Args:
            file_id: 文件 ID
            filename: 文件名（不含路径），默认使用 tts_async_{file_id}.{ext}
            output_dir: 输出目录，默认使用 ./assets/audios
            file_type: 文件类型 (audio/subtitle/extra_info)

        Returns:
            保存的文件完整路径
        """
        # 确定输出目录
        if output_dir is None:
            output_dir = _get_default_output_dir()
        else:
            output_dir = Path(output_dir)

        # 确保目录存在
        output_dir.mkdir(parents=True, exist_ok=True)

        # 确定文件名
        if filename is None:
            ext = "mp3" if file_type == "audio" else file_type
            filename = f"tts_async_{file_id}.{ext}"

        output_path = output_dir / filename

        # 第一步：获取文件元数据和下载 URL
        response = requests.get(
            f"{self.BASE_URL}/v1/files/retrieve",
            headers=self._get_headers(),
            params={"file_id": str(file_id), "type": file_type}
        )
        response.raise_for_status()

        result = response.json()

        if result.get("base_resp", {}).get("status_code") != 0:
            raise APIError(
                f"API Error: {result['base_resp']['status_msg']} "
                f"(code: {result['base_resp']['status_code']})"
            )

        # 提取下载 URL
        download_url = result.get("file", {}).get("download_url")
        if not download_url:
            raise APIError(f"No download URL in response for file_id: {file_id}")

        # 第二步：从下载 URL 获取实际文件内容
        audio_response = requests.get(download_url, timeout=120)
        audio_response.raise_for_status()

        with open(output_path, "wb") as f:
            f.write(audio_response.content)

        file_size = len(audio_response.content)
        print(f"File downloaded to: {output_path}")
        print(f"  Size: {file_size} bytes")
        return str(output_path)


class APIError(Exception):
    """API 错误异常"""
    pass


def main():
    """命令行使用示例"""
    import argparse

    parser = argparse.ArgumentParser(description="MiniMax Async Text-to-Speech")
    parser.add_argument("--text", "-t", required=True, help="Text to synthesize")
    parser.add_argument("--voice", "-v", required=True, help="Voice ID")
    parser.add_argument("--model", "-m", default="speech-2.8-hd", help="Model name")
    parser.add_argument("--output", "-o", default="output.mp3", help="Output file")
    parser.add_argument("--wait", "-w", action="store_true", help="Wait for completion")

    args = parser.parse_args()

    client = MiniMaxAsyncTTS()

    # 创建任务
    print("Creating async task...")
    task = client.create_task(
        text=args.text,
        voice_id=args.voice,
        model=args.model
    )
    print(f"Task created: {task['task_id']}")

    if args.wait:
        print("Waiting for completion...")
        result = client.wait_for_completion(task["task_id"])
        print(f"Task completed! File ID: {result['file_id']}")
        client.download_result(result["file_id"], args.output)


if __name__ == "__main__":
    main()
