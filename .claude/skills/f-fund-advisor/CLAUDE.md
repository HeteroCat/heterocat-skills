# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

fund-tools is a CLI-based fund portfolio management system (基金持仓管理系统) for managing fund holdings, importing CSV data, syncing with external MCP services, and displaying statistics.

## Development Commands

```bash
# Run CLI (via bash script)
bash scripts/fund-cli.sh --help
bash scripts/fund-cli.sh <command> [options]

# Common commands
bash scripts/fund-cli.sh init                    # Initialize environment (mcporter + qieman-mcp)
bash scripts/fund-cli.sh import-csv tools/data/sample.csv  # Import holdings from CSV
bash scripts/fund-cli.sh sync --all              # Sync fund data from MCP service
bash scripts/fund-cli.sh group -c fund_manager   # Group by fund manager
bash scripts/fund-cli.sh query -c fund_name -v "货币"  # Query funds by name
bash scripts/fund-cli.sh detail 004137           # View specific fund detail

# Run unit tests
cd tools && ./venv/bin/python -m pytest tests/ -v
```

## Development Workflow

### Collaborative Development Process

When completing a feature or fix, follow this workflow:

1. **Check current status**: `git status`
2. **Stage changes**: `git add <files>` or `git add .`
3. **Run unit tests**: `cd tools && ./venv/bin/python -m pytest tests/ -v`
4. **Commit with conventional message**: `git commit -m "type: description"`
5. **Push to remote**: `git push`

Claude should automatically commit and push after completing tasks unless the user specifies otherwise.

### Running Tests

```bash
# Run all tests
cd tools && ./venv/bin/python -m pytest tests/ -v

# Run specific test class
cd tools && ./venv/bin/python -m pytest tests/test_fund_tools.py::TestDatabase -v

# Run with coverage
cd tools && ./venv/bin/python -m pytest tests/ -v --cov=src
```

**Important**: All tests must pass before committing changes.

### Git Commands Reference

```bash
# Check status
git status

# Stage specific files
git add <file1> <file2>

# Stage all changes
git add .

# Commit with message
git commit -m "type: description"

# Push to remote
git push

# Pull latest changes
git pull
```

### Commit Message Convention

Follow conventional commits format:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `refactor:` - Code refactoring
- `test:` - Adding tests
- `chore:` - Maintenance tasks

Example:
```
feat: 添加投资类型分布统计功能
fix: 修复CSV导入列名换行符问题
docs: 更新README安装说明
```

### Code Style

- Use Python 3.10+ features
- Follow PEP 8 naming conventions
- Use dataclasses for data models
- Use Click for CLI commands
- Use Rich for terminal output

## Architecture

```
fund-tools/
├── SKILL.md              # AgentSkills skill 定义
├── scripts/              # Skill 调用脚本
│   └── fund-cli.sh      # CLI 包装脚本 (bash)
├── references/           # 参考文档
├── assets/               # 静态资源
└── tools/                # Python 包 (可安装)
    ├── pyproject.toml   # 包配置
    ├── requirements.txt # 依赖列表
    ├── venv/            # 虚拟环境
    ├── data/            # 数据文件
    └── src/             # 源代码
        ├── cli.py       # CLI 入口 (Click-based)
        ├── models.py    # Data models
        ├── database.py  # SQLite operations
        ├── csv_importer.py   # CSV parsing
        ├── mcp_service.py    # MCP integration
        ├── statistics.py     # Rich-based output
        └── env_checker.py    # Environment validation
```

## Key Design Decisions

- **SQLite database** with three tables: `fund_holdings` (user holdings), `fund_info` (fund metadata), `fund_holdings_detail` (stock/bond holdings)
- **Composite primary key** for holdings: `(fund_account, trade_account, fund_code)`
- **Upsert pattern** throughout database operations for idempotent imports
- **Batch processing** in MCP service (max 20 funds per API call)
- **Multiple encoding support** for CSV import (utf-8, utf-8-sig, gbk, gb18030)

## External Dependencies

- **mcporter**: External CLI tool required for MCP service integration
- **qieman-mcp**: MCP server for fund data (configured in `~/.mcporter/mcporter.json`)

## CSV Import Format

Required columns (Chinese names):
- 基金代码, 基金名称, 基金账户, 交易账户, 持有份额, 份额日期, 基金净值, 净值日期, 资产情况（结算币种）

## Fund Types

Defined in `FundType` enum for future expansion: `PUBLIC_FUND`, `ETF`, `LOF`, `CLOSED_END`