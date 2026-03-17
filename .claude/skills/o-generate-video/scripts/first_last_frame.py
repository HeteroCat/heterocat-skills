#!/usr/bin/env python3
"""
Doubao Seedance Video Generation - First/Last Frame Video
首尾帧视频脚本

Usage:
    python first_last_frame.py "提示词" -f first.jpg -l last.jpg [options]

Examples:
    python first_last_frame.py "镜头360度环绕" -f ./start.jpg -l ./end.jpg
    python first_last_frame.py "人物变形动画" -f face1.png -l face2.png -t 10
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
from utils import (
    print_info, print_success, print_error,
    image_to_base64, generate_output_filename
)
from api_client import DoubaoVideoAPI


def build_content(prompt: str, first_frame: str, last_frame: str = None) -> list:
    """Build content array with text and frames"""
    content = [{"type": "text", "text": prompt}]

    # Add first frame with role (required when using multiple images)
    first_base64 = image_to_base64(first_frame)
    first_image = {
        "type": "image_url",
        "image_url": {"url": first_base64}
    }
    # Add role when we have both first and last frames
    if last_frame:
        first_image["role"] = "first_frame"
    content.append(first_image)

    # Add last frame if provided
    if last_frame:
        last_base64 = image_to_base64(last_frame)
        content.append({
            "type": "image_url",
            "image_url": {"url": last_base64},
            "role": "last_frame"
        })

    return content


def main():
    parser = argparse.ArgumentParser(
        description="豆包 Seedance 首尾帧视频",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python first_last_frame.py "镜头360度环绕" -f start.jpg -l end.jpg
  python first_last_frame.py "变形动画" -f face1.png -l face2.png -t 10
  python first_last_frame.py "单首帧视频" -f start.jpg -t 8 --no-audio
        """
    )

    parser.add_argument("prompt", help="视频描述提示词")
    parser.add_argument("-f", "--first", required=True,
                       help="首帧图片路径")
    parser.add_argument("-l", "--last",
                       help="尾帧图片路径（可选）")
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
    try:
        content = build_content(args.prompt, args.first, args.last)
    except (FileNotFoundError, ValueError) as e:
        print_error(str(e))
        sys.exit(1)

    # Create API client
    try:
        api = DoubaoVideoAPI(api_key=args.api_key)
    except ValueError as e:
        print_error(str(e))
        sys.exit(1)

    try:
        print_info("=" * 50)
        print_info("豆包 Seedance 首尾帧视频")
        print_info("=" * 50)
        print_info(f"提示词: {args.prompt}")
        print_info(f"首帧: {args.first}")
        if args.last:
            print_info(f"尾帧: {args.last}")

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
