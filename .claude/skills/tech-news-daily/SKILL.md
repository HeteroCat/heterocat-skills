---
name: tech-news-daily
description: 获取每日科技圈最新消息，支持从多个科技新闻源（TechCrunch、The Verge、36氪等）获取最新资讯，并协助生成结构化的科技日报。适用于需要每日跟踪科技趋势、了解行业动态的场景。
dependency:
  python:
    - feedparser>=6.0.0
    - requests>=2.31.0
---

# 科技新闻日报生成器

## 任务目标
- 本 Skill 用于：自动获取科技圈最新消息并生成每日科技日报
- 能力包含：
  1. 从多个科技新闻源获取最新资讯（TechCrunch、The Verge、Ars Technica、36氪等）
  2. 按类别筛选和整理新闻内容
  3. 翻译并生成中文科技日报
- 触发条件：用户请求获取今日科技新闻、生成科技日报或询问科技资讯

## 前置准备
- 无需额外配置，所有新闻源均为公开 RSS，无需鉴权

## 操作步骤

### 1. 获取最新新闻数据
调用脚本获取多个科技新闻源的最新资讯：

```bash
# 获取所有源的最新新闻（默认 30 条）
python scripts/fetch_tech_news.py --limit 30

# 指定使用特定源
python scripts/fetch_tech_news.py --limit 30 --sources techcrunch theverge 36kr

# 查看所有可用源
python scripts/fetch_tech_news.py --list-sources
```

参数说明：
- `--limit`: 获取新闻总数（默认 30，建议 20-50）
- `--sources`: 指定使用的源（可选: techcrunch, theverge, arstechnica, venturebeat, mitreview, 36kr, tmt, huxiu）
- `--list-sources`: 列出所有可用源
- `--output`: 输出到文件
- `--pretty`: 美化 JSON 输出

脚本输出：JSON 格式的新闻列表，包含标题、链接、来源、时间、摘要等信息。

### 2. 筛选和分类
根据以下维度对新闻进行筛选和分类：
- **技术领域**：AI、云计算、区块链、移动开发、Web 开发等
- **重要性**：根据分数（score）和评论数排序
- **相关性**：过滤与日报主题相关的内容

可参考 [references/news-categories.md](references/news-categories.md) 中的分类标准。

### 3. 翻译和整理
使用智能体的语言能力：
- 翻译新闻标题和摘要为中文
- 提取关键信息（公司、技术、产品等）
- 添加简短评论或观点

### 4. 生成日报
按以下结构生成科技日报：

```
# [日期] 科技日报

## 📈 热门话题
- [标题] (链接)
  简要描述...

## 🤖 人工智能
- ...

## 💻 开发技术
- ...

## 🔧 其他资讯
- ...
```

## 资源索引
- **必要脚本**：[scripts/fetch_tech_news.py](scripts/fetch_tech_news.py)（从多个科技新闻源获取最新资讯）
- **参考文档**：[references/news-categories.md](references/news-categories.md)（新闻分类标准和示例）

## 注意事项
- 所有新闻源均为公开 RSS，无需 API Key 或鉴权
- 支持中英文混合源，智能体需具备翻译和理解能力
- 可根据实际需求调整获取的新闻数量和筛选标准
- 建议每日固定时间生成日报，保持连续性
- 对于重要的新闻，可以附加更多深度分析
- 脚本会自动去重，避免同一新闻在多个源重复

## 使用示例

### 示例 1：生成今日科技日报
```bash
# 步骤 1：获取最新 30 条新闻（使用所有源）
python scripts/fetch_tech_news.py --limit 30 --pretty

# 步骤 2：智能体根据返回的数据，筛选重要新闻、翻译标题、生成日报
```

### 示例 2：只使用英文源获取 AI 相关新闻
```bash
# 只使用英文源
python scripts/fetch_tech_news.py --limit 50 --sources techcrunch venturebeat mitreview

# 智能体筛选与 AI 相关的内容并生成日报
```

### 示例 3：使用中文源获取科技新闻
```bash
# 只使用中文源
python scripts/fetch_tech_news.py --limit 30 --sources 36kr tmt huxiu
```

### 示例 4：查看所有可用源
```bash
# 列出所有可用源
python scripts/fetch_tech_news.py --list-sources
```

### 示例 5：快速浏览热门新闻
```bash
# 获取前 10 条新闻并保存到文件
python scripts/fetch_tech_news.py --limit 10 --output news.json --pretty
```
