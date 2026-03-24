# HeteroCat Skills

[![Skills](https://img.shields.io/badge/Skills-42+-blue)](.claude/skills)
[![License](https://img.shields.io/badge/License-Apache%202.0-green)](LICENSE)

**HeteroCat Skills** 是一个 Claude Code 技能库，收录了一系列开箱即用的 Agent Skills，帮助 AI 智能体在内容创作、AI 绘图、科研检索、金融投资、语音视频处理、工作流辅助等场景下快速扩展能力。

---

## 技能总览

### 🤖 内容创作

| 技能 | 描述 | 核心能力 |
|------|------|----------|
| **m-auto-redbook** | 小红书笔记素材创作 | 智能撰写标题正文、生成封面/正文图片卡片、多主题样式 |
| **o-generate-video** | 豆包视频生成 | 文生视频、图生视频、首尾帧视频、多片段连续生成 |
| **o-minimax** | MiniMax 语音与音乐 | 高品质 TTS 语音合成、音色克隆/设计、AI 音乐生成 |
| **o-suno-music** | Suno AI 音乐生成 | 灵感模式/自定义模式生成音乐 |
| **a-x-api** | X (Twitter) 发布与获取 | 发布推文（支持图文/视频）、获取用户推文、搜索推文 |
| **m-auto-wechat** | 微信公众号发布 | 通过 API 或 Chrome CDP 发布文章到微信公众号 |
| **o-article-illustrator** | 文章智能配图 | 分析文章结构、AI 生成插图、Type × Style 双维度配图策略 |
| **p-PPTmaker** | AI 演示文稿制作 | 内容结构化→设计选型→AI插画/HTML构建→PPTX导出 |
| **o-remotion** | Remotion 视频开发 | React 代码生成视频的最佳实践、组件化视频制作 |

### 🎨 AI 绘图与图像

| 技能 | 描述 | 核心能力 |
|------|------|----------|
| **o-nano-banana2** | AI 图像生成与编辑 | 文生图、图生图、基于 OpenRouter 的 Gemini 图像模型 |

### 💰 金融投资

| 技能 | 描述 | 核心能力 |
|------|------|----------|
| **f-fund-advisor** | 基金投资顾问 | 全平台持仓导入、组合分析、基金诊断、回测、资产配置方案 |
| **f-fund-assistant** | 基金投资助手 | 实时估值查询、持仓管理、收益计算、大盘行情、北向资金 |
| **f-fund-screener** | 基金量化筛选 | 夏普/索提诺/卡玛比率筛选、纯债/固收+/股票基金分类筛选 |
| **f-fundamentals** | 股票基本面分析 | 财务数据获取、Piotroski F-Score 评分、价值股筛选 |
| **f-mx-data** | 妙想金融数据 | 东方财富实时行情、财务数据、关联关系数据查询 |
| **f-mx-search** | 妙想金融搜索 | 金融资讯智能筛选、新闻/公告/研报/政策检索 |
| **f-mx-select-stock** | 妙想智能选股 | 基于指标选股、板块成分股筛选、股票推荐 |
| **f-mx-selfselect** | 妙想自选股管理 | 自选股增删改查、行情监控 |
| **f-mx-stock-simulator** | 股票模拟组合 | 模拟交易、持仓管理、资金查询、历史成交 |

### 🛠️ 开发工具

| 技能 | 描述 | 核心能力 |
|------|------|----------|
| **t-writing-skills** | 技能创建规范 | 基于 TDD 的技能编写方法论、测试验证流程 |
| **a-skill-creator** | 技能创建向导 | 从零开始创建新技能的完整流程、打包脚本、最佳实践 |
| **t-frontend-design** | 前端设计开发 | 创建高品质、非模板化的前端界面 |
| **t-supabase** | Supabase/Postgres 最佳实践 | 查询优化、性能调优、模式设计 |
| **a-find-skills** | 技能发现助手 | 智能匹配用户需求与可用技能、一键安装 |

### 📊 数据与科研

| 技能 | 描述 | 核心能力 |
|------|------|----------|
| **p-arxiv** | arXiv 论文检索 | 关键词/作者/标题搜索、学科分类过滤、元数据获取 |
| **p-tech-news-daily** | 每日科技新闻 | 聚合 TechCrunch/36氪等多源资讯、生成结构化日报 |
| **p-bar-chart-race-generator** | 动态柱状图生成 | CSV 数据转 D3 动画、时序排名可视化、HTML 导出 |
| **p-yt-dlp** | 视频下载 | 基于 yt-dlp 下载 YouTube/B站/抖音等视频、提取音频 |

### 🔧 工作流与团队协作 (Superpowers)

| 技能 | 描述 | 核心能力 |
|------|------|----------|
| **t-using-superpowers** | 技能使用指南 | 如何发现和使用技能、工具调用规范 |
| **t-brainstorming** | 创意构思 | 将想法转化为完整设计方案的对话流程 |
| **t-writing-plans** | 计划编写 | 多步骤任务的实施计划制定 |
| **t-executing-plans** | 计划执行 | 独立会话中执行实施计划 |
| **t-subagent-driven-development** | 子代理驱动开发 | 并行执行独立子任务 |
| **t-test-driven-development** | 测试驱动开发 | RED-GREEN-REFACTOR 开发循环 |
| **t-systematic-debugging** | 系统化调试 | 结构化的问题诊断和修复流程 |
| **t-dispatching-parallel-agents** | 并行代理调度 | 同时处理多个独立任务 |
| **t-using-git-worktrees** | Git 工作树使用 | 创建隔离的工作空间 |
| **t-finishing-a-development-branch** | 完成开发分支 | 决定如何集成已完成的工作 |
| **t-requesting-code-review** | 请求代码审查 | 提交前验证工作质量 |
| **t-receiving-code-review** | 接收代码审查 | 处理审查反馈的最佳实践 |
| **t-verification-before-completion** | 完成前验证 | 提交前运行验证命令 |

### 🌐 浏览器自动化

| 技能 | 描述 | 核心能力 |
|------|------|----------|
| **a-agent-browser** | 浏览器自动化 | 网页导航、表单填写、截图、视频录制 |

### 🎬 音视频处理

| 技能 | 描述 | 核心能力 |
|------|------|----------|
| **o-whisper-subtitle** | 字幕自动生成 | 音频/视频转 SRT 字幕、多格式支持、批量处理 |

---

## 快速开始

### 方式一：自然语言调用（推荐）

Claude 会自动识别你的需求并调用相应技能：

```
"搜索关于大语言模型的最新 arXiv 论文"
"帮我生成一张赛博朋克风格的猫咪图片"
"把这段采访音频转成字幕文件"
"获取马斯克最近的推文"
"帮我写一段治愈系音乐"
"查询贵州茅台最新股价"
"帮我分析我的基金持仓组合"
"筛选夏普比率大于1的纯债基金"
"下载这个 YouTube 视频"
"生成一个女孩在海边漫步的视频"
```

### 方式二：手动执行脚本

进入技能目录，按 SKILL.md 说明运行：

```bash
# 示例：使用 MiniMax 合成语音
python .claude/skills/o-minimax/scripts/text_to_audio.py

# 示例：生成动态柱状图
python .claude/skills/p-bar-chart-race-generator/scripts/generate_race.py

# 示例：使用 nano-banana2 生成图片
python .claude/skills/o-nano-banana2/scripts/generate_image.py "一只可爱的猫咪"

# 示例：下载视频
python .claude/skills/p-yt-dlp/scripts/download.py "https://www.youtube.com/watch?v=xxx"

# 示例：豆包文生视频
python .claude/skills/o-generate-video/scripts/text_to_video.py "海边落日，金色的太阳缓缓沉入海平面"
```

---

## 环境变量配置

所有 API 密钥配置在根目录 `.env` 文件中：

| 技能 | 环境变量 | 说明 |
|------|----------|------|
| o-nano-banana2 | `OPENROUTER_API_KEY` | OpenRouter API 密钥 |
| o-minimax | `MINIMAX_API_KEY` | MiniMax 平台 API 密钥 |
| o-generate-video | `ARK_API_KEY` | 豆包/火山引擎 API 密钥 |
| o-suno-music | `DMX_API_KEY` | Suno API 密钥（通过 dmxapi） |
| o-whisper-subtitle | `OPENAI_API_KEY` | OpenAI API 密钥 |
| a-x-api (获取) | `X_BEARER_TOKEN` | 只读访问 Bearer Token |
| a-x-api (发布) | `X_API_KEY`, `X_API_SECRET`, `X_ACCESS_TOKEN`, `X_ACCESS_TOKEN_SECRET` | OAuth 1.0a 四件套 |
| m-auto-redbook | `XHS_COOKIE`（可选） | 小红书 Cookie，用于自动发布 |
| m-auto-wechat | `WECHAT_APP_ID`, `WECHAT_APP_SECRET` | 微信公众号 AppID/Secret |
| f-mx-data/f-mx-search/f-mx-select-stock | `MX_APIKEY` | 东方财富妙想平台 API Key |
| f-fund-advisor | `QIEMAN_API_KEY` | 且慢 MCP 服务 API Key |
| f-fund-assistant | - | 无需配置 |
| f-fund-screener | - | 无需配置 |
| p-arxiv | - | 无需配置 |
| p-tech-news-daily | - | 无需配置 |

---

## 技能打包与安装

### 打包所有技能

```bash
# 打包为 .skill 格式（Claude Code 原生格式）
python package_skills.py

# 打包为 .zip 格式（通用格式）
python package_zip.py
```

打包后的文件会输出到：
- `.skill` 文件 → `dist/` 目录
- `.zip` 文件 → `zip_dist/` 目录

### 安装技能

在 Claude Code 中执行：

```bash
# 本地安装
/skills install /path/to/skill-name.skill

# 在线安装
/skills install https://example.com/skill-name.skill
```

---

## 技能命名规范

技能按类别使用前缀组织：

| 前缀 | 类别 | 示例 |
|------|------|------|
| `a-` | Agent 工具 | a-agent-browser, a-find-skills, a-skill-creator, a-x-api |
| `f-` | 金融投资 | f-fund-assistant, f-mx-data, f-fundamentals |
| `m-` | 媒体/内容 | m-auto-redbook, m-auto-wechat |
| `o-` | 输出/创作 | o-generate-video, o-nano-banana2, o-minimax |
| `p-` | 生产力 | p-arxiv, p-tech-news-daily, p-PPTmaker, p-yt-dlp |
| `t-` | 团队/工作流 (Superpowers) | t-brainstorming, t-writing-plans, t-systematic-debugging |

---

## 项目结构

```
.claude/skills/
├── a-agent-browser/            # 浏览器自动化
├── a-find-skills/              # 技能发现
├── a-skill-creator/            # 技能创建向导
├── a-x-api/                    # X (Twitter) API
├── f-fund-advisor/             # 基金投资顾问
├── f-fund-assistant/           # 基金投资助手
├── f-fund-screener/            # 基金量化筛选
├── f-fundamentals/             # 股票基本面分析
├── f-mx-data/                  # 妙想金融数据
├── f-mx-search/                # 妙想金融搜索
├── f-mx-select-stock/          # 妙想智能选股
├── f-mx-selfselect/            # 妙想自选股管理
├── f-mx-stock-simulator/       # 股票模拟交易
├── m-auto-redbook/             # 小红书笔记创作
├── m-auto-wechat/              # 微信公众号发布
├── o-article-illustrator/      # 文章智能配图
├── o-generate-video/           # 豆包视频生成
├── o-minimax/                  # MiniMax 语音/音乐
├── o-nano-banana2/             # AI 图像生成与编辑
├── o-remotion/                 # Remotion 视频开发
├── o-suno-music/               # Suno AI 音乐生成
├── o-whisper-subtitle/         # 字幕生成
├── p-arxiv/                    # arXiv 论文检索
├── p-bar-chart-race-generator/ # 动态柱状图
├── p-PPTmaker/                 # PPT 制作
├── p-tech-news-daily/          # 每日科技新闻
├── p-yt-dlp/                   # 视频下载
└── t-*/                        # Superpowers 工作流技能
    ├── t-brainstorming
    ├── t-dispatching-parallel-agents
    ├── t-executing-plans
    ├── t-finishing-a-development-branch
    ├── t-frontend-design
    ├── t-receiving-code-review
    ├── t-requesting-code-review
    ├── t-subagent-driven-development
    ├── t-supabase
    ├── t-systematic-debugging
    ├── t-test-driven-development
    ├── t-using-git-worktrees
    ├── t-using-superpowers
    ├── t-verification-before-completion
    ├── t-writing-plans
    └── t-writing-skills

dist/                           # 打包输出的 .skill 文件
zip_dist/                       # 打包输出的 .zip 文件
package_skills.py               # 打包为 .skill 格式
package_zip.py                  # 打包为 .zip 格式
```

---

## 创建新技能

使用内置向导快速创建：

```
"帮我创建一个新技能"
```

或手动初始化：

```bash
python .claude/skills/a-skill-creator/scripts/init_skill.py my-skill \
  --path ./.claude/skills
```

然后编辑生成的 `SKILL.md` 和脚本文件，完成后打包：

```bash
python .claude/skills/a-skill-creator/scripts/package_skill.py .claude/skills/my-skill
```

---

## 贡献指南

欢迎提交新技能或改进现有技能！

1. Fork 本仓库
2. 创建新技能或修改现有技能
3. 确保包含完整的 `SKILL.md` 文档
4. 提交 Pull Request

---

## 许可证

[Apache License 2.0](LICENSE)

Copyright 2025-2026 HeteroCat

Licensed under the Apache License, Version 2.0.

---

*由 HeteroCat 维护 | 用 ❤️ 和 🤖 构建*
