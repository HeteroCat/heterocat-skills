#!/usr/bin/env python3
"""
Suno AI 音乐生成脚本
支持灵感模式和自定义模式
使用 dmxapi.cn API
"""

import os
import sys
import time
import json
import argparse
import requests
from pathlib import Path
from typing import Optional, Dict, Any, List


def _get_default_output_dir() -> Path:
    """获取默认音频输出目录"""
    return Path.cwd() / "assets" / "audios"


class SunoMusicGenerator:
    """Suno AI 音乐生成客户端"""

    BASE_URL = "https://www.dmxapi.cn/suno"

    # 支持的模型版本
    MODELS = ["chirp-v5", "chirp-v4", "chirp-v3"]

    # 可用的音乐风格
    STYLES = [
        'pop', 'rock', 'electronic', 'classical', 'jazz',
        'hip-hop', 'r&b', 'country', 'folk', 'blues',
        'reggae', 'latin', 'ambient', 'cinematic', 'lo-fi',
        'trap', 'house', 'techno', 'dubstep', 'romantic',
        'upbeat', 'melancholic', 'energetic', 'peaceful', 'dramatic'
    ]

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化音乐生成客户端

        Args:
            api_key: DMX API Key (支持 DMX_API_KEY 或 302AI_API_KEY)
        """
        raw_key = api_key or os.getenv("DMX_API_KEY") or os.getenv("302AI_API_KEY")

        if not raw_key:
            raise ValueError(
                "API key is required.\n"
                "Please set DMX_API_KEY or 302AI_API_KEY environment variable:\n"
                "  export DMX_API_KEY='your_api_key_here'\n"
                "Or pass api_key parameter to SunoMusicGenerator()."
            )

        self.api_key = raw_key.strip()

    def _get_headers(self, content_type: bool = True) -> Dict[str, str]:
        """获取请求头"""
        headers = {"Authorization": f"Bearer {self.api_key}"}
        if content_type:
            headers["Content-Type"] = "application/json"
            headers["Accept"] = "application/json"
        return headers

    def generate_inspiration(
        self,
        description: str,
        make_instrumental: bool = False,
        model: str = "chirp-v5"
    ) -> List[Dict[str, str]]:
        """
        灵感模式生成音乐

        Args:
            description: 音乐创作描述
            make_instrumental: 是否生成纯音乐（无歌词）
            model: 模型版本

        Returns:
            音乐列表，每个包含 audio_url 和 image_url
        """
        if model not in self.MODELS:
            raise ValueError(f"Unsupported model: {model}. Choose from {self.MODELS}")

        print(f"🎵 提交音乐生成任务（灵感模式）...")
        print(f"   描述: {description}")
        print(f"   纯音乐: {make_instrumental}")
        print(f"   模型: {model}")

        # 提交任务
        payload = {
            "gpt_description_prompt": description,
            "make_instrumental": make_instrumental,
            "mv": model,
            "notify_hook": ""
        }

        response = requests.post(
            f"{self.BASE_URL}/submit/music",
            headers=self._get_headers(),
            json=payload
        )
        response.raise_for_status()
        result = response.json()

        if result.get("code") != "success":
            raise Exception(f"任务提交失败: {result.get('message', 'Unknown error')}")

        task_id = result.get("data")
        if not task_id:
            raise Exception("任务 ID 获取失败")

        print(f"✅ 任务已提交，ID: {task_id}")

        # 轮询任务状态
        return self._poll_task(task_id)

    def generate_custom(
        self,
        lyrics: str,
        title: str,
        tags: Optional[str] = None,
        model: str = "chirp-v5"
    ) -> List[Dict[str, str]]:
        """
        自定义模式生成音乐

        Args:
            lyrics: 歌词内容
            title: 歌曲标题
            tags: 音乐风格标签（逗号分隔）
            model: 模型版本

        Returns:
            音乐列表，每个包含 audio_url 和 image_url
        """
        if model not in self.MODELS:
            raise ValueError(f"Unsupported model: {model}. Choose from {self.MODELS}")

        print(f"🎵 提交音乐生成任务（自定义模式）...")
        print(f"   标题: {title}")
        print(f"   风格: {tags or '未指定'}")
        print(f"   模型: {model}")

        # 提交任务
        payload = {
            "prompt": lyrics,
            "title": title,
            "mv": model
        }

        if tags:
            payload["tags"] = tags

        response = requests.post(
            f"{self.BASE_URL}/submit/music",
            headers=self._get_headers(),
            json=payload
        )
        response.raise_for_status()
        result = response.json()

        if result.get("code") != "success":
            raise Exception(f"任务提交失败: {result.get('message', 'Unknown error')}")

        task_id = result.get("data")
        if not task_id:
            raise Exception("任务 ID 获取失败")

        print(f"✅ 任务已提交，ID: {task_id}")

        # 轮询任务状态
        return self._poll_task(task_id)

    def _poll_task(self, task_id: str, max_attempts: int = 60, interval: int = 3) -> List[Dict[str, str]]:
        """
        轮询任务状态

        Args:
            task_id: 任务ID
            max_attempts: 最大尝试次数
            interval: 轮询间隔（秒）

        Returns:
            音乐列表
        """
        print(f"⏳ 等待音乐生成完成...")

        for attempt in range(max_attempts):
            time.sleep(interval)

            response = requests.get(
                f"{self.BASE_URL}/fetch/{task_id}",
                headers=self._get_headers(content_type=False)
            )
            response.raise_for_status()
            result = response.json()

            task_data = result.get("data", {})
            status = task_data.get("status")
            progress = task_data.get("progress", "0%")

            print(f"   进度: {progress} ({attempt + 1}/{max_attempts})")

            if status == "SUCCESS":
                songs = task_data.get("data", [])
                if not songs:
                    raise Exception("未生成任何音乐")

                print(f"✅ 音乐生成完成！共 {len(songs)} 首")

                results = []
                for i, song in enumerate(songs, 1):
                    print(f"\n🎵 歌曲 {i}:")
                    print(f"   标题: {song.get('title', 'Untitled')}")
                    print(f"   时长: {song.get('duration', 0)}秒")
                    print(f"   音频: {song.get('audio_url', 'N/A')}")
                    print(f"   封面: {song.get('image_url', 'N/A')}")

                    results.append({
                        "title": song.get("title", "Untitled"),
                        "duration": song.get("duration", 0),
                        "audio_url": song.get("audio_url", ""),
                        "image_url": song.get("image_url", "")
                    })

                return results

            if status == "FAILED":
                raise Exception("音乐生成失败")

        raise Exception(f"音乐生成超时（{max_attempts * interval}秒）")

    def download_audio(
        self,
        audio_url: str,
        filename: Optional[str] = None,
        output_dir: Optional[str] = None
    ) -> str:
        """
        下载音频文件

        Args:
            audio_url: 音频URL
            filename: 文件名（不含路径）
            output_dir: 输出目录

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
            filename = f"suno_{int(time.time())}.mp3"

        output_path = output_dir / filename

        print(f"⬇️  下载音频: {audio_url}")

        response = requests.get(audio_url, stream=True)
        response.raise_for_status()

        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"✅ 音频已保存: {output_path}")
        return str(output_path)


