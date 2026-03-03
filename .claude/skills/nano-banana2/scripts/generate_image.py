#!/usr/bin/env python3
"""
使用 OpenRouter 的 Google Gemini 模型生成/编辑图片

支持:
1. 文生图 (text-to-image): 根据描述生成图片
2. 图生图 (image-to-image): 基于已有图片进行修改编辑

环境变量:
    OPENROUTER_API_KEY: OpenRouter API 密钥

用法:
    # 文生图
    python generate_image.py "描述文本" [--output OUTPUT_PATH]

    # 图生图 - 基于图片进行修改
    python generate_image.py --image ./input.png "修改指令" [--output OUTPUT_PATH]

示例:
    # 文生图
    python generate_image.py "Generate a beautiful sunset over mountains"
    python generate_image.py "一只可爱的猫咪" --output ./cat.png

    # 图生图
    python generate_image.py --image ./photo.png "Change the style to cyberpunk"
    python generate_image.py --image ./portrait.jpg "Change the person to wear a red jacket" --output ./edited.png
"""

import os
import sys
import argparse
import base64
import requests
import json


def encode_image_to_base64(image_path):
    """将本地图片转换为 base64 data URL"""
    try:
        with open(image_path, "rb") as f:
            image_bytes = f.read()

        # 检测文件类型
        ext = os.path.splitext(image_path)[1].lower()
        mime_type = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.webp': 'image/webp',
            '.gif': 'image/gif'
        }.get(ext, 'image/png')

        base64_data = base64.b64encode(image_bytes).decode('utf-8')
        return f"data:{mime_type};base64,{base64_data}"
    except Exception as e:
        print(f"❌ 读取图片失败: {e}")
        return None


def generate_image(prompt, api_key=None, image_path=None):
    """
    使用 OpenRouter 的 Google Gemini 模型生成/编辑图片

    Args:
        prompt: 图片描述文本或修改指令
        api_key: OpenRouter API 密钥（可选，默认从环境变量读取）
        image_path: 输入图片路径（可选，用于图生图模式）

    Returns:
        包含图片数据的字典，失败返回 None
    """
    if api_key is None:
        api_key = os.environ.get("OPENROUTER_API_KEY")

    if not api_key:
        print("❌ 错误: 未设置 OPENROUTER_API_KEY 环境变量")
        print("请设置环境变量: export OPENROUTER_API_KEY='your-api-key'")
        return None

    # 构建消息内容
    if image_path:
        # 图生图模式
        base64_image = encode_image_to_base64(image_path)
        if not base64_image:
            return None

        content = [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": base64_image}}
        ]
        print(f"🖼️  图生图模式 - 基于图片: {image_path}")
    else:
        # 文生图模式
        content = prompt
        print(f"📝 文生图模式")

    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        data=json.dumps({
            "model": "google/gemini-3.1-flash-image-preview",
            "messages": [
                {
                    "role": "user",
                    "content": content
                }
            ],
            "modalities": ["image", "text"]
        })
    )

    if response.status_code != 200:
        print(f"❌ API 请求失败: {response.status_code}")
        print(f"响应: {response.text}")
        return None

    result = response.json()

    # 检查响应结构
    if not result.get("choices"):
        print("❌ API 响应中没有 choices")
        print(f"响应: {json.dumps(result, indent=2)}")
        return None

    message = result["choices"][0].get("message", {})

    # 提取图片数据
    images = []
    if message.get("images"):
        images = message["images"]
    elif message.get("content"):
        # 尝试从 content 中解析图片
        content = message["content"]
        if isinstance(content, list):
            for item in content:
                if isinstance(item, dict) and item.get("type") == "image_url":
                    images.append(item)

    if not images:
        print("⚠️ 未在响应中找到图片")
        print(f"响应内容: {json.dumps(message, indent=2)}")
        return None

    return {
        "images": images,
        "text": message.get("content", "") if isinstance(message.get("content"), str) else ""
    }


def save_image(image_data, output_path):
    """
    保存 base64 编码的图片到文件

    Args:
        image_data: 包含 image_url 的字典
        output_path: 输出文件路径

    Returns:
        成功返回文件路径，失败返回 None
    """
    try:
        image_url = image_data.get("image_url", {}).get("url", "")

        if not image_url:
            print("❌ 图片数据中没有 URL")
            return None

        # 处理 base64 data URL
        if image_url.startswith("data:image"):
            # 提取 base64 数据
            base64_data = image_url.split(",")[1]
            image_bytes = base64.b64decode(base64_data)
        else:
            # 普通 URL，下载图片
            response = requests.get(image_url)
            image_bytes = response.content

        # 确保输出目录存在
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # 保存图片
        with open(output_path, "wb") as f:
            f.write(image_bytes)

        return output_path

    except Exception as e:
        print(f"❌ 保存图片失败: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(
        description="使用 OpenRouter 的 Google Gemini 模型生成/编辑图片",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 文生图
  %(prog)s "A beautiful sunset over mountains"
  %(prog)s "一只可爱的猫咪" --output ./cat.png

  # 图生图 (基于已有图片修改)
  %(prog)s --image ./input.png "Change to cyberpunk style"
  %(prog)s --image ./portrait.jpg "Change the person to wear a red jacket" --output ./edited.png
        """
    )
    parser.add_argument(
        "prompt",
        help="图片描述文本或修改指令"
    )
    parser.add_argument(
        "--image", "-i",
        help="输入图片路径（用于图生图模式，基于该图片进行修改）"
    )
    parser.add_argument(
        "--output", "-o",
        help="输出文件路径（默认: generated_image.png）",
        default="generated_image.png"
    )
    parser.add_argument(
        "--api-key",
        help="OpenRouter API 密钥（默认从环境变量 OPENROUTER_API_KEY 读取）"
    )

    args = parser.parse_args()

    print(f"🎨 正在生成图片...")
    print(f"📝 提示词: {args.prompt}")

    # 生成图片
    result = generate_image(args.prompt, args.api_key, args.image)

    if not result:
        sys.exit(1)

    # 保存图片
    if result.get("images"):
        image = result["images"][0]
        saved_path = save_image(image, args.output)

        if saved_path:
            print(f"✅ 图片已保存: {saved_path}")

            # 显示文本响应（如果有）
            if result.get("text"):
                print(f"💬 模型回复: {result['text']}")
        else:
            print("❌ 保存图片失败")
            sys.exit(1)
    else:
        print("❌ 未生成图片")
        sys.exit(1)


if __name__ == "__main__":
    main()
