#!/usr/bin/env python3
"""
获取 X (Twitter) 用户信息

用法:
    python get_user_info.py <username>

示例:
    python get_user_info.py cheerselflin
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


def get_user_info(username):
    """获取用户信息"""
    params = {
        "user.fields": "created_at,description,public_metrics,profile_image_url,verified",
    }

    return api_request(f"/users/by/username/{username}", params)


def main():
    if len(sys.argv) < 2:
        print("用法: python get_user_info.py <username>", file=sys.stderr)
        sys.exit(1)

    username = sys.argv[1]

    try:
        result = get_user_info(username)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
