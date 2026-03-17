#!/usr/bin/env python3
"""
Whisper 字幕生成脚本
使用 OpenAI Whisper API 将音频文件转换为 SRT 字幕文件
"""

from openai import OpenAI
import os
import sys
import argparse


def transcribe_audio(audio_path: str, output_path: str = None, api_key: str = None) -> str:
    """
    使用 Whisper API 转录音频文件生成 SRT 字幕

    Args:
        audio_path: 音频文件路径
        output_path: 输出字幕文件路径（可选，默认为音频文件名.srt）
        api_key: OpenAI API 密钥（可选，默认从环境变量 OPENAI_API_KEY 获取）

    Returns:
        生成的字幕文件路径
    """
    # 检查音频文件是否存在
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"找不到音频文件: '{audio_path}'")

    # 设置 API 密钥优先级：参数 > 环境变量
    if api_key is None:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("未提供 API 密钥。请设置 OPENAI_API_KEY 环境变量或通过 --api-key 参数提供")

    # 初始化客户端
    client = OpenAI(api_key=api_key)

    # 设置默认输出文件名
    if output_path is None:
        base_name = os.path.splitext(audio_path)[0]
        output_path = f"{base_name}.srt"

    print(f"正在处理音频文件: {audio_path}")
    print("正在生成 SRT 字幕，请稍候...")

    try:
        with open(audio_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="srt"
            )

        # 写入字幕文件
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(transcription)

        print(f"✓ 字幕生成成功！")
        print(f"  输出文件: {output_path}")

        # 打印前 5 条字幕预览
        lines = transcription.splitlines()
        preview_lines = []
        subtitle_count = 0
        for line in lines:
            preview_lines.append(line)
            if line.strip() == "":
                subtitle_count += 1
                if subtitle_count >= 3:
                    break

        print("\n字幕预览（前3条）:")
        print("-" * 40)
        print("\n".join(preview_lines))
        print("-" * 40)

        return output_path

    except Exception as e:
        raise RuntimeError(f"转录过程中发生错误: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="使用 OpenAI Whisper API 生成 SRT 字幕文件",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python whisper_subtitle.py audio.mp3
  python whisper_subtitle.py audio.mp3 -o subtitle.srt
  python whisper_subtitle.py audio.mp3 --api-key your-api-key
        """
    )

    parser.add_argument("audio_file", help="输入音频文件路径")
    parser.add_argument("-o", "--output", help="输出 SRT 文件路径（可选）")
    parser.add_argument("--api-key", help="OpenAI API 密钥（可选，默认从 OPENAI_API_KEY 环境变量获取）")

    args = parser.parse_args()

    try:
        transcribe_audio(args.audio_file, args.output, args.api_key)
    except FileNotFoundError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)
    except RuntimeError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n操作已取消", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
