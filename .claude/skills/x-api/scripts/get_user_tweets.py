#!/usr/bin/env python3
"""
获取 X (Twitter) 用户的最新推文

用法:
    python get_user_tweets.py <username> [max_results]

示例:
    python get_user_tweets.py cheerselflin 5
"""

import sys
import os
import json
import urllib.request
import urllib.error
from urllib.parse import urlencode

API_BASE_URL = "https://api.x.com/2"
BEARER_TOKEN = os.environ.get("X_BEARER_TOKEN")


def api_request(endpoint, params=None):
    """发起 API 请求"""
    if not BEARER_TOKEN:
        raise ValueError("X_BEARER_TOKEN 环境变量未配置")

    url = f"{API_BASE_URL}{endpoint}"
    if params:
        url += "?" + urlencode(params)

    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {BEARER_TOKEN}",
            "Content-Type": "application/json",
        }
    )

    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        raise Exception(f"API 请求失败: {e.code} {e.reason} - {error_body}")


def get_user_id(username):
    """通过用户名获取用户 ID"""
    data = api_request(f"/users/by/username/{username}", {"user.fields": "id"})
    return data["data"]["id"]


def get_user_tweets(username, max_results=5):
    """获取用户最新推文"""
    user_id = get_user_id(username)

    params = {
        "max_results": min(max(max_results, 1), 100),
        "tweet.fields": "created_at,public_metrics,attachments",
        "expansions": "attachments.media_keys",
        "media.fields": "url,preview_image_url,type,width,height,variants",
    }

    return api_request(f"/users/{user_id}/tweets", params)


def format_output(data):
    """格式化输出推文"""
    tweets = data.get("data", [])
    media_map = {m["media_key"]: m for m in data.get("includes", {}).get("media", [])}

    output = []
    for i, tweet in enumerate(tweets, 1):
        # 基本信息
        created_at = tweet.get("created_at", "").replace("T", " ").replace("Z", "")[:19]  # 显示到秒
        text = tweet.get("text", "")
        metrics = tweet.get("public_metrics", {})

        output.append(f"\n{'='*60}")
        output.append(f"[{i}] {created_at}")
        output.append(f"{'='*60}")
        output.append(f"{text}")
        output.append("")

        # 互动数据
        likes = metrics.get("like_count", 0)
        retweets = metrics.get("retweet_count", 0)
        replies = metrics.get("reply_count", 0)
        views = metrics.get("impression_count", 0)
        output.append(f"❤️ {likes}  🔄 {retweets}  💬 {replies}  👁 {views:,}")

        # 媒体信息
        media_keys = tweet.get("attachments", {}).get("media_keys", [])
        if media_keys:
            output.append("")
            for key in media_keys:
                media = media_map.get(key)
                if not media:
                    continue

                media_type = media.get("type")
                width = media.get("width", 0)
                height = media.get("height", 0)

                if media_type == "photo":
                    # 图片
                    url = media.get("url", "")
                    output.append(f"📷 图片 ({width}x{height})")
                    output.append(f"   {url}")

                elif media_type == "video":
                    # 视频 - 只取最高清版本
                    variants = media.get("variants", [])
                    mp4_variants = [v for v in variants if v.get("content_type") == "video/mp4"]

                    if mp4_variants:
                        # 按比特率排序，取最高的（最清晰的）
                        best = max(mp4_variants, key=lambda x: x.get("bit_rate", 0))
                        video_url = best.get("url", "")
                        output.append(f"🎬 视频 ({width}x{height})")
                        output.append(f"   {video_url}")

                    preview = media.get("preview_image_url", "")
                    if preview:
                        output.append(f"   预览图: {preview}")

    return "\n".join(output)


def main():
    if len(sys.argv) < 2:
        print("用法: python get_user_tweets.py <username> [max_results]", file=sys.stderr)
        sys.exit(1)

    username = sys.argv[1]
    max_results = int(sys.argv[2]) if len(sys.argv) > 2 else 5

    try:
        result = get_user_tweets(username, max_results)
        # 输出格式化结果
        print(format_output(result))
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
