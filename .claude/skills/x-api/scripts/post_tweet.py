#!/usr/bin/env python3
"""
发布推文到 X (Twitter) - OAuth 1.0a

用法:
    python post_tweet.py "推文内容"
    python post_tweet.py "推文内容" --media /path/to/image.jpg
    python post_tweet.py "推文内容" --media-id MEDIA_ID123

示例:
    python post_tweet.py "Hello, World!"
    python post_tweet.py "Check out this photo!" --media ./photo.png
    python post_tweet.py "Multiple images" -m ./img1.jpg -m ./img2.jpg
"""

import sys
import os
import json
import urllib.request
import urllib.error
import base64
import hashlib
import hmac
import time
import random
from urllib.parse import quote

API_BASE_URL = "https://api.x.com/2"
API_KEY = os.environ.get("X_API_KEY")
API_SECRET = os.environ.get("X_API_SECRET")
ACCESS_TOKEN = os.environ.get("X_ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.environ.get("X_ACCESS_TOKEN_SECRET")


def create_oauth_signature(method, url, params, signing_key):
    """创建 OAuth 1.0a 签名"""
    # 按参数名排序并编码
    sorted_params = sorted(params.items())
    param_string = "&".join(
        f"{quote(k, safe='')}={quote(v, safe='')}" for k, v in sorted_params
    )

    # 构建签名基字符串
    base_string = "&".join([
        method.upper(),
        quote(url, safe=''),
        quote(param_string, safe='')
    ])

    # HMAC-SHA1 签名
    signature = hmac.new(
        signing_key.encode('utf-8'),
        base_string.encode('utf-8'),
        hashlib.sha1
    ).digest()

    return base64.b64encode(signature).decode('utf-8')


def create_auth_header(method, url, oauth_params):
    """创建 OAuth 认证头"""
    # 合并 OAuth 参数
    oauth_params = {
        **oauth_params,
        "oauth_consumer_key": API_KEY,
        "oauth_token": ACCESS_TOKEN,
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp": str(int(time.time())),
        "oauth_nonce": hashlib.md5(str(random.random()).encode()).hexdigest(),
        "oauth_version": "1.0",
    }

    # 创建签名密钥
    signing_key = f"{quote(API_SECRET, safe='')}&{quote(ACCESS_TOKEN_SECRET, safe='')}"

    # 生成签名
    oauth_params["oauth_signature"] = create_oauth_signature(
        method, url, oauth_params, signing_key
    )

    # 构建 Authorization 头
    auth_header = "OAuth " + ", ".join(
        f'{quote(k, safe="")}="{quote(v, safe="")}"'
        for k, v in sorted(oauth_params.items())
        if k.startswith("oauth_")
    )

    return auth_header


def post_tweet(text, reply_to=None, media_ids=None):
    """发布推文"""
    if not all([API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET]):
        raise ValueError(
            "缺少 OAuth 1.0a 认证环境变量。请配置:\n"
            "  - X_API_KEY\n"
            "  - X_API_SECRET\n"
            "  - X_ACCESS_TOKEN\n"
            "  - X_ACCESS_TOKEN_SECRET"
        )

    url = f"{API_BASE_URL}/tweets"

    # 请求体
    payload = {"text": text}
    if reply_to:
        payload["reply"] = {"in_reply_to_tweet_id": reply_to}

    # 添加媒体
    if media_ids:
        payload["media"] = {"media_ids": media_ids}

    body = json.dumps(payload).encode('utf-8')

    # OAuth 参数（不含请求体参数）
    oauth_params = {}

    # 创建请求
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": create_auth_header("POST", url, oauth_params),
            "Content-Type": "application/json",
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        try:
            error_data = json.loads(error_body)
            detail = error_data.get("detail", error_body)
        except:
            detail = error_body

        # 处理特定错误
        if e.code == 401:
            raise Exception(
                "认证失败 (401)。请检查:\n"
                "1. X_API_KEY 和 X_API_SECRET 是否正确\n"
                "2. X_ACCESS_TOKEN 和 X_ACCESS_TOKEN_SECRET 是否正确\n"
                "3. 应用是否有写权限 (Write permission)"
            )
        elif e.code == 403:
            raise Exception(
                "权限不足 (403)。请确保:\n"
                "1. 应用已启用 'Read and Write' 权限\n"
                "2. Access Token 已刷新以应用新权限"
            )
        elif e.code == 429:
            raise Exception("请求过于频繁 (429)，请稍后再试")
        else:
            raise Exception(f"API 请求失败: {e.code} - {detail}")


def format_output(data):
    """格式化输出结果"""
    tweet = data.get("data", {})
    tweet_id = tweet.get("id")
    text = tweet.get("text")

    output = []
    output.append("\n" + "=" * 60)
    output.append("✅ 推文发布成功！")
    output.append("=" * 60)
    output.append(f"\n📝 内容:\n{text}")
    output.append(f"\n🔗 链接: https://x.com/i/web/status/{tweet_id}")
    output.append(f"🆔 ID: {tweet_id}")

    return "\n".join(output)


def main():
    import argparse

    parser = argparse.ArgumentParser(description='发布推文到 X (Twitter)')
    parser.add_argument('text', help='推文内容')
    parser.add_argument('--media', '-m', help='媒体文件路径或 media_id（可多次使用）', action='append')
    parser.add_argument('--media-id', help='已上传的 media_id（可多次使用）', action='append')
    parser.add_argument('--reply', '-r', help='回复的推文 ID')

    args = parser.parse_args()

    text = args.text
    media_ids = []

    # 处理 media_id 参数
    if args.media_id:
        media_ids.extend(args.media_id)

    # 处理媒体文件上传
    if args.media:
        for media_path in args.media:
            if os.path.exists(media_path):
                # 需要上传文件
                print(f"正在上传媒体: {media_path}...")
                try:
                    # 动态导入 upload_media 模块
                    import importlib.util
                    script_dir = os.path.dirname(os.path.abspath(__file__))
                    upload_script = os.path.join(script_dir, 'upload_media.py')

                    spec = importlib.util.spec_from_file_location("upload_media", upload_script)
                    upload_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(upload_module)

                    result = upload_module.upload_media(media_path)
                    media_id = result.get("media_id_string")
                    media_ids.append(media_id)
                    print(f"✅ 上传成功: {media_id}")
                except Exception as e:
                    print(f"❌ 上传失败: {e}", file=sys.stderr)
                    sys.exit(1)
            else:
                # 可能是 media_id
                media_ids.append(media_path)

    # 检查推文长度 (X 限制 280 字符，图片不占用字符数)
    if len(text) > 280:
        print(f"错误: 推文内容超过 280 字符限制 (当前 {len(text)} 字符)", file=sys.stderr)
        sys.exit(1)

    try:
        result = post_tweet(text, reply_to=args.reply, media_ids=media_ids if media_ids else None)
        print(format_output(result))
    except Exception as e:
        print(f"\n❌ {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
