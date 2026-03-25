#!/usr/bin/env python3
"""
获取 X (Twitter) 用户的最新推文 - 飞书友好格式

用法:
    python get_user_tweets.py <username> [max_results]

示例:
    python get_user_tweets.py cheerselflin 5

输出格式 (2026-02-28优化):
- 标题：# 序号. YYYY-MM-DD HH:MM
- 推文内容：使用 > 引用块展示原文
- 媒体：直接链接格式 "图片: https://..." / "视频: https://..."
- 统计：❤️likes 🔄RTs 💬回复 🔁quotes
- 无 Markdown 图像语法 ![alt](url)（飞书不渲染）
- 无代码块
"""

import sys
import os
import json
import urllib.request
import urllib.error
from urllib.parse import urlencode
from datetime import datetime

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


def format_tweet(tweet, media_map, index):
    """格式化单条推文为飞书友好格式"""
    created_at = tweet.get("created_at", "")
    # 转换时间格式
    try:
        dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        time_str = dt.strftime("%Y-%m-%d %H:%M")
    except:
        time_str = created_at[:16].replace("T", " ")

    text = tweet.get("text", "")
    metrics = tweet.get("public_metrics", {})
    media_keys = tweet.get("attachments", {}).get("media_keys", [])

    # 统计
    likes = metrics.get("like_count", 0)
    retweets = metrics.get("retweet_count", 0)
    replies = metrics.get("reply_count", 0)
    quotes = metrics.get("quote_count", 0)

    lines = []
    # 标题
    lines.append(f"# {index}. {time_str}")
    lines.append("")

    # 推文内容（引用块）
    lines.append(f"> {text}")
    lines.append("")

    # 媒体
    for key in media_keys:
        media = media_map.get(key)
        if not media:
            continue

        media_type = media.get("type")

        if media_type == "photo":
            url = media.get("url", "")
            lines.append(f"图片: {url}")

        elif media_type == "video":
            # 视频取最高清版本
            variants = media.get("variants", [])
            mp4_variants = [v for v in variants if v.get("content_type") == "video/mp4"]
            if mp4_variants:
                best = max(mp4_variants, key=lambda x: x.get("bit_rate", 0))
                video_url = best.get("url", "")
                lines.append(f"视频: {video_url}")

            preview = media.get("preview_image_url", "")
            if preview:
                lines.append(f"预览图: {preview}")

    lines.append("")
    # 统计
    lines.append(f"❤️{likes} 🔄{retweets} 💬{replies} 🔁{quotes}")
    lines.append("")

    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("用法: python get_user_tweets.py <username> [max_results]", file=sys.stderr)
        print("\n示例:", file=sys.stderr)
        print("  python get_user_tweets.py cheerselflin 5", file=sys.stderr)
        sys.exit(1)

    username = sys.argv[1]
    max_results = int(sys.argv[2]) if len(sys.argv) > 2 else 5

    try:
        result = get_user_tweets(username, max_results)

        tweets = result.get("data", [])
        media_map = {m["media_key"]: m for m in result.get("includes", {}).get("media", [])}

        output = []
        for i, tweet in enumerate(tweets, 1):
            output.append(format_tweet(tweet, media_map, i))

        print("\n".join(output))

    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
