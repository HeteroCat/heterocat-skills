#!/usr/bin/env python3
"""
Doubao Seedance Video Generation - Utilities
"""
import base64
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime

from config import VALID_IMAGE_EXTENSIONS


def print_info(message: str):
    """Print info message in blue"""
    print(f"\033[0;34m[INFO]\033[0m {message}")


def print_success(message: str):
    """Print success message in green"""
    print(f"\033[0;32m[SUCCESS]\033[0m {message}")


def print_error(message: str):
    """Print error message in red"""
    print(f"\033[0;31m[ERROR]\033[0m {message}", file=sys.stderr)


def print_warning(message: str):
    """Print warning message in yellow"""
    print(f"\033[1;33m[WARNING]\033[0m {message}")


def print_progress(message: str):
    """Print progress message in cyan"""
    print(f"\033[0;36m[PROGRESS]\033[0m {message}")


def image_to_base64(image_path: str) -> str:
    """
    Convert image file to base64 data URI

    Args:
        image_path: Path to image file

    Returns:
        Data URI string (e.g., "data:image/jpeg;base64,...")

    Raises:
        FileNotFoundError: If image file doesn't exist
        ValueError: If image format is not supported
    """
    path = Path(image_path)

    if not path.exists():
        raise FileNotFoundError(f"图片文件不存在: {image_path}")

    ext = path.suffix.lower()
    if ext not in VALID_IMAGE_EXTENSIONS:
        raise ValueError(f"不支持的图片格式: {ext}（支持: {', '.join(VALID_IMAGE_EXTENSIONS)}）")

    # Determine MIME type
    mime_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
    }
    mime_type = mime_types[ext]

    # Read and encode image
    with open(path, "rb") as f:
        image_data = f.read()
        base64_data = base64.b64encode(image_data).decode("utf-8")

    return f"data:{mime_type};base64,{base64_data}"


def sanitize_filename(text: str, max_length: int = 20) -> str:
    """
    Sanitize text for use in filename

    Args:
        text: Input text
        max_length: Maximum length

    Returns:
        Sanitized filename string
    """
    # Take first max_length characters
    text = text[:max_length]

    # Replace spaces with underscores
    text = text.replace(" ", "_")

    # Remove invalid characters
    valid_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-")
    text = "".join(c for c in text if c in valid_chars)

    # Fallback if empty
    if not text:
        text = "video"

    return text


def generate_output_filename(prompt: str, output_dir: str) -> str:
    """
    Generate output filename based on prompt

    Args:
        prompt: Video prompt
        output_dir: Output directory

    Returns:
        Full path for output file
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_prompt = sanitize_filename(prompt)

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    return str(output_path / f"{safe_prompt}_{timestamp}.mp4")
