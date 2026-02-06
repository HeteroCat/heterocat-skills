# HeteroCat 技能库

欢迎来到 HeteroCat 技能库（HeteroCat Skills）！

本仓库收集了一组可复用的 Agent Skills（技能说明 + 示例脚本），用于扩展 AI 智能体在科研检索、资讯聚合、语音音频处理等场景下的执行能力。

## 📂 可用技能

目前提供以下技能：

### 1. [arXiv API 技能](.claude/skills/arxiv/SKILL.md)
**描述：** 从 arXiv 开放仓库搜索并检索学术论文。
- **主要功能：**
  - 按关键词、作者或论文 ID 搜索。
  - 按学科分类（如计算机科学、物理学）过滤。
  - 检索论文元数据（摘要、作者、日期）。

### 2. [每日科技新闻](.claude/skills/tech-news-daily/SKILL.md)
**描述：** 自动从多个来源获取最新的科技新闻并生成结构化的每日报告。
- **主要功能：**
  - 聚合来自 TechCrunch、The Verge、36氪等的新闻。
  - 按主题（AI、云计算、移动开发等）筛选和分类新闻。
  - 生成摘要并翻译内容以生成每日简报。

### 3. [MiniMax 工具集](.claude/skills/minimax/SKILL.md)
**描述：** MiniMax 语音合成与音乐生成 API 的 Python 客户端工具集。
- **主要功能：**
  - **语音合成**：支持同步（短文本）和异步（长文本）模式，提供高清音质。
  - **音色管理**：支持音色查询、复刻和设计，满足个性化需求。
  - **音乐生成**：根据歌词和风格描述生成原创音乐。

### 4. [Whisper 字幕生成](.claude/skills/whisper-subtitle/SKILL.md)
**描述：** 基于 OpenAI Whisper API，将音频/视频中的语音转写为 SRT 字幕文件。
- **主要功能：**
  - 支持 `mp3/mp4/m4a/wav/webm` 等常见格式输入。
  - 支持命令行调用与 Python 模块调用。
  - 自动生成标准 SRT 时间轴字幕。

### 5. [Bar Chart Race 生成器](.claude/skills/bar-chart-race-generator/SKILL.md)
**描述：** 将 CSV 时序排名数据转换为 D3 动态柱状图竞赛（Bar Chart Race）HTML 可视化。
- **主要功能：**
  - 自动校验 CSV 字段（如 `date/name/category/value`）。
  - 生成可交互动画图表（重播、速度切换、平滑数值过渡）。
  - 适用于历史趋势、排名变化、竞争格局演变展示。

### 6. [Doubao 视频生成](.claude/skills/generate-video/SKILL.md)
**描述：** 基于豆包 Seedance API 进行文生视频、图生视频、首尾帧视频和连续视频生成。
- **主要功能：**
  - 文生视频（text-to-video）。
  - 图生视频（image-to-video，多参考图）。
  - 首尾帧视频与多段连续视频拼接。
  - 支持时长、分辨率、比例、音频等参数控制。

### 7. [Auto-Redbook Skills](.claude/skills/auto-redbook-skills/SKILL.md)
**描述：** 自动生成小红书封面与图文卡片，并支持可选自动发布流程。
- **主要功能：**
  - 根据 Markdown 内容渲染封面与多张正文卡片。
  - 支持多主题样式和多种分页模式（separator / auto-fit / auto-split / dynamic）。
  - 提供发布脚本，可配合 Cookie 进行自动发布。

## 🚀 快速开始

### 1) 浏览技能文档
每个技能位于 `.claude/skills/<skill-name>/` 目录下，并附带 `SKILL.md`：

- `.claude/skills/arxiv/SKILL.md`
- `.claude/skills/tech-news-daily/SKILL.md`
- `.claude/skills/minimax/SKILL.md`
- `.claude/skills/whisper-subtitle/SKILL.md`
- `.claude/skills/bar-chart-race-generator/SKILL.md`
- `.claude/skills/generate-video/SKILL.md`
- `.claude/skills/auto-redbook-skills/SKILL.md`

### 2) 按技能执行对应脚本
常用脚本示例：

- 科技新闻聚合：`.claude/skills/tech-news-daily/scripts/fetch_tech_news.py`
- MiniMax 语音合成：`.claude/skills/minimax/scripts/text_to_audio.py`
- Whisper 字幕生成：`.claude/skills/whisper-subtitle/scripts/whisper_subtitle.py`
- Bar Chart Race 生成：`.claude/skills/bar-chart-race-generator/scripts/generate_race.py`
- Doubao 文生视频：`.claude/skills/generate-video/scripts/text_to_video.py`
- 小红书卡片渲染：`.claude/skills/auto-redbook-skills/scripts/render_xhs.py`

### 3) 配置必要环境变量（按需）
- OpenAI 相关技能：`OPENAI_API_KEY`
- MiniMax 相关技能：`MINIMAX_API_KEY`（部分脚本还可使用 `MINIMAX_GROUP_ID`）
- Doubao 视频生成：`ARK_API_KEY`
- 小红书发布（可选）：`XHS_COOKIE`

## 📁 仓库结构

```text
.claude/skills/
├── arxiv/
├── tech-news-daily/
├── minimax/
├── whisper-subtitle/
├── bar-chart-race-generator/
├── generate-video/
└── auto-redbook-skills/
```

## 🤝 贡献

欢迎贡献！如果你有新的技能想法或想要改进现有的技能，请随时提交 Pull Request。

---
*由 HeteroCat(Jasonhuang) 提供支持*
