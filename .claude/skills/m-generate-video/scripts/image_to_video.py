#!/usr/bin/env python3
"""
Doubao Seedance Video Generation - Image to Video
图生视频脚本

Usage:
    python image_to_video.py "提示词" -i image.jpg [options]

Examples:
    python image_to_video.py "女孩睁开眼，温柔地看向镜头" -i ./girl.png
    python image_to_video.py "画面中的人物动起来" -i photo.jpg -t 8 --no-audio
"""
import argparse
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from config import (
    DEFAULT_MODEL,
    LITE_I2V_MODEL,
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


def build_content(prompt: str, image_paths: list) -> list:
    """Build content array with text and images"""
    content = [{"type": "text", "text": prompt}]

    for img_path in image_paths:
        base64_data = image_to_base64(img_path)
        # For multi-image (lite-i2v), all images use role "reference_image"
        if len(image_paths) > 1:
            content.append({
                "type": "image_url",
                "image_url": {"url": base64_data},
                "role": "reference_image"
            })
        else:
            content.append({
                "type": "image_url",
                "image_url": {"url": base64_data}
            })

    return content


def main():
    parser = argparse.ArgumentParser(
        description="豆包 Seedance 图生视频",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python image_to_video.py "女孩睁开眼" -i ./girl.png
  python image_to_video.py "人物动起来" -i photo.jpg -t 8
  python image_to_video.py "[图1]和[图2]一起跳舞" -i "img1.jpg,img2.jpg"
        """
    )

    parser.add_argument("prompt", help="视频描述提示词")
    parser.add_argument("-i", "--image", required=True,
                       help="参考图片路径（支持多张，逗号分隔）")
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
    parser.add_argument("--model", default=None,
                       help=f"模型ID (默认: {DEFAULT_MODEL}，多图自动切换lite-i2v)")
    parser.add_argument("-o", "--output", default=DEFAULT_OUTPUT_DIR,
                       help=f"输出目录 (默认: {DEFAULT_OUTPUT_DIR})")
    parser.add_argument("-k", "--api-key", default=None,
                       help="API Key (默认从环境变量 ARK_API_KEY 读取)")

    args = parser.parse_args()

    # Validate duration
    if args.time not in VALID_DURATIONS:
        print_error(f"时长必须在 4-12 秒之间")
        sys.exit(1)

    # Parse image paths
    image_paths = [p.strip() for p in args.image.split(",")]

    # Determine model
    model = args.model or DEFAULT_MODEL
    use_lite_model = model == LITE_I2V_MODEL

    if len(image_paths) > 1 and not args.model:
        model = LITE_I2V_MODEL
        use_lite_model = True
        print_warning(f"检测到多张参考图，自动切换至 lite-i2v 模型")

    # lite-i2v model doesn't support audio generation
    generate_audio = not args.no_audio
    if use_lite_model and generate_audio:
        generate_audio = False
        print_warning(f"{LITE_I2V_MODEL} 不支持音频生成，自动禁用")

    # Build content
    try:
        content = build_content(args.prompt, image_paths)
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
        print_info("豆包 Seedance 图生视频")
        print_info("=" * 50)
        print_info(f"提示词: {args.prompt}")
        print_info(f"参考图片: {', '.join(image_paths)}")

        # Create task
        task_id = api.create_task(
            model=model,
            content=content,
            duration=args.time,
            ratio=args.ratio,
            resolution=args.resolution,
            generate_audio=generate_audio,
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
