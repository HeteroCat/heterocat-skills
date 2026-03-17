#!/usr/bin/env python3
"""
Hacker News API 客户端
获取 Hacker News 最新科技新闻
"""

import argparse
import json
import sys
from datetime import datetime
from typing import List, Dict, Any

import requests


def fetch_new_stories() -> List[int]:
    """
    获取最新故事的 ID 列表

    Returns:
        List[int]: 故事 ID 列表
    """
    url = "https://hacker-news.firebaseio.com/v0/newstories.json"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"获取最新故事列表失败: {e}", file=sys.stderr)
        sys.exit(1)


def fetch_story_item(story_id: int) -> Dict[str, Any]:
    """
    获取单个故事的详细信息

    Args:
        story_id: 故事 ID

    Returns:
        Dict[str, Any]: 故事详情
    """
    url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"获取故事 {story_id} 详情失败: {e}", file=sys.stderr)
        return {}


def fetch_stories(limit: int = 20) -> List[Dict[str, Any]]:
    """
    获取最新的多条故事

    Args:
        limit: 获取数量

    Returns:
        List[Dict[str, Any]]: 故事列表
    """
    # 获取最新故事 ID 列表
    story_ids = fetch_new_stories()
    story_ids = story_ids[:limit]

    # 获取每个故事的详情
    stories = []
    for story_id in story_ids:
        story = fetch_story_item(story_id)
        if story and story.get("type") == "story":
            # 添加可读的时间戳
            timestamp = story.get("time", 0)
            story["datetime"] = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
            stories.append(story)

    return stories


def format_story(story: Dict[str, Any]) -> Dict[str, Any]:
    """
    格式化故事信息，提取关键字段

    Args:
        story: 原始故事数据

    Returns:
        Dict[str, Any]: 格式化后的故事
    """
    return {
        "id": story.get("id"),
        "title": story.get("title"),
        "url": story.get("url"),
        "score": story.get("score", 0),
        "by": story.get("by"),
        "time": story.get("time"),
        "datetime": story.get("datetime"),
        "descendants": story.get("descendants", 0),  # 评论数
        "hn_link": f"https://news.ycombinator.com/item?id={story.get('id')}"
    }


def main():
    parser = argparse.ArgumentParser(description="获取 Hacker News 最新科技新闻")
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="获取新闻数量（默认: 20）"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="输出文件路径（默认: 标准输出）"
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="美化 JSON 输出"
    )

    args = parser.parse_args()

    # 获取新闻
    stories = fetch_stories(args.limit)

    # 格式化新闻
    formatted_stories = [format_story(story) for story in stories]

    # 输出
    if args.pretty:
        output = json.dumps(formatted_stories, ensure_ascii=False, indent=2)
    else:
        output = json.dumps(formatted_stories, ensure_ascii=False)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"已获取 {len(formatted_stories)} 条新闻，保存至 {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
