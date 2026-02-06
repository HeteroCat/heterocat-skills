#!/usr/bin/env python3
"""
Doubao Seedance Video Generation - Continuous Video Chain
连续视频生成脚本

使用前一个视频的尾帧作为后一个视频的首帧，生成多个连续的视频片段。
自动生成完整长视频（使用 FFmpeg 拼接）。

Usage:
    python continuous_video.py -f prompts.txt [options]
    python continuous_video.py -p "提示词1" -p "提示词2" -p "提示词3" [options]

Examples:
    # 从文件读取多个提示词并生成连续视频（默认自动拼接）
    python continuous_video.py -f prompts.txt -i initial_image.jpg

    # 直接传入多个提示词
    python continuous_video.py -p "女孩睁开眼" -p "女孩奔跑" -p "女孩休息" -i start.jpg

    # 不拼接视频（只生成片段）
    python continuous_video.py -f prompts.txt -i start.jpg --no-concat
"""
import argparse
import json
import sys
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from config import (
    DEFAULT_MODEL,
    DEFAULT_DURATION,
    DEFAULT_RATIO,
    DEFAULT_RESOLUTION,
    DEFAULT_GENERATE_AUDIO,
    DEFAULT_OUTPUT_DIR,
    VALID_RATIOS,
    VALID_RESOLUTIONS,
    VALID_DURATIONS,
)
from utils import (
    print_info, print_success, print_error, print_warning,
    image_to_base64, generate_output_filename
)
from api_client import DoubaoVideoAPI


def load_prompts_from_file(filepath: str) -> List[str]:
    """Load prompts from file (one per line)"""
    with open(filepath, 'r', encoding='utf-8') as f:
        prompts = [line.strip() for line in f if line.strip()]
    return prompts


def build_content_with_frame(prompt: str, frame_url: Optional[str] = None) -> list:
    """Build content array with text and optional frame image"""
    content = [{"type": "text", "text": prompt}]

    if frame_url:
        # Check if it's a local file or URL
        if frame_url.startswith(('http://', 'https://', 'data:')):
            content.append({
                "type": "image_url",
                "image_url": {"url": frame_url}
            })
        else:
            # Local file, convert to base64
            base64_data = image_to_base64(frame_url)
            content.append({
                "type": "image_url",
                "image_url": {"url": base64_data}
            })

    return content


def generate_single_video(
    api: DoubaoVideoAPI,
    prompt: str,
    initial_frame: Optional[str],
    model: str,
    duration: int,
    ratio: str,
    resolution: str,
    generate_audio: bool,
    seed: Optional[int],
    output_dir: str
) -> Tuple[Optional[str], Optional[str]]:
    """
    Generate a single video and return video path and last frame URL

    Returns:
        (video_path, last_frame_url) or (None, None) if failed
    """
    try:
        # Build content
        content = build_content_with_frame(prompt, initial_frame)

        print_info(f"生成视频: {prompt[:50]}...")
        if initial_frame:
            print_info(f"使用首帧: {initial_frame[:80]}...")

        # Create task with return_last_frame=True to get last frame URL
        task_id = api.create_task(
            model=model,
            content=content,
            duration=duration,
            ratio=ratio,
            resolution=resolution,
            generate_audio=generate_audio,
            seed=seed,
            return_last_frame=True,
        )

        # Poll for result, requesting last frame URL
        result = api.poll_task(task_id, return_last_frame=True)

        # Parse result (format: "video_url|last_frame_url" or just "video_url")
        if "|" in result:
            video_url, last_frame_url = result.split("|", 1)
        else:
            video_url = result
            last_frame_url = None

        # Generate output filename
        output_file = generate_output_filename(prompt, output_dir)

        # Download video
        api.download_video(video_url, output_file)

        # Log last frame info
        if last_frame_url:
            print_success(f"获取尾帧 URL: {last_frame_url[:80]}...")
        else:
            print_warning("API 未返回尾帧 URL，将尝试本地提取")
            last_frame_url = extract_last_frame(output_file)

        return output_file, last_frame_url

    except Exception as e:
        print_error(f"视频生成失败: {str(e)}")
        return None, None


