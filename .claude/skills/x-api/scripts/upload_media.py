#!/usr/bin/env python3
"""
上传媒体文件到 X (Twitter) - 支持 chunked upload（大视频文件）

用法:
    python upload_media.py <文件路径>

示例:
    python upload_media.py /path/to/image.jpg
    python upload_media.py /path/to/video.mp4
"""

import sys
import os
import json
import urllib.request
import urllib.error
import urllib.parse
import base64
import hashlib
import hmac
import time
import random
from urllib.parse import quote

# X API v1.1 媒体上传端点
UPLOAD_URL = "https://upload.x.com/1.1/media/upload.json"

API_KEY = os.environ.get("X_API_KEY")
API_SECRET = os.environ.get("X_API_SECRET")
ACCESS_TOKEN = os.environ.get("X_ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.environ.get("X_ACCESS_TOKEN_SECRET")

# Chunk size for video upload (5MB)
CHUNK_SIZE = 5 * 1024 * 1024


def create_oauth_signature(method, url, params, signing_key):
    """创建 OAuth 1.0a 签名"""
    sorted_params = sorted(params.items())
    param_string = "&".join(
        f"{quote(k, safe='')}={quote(v, safe='')}" for k, v in sorted_params
    )

    base_string = "&".join([
        method.upper(),
        urllib.parse.quote(url, safe=''),
        urllib.parse.quote(param_string, safe='')
    ])

    signature = hmac.new(
        signing_key.encode('utf-8'),
        base_string.encode('utf-8'),
        hashlib.sha1
    ).digest()

    return base64.b64encode(signature).decode('utf-8')


def create_auth_header(method, url, params=None):
    """创建 OAuth 认证头"""
    if params is None:
        params = {}

    # 解析 URL 中的查询参数
    parsed_url = urllib.parse.urlparse(url)
    url_params = dict(urllib.parse.parse_qsl(parsed_url.query))

    # 合并参数：URL 参数 + 传入的参数
    all_params = {**url_params, **params}

    oauth_params = {
        **all_params,
        "oauth_consumer_key": API_KEY,
        "oauth_token": ACCESS_TOKEN,
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp": str(int(time.time())),
        "oauth_nonce": hashlib.md5(str(random.random()).encode()).hexdigest(),
        "oauth_version": "1.0",
    }

    # 使用不带查询参数的 URL 进行签名
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"

    signing_key = f"{quote(API_SECRET, safe='')}&{quote(ACCESS_TOKEN_SECRET, safe='')}"
    oauth_params["oauth_signature"] = create_oauth_signature(method, base_url, oauth_params, signing_key)

    auth_header = "OAuth " + ", ".join(
        f'{quote(k, safe="")}="{quote(v, safe="")}"'
        for k, v in sorted(oauth_params.items())
        if k.startswith("oauth_")
    )

    return auth_header


def api_request(url, data=None, headers=None, method="GET", oauth_params=None):
    """发起 API 请求"""
    if headers is None:
        headers = {}
    if oauth_params is None:
        oauth_params = {}

    headers["Authorization"] = create_auth_header(method, url, oauth_params)

    req = urllib.request.Request(
        url,
        data=data,
        headers=headers,
        method=method
    )

    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        raise Exception(f"API 请求失败: {e.code} - {error_body}")


def upload_media_simple(file_path, file_data, mime_type):
    """简单上传（适用于小图片）"""
    file_name = os.path.basename(file_path)

    # 构建 multipart/form-data
    boundary = "----WebKitFormBoundary" + os.urandom(16).hex()

    body = b''
    body += f"--{boundary}\r\n".encode()
    body += f'Content-Disposition: form-data; name="media"; filename="{file_name}"\r\n'.encode()
    body += f"Content-Type: {mime_type}\r\n\r\n".encode()
    body += file_data
    body += f"\r\n--{boundary}--\r\n".encode()

    req = urllib.request.Request(
        UPLOAD_URL,
        data=body,
        headers={
            "Authorization": create_auth_header("POST", UPLOAD_URL),
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        },
        method="POST"
    )

    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode("utf-8"))


