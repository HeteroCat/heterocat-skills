---
name: x-api
description: "使用 X (Twitter) API v2 获取推文、用户信息等数据。用于：获取指定用户的最新推文、搜索推文、获取用户信息。需要配置 X_BEARER_TOKEN 环境变量。当用户需要获取 Twitter/X 上的推文或用户信息时触发。"
---

# X (Twitter) API

使用 X API v2 获取推文和用户信息。

## 前置要求

确保环境变量中已配置：
- `X_BEARER_TOKEN` - X API Bearer Token

## 可用功能

### 1. 获取用户最新推文

使用 `get_user_tweets.py` 脚本获取指定用户的最新推文。

**用法**:
```bash
python scripts/get_user_tweets.py <username> [max_results]
```

**参数**:
- `username` (string): 用户名（不含 @）
- `max_results` (number, 可选): 返回推文数量，默认 5，最大 100

**示例**:
```bash
python scripts/get_user_tweets.py cheerselflin 5
```

### 2. 搜索推文

使用 `search_tweets.py` 脚本搜索公开推文。

**用法**:
```bash
python scripts/search_tweets.py "<query>" [max_results]
```

**参数**:
- `query` (string): 搜索查询（支持 X 搜索语法，如 "from:username"、"#hashtag"）
- `max_results` (number, 可选): 返回推文数量，默认 10，最大 100

**示例**:
```bash
python scripts/search_tweets.py "from:cheerselflin" 5
```

### 3. 获取用户信息

使用 `get_user_info.py` 脚本获取用户详细信息。

**用法**:
```bash
python scripts/get_user_info.py <username>
```

**示例**:
```bash
python scripts/get_user_info.py cheerselflin
```

## 返回数据格式

### 推文数据
```json
{
  "id": "1234567890",
  "text": "推文内容",
  "created_at": "2024-01-01T00:00:00Z",
  "public_metrics": {
    "retweet_count": 10,
    "reply_count": 5,
    "like_count": 20,
    "quote_count": 2
  }
}
```

### 用户数据
```json
{
  "id": "1234567890",
  "name": "显示名称",
  "username": "cheerselflin",
  "description": "个人简介",
  "public_metrics": {
    "followers_count": 1000,
    "following_count": 500,
    "tweet_count": 10000,
    "listed_count": 50
  },
  "created_at": "2010-01-01T00:00:00Z",
  "profile_image_url": "https://...",
  "verified": false
}
```

## 错误处理

脚本会处理以下错误：
- `401` - 认证失败，检查 Bearer Token
- `403` - 权限不足或超出请求限制
- `404` - 用户不存在
- `429` - 请求过于频繁，需要等待重置

## 注意事项

1. **请求限制**: X API v2 有速率限制
2. **数据保留**: `search/recent` 仅返回最近 7 天的推文
3. **认证**: 仅支持 Bearer Token 认证（只读访问）

## 参考文档

- [X API v2 文档](https://docs.x.com/x-api/introduction)