def main():
    """命令行使用示例"""
    parser = argparse.ArgumentParser(
        description="Suno AI 音乐生成",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 灵感模式
  python3 generate_music.py --mode inspiration --description "中国风trap音乐" --instrumental

  # 自定义模式
  python3 generate_music.py --mode custom --lyrics "歌词内容" --title "歌曲标题" --tags "pop,upbeat"

  # 下载音频
  python3 generate_music.py --mode inspiration --description "轻松的爵士乐" --download
        """
    )

    parser.add_argument("--mode", "-m", required=True, choices=["inspiration", "custom"],
                        help="生成模式：inspiration（灵感）或 custom（自定义）")

    # 灵感模式参数
    parser.add_argument("--description", "-d", help="音乐描述（灵感模式）")
    parser.add_argument("--instrumental", "-i", action="store_true", help="生成纯音乐（灵感模式）")

    # 自定义模式参数
    parser.add_argument("--lyrics", "-l", help="歌词内容（自定义模式）")
    parser.add_argument("--title", "-t", help="歌曲标题（自定义模式）")
    parser.add_argument("--tags", help="音乐风格标签，逗号分隔（自定义模式）")

    # 通用参数
    parser.add_argument("--model", default="chirp-v5", choices=SunoMusicGenerator.MODELS,
                        help="模型版本（默认: chirp-v5）")
    parser.add_argument("--download", action="store_true", help="下载生成的音频文件")
    parser.add_argument("--output", "-o", help="输出目录（下载时使用）")

    args = parser.parse_args()

    try:
        generator = SunoMusicGenerator()

        if args.mode == "inspiration":
            if not args.description:
                parser.error("灵感模式需要 --description 参数")

            results = generator.generate_inspiration(
                description=args.description,
                make_instrumental=args.instrumental,
                model=args.model
            )

        else:  # custom
            if not args.lyrics or not args.title:
                parser.error("自定义模式需要 --lyrics 和 --title 参数")

            results = generator.generate_custom(
                lyrics=args.lyrics,
                title=args.title,
                tags=args.tags,
                model=args.model
            )

        # 下载音频
        if args.download and results:
            print("\n📥 开始下载音频文件...")
            for i, result in enumerate(results, 1):
                if result.get("audio_url"):
                    filename = f"{result.get('title', f'song_{i}').replace(' ', '_')}.mp3"
                    generator.download_audio(
                        audio_url=result["audio_url"],
                        filename=filename,
                        output_dir=args.output
                    )

        # 输出JSON结果
        print("\n" + "="*50)
        print("JSON 结果:")
        print(json.dumps(results, indent=2, ensure_ascii=False))

    except Exception as e:
        print(f"❌ 错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
