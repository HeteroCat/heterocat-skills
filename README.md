# HeteroCat Skills

[![Skills](https://img.shields.io/badge/Skills-45+-blue)](.claude/skills)
[![License](https://img.shields.io/badge/License-Apache%202.0-green)](LICENSE)

**HeteroCat Skills** 是一个 Claude Code 技能库，提供开箱即用的 Agent Skills，按功能前缀分类组织，帮助 AI 智能体快速扩展能力。

---

## 技能分类

| 前缀 | 类别 | 说明 |
|------|------|------|
| `a-` | **通用工具** | Agent 基础能力、浏览器自动化、API 接口等 |
| `p-` | **数据调研** | 科研检索、资讯获取、数据分析、 productivity 工具 |
| `m-` | **内容创作** | 媒体内容生成、社媒发布、图文视频创作 |
| `t-` | **代码开发** | 软件开发、前端设计、数据库、工作流 |
| `f-` | **金融投资** | 基金股票、投资组合、金融数据查询 |

---

## 技能总览

### a- 通用工具 (Agent Tools)

| 技能 | 描述 | 核心能力 |
|------|------|----------|
| **a-agent-browser** | 浏览器自动化 | 网页导航、表单填写、截图、视频录制、数据提取 |
| **a-x-api** | X (Twitter) 数据获取 | 获取用户推文、搜索推文、查询用户信息 |
| **a-find-skills** | 技能发现助手 | 智能匹配需求与可用技能、一键安装 |
| **a-skill-creator** | 技能创建向导 | 从零创建技能、打包脚本、最佳实践 |

### p- 数据调研 (Productivity & Research)

| 技能 | 描述 | 核心能力 |
|------|------|----------|
| **p-arxiv** | arXiv 论文检索 | 关键词/作者/标题搜索、学科分类过滤、元数据获取 |
| **p-tech-news-daily** | 每日科技新闻 | 聚合 TechCrunch/The Verge/36氪等资讯、生成结构化日报 |
| **p-bar-chart-race-generator** | 动态柱状图生成 | CSV 数据转 D3 动画、时序排名可视化、HTML 导出 |
| **p-yt-dlp** | 视频下载 | 基于 yt-dlp 下载 YouTube/B站/抖音等视频、提取音频 |
| **p-PPTmaker** | AI 演示文稿制作 | 内容结构化→设计选型→AI插画→PPTX导出 |

### m- 内容创作 (Media & Content)

| 技能 | 描述 | 核心能力 |
|------|------|----------|
| **m-auto-redbook** | 小红书笔记创作 | 智能撰写标题正文、生成封面/正文图片卡片 |
| **m-auto-wechat** | 微信公众号发布 | API/CDP 方式发布图文/文章到微信公众号 |
| **m-auto-x** | X (Twitter) 自动发布 | 自动发推、图文/视频发布、批量上传 |
| **m-article-illustrator** | 文章智能配图 | 分析文章结构、AI 生成插图、Type × Style 策略 |
| **m-generate-video** | 豆包视频生成 | 文生视频、图生视频、首尾帧视频、多片段连续生成 |
| **m-minimax** | MiniMax 语音与音乐 | 高品质 TTS 语音合成、音色克隆/设计、AI 音乐生成 |
| **m-nano-banana2** | AI 图像生成与编辑 | 文生图、图生图、基于 Gemini 图像模型 |
| **m-remotion** | Remotion 视频开发 | React 代码生成视频、组件化视频制作 |
| **m-suno-music** | Suno AI 音乐生成 | 灵感模式/自定义模式生成音乐 |
| **m-whisper-subtitle** | 字幕自动生成 | 音频/视频转 SRT 字幕、多格式支持、批量处理 |

### t- 代码开发 (Team & Development)

| 技能 | 描述 | 核心能力 |
|------|------|----------|
| **t-frontend-design** | 前端设计开发 | 创建高品质、非模板化的前端界面 |
| **t-supabase** | Supabase/Postgres | 查询优化、性能调优、模式设计 |
| **t-writing-skills** | 技能创建规范 | TDD 方法论、测试验证流程 |
| **t-brainstorming** | 创意构思 | 将想法转化为完整设计方案的对话流程 |
| **t-writing-plans** | 计划编写 | 多步骤任务的实施计划制定 |
| **t-executing-plans** | 计划执行 | 独立会话中执行实施计划 |
| **t-test-driven-development** | 测试驱动开发 | RED-GREEN-REFACTOR 开发循环 |
| **t-systematic-debugging** | 系统化调试 | 结构化问题诊断和修复流程 |
| **t-subagent-driven-development** | 子代理驱动开发 | 并行执行独立子任务 |
| **t-dispatching-parallel-agents** | 并行代理调度 | 同时处理多个独立任务 |
| **t-using-git-worktrees** | Git 工作树使用 | 创建隔离的工作空间 |
| **t-finishing-a-development-branch** | 完成开发分支 | 决定如何集成已完成的工作 |
| **t-requesting-code-review** | 请求代码审查 | 提交前验证工作质量 |
| **t-receiving-code-review** | 接收代码审查 | 处理审查反馈的最佳实践 |
| **t-verification-before-completion** | 完成前验证 | 提交前运行验证命令 |
| **t-using-superpowers** | 技能使用指南 | 如何发现和使用技能、工具调用规范 |

### f- 金融投资 (Financial)

| 技能 | 描述 | 核心能力 |
|------|------|----------|
| **f-fund-advisor** | 基金投资顾问 | 全平台持仓导入、组合分析、基金诊断、资产配置方案 |
| **f-fund-assistant** | 基金投资助手 | 实时估值查询、持仓管理、收益计算、大盘行情、北向资金 |
| **f-fund-screener** | 基金量化筛选 | 夏普/索提诺/卡玛比率筛选、纯债/固收+/股票基金分类筛选 |
| **f-fundamentals** | 股票基本面分析 | 财务数据获取、Piotroski F-Score 评分、价值股筛选 |
| **f-mx-data** | 妙想金融数据 | 东方财富实时行情、财务数据、关联关系数据查询 |
| **f-mx-search** | 妙想金融搜索 | 金融资讯智能筛选、新闻/公告/研报/政策检索 |
| **f-mx-select-stock** | 妙想智能选股 | 基于指标选股、板块成分股筛选、股票推荐 |
| **f-mx-selfselect** | 妙想自选股管理 | 自选股增删改查、行情监控 |
| **f-mx-stock-simulator** | 股票模拟组合 | 模拟交易、持仓管理、资金查询、历史成交 |

---

## 快速开始

### 方式一：自然语言调用（推荐）

Claude 会自动识别需求并调用相应技能：

```
"搜索关于大语言模型的最新 arXiv 论文"          # p-arxiv
"获取今天的科技新闻"                          # p-tech-news-daily
"下载这个 YouTube 视频"                       # p-yt-dlp
"生成一张赛博朋克风格的猫咪图片"              # m-nano-banana2
"创建一个海边落日的视频"                      # m-generate-video
"帮我写一段治愈系音乐"                        # m-suno-music
"发布一条推文：今天天气不错"                  # m-auto-x
"查询贵州茅台最新股价"                        # f-mx-data
"分析我的基金持仓组合"                        # f-fund-advisor
"帮我调试这个 Python 脚本"                    # t-systematic-debugging
```

### 方式二：手动执行脚本

进入技能目录，按 SKILL.md 说明运行：

```bash
# p- 数据调研
python .claude/skills/p-arxiv/scripts/search_papers.py "transformer"
python .claude/skills/p-tech-news-daily/scripts/fetch_tech_news.py --limit 20
python .claude/skills/p-yt-dlp/scripts/download.py "https://youtube.com/watch?v=xxx"

# m- 内容创作
python .claude/skills/m-nano-banana2/scripts/generate_image.py "一只可爱的猫咪"
python .claude/skills/m-generate-video/scripts/text_to_video.py "海边落日"
python .claude/skills/m-auto-x/scripts/post.py "Hello, X!" -m ./photo.jpg
python .claude/skills/m-whisper-subtitle/scripts/generate_srt.py ./audio.mp3

# f- 金融投资
python .claude/skills/f-mx-data/scripts/get_stock_quote.py 600519
python .claude/skills/f-fund-assistant/scripts/get_fund_nav.py 110022

# t- 代码开发
python .claude/skills/t-frontend-design/scripts/create_component.py
```

---

## 环境变量配置

在根目录 `.env` 文件中配置 API 密钥：

| 技能 | 环境变量 | 说明 |
|------|----------|------|
| **m-nano-banana2** | `OPENROUTER_API_KEY` | OpenRouter API 密钥 |
| **m-minimax** | `MINIMAX_API_KEY` | MiniMax API 密钥 |
| **m-generate-video** | `ARK_API_KEY` | 豆包/火山引擎 API 密钥 |
| **m-suno-music** | `DMX_API_KEY` | Suno API 密钥 |
| **m-whisper-subtitle** | `OPENAI_API_KEY` | OpenAI API 密钥 |
| **m-auto-redbook** | `XHS_COOKIE` | 小红书 Cookie（可选） |
| **m-auto-wechat** | `WECHAT_APP_ID`, `WECHAT_APP_SECRET` | 微信公众号凭证 |
| **m-auto-x** / **a-x-api** | `X_API_KEY`, `X_API_SECRET`, `X_ACCESS_TOKEN`, `X_ACCESS_TOKEN_SECRET` | X OAuth 1.0a |
| **f-mx-*** | `MX_APIKEY` | 东方财富妙想 API Key |
| **f-fund-advisor** | `QIEMAN_API_KEY` | 且慢 MCP API Key |

---

## 技能打包与安装

### 打包所有技能

```bash
# 打包为 .skill 格式（Claude Code 原生格式）
python package_skills.py

# 打包为 .zip 格式（通用格式）
python package_zip.py
```

输出目录：
- `.skill` 文件 → `dist/`
- `.zip` 文件 → `zip_dist/`

### 安装技能

```bash
# 本地安装
/skills install /path/to/skill-name.skill

# 在线安装
/skills install https://example.com/skill-name.skill
```

---

## 创建新技能

使用内置向导：

```
"帮我创建一个新技能"
```

或手动初始化：

```bash
python .claude/skills/a-skill-creator/scripts/init_skill.py my-skill \
  --path ./.claude/skills
```

编辑 `SKILL.md` 和脚本后打包：

```bash
python .claude/skills/a-skill-creator/scripts/package_skill.py .claude/skills/my-skill
```

---

## 许可证

[Apache License 2.0](LICENSE)

Copyright 2025-2026 HeteroCat

---

*由 HeteroCat 维护 | 用 ❤️ 和 🤖 构建*
