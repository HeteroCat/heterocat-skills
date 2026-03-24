# HeteroCat Skills

[![Skills](https://img.shields.io/badge/Skills-27+-blue)](.claude/skills)
[![License](https://img.shields.io/badge/License-Apache%202.0-green)](LICENSE)

**HeteroCat Skills** 是一个 Claude Code 技能库，收录了一系列开箱即用的 Agent Skills，帮助 AI 智能体在内容创作、AI 绘图、科研检索、语音视频处理、数据可视化等场景下快速扩展能力。

---

## 技能总览

### 内容创作

| 技能 | 描述 | 核心能力 |
|------|------|----------|
| **auto-redbook-skills** | 小红书笔记素材创作 | 智能撰写标题正文、生成封面/正文图片卡片、多主题样式 |
| **generate-video** | 豆包视频生成 | 文生视频、图生视频、首尾帧视频、多片段连续生成 |
| **minimax** | MiniMax 语音与音乐 | 高品质 TTS 语音合成、音色克隆/设计、AI 音乐生成 |
| **remotion-best-practices** | Remotion 视频开发 | React 代码生成视频的最佳实践、组件化视频制作 |
| **x-api** | X (Twitter) 发布与获取 | 发布推文（支持图文/视频）、获取用户推文、搜索推文、用户信息查询、媒体上传 |

### AI 绘图与图像

| 技能 | 描述 | 核心能力 |
|------|------|----------|
| **nano-banana2** | AI 图像生成与编辑 | 文生图、图生图、基于 OpenRouter 的 Gemini 图像模型、提示词优化指南 |
| **article-illustrator** | 文章智能配图 | 分析文章结构、AI 生成插图、Type × Style 双维度配图策略 |

### 金融投资

| 技能 | 描述 | 核心能力 |
|------|------|----------|
| **fund-advisor** | 基金投资顾问 | 全平台持仓导入、组合分析、基金诊断、回测、资产配置方案 |
| **fund-assistant** | 基金投资助手 | 实时估值查询、持仓管理、收益计算、大盘行情、北向资金 |
| **fund-screener** | 基金量化筛选 | 夏普/索提诺/卡玛比率筛选、纯债/固收+/股票基金分类筛选 |
| **fundamentals** | 股票基本面分析 | 财务数据获取、Piotroski F-Score 评分、价值股筛选 |
| **mx-data** | 妙想金融数据 | 东方财富实时行情、财务数据、关联关系数据查询 |
| **mx-search** | 妙想金融搜索 | 金融资讯智能筛选、新闻/公告/研报/政策检索 |
| **mx-select-stock** | 妙想智能选股 | 基于指标选股、板块成分股筛选、股票推荐 |
| **mx-selfselect** | 妙想自选股管理 | 自选股增删改查、行情监控 |
| **mx-stock-simulator** | 股票模拟组合 | 模拟交易、持仓管理、资金查询、历史成交 |

### 开发工具

| 技能 | 描述 | 核心能力 |
|------|------|----------|
| **skill-creator** | 技能创建向导 | 从零开始创建新技能的完整流程、打包脚本、最佳实践 |
| **mcp-builder** | MCP 服务器开发 | 构建 Model Context Protocol 服务器的完整指南 |
| **find-skills** | 技能发现助手 | 智能匹配用户需求与可用技能、一键安装 |

### 数据与科研

| 技能 | 描述 | 核心能力 |
|------|------|----------|
| **arxiv** | arXiv 论文检索 | 关键词/作者/标题搜索、学科分类过滤、元数据获取 |
| **tech-news-daily** | 每日科技新闻 | 聚合 TechCrunch/36氪等多源资讯、生成结构化日报 |
| **bar-chart-race-generator** | 动态柱状图生成 | CSV 数据转 D3 动画、时序排名可视化、HTML 导出 |

### 音视频处理

| 技能 | 描述 | 核心能力 |
|------|------|----------|
| **whisper-subtitle** | 字幕自动生成 | 音频/视频转 SRT 字幕、多格式支持、批量处理 |

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
```

### 方式二：手动执行脚本

进入技能目录，按 SKILL.md 说明运行：

```bash
# 示例：使用 MiniMax 合成语音
python .claude/skills/minimax/scripts/text_to_audio.py

# 示例：生成动态柱状图
python .claude/skills/bar-chart-race-generator/scripts/generate_race.py

# 示例：使用 nano-banana2 生成图片
python .claude/skills/nano-banana2/scripts/generate_image.py "一只可爱的猫咪"

# 示例：基于图片进行编辑（图生图）
python .claude/skills/nano-banana2/scripts/generate_image.py --image ./input.png "改变风格为油画"
```

---

## 环境变量配置

| 技能 | 环境变量 | 说明 |
|------|----------|------|
| nano-banana2 | `OPENROUTER_API_KEY` | OpenRouter API 密钥（用于 Gemini 图像生成） |
| minimax | `MINIMAX_API_KEY` | MiniMax 平台 API 密钥 |
| generate-video | `ARK_API_KEY` | 豆包/火山引擎 API 密钥 |
| whisper-subtitle | `OPENAI_API_KEY` | OpenAI API 密钥 |
| x-api (获取) | `X_BEARER_TOKEN` | 只读访问 Bearer Token |
| x-api (发布) | `X_API_KEY`, `X_API_SECRET`, `X_ACCESS_TOKEN`, `X_ACCESS_TOKEN_SECRET` | OAuth 1.0a 四件套 |
| auto-redbook-skills | `XHS_COOKIE`（可选） | 小红书 Cookie，用于自动发布 |
| **mx-data/mx-search/mx-select-stock** | `MX_APIKEY` | 东方财富妙想平台 API Key |
| **fund-advisor** | `QIEMAN_API_KEY` | 且慢 MCP 服务 API Key |
| fund-assistant | - | 无需配置 |
| fund-screener | - | 无需配置 |
| arxiv | - | 无需配置 |
| tech-news-daily | - | 无需配置 |

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

## 项目结构

```
.claude/skills/
├── arxiv/                      # arXiv 论文检索
├── auto-redbook-skills/        # 小红书笔记创作
├── bar-chart-race-generator/   # 动态柱状图
├── find-skills/                # 技能发现
├── fund-advisor/               # 基金投资顾问
├── fund-assistant/             # 基金投资助手
├── fund-screener/              # 基金量化筛选
├── fundamentals/               # 股票基本面分析
├── generate-video/             # 豆包视频生成
├── mcp-builder/                # MCP 服务器开发
├── minimax/                    # MiniMax 语音/音乐
├── mx-skills/                  # 东方财富妙想系列
│   ├── mx-data/                # 金融数据查询
│   ├── mx-search/              # 金融资讯搜索
│   ├── mx-select-stock/        # 智能选股
│   ├── mx-selfselect/          # 自选股管理
│   └── mx-stock-simulator/     # 股票模拟交易
├── nano-banana2/               # AI 图像生成与编辑
├── o-article-illustrator/      # 文章智能配图
├── remotion-best-practices/    # Remotion 视频开发
├── skill-creator/              # 技能创建指南
├── tech-news-daily/            # 每日科技新闻
├── whisper-subtitle/           # 字幕生成
└── x-api/                      # X (Twitter) 发布与获取

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
python .claude/skills/skill-creator/scripts/init_skill.py my-skill \
  --path ./.claude/skills
```

然后编辑生成的 `SKILL.md` 和脚本文件，完成后打包：

```bash
python .claude/skills/skill-creator/scripts/package_skill.py .claude/skills/my-skill
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

Copyright 2024 HeteroCat

Licensed under the Apache License, Version 2.0.

---

*由 HeteroCat 维护 | 用 ❤️ 和 🤖 构建*
