#!/usr/bin/env python3
"""
Doubao Seedance Video Generation - Text to Video
文生视频脚本

Usage:
    python text_to_video.py "提示词" [options]

Examples:
    python text_to_video.py "海边落日，金色的太阳缓缓沉入海平面"
    python text_to_video.py "美女在办公室办公" -t 8 -r 16:9 --resolution 1080p
"""
import argparse
import sys
from pathlib import Path

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
from utils import print_info, print_success, print_error, generate_output_filename
from api_client import DoubaoVideoAPI


def build_content(prompt: str) -> list:
    """Build content array with text only"""
    return [{"type": "text", "text": prompt}]


def main():
    parser = argparse.ArgumentParser(
        description="豆包 Seedance 文生视频",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python text_to_video.py "海边落日，金色的太阳缓缓沉入海平面"
  python text_to_video.py "美女在办公室办公" -t 8 -r 16:9 --resolution 1080p
  python text_to_video.py "一只橘猫在公园散步" --no-audio --seed 12345
        """
    )

    parser.add_argument("prompt", help="视频描述提示词")
    parser.add_argument("-t", "--time", type=int, default=DEFAULT_DURATION,
                       help=f"视频时长: 4-12秒 (默认: {DEFAULT_DURATION})")
    parser.add_argument("-r", "--ratio", default=DEFAULT_RATIO,
                       choices=VALID_RATIOS, help=f"宽高比 (默认: {DEFAULT_RATIO})")
    parser.add_argument("--resolution", default=DEFAULT_RESOLUTION,
                       choices=VALID_RESOLUTIONS, help=f"分辨率 (默认: {DEFAULT_RESOLUTION})")
    parser.add_argument("--no-audio", action="store_true",
                       help="不生成音频 (默认生成音频)")
    parser.add_argument("--seed", type=int, help="随机种子")
    parser.add_argument("--camera-fixed", action="store_true",
                       help="固定相机")
    parser.add_argument("--watermark", action="store_true",
                       help="添加水印")
    parser.add_argument("--model", default=DEFAULT_MODEL,
                       help=f"模型ID (默认: {DEFAULT_MODEL})")
    parser.add_argument("-o", "--output", default=DEFAULT_OUTPUT_DIR,
                       help=f"输出目录 (默认: {DEFAULT_OUTPUT_DIR})")
    parser.add_argument("-k", "--api-key", default=None,
                       help="API Key (默认从环境变量 ARK_API_KEY 读取)")

    args = parser.parse_args()

    # Validate duration
    if args.time not in VALID_DURATIONS:
        print_error(f"时长必须在 4-12 秒之间")
        sys.exit(1)

    # Build content
    content = build_content(args.prompt)

    # Create API client
    try:
        api = DoubaoVideoAPI(api_key=args.api_key)
    except ValueError as e:
        print_error(str(e))
        sys.exit(1)

    try:
        print_info("=" * 50)
        print_info("豆包 Seedance 文生视频")
        print_info("=" * 50)
        print_info(f"提示词: {args.prompt}")

        # Create task
        task_id = api.create_task(
            model=args.model,
            content=content,
            duration=args.time,
            ratio=args.ratio,
            resolution=args.resolution,
            generate_audio=not args.no_audio,
            camera_fixed=args.camera_fixed,
            watermark=args.watermark,
            seed=args.seed,
        )

        # Poll for result
        video_url = api.poll_task(task_id)

        # Generate output filename
        output_file = generate_output_filename(args.prompt, args.output)

        # Download video
        api.download_video(video_url, output_file)

        print_info("=" * 50)
        print_success("全部完成！")
        print_success(f"视频已保存: {output_file}")
        print_info("=" * 50)

    except Exception as e:
        print_error(f"处理失败: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
