# HeteroCat Skills

[![Skills](https://img.shields.io/badge/Skills-10+-blue)](.claude/skills)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

HeteroCat Skills 是一个 Claude 技能库，收集了一系列可复用的 Agent Skills，用于扩展 AI 智能体在内容创作、科研检索、语音处理、数据可视化等场景下的能力。

---

## 技能列表

### 内容创作

| 技能 | 描述 | 核心功能 |
|------|------|----------|
| **auto-redbook-skills** | 小红书笔记素材创作 | 生成封面/正文卡片、多主题样式、自动发布支持 |
| **generate-video** | 豆包视频生成 | 文生视频、图生视频、首尾帧视频、连续视频拼接 |
| **minimax** | MiniMax 语音与音乐 | 语音合成（TTS）、音色管理（复刻/设计）、音乐生成 |

### 开发工具

| 技能 | 描述 | 核心功能 |
|------|------|----------|
| **skill-creator** | 技能创建指南 | 创建新技能的完整流程、打包脚本、最佳实践 |
| **mcp-builder** | MCP 服务器开发 | 构建 Model Context Protocol 服务器的完整指南 |
| **find-skills** | 技能发现助手 | 帮助用户发现可用技能、安装技能 |

### 数据与科研

| 技能 | 描述 | 核心功能 |
|------|------|----------|
| **arxiv** | arXiv 论文检索 | 搜索论文、按学科过滤、获取元数据 |
| **tech-news-daily** | 每日科技新闻 | 聚合多源科技新闻、生成结构化日报 |
| **whisper-subtitle** | 字幕生成 | 音频/视频转 SRT 字幕、支持多格式 |
| **bar-chart-race-generator** | 动态柱状图 | CSV 转 D3 动画图表、时序排名可视化 |

---

## 快速开始

### 方式一：直接使用技能（推荐）

Claude 会自动识别并使用相关技能。只需描述你的需求：

```
"帮我搜索关于深度学习的 arXiv 论文"
"生成一段关于春天的音乐"
"把这段音频转成字幕"
```

### 方式二：手动运行脚本

进入具体技能目录，查看 SKILL.md 并按说明执行：

```bash
# 示例：使用 MiniMax 语音合成
python .claude/skills/minimax/scripts/text_to_audio.py

# 示例：生成 Bar Chart Race
python .claude/skills/bar-chart-race-generator/scripts/generate_race.py
```

### 环境变量配置

| 技能 | 所需环境变量 |
|------|-------------|
| arxiv | 无需配置 |
| minimax | `MINIMAX_API_KEY` |
| generate-video | `ARK_API_KEY` |
| whisper-subtitle | `OPENAI_API_KEY` |
| tech-news-daily | 无需配置 |
| auto-redbook-skills | `XHS_COOKIE`（可选，用于发布） |

---

## 技能打包与分发

### 打包所有技能

```bash
python package_skills.py
```

打包后的 `.skill` 文件会输出到 `dist/` 目录。

### 安装技能

在 Claude Code 中：

```bash
/skills install /path/to/skill-name.skill
```

或使用在线链接：

```bash
/skills install https://example.com/skill-name.skill
```

---

## 项目结构

```
.claude/skills/
├── arxiv/                  # arXiv 论文检索
├── auto-redbook-skills/    # 小红书笔记创作
├── bar-chart-race-generator/  # 动态柱状图
├── find-skills/            # 技能发现
├── generate-video/         # 豆包视频生成
├── mcp-builder/            # MCP 服务器开发
├── minimax/                # MiniMax 语音/音乐
├── skill-creator/          # 技能创建指南
├── tech-news-daily/        # 每日科技新闻
└── whisper-subtitle/       # 字幕生成

dist/                       # 打包输出的 .skill 文件
package_skills.py           # 技能打包脚本
```

---

## 创建新技能

使用内置的 `skill-creator` 技能：

```
"帮我创建一个新技能"
```

或手动运行初始化脚本：

```bash
python .claude/skills/skill-creator/scripts/init_skill.py my-skill --path ./.claude/skills
```

---

## 贡献指南

欢迎贡献新技能或改进现有技能！

1. Fork 本仓库
2. 创建新技能或修改现有技能
3. 确保 SKILL.md 完整且清晰
4. 提交 Pull Request

---

## 许可证

[MIT](LICENSE)

---

*由 HeteroCat (Jasonhuang) 维护*
