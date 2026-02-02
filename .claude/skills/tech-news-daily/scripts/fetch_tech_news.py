#!/usr/bin/env python3
"""
多源科技新闻聚合器
支持从多个科技新闻网站 RSS 源获取最新资讯
"""

import argparse
import json
import sys
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Set
import feedparser


# 默认 RSS 源配置
DEFAULT_SOURCES = {
    "techcrunch": "https://techcrunch.com/feed/",
    "theverge": "https://www.theverge.com/rss/index.xml",
    "arstechnica": "https://feeds.arstechnica.com/arstechnica/index",
    "venturebeat": "https://venturebeat.com/feed/",
    "mitreview": "https://www.technologyreview.com/feed/",
    "36kr": "https://36kr.com/feed",
    "tmt": "https://www.tmtpost.com/feed",
    "huxiu": "https://www.huxiu.com/rss/0.xml",
}


def get_content_hash(title: str, url: str) -> str:
    """
    生成内容哈希，用于去重

    Args:
        title: 新闻标题
        url: 新闻链接

    Returns:
        str: MD5 哈希值
    """
    content = f"{title}{url}".encode('utf-8')
    return hashlib.md5(content).hexdigest()


def parse_rss_feed(source_name: str, feed_url: str, seen_hashes: Set[str]) -> List[Dict[str, Any]]:
    """
    解析单个 RSS 源

    Args:
        source_name: 源名称
        feed_url: RSS feed URL
        seen_hashes: 已见过的哈希集合，用于去重

    Returns:
        List[Dict[str, Any]]: 新闻列表
    """
    print(f"正在获取 {source_name}...", file=sys.stderr)

    try:
        feed = feedparser.parse(feed_url)

        if feed.bozo:
            print(f"警告: {source_name} 解析可能存在问题", file=sys.stderr)

        entries = []
        for entry in feed.entries:
            title = entry.get('title', '')
            link = entry.get('link', '')

            if not title or not link:
                continue

            # 去重
            content_hash = get_content_hash(title, link)
            if content_hash in seen_hashes:
                continue

            seen_hashes.add(content_hash)

            # 解析时间
            published = entry.get('published', '')
            datetime_str = published
            timestamp = 0

            if published:
                try:
                    # 尝试解析时间戳
                    parsed_time = feedparser._parse_date(published)
                    if parsed_time:
                        timestamp = int(parsed_time.timestamp())
                        datetime_str = parsed_time.strftime("%Y-%m-%d %H:%M:%S")
                except:
                    pass

            entries.append({
                "id": content_hash,  # 使用哈希作为 ID
                "title": title,
                "url": link,
                "source": source_name,
                "score": 0,  # RSS 不提供分数
                "by": entry.get('author', ''),
                "time": timestamp,
                "datetime": datetime_str,
                "descendants": 0,  # RSS 不提供评论数
                "summary": entry.get('summary', ''),
                "published": published,
                "hn_link": link  # 直接使用原链接
            })

        print(f"从 {source_name} 获取了 {len(entries)} 条新闻", file=sys.stderr)
        return entries

    except Exception as e:
        print(f"获取 {source_name} 失败: {e}", file=sys.stderr)
        return []


def fetch_news(sources: Dict[str, str], limit: int = 20) -> List[Dict[str, Any]]:
    """
    从多个源获取新闻

    Args:
        sources: RSS 源字典 {name: url}
        limit: 总数量限制

    Returns:
        List[Dict[str, Any]]: 新闻列表
    """
    all_entries = []
    seen_hashes = set()

    # 从所有源获取新闻
    for source_name, feed_url in sources.items():
        entries = parse_rss_feed(source_name, feed_url, seen_hashes)
        all_entries.extend(entries)

    # 按时间排序
    all_entries.sort(key=lambda x: x.get('time', 0), reverse=True)

    # 限制数量
    return all_entries[:limit]


def main():
    parser = argparse.ArgumentParser(description="从多个科技新闻源获取最新资讯")
    parser.add_argument(
        "--limit",
        type=int,
        default=30,
        help="获取新闻总数（默认: 30）"
    )
    parser.add_argument(
        "--sources",
        type=str,
        nargs='+',
        help="指定使用的源（可选: techcrunch, theverge, arstechnica, venturebeat, mitreview, 36kr, tmt, huxiu），默认使用全部"
    )
    parser.add_argument(
        "--list-sources",
        action="store_true",
        help="列出所有可用源"
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

    # 列出所有源
    if args.list_sources:
        print("可用源:")
        for name, url in DEFAULT_SOURCES.items():
            print(f"  {name}: {url}")
        return

    # 确定使用的源
    if args.sources:
        # 验证源名称
        invalid_sources = [s for s in args.sources if s not in DEFAULT_SOURCES]
        if invalid_sources:
            print(f"错误: 无效的源名称: {', '.join(invalid_sources)}", file=sys.stderr)
            print(f"可用源: {', '.join(DEFAULT_SOURCES.keys())}", file=sys.stderr)
            sys.exit(1)

        selected_sources = {name: DEFAULT_SOURCES[name] for name in args.sources}
    else:
        selected_sources = DEFAULT_SOURCES

    # 获取新闻
    stories = fetch_news(selected_sources, args.limit)

    # 输出
    if args.pretty:
        output = json.dumps(stories, ensure_ascii=False, indent=2)
    else:
        output = json.dumps(stories, ensure_ascii=False)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"已获取 {len(stories)} 条新闻，保存至 {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
