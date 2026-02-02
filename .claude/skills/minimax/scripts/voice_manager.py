#!/usr/bin/env python3
"""
MiniMax 音色管理 API 客户端
支持查询音色、音色复刻、音色设计、文件上传
APIs:
- POST /v1/get_voice (查询音色)
- POST /v1/voice_clone (音色复刻)
- POST /v1/voice_design (音色设计)
- POST /v1/files/upload (文件上传)
"""

import os
import json
import base64
import requests
from typing import Optional, Dict, Any, List, Union
from pathlib import Path


def _get_default_output_dir() -> Path:
    """获取默认音频输出目录"""
    return Path.cwd() / "assets" / "audios"


class MiniMaxVoiceManager:
    """MiniMax 音色管理客户端"""

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

    # 音效选项
    SOUND_EFFECTS = [
        "spacious_echo",      # 空旷回音
        "auditorium_echo",    # 礼堂广播
        "lofi_telephone",     # 电话失真
        "robotic",            # 电音
    ]

    def __init__(self, api_key: Optional[str] = None, group_id: Optional[str] = None):
        """
        初始化音色管理客户端

        Args:
            api_key: MiniMax API Key
            group_id: MiniMax Group ID
        """
        self.api_key = api_key or os.getenv("MINIMAX_API_KEY")
        self.group_id = group_id or os.getenv("MINIMAX_GROUP_ID")

        if not self.api_key:
            raise ValueError("API key is required. Set MINIMAX_API_KEY env var or pass api_key parameter.")

    def _get_headers(self, content_type: str = "application/json") -> Dict[str, str]:
        """获取请求头"""
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        if content_type:
            headers["Content-Type"] = content_type
        if self.group_id:
            headers["X-Minimax-Group-Id"] = self.group_id
        return headers

    # ============ 查询音色 ============

    def list_voices(
        self,
        voice_type: str = "all"
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        查询可用音色

        Args:
            voice_type: 音色类型，可选 system/voice_cloning/voice_generation/all

        Returns:
            包含各类音色的字典
        """
        if voice_type not in ["system", "voice_cloning", "voice_generation", "all"]:
            raise ValueError(f"Invalid voice_type: {voice_type}")

        response = requests.post(
            f"{self.BASE_URL}/v1/get_voice",
            headers=self._get_headers(),
            json={"voice_type": voice_type}
        )
        response.raise_for_status()

        result = response.json()

        if result.get("base_resp", {}).get("status_code") != 0:
            raise APIError(
                f"API Error: {result['base_resp']['status_msg']} "
                f"(code: {result['base_resp']['status_code']})"
            )

        return {
            "system": result.get("system_voice", []),
            "voice_cloning": result.get("voice_cloning", []),
            "voice_generation": result.get("voice_generation", []),
        }

    def get_system_voices(self) -> List[Dict[str, Any]]:
        """获取系统音色列表"""
        return self.list_voices("system")["system"]

    def get_cloned_voices(self) -> List[Dict[str, Any]]:
        """获取复刻音色列表"""
        return self.list_voices("voice_cloning")["voice_cloning"]

    def get_generated_voices(self) -> List[Dict[str, Any]]:
        """获取文生音色列表"""
        return self.list_voices("voice_generation")["voice_generation"]

    # ============ 文件上传 ============

    def upload_voice_clone_file(
        self,
        file_path: Union[str, Path],
        purpose: str = "voice_clone"
    ) -> Dict[str, Any]:
        """
        上传音色复刻音频文件

        Args:
            file_path: 音频文件路径
            purpose: 文件用途，voice_clone 或 prompt_audio

        Returns:
            包含 file_id 的字典
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path, "rb") as f:
            files = {"file": (file_path.name, f, "audio/mpeg")}
            data = {"purpose": purpose}

            response = requests.post(
                f"{self.BASE_URL}/v1/files/upload",
                headers=self._get_headers(content_type=""),
                data=data,
                files=files
            )

        response.raise_for_status()
        result = response.json()

        if result.get("base_resp", {}).get("status_code") != 0:
            raise APIError(
                f"API Error: {result['base_resp']['status_msg']} "
                f"(code: {result['base_resp']['status_code']})"
            )

        file_obj = result.get("file", {})
        return {
            "file_id": file_obj.get("file_id"),
            "bytes": file_obj.get("bytes"),
            "filename": file_obj.get("filename"),
            "created_at": file_obj.get("created_at"),
        }

    def upload_prompt_audio(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        上传示例音频（用于增强复刻效果）

        Args:
            file_path: 音频文件路径（需 < 8 秒）

        Returns:
            包含 file_id 的字典
        """
        return self.upload_voice_clone_file(file_path, purpose="prompt_audio")

    # ============ 音色复刻 ============

    def clone_voice(
        self,
        file_id: Union[str, int],
        voice_id: str,
        text: Optional[str] = None,
        model: Optional[str] = None,
        clone_prompt: Optional[Dict] = None,
        language_boost: Optional[str] = None,
        need_noise_reduction: bool = False,
        need_volume_normalization: bool = False,
        aigc_watermark: bool = False,
        continuous_sound: bool = False,
    ) -> Dict[str, Any]:
        """
        音色快速复刻

        Args:
            file_id: 上传的音频文件 ID
            voice_id: 自定义的音色 ID（8-256 字符，首字符为字母，允许数字、字母、-、_）
            text: 试听文本（可选，若提供则生成试听音频）
            model: 试听使用的模型（提供 text 时必填）
            clone_prompt: 示例音频配置 {"prompt_audio": file_id, "prompt_text": text}
            language_boost: 语言增强
            need_noise_reduction: 是否降噪
            need_volume_normalization: 是否音量归一化
            aigc_watermark: 是否添加水印
            continuous_sound: 连续声音优化

        Returns:
            复刻结果，包含 demo_audio（如有试听）
        """
        if text and not model:
            raise ValueError("model is required when text is provided for preview")

        if model and model not in self.MODELS:
            raise ValueError(f"Unsupported model: {model}")

        payload: Dict[str, Any] = {
            "file_id": int(file_id),
            "voice_id": voice_id,
            "need_noise_reduction": need_noise_reduction,
            "need_volume_normalization": need_volume_normalization,
            "aigc_watermark": aigc_watermark,
            "continuous_sound": continuous_sound,
        }

        if text:
            payload["text"] = text
            payload["model"] = model

        if clone_prompt:
            payload["clone_prompt"] = clone_prompt

        if language_boost:
            payload["language_boost"] = language_boost

        response = requests.post(
            f"{self.BASE_URL}/v1/voice_clone",
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
            "voice_id": voice_id,
            "demo_audio": result.get("demo_audio"),
            "input_sensitive": result.get("input_sensitive"),
        }

    # ============ 音色设计 ============

    def design_voice(
        self,
        prompt: str,
        preview_text: str,
        voice_id: Optional[str] = None,
        aigc_watermark: bool = False,
    ) -> Dict[str, Any]:
        """
        音色设计（文生音色）

        Args:
            prompt: 音色描述文本
            preview_text: 试听音频文本
            voice_id: 自定义音色 ID（可选，不传则自动生成）
            aigc_watermark: 是否添加水印

        Returns:
            包含 voice_id 和 trial_audio 的字典
        """
        payload: Dict[str, Any] = {
            "prompt": prompt,
            "preview_text": preview_text,
            "aigc_watermark": aigc_watermark,
        }

        if voice_id:
            payload["voice_id"] = voice_id

        response = requests.post(
            f"{self.BASE_URL}/v1/voice_design",
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
            "voice_id": result.get("voice_id"),
            "trial_audio": result.get("trial_audio"),
        }

    def save_trial_audio(
        self,
        result: Dict[str, Any],
        filename: Optional[str] = None,
        output_dir: Optional[str] = None
    ) -> str:
        """
        保存试听音频

        Args:
            result: design_voice 返回的结果
            filename: 文件名（不含路径），默认使用 trial_{voice_id}.mp3
            output_dir: 输出目录，默认使用 ./assets/audios

        Returns:
            保存的文件完整路径
        """
        trial_audio_hex = result.get("trial_audio")
        if not trial_audio_hex:
            raise ValueError("No trial audio in result")

        # 确定输出目录
        if output_dir is None:
            output_dir = _get_default_output_dir()
        else:
            output_dir = Path(output_dir)

        # 确保目录存在
        output_dir.mkdir(parents=True, exist_ok=True)

        # 确定文件名
        if filename is None:
            voice_id = result.get("voice_id", "unknown")
            filename = f"trial_{voice_id}.mp3"

        output_path = output_dir / filename

        audio_bytes = bytes.fromhex(trial_audio_hex)
        with open(output_path, "wb") as f:
            f.write(audio_bytes)

        print(f"Trial audio saved to: {output_path}")
        return str(output_path)


class APIError(Exception):
    """API 错误异常"""
    pass


def main():
    """命令行使用示例"""
    import argparse

    parser = argparse.ArgumentParser(description="MiniMax Voice Manager")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # list voices
    list_parser = subparsers.add_parser("list", help="List voices")
    list_parser.add_argument("--type", default="all", help="Voice type")

    # clone voice
    clone_parser = subparsers.add_parser("clone", help="Clone voice")
    clone_parser.add_argument("--file", required=True, help="Audio file path")
    clone_parser.add_argument("--voice-id", required=True, help="Voice ID")
    clone_parser.add_argument("--text", help="Preview text")
    clone_parser.add_argument("--model", default="speech-2.8-hd", help="Model")

    # design voice
    design_parser = subparsers.add_parser("design", help="Design voice")
    design_parser.add_argument("--prompt", required=True, help="Voice description")
    design_parser.add_argument("--preview", required=True, help="Preview text")
    design_parser.add_argument("--output", default="trial.mp3", help="Output file")

    args = parser.parse_args()

    manager = MiniMaxVoiceManager()

    if args.command == "list":
        voices = manager.list_voices(args.type)
        for category, voice_list in voices.items():
            if voice_list:
                print(f"\n{category.upper()}:")
                for v in voice_list:
                    print(f"  - {v.get('voice_id')}: {v.get('voice_name', 'N/A')}")

    elif args.command == "clone":
        print("Uploading file...")
        upload = manager.upload_voice_clone_file(args.file)
        print(f"File uploaded: {upload['file_id']}")

        print("Cloning voice...")
        result = manager.clone_voice(
            file_id=upload["file_id"],
            voice_id=args.voice_id,
            text=args.text,
            model=args.model if args.text else None
        )
        print(f"Voice cloned: {result['voice_id']}")
        if result.get("demo_audio"):
            print(f"Demo audio: {result['demo_audio']}")

    elif args.command == "design":
        print("Designing voice...")
        result = manager.design_voice(
            prompt=args.prompt,
            preview_text=args.preview
        )
        print(f"Voice designed: {result['voice_id']}")
        manager.save_trial_audio(result, args.output)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
