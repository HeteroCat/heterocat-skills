# HeteroCat Skills

[![Skills](https://img.shields.io/badge/Skills-12+-blue)](.claude/skills)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

**HeteroCat Skills** 是一个 Claude Code 技能库，收录了一系列开箱即用的 Agent Skills，帮助 AI 智能体在内容创作、科研检索、语音视频处理、数据可视化等场景下快速扩展能力。

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
"帮我写一段治愈系音乐"
"把这段采访音频转成字幕文件"
"获取马斯克最近的推文"
```

### 方式二：手动执行脚本

进入技能目录，按 SKILL.md 说明运行：

```bash
# 示例：使用 MiniMax 合成语音
python .claude/skills/minimax/scripts/text_to_audio.py

# 示例：生成动态柱状图
python .claude/skills/bar-chart-race-generator/scripts/generate_race.py
```

---

## 环境变量配置

| 技能 | 环境变量 | 说明 |
|------|----------|------|
| minimax | `MINIMAX_API_KEY` | MiniMax 平台 API 密钥 |
| generate-video | `ARK_API_KEY` | 豆包/火山引擎 API 密钥 |
| whisper-subtitle | `OPENAI_API_KEY` | OpenAI API 密钥 |
| x-api (获取) | `X_BEARER_TOKEN` | 只读访问 Bearer Token |
| x-api (发布) | `X_API_KEY`, `X_API_SECRET`, `X_ACCESS_TOKEN`, `X_ACCESS_TOKEN_SECRET` | OAuth 1.0a 四件套 |
| auto-redbook-skills | `XHS_COOKIE`（可选） | 小红书 Cookie，用于自动发布 |
| arxiv | - | 无需配置 |
| tech-news-daily | - | 无需配置 |

---

## 技能打包与安装

### 打包所有技能

```bash
python package_skills.py
```

打包后的 `.skill` 文件会输出到 `dist/` 目录。

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
├── generate-video/             # 豆包视频生成
├── mcp-builder/                # MCP 服务器开发
├── minimax/                    # MiniMax 语音/音乐
├── remotion-best-practices/    # Remotion 视频开发
├── skill-creator/              # 技能创建指南
├── tech-news-daily/            # 每日科技新闻
├── whisper-subtitle/           # 字幕生成
└── x-api/                      # X (Twitter) 发布与获取

dist/                           # 打包输出的 .skill 文件
package_skills.py               # 技能打包脚本
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

---

## 贡献指南

欢迎提交新技能或改进现有技能！

1. Fork 本仓库
2. 创建新技能或修改现有技能
3. 确保包含完整的 `SKILL.md` 文档
4. 提交 Pull Request

---

## 许可证

[MIT](LICENSE)

---

*由 [HeteroCat](https://github.com/yourusername) 维护 | 用 ❤️ 和 🤖 构建*