def upload_media_chunked(file_path, file_data, mime_type):
    """分块上传（适用于视频）"""
    file_size = len(file_data)
    file_name = os.path.basename(file_path)

    # 检测媒体类别
    media_category = None
    if mime_type.startswith('video/'):
        media_category = "tweet_video"
    elif mime_type == 'image/gif':
        media_category = "tweet_gif"
    elif mime_type.startswith('image/'):
        media_category = "tweet_image"

    print(f"  媒体类型: {mime_type}")
    print(f"  媒体类别: {media_category}")

    # Step 1: INIT - 初始化上传
    print("  [1/3] 初始化上传...")
    init_params = {
        "command": "INIT",
        "total_bytes": str(file_size),
        "media_type": mime_type,
    }
    if media_category:
        init_params["media_category"] = media_category

    init_data = urllib.parse.urlencode(init_params).encode()
    init_result = api_request(UPLOAD_URL, data=init_data, headers={
        "Content-Type": "application/x-www-form-urlencoded"
    }, method="POST", oauth_params=init_params)

    media_id = init_result.get("media_id_string")
    print(f"  ✓ Media ID: {media_id}")

    # Step 2: APPEND - 上传数据块
    print("  [2/3] 上传数据块...")
    segment_index = 0
    bytes_sent = 0

    while bytes_sent < file_size:
        chunk = file_data[bytes_sent:bytes_sent + CHUNK_SIZE]
        chunk_size = len(chunk)

        # 构建 multipart 请求体
        boundary = "----WebKitFormBoundary" + os.urandom(16).hex()

        body = b''
        body += f"--{boundary}\r\n".encode()
        body += b'Content-Disposition: form-data; name="media"; filename="chunk"\r\n'
        body += b"Content-Type: application/octet-stream\r\n\r\n"
        body += chunk
        body += f"\r\n--{boundary}--\r\n".encode()

        # APPEND 参数作为查询参数
        append_params = {
            "command": "APPEND",
            "media_id": media_id,
            "segment_index": str(segment_index),
        }

        # 构建带查询参数的 URL
        append_url = f"{UPLOAD_URL}?{urllib.parse.urlencode(append_params)}"

        # OAuth 签名 - URL 已包含查询参数，params 应只包含 OAuth 相关参数
        req = urllib.request.Request(
            append_url,
            data=body,
            headers={
                "Authorization": create_auth_header("POST", append_url),
                "Content-Type": f"multipart/form-data; boundary={boundary}",
            },
            method="POST"
        )

        with urllib.request.urlopen(req) as response:
            response.read()  # 消费响应

        bytes_sent += chunk_size
        segment_index += 1
        progress = (bytes_sent / file_size) * 100
        print(f"    进度: {progress:.1f}% ({bytes_sent}/{file_size} bytes)")

    print(f"  ✓ 分块上传完成 ({segment_index} 个块)")

    # Step 3: FINALIZE - 完成上传
    print("  [3/3] 完成上传...")
    finalize_params = {
        "command": "FINALIZE",
        "media_id": media_id,
    }

    finalize_data = urllib.parse.urlencode(finalize_params).encode()
    finalize_result = api_request(UPLOAD_URL, data=finalize_data, headers={
        "Content-Type": "application/x-www-form-urlencoded"
    }, method="POST", oauth_params=finalize_params)

    # Step 4: STATUS - 等待处理完成（视频需要）
    if media_category == "tweet_video":
        print("  [4/4] 等待视频处理...")
        max_retries = 30
        retry = 0

        while retry < max_retries:
            time.sleep(2)

            status_params = {
                "command": "STATUS",
                "media_id": media_id,
            }

            status_url = f"{UPLOAD_URL}?{urllib.parse.urlencode(status_params)}"
            status_result = api_request(status_url, oauth_params=status_params)

            processing_info = status_result.get("processing_info", {})
            state = processing_info.get("state", "unknown")

            if state == "succeeded":
                print("  ✓ 视频处理完成")
                break
            elif state == "failed":
                error = processing_info.get("error", {})
                raise Exception(f"视频处理失败: {error.get('message', '未知错误')}")
            elif state == "in_progress":
                progress = processing_info.get("progress_percent", 0)
                print(f"    处理中... {progress}%")

            retry += 1
        else:
            print("  ⚠ 等待超时，视频可能仍在处理中")

    return finalize_result


def upload_media(file_path):
    """上传媒体文件（自动选择上传方式）"""
    if not all([API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET]):
        raise ValueError(
            "缺少 OAuth 1.0a 认证环境变量。请配置:\n"
            "  - X_API_KEY\n"
            "  - X_API_SECRET\n"
            "  - X_ACCESS_TOKEN\n"
            "  - X_ACCESS_TOKEN_SECRET"
        )

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")

    # 读取文件
    with open(file_path, 'rb') as f:
        file_data = f.read()

    file_name = os.path.basename(file_path)
    file_size = len(file_data)

    # 检测 MIME 类型
    mime_type = "application/octet-stream"
    ext = os.path.splitext(file_path)[1].lower()
    mime_types = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.webp': 'image/webp',
        '.mp4': 'video/mp4',
        '.mov': 'video/quicktime',
    }
    mime_type = mime_types.get(ext, 'application/octet-stream')

    print(f"上传文件: {file_name}")
    print(f"  大小: {file_size:,} bytes ({file_size / 1024 / 1024:.2f} MB)")
    print(f"  MIME: {mime_type}")

    # 根据文件类型选择上传方式
    is_video = mime_type.startswith('video/')
    is_large = file_size > CHUNK_SIZE

    if is_video or is_large:
        # 使用分块上传
        print("  模式: 分块上传 (Chunked)")
        return upload_media_chunked(file_path, file_data, mime_type)
    else:
        # 使用简单上传
        print("  模式: 简单上传")
        return upload_media_simple(file_path, file_data, mime_type)


def main():
    if len(sys.argv) < 2:
        print("用法: python upload_media.py <文件路径>", file=sys.stderr)
        print("\n支持的格式: JPG, PNG, GIF, WEBP, MP4, MOV", file=sys.stderr)
        print("\n注意: 视频文件建议使用 H.264 编码的 MP4 格式", file=sys.stderr)
        sys.exit(1)

    file_path = sys.argv[1]

    try:
        result = upload_media(file_path)
        media_id = result.get("media_id_string")

        print("\n" + "=" * 60)
        print("✅ 媒体上传成功！")
        print("=" * 60)
        print(f"\n🆔 Media ID: {media_id}")
        print(f"📁 文件名: {os.path.basename(file_path)}")
        print(f"📐 尺寸: {result.get('size', 'unknown')} bytes")
        print(f"⏱️  过期时间: {result.get('expires_after_secs', 'unknown')} 秒")
        print(f"\n💡 使用方式:")
        print(f'   python post_tweet.py "推文内容" --media-id {media_id}')

    except Exception as e:
        print(f"\n❌ {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
