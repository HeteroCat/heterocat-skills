# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is **HeteroCat Skills** - a Claude Code skills library containing agent skills for content creation, AI image generation, financial analysis, research, and more. Skills are located in `.claude/skills/`.

## Skill Naming Conventions

Skills are organized with category prefixes:

| Prefix | Category | Examples |
|--------|----------|----------|
| `a-` | Agent tools | a-agent-browser, a-find-skills, a-skill-creator |
| `f-` | Financial | f-fund-assistant, f-mx-data, f-fundamentals |
| `m-` | Media/Content | m-auto-redbook, m-auto-wechat |
| `o-` | Output/Creation | o-generate-video, o-nano-banana2, o-minimax |
| `p-` | Productivity | p-arxiv, p-tech-news-daily, p-PPTmaker |
| `t-` | Team/Workflow | t-brainstorming, t-writing-plans, t-systematic-debugging |

## Common Commands

### Package All Skills

```bash
# Package as .skill files (Claude Code native format)
python package_skills.py

# Package as .zip files (universal format)
python package_zip.py
```

Output directories:
- `.skill` files → `dist/`
- `.zip` files → `zip_dist/`

### Create a New Skill

```bash
# Initialize new skill structure
python .claude/skills/a-skill-creator/scripts/init_skill.py my-skill --path ./.claude/skills

# Package a single skill
python .claude/skills/a-skill-creator/scripts/package_skill.py .claude/skills/my-skill
```

### Skill Development

```bash
# Validate skill structure
python .claude/skills/a-skill-creator/scripts/quick_validate.py .claude/skills/my-skill

# Run skill evaluation (creates test scenarios)
python .claude/skills/a-skill-creator/scripts/run_eval.py .claude/skills/my-skill
```

## Skill Structure

Each skill directory follows this structure:

```
.claude/skills/{skill-name}/
├── SKILL.md                    # Required: skill definition with frontmatter
├── scripts/                    # Optional: executable scripts
│   └── *.py, *.js, *.sh
├── references/                 # Optional: documentation, schemas
│   └── *.md
├── assets/                     # Optional: images, templates
│   └── *
└── agents/                     # Optional: subagent definitions
    └── *.md
```

The `SKILL.md` file must include YAML frontmatter:

```yaml
---
name: skill-name
description: "Description of when to use this skill"
---
```

## Environment Variables

All API keys and credentials are stored in `.env` at the repository root. Key variables include:

| Variable | Purpose |
|----------|---------|
| `OPENROUTER_API_KEY` | AI image generation (nano-banana2) |
| `MINIMAX_API_KEY` | Voice synthesis & music generation |
| `ARK_API_KEY` | Doubao video generation |
| `X_BEARER_TOKEN` | X/Twitter read access |
| `X_API_KEY`, `X_API_SECRET`, `X_ACCESS_TOKEN`, `X_ACCESS_TOKEN_SECRET` | X/Twitter OAuth 1.0a |
| `XHS_COOKIE` | Xiaohongshu auto-posting |
| `MX_APIKEY` | Dongfang Wealth financial data |
| `DMX_API_KEY` | Suno music generation |
| `WECHAT_APP_ID`, `WECHAT_APP_SECRET` | WeChat Official Account posting |

## Key Files

| File | Purpose |
|------|---------|
| `.env` | Environment variables (API keys) |
| `skills-lock.json` | Tracks external skills with git hashes |
| `.claude/settings.local.json` | Claude Code local settings |
| `package_skills.py` | Build script for .skill format |
| `package_zip.py` | Build script for .zip format |

## Installing Skills

Skills can be installed in Claude Code via:

```bash
/skills install /path/to/skill-name.skill
```

## External Skills

Some skills are sourced from external GitHub repos and tracked in `skills-lock.json`:
- fund-advisor → realqiyan/fund-advisor
- fund-assistant → xer97/fund-assistant
- fund-screener → sososun/mutual-fund-skills
- fundamentals → staskh/trading_skills
- agent-browser → vercel-labs/agent-browser

When updating external skills, verify the source repository for changes.

## Language

默认使用中文回复用户。