def extract_last_frame(video_path: str) -> Optional[str]:
    """
    Extract the last frame from a video using FFmpeg

    Returns:
        Path to the extracted frame image
    """
    video_path = Path(video_path)
    frame_path = video_path.parent / f"{video_path.stem}_last_frame.jpg"

    try:
        # Use FFmpeg to extract last frame
        cmd = [
            'ffmpeg',
            '-i', str(video_path),
            '-sseof', '-0.1',  # Seek to 0.1s before end
            '-vframes', '1',    # Extract 1 frame
            '-q:v', '2',        # High quality
            str(frame_path)
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0 and frame_path.exists():
            print_success(f"提取尾帧: {frame_path}")
            return str(frame_path)
        else:
            print_warning(f"无法提取尾帧: {result.stderr}")
            return None

    except FileNotFoundError:
        print_warning("FFmpeg 未安装，无法提取尾帧")
        return None
    except Exception as e:
        print_warning(f"提取尾帧失败: {str(e)}")
        return None


def concatenate_videos(video_paths: List[str], output_path: str) -> bool:
    """
    Concatenate multiple videos using FFmpeg

    Returns:
        True if successful
    """
    if not video_paths:
        print_error("没有视频可以拼接")
        return False

    # Create concat list file
    concat_list = Path(output_path).parent / "concat_list.txt"

    try:
        with open(concat_list, 'w', encoding='utf-8') as f:
            for video_path in video_paths:
                # Escape single quotes in path
                escaped_path = str(video_path).replace("'", "'\\''")
                f.write(f"file '{escaped_path}'\n")

        # Run FFmpeg concat
        cmd = [
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', str(concat_list),
            '-c', 'copy',
            output_path
        ]

        print_info(f"正在拼接 {len(video_paths)} 个视频...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

        # Clean up concat list
        concat_list.unlink(missing_ok=True)

        if result.returncode == 0:
            print_success(f"视频拼接完成: {output_path}")
            return True
        else:
            print_error(f"视频拼接失败: {result.stderr}")
            return False

    except FileNotFoundError:
        print_error("FFmpeg 未安装，无法拼接视频")
        return False
    except Exception as e:
        print_error(f"视频拼接失败: {str(e)}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="豆包 Seedance 连续视频生成",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # 从文件读取提示词（每行一个）
  python continuous_video.py -f prompts.txt -i initial.jpg

  # 直接传入多个提示词
  python continuous_video.py -p "女孩睁开眼" -p "女孩奔跑" -p "女孩休息" -i start.jpg

  # 生成并拼接成完整视频
  python continuous_video.py -f prompts.txt -i start.jpg --concat

Prompts file format (prompts.txt):
  女孩抱着狐狸，女孩睁开眼，温柔地看向镜头
  女孩和狐狸在草地上奔跑，阳光明媚
  女孩和狐狸坐在树下休息
        """
    )

    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("-f", "--file",
                            help="从文件读取提示词（每行一个）")
    input_group.add_argument("-p", "--prompt", action="append", dest="prompts",
                            help="提示词（可多次使用）")

    # Initial frame
    parser.add_argument("-i", "--initial-image",
                       help="初始首帧图片路径（第一个视频使用）")

    # Video parameters
    parser.add_argument("-t", "--time", type=int, default=DEFAULT_DURATION,
                       help=f"每个视频时长: 4-12秒 (默认: {DEFAULT_DURATION})")
    parser.add_argument("-r", "--ratio", default=DEFAULT_RATIO,
                       choices=VALID_RATIOS, help=f"宽高比 (默认: {DEFAULT_RATIO})")
    parser.add_argument("--resolution", default=DEFAULT_RESOLUTION,
                       choices=VALID_RESOLUTIONS, help=f"分辨率 (默认: {DEFAULT_RESOLUTION})")
    parser.add_argument("--no-audio", action="store_true",
                       help="不生成音频 (默认生成音频)")
    parser.add_argument("--seed", type=int, help="随机种子（所有视频使用相同种子）")
    parser.add_argument("--model", default=DEFAULT_MODEL,
                       help=f"模型ID (默认: {DEFAULT_MODEL})")
    parser.add_argument("-o", "--output", default=DEFAULT_OUTPUT_DIR,
                       help=f"输出目录 (默认: {DEFAULT_OUTPUT_DIR})")
    parser.add_argument("-k", "--api-key", default=None,
                       help="API Key (默认从环境变量 ARK_API_KEY 读取)")

    # Concatenation
    parser.add_argument("--no-concat", action="store_true",
                       help="不拼接视频（默认会自动拼接所有片段）")
    parser.add_argument("--concat-output",
                       help="拼接后的视频输出路径（默认自动生成）")

    args = parser.parse_args()

    # Load prompts
    if args.file:
        prompts = load_prompts_from_file(args.file)
        print_info(f"从文件加载了 {len(prompts)} 个提示词")
    else:
        prompts = args.prompts

    if not prompts:
        print_error("没有有效的提示词")
        sys.exit(1)

    print_info(f"将生成 {len(prompts)} 个连续视频")

    # Validate duration
    if args.time not in VALID_DURATIONS:
        print_error(f"时长必须在 4-12 秒之间")
        sys.exit(1)

    # Create API client
    try:
        api = DoubaoVideoAPI(api_key=args.api_key)
    except ValueError as e:
        print_error(str(e))
        sys.exit(1)

    # Generate videos
    generated_videos = []
    last_frame = args.initial_image

    print_info("=" * 60)
    print_info("开始生成连续视频")
    print_info("=" * 60)

    for i, prompt in enumerate(prompts, 1):
        print_info(f"\n[{i}/{len(prompts)}] 生成第 {i} 个视频")
        print_info("-" * 60)

        video_path, next_frame = generate_single_video(
            api=api,
            prompt=prompt,
            initial_frame=last_frame,
            model=args.model,
            duration=args.time,
            ratio=args.ratio,
            resolution=args.resolution,
            generate_audio=not args.no_audio,
            seed=args.seed,
            output_dir=args.output
        )

        if video_path:
            generated_videos.append(video_path)
            last_frame = next_frame
            print_success(f"第 {i} 个视频生成成功")
        else:
            print_error(f"第 {i} 个视频生成失败，中止后续生成")
            break

    # Summary
    print_info("\n" + "=" * 60)
    print_info("生成完成")
    print_info("=" * 60)
    print_success(f"成功生成 {len(generated_videos)}/{len(prompts)} 个视频")

    for i, video in enumerate(generated_videos, 1):
        print_info(f"  视频 {i}: {video}")

    # Concatenate by default (unless --no-concat is specified)
    if not args.no_concat and len(generated_videos) > 1:
        print_info("\n" + "=" * 60)
        print_info("开始拼接视频")
        print_info("=" * 60)

        if args.concat_output:
            concat_output = args.concat_output
        else:
            timestamp = Path(generated_videos[0]).stem.split('_')[-1]
            concat_output = str(Path(args.output) / f"continuous_video_{timestamp}.mp4")

        if concatenate_videos(generated_videos, concat_output):
            print_success(f"完整视频: {concat_output}")

    print_info("=" * 60)


if __name__ == "__main__":
    main()
