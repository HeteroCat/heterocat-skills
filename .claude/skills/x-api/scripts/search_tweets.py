#!/usr/bin/env python3
"""
搜索 X (Twitter) 推文

用法:
    python search_tweets.py "<query>" [max_results]

示例:
    python search_tweets.py "from:cheerselflin" 10
    python search_tweets.py "#Python" 20
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


def search_tweets(query, max_results=10):
    """搜索推文"""
    params = {
        "query": query,
        "max_results": min(max(max_results, 1), 100),
        "tweet.fields": "created_at,public_metrics,author_id",
    }

    return api_request("/tweets/search/recent", params)


def main():
    if len(sys.argv) < 2:
        print("用法: python search_tweets.py \"<query>\" [max_results]", file=sys.stderr)
        sys.exit(1)

    query = sys.argv[1]
    max_results = int(sys.argv[2]) if len(sys.argv) > 2 else 10

    try:
        result = search_tweets(query, max_results)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
