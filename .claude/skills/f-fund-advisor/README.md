# Fund Advisor - 基金投资顾问工具

提供个人基金持仓统一管理功能，支持所有平台持仓导入、分析、查询；提供基金基础数据、持仓明细、持仓穿透等基于数据查询；提供投资组合分析、投资规划、组合回测服务；提供财经资讯、热点新闻、财经新闻查询；提供基金搜索、公告查询等服务。

## 核心能力

1. 管理用户的基金持仓数据，用户可以通过基金E账户导出所有持仓数据（包括：支付宝、京东金融、腾讯理财、雪球基金、且慢等所有平台的场外基金持仓数据），导入数据时会创建数据库文件存储用户导入的数据，后续可以配合qieman-mcp的数据查询能力进行持仓数据的综合分析。数据目录可通过 `FUND_ADVISOR_DATA_PATH` 环境变量配置，默认为 `$HOME/.fund-advisor`，数据库文件名为 `fund_portfolio_v1.db`。

2. 本技能整合qieman-mcp的五大核心能力模块：

| 模块 | 能力说明 |
| ------ | ---------- |
| 金融数据 | 基金基础信息、净值历史、持仓明细、风险指标、业绩表现等 |
| 投研服务 | 基金筛选、基金诊断、回测分析、相关性分析、风险评估等 |
| 投顾服务 | 资产配置方案、投资规划、风险匹配、财务分析等 |
| 投顾内容 | 实时资讯解读、热点话题、基金经理观点、财经新闻等 |
| 通用服务 | 交易日查询、图表渲染、PDF生成、时间查询等 |

完整工具清单见 [references/mcp-tools-full.md](references/mcp-tools-full.md)

## 项目架构

```
fund-advisor/
├── SKILL.md              # AgentSkills 技能定义
├── CLAUDE.md             # Claude Code 开发指南
├── README.md             # 项目说明
├── scripts/
│   └── fund-cli.sh       # CLI 包装脚本（自动管理 venv）
├── references/           # 参考文档
│   ├── mcp-tools-full.md # MCP 工具完整清单
│   ├── mcp-tools.md      # MCP 工具基础文档
│   ├── csv-format.md     # CSV 导入格式规范
│   └── REFERENCE.md      # 项目架构说明
├── assets/               # 静态资源
└── tools/                # Python 包
    ├── pyproject.toml    # 包配置
    ├── requirements.txt  # 依赖列表
    ├── venv/             # 虚拟环境（自动创建）
    ├── data/             # 数据文件
    └── src/              # 源代码
        ├── cli.py        # CLI 入口（Click）
        ├── models.py     # 数据模型（dataclass）
        ├── database.py   # SQLite 数据库操作
        ├── csv_importer.py    # CSV 导入解析
        ├── mcp_service.py     # MCP 服务集成
        ├── statistics.py      # Rich 统计视图
        ├── env_checker.py     # 环境检查
        └── config.py          # 配置管理
```

## Tools 模块详解

本项目的核心功能实现在 `tools/src/` 目录下，采用模块化设计，各模块职责清晰。

### cli.py - CLI 入口和命令定义

命令行接口模块，基于 [Click](https://click.palletsprojects.com/) 框架实现，提供完整的命令行交互体验。

**核心组件：**

- `cli` - 主命令组，管理全局选项（如数据库路径）
- `init` - 环境初始化命令，检查并配置 mcporter 和 qieman-mcp
- `import-csv` - CSV 文件导入命令，支持持仓数据批量导入
- `reset` - 清空持仓记录命令（带确认提示）
- `detail` - 基金详情查看命令，展示基金基础信息和持仓明细
- `group` - 分组统计命令，支持按多种维度分组汇总
- `query` - 条件查询命令，支持模糊匹配筛选持仓
- `sync` - 数据同步命令，从 MCP 服务获取基金数据

**设计特点：**

- 使用 `click.pass_context` 实现命令间上下文共享
- 通过 Rich Console 提供彩色终端输出
- 支持自定义数据库路径（`--db` 选项）

### models.py - 数据模型定义

定义系统的核心数据结构，使用 Python `dataclass` 实现类型安全的数据模型。

**枚举类型：**

| 枚举 | 说明 | 取值 |
|------|------|------|
| `FundType` | 基金类型 | PUBLIC_FUND, ETF, LOF, CLOSED_END |
| `GroupColumn` | 分组统计列 | fund_code, fund_name, fund_manager, invest_type 等 |

**数据类：**

| 类名 | 说明 | 主要字段 |
|------|------|----------|
| `FundHolding` | 用户持仓记录 | fund_code, fund_name, holding_shares, nav, asset_value |
| `FundInfo` | 基金基础信息 | fund_code, fund_invest_type, risk_5_level, nav, manager_names |
| `FundHoldingsDetail` | 基金持仓详情 | report_date, top_stocks, top_bonds |
| `StockHolding` | 股票持仓明细 | stock_code, stock_name, holding_ratio |
| `BondHolding` | 债券持仓明细 | bond_code, bond_name, holding_ratio |

**关键设计：**

- `FundHolding.primary_key` 属性返回复合主键元组 `(fund_account, trade_account, fund_code)`
- `FundInfo.is_money_market_fund()` 方法判断是否为货币基金

### database.py - 数据库操作层

SQLite 数据库操作封装，提供 CRUD 操作和统计查询功能。

**数据库表结构：**

| 表名 | 主键 | 说明 |
|------|------|------|
| `fund_holdings` | `(fund_account, trade_account, fund_code)` | 用户持仓数据 |
| `fund_info` | `fund_code` | 基金基础信息 |
| `fund_holdings_detail` | `fund_code` | 基金持仓详情 |

**核心方法：**

```python
# 持仓操作
upsert_fund_holding(holding)    # 插入或更新持仓（幂等）
get_fund_holdings()             # 获取所有持仓
clear_all_holdings()            # 清空持仓

# 基金信息操作
upsert_fund_info(info)          # 插入或更新基金信息
get_fund_info(fund_code)        # 获取单只基金信息

# 持仓详情操作
upsert_fund_holdings_detail(detail)  # 插入或更新持仓详情
get_fund_holdings_detail(fund_code)  # 获取持仓详情

# 统计查询
get_group_statistics(column)    # 分组统计
query_holdings(column, value)   # 条件查询
get_all_fund_code()             # 获取所有基金代码
```

**设计特点：**

- 使用上下文管理器管理数据库连接
- 所有写操作采用 `ON CONFLICT DO UPDATE` 实现 upsert 模式
- 为 `fund_code`、`fund_account`、`fund_manager` 创建索引优化查询性能
- 股票/债券持仓以 JSON 格式存储

### csv_importer.py - CSV 导入功能

CSV 文件解析和导入模块，支持多种编码格式和智能表头识别。

- 数据获取和导入方法：通过基金E账户导出Excel，转换成csv文件后发生给你的Agent。

**核心功能：**

| 方法 | 说明 |
|------|------|
| `import_from_csv()` | 执行 CSV 导入，返回成功/失败数量 |
| `validate_csv()` | 验证 CSV 文件格式 |
| `_find_header_row()` | 智能查找表头行位置 |
| `_normalize_reader()` | 标准化列名（处理换行符、空格） |
| `_parse_row()` | 解析单行数据为 FundHolding 对象 |
| `_parse_date()` | 多格式日期解析 |

**支持的 CSV 列名映射：**

| CSV 列名 | 模型字段 |
|----------|----------|
| 基金代码 | fund_code |
| 基金名称 | fund_name |
| 基金账户 | fund_account |
| 交易账户 | trade_account |
| 持有份额 | holding_shares |
| 基金净值 | nav |
| 资产情况（结算币种） | asset_value |

**智能处理：**

- **编码自动检测**：依次尝试 utf-8 → utf-8-sig → gbk → gb18030
- **表头智能定位**：通过关键词匹配找到包含"基金代码"、"基金名称"的行
- **列名容错**：处理列名中的换行符、多余空格等变体
- **日期格式兼容**：支持 `%Y/%m/%d`、`%Y-%m-%d`、`%Y.%m.%d`、`%Y年%m月%d日`

### mcp_service.py - MCP 服务集成

通过 mcporter CLI 调用盈米且慢 MCP 服务，获取基金基础信息和持仓详情。

**核心方法：**

| 方法 | 说明 |
|------|------|
| `get_funds_detail(fund_codes)` | 批量获取基金详细信息 |
| `get_funds_holding(fund_codes)` | 批量获取基金持仓情况 |
| `sync_fund_info(fund_codes, db)` | 同步基金信息到数据库 |
| `sync_fund_holdings(fund_codes, db)` | 同步持仓详情到数据库 |

**MCP 工具调用：**

```python
# 调用 qieman-mcp.BatchGetFundsDetail
mcporter call qieman-mcp.BatchGetFundsDetail \
  --args '{"fundCodes":["004137"]}' --output json

# 调用 qieman-mcp.BatchGetFundsHolding
mcporter call qieman-mcp.BatchGetFundsHolding \
  --args '{"fundCodes":["004137"]}' --output json
```

**数据处理：**

- 从 MCP 返回的 JSON 数据中解析基金名称、投资类型、风险等级、净值、收益率等
- 解析重仓股/重仓债信息（代码、名称、占比、金额）
- 批量处理支持每批最多 10 只基金

### statistics.py - 统计视图功能

基于 [Rich](https://github.com/Textualize/rich) 库实现终端美化输出，提供直观的数据展示。

**核心方法：**

| 方法 | 说明 |
|------|------|
| `show_group_statistics(column)` | 显示分组统计表格 |
| `show_query_result(column, value)` | 显示查询结果表格 |
| `show_fund_detail(fund_code)` | 显示基金详情面板 |

**输出示例：**

```
╭─────────────── 基金基础信息 ───────────────╮
│ 基金代码: 004137                          │
│ 基金名称: 易方达中证红利ETF联接A          │
│ 投资类型: 指数型                          │
│ 风险等级: 4                               │
│ 最新净值: 1.4523 (2024-01-15)            │
╰───────────────────────────────────────────╯

┌─────────────────────────────────────────────┐
│              投资类型分布                    │
├──────────────┬────────┬────────────┬───────┤
│ 投资类型     │ 持仓数 │ 资产价值   │ 占比  │
├──────────────┼────────┼────────────┼───────┤
│ 股票型       │      5 │ ¥50,000.00 │ 50.0% │
│ 债券型       │      3 │ ¥30,000.00 │ 30.0% │
│ 货币型       │      2 │ ¥20,000.00 │ 20.0% │
└──────────────┴────────┴────────────┴───────┘
```

**设计特点：**

- 使用 Rich Table 和 Panel 组件实现美观的表格和面板
- 支持中文字符正确对齐
- 查询结果限制显示 50 条，避免终端溢出
- 自动计算占比和汇总信息

### env_checker.py - 环境检查

环境初始化和状态检查模块，确保系统依赖正确配置。

**检查项：**

| 检查项 | 方法 | 说明 |
|--------|------|------|
| mcporter 安装 | `check_mcporter_installed()` | 检查 mcporter CLI 是否在 PATH 中 |
| API Key 配置 | `check_api_key_configured()` | 检查 `QIEMAN_API_KEY` 环境变量 |
| 配置文件 | `check_mcporter_config_exists()` | 检查 `~/.mcporter/mcporter.json` |
| qieman-mcp | `check_qieman_mcp_configured()` | 检查 MCP 服务器配置 |

**初始化流程：**

```
init_environment()
    │
    ├─► 检查 mcporter 安装 ──► 未安装则报错退出
    │
    ├─► 检查配置文件存在
    │
    ├─► 检查 qieman-mcp 配置
    │       │
    │       └─► 未配置则检查 API Key ──► 配置 qieman-mcp
    │
    └─► 测试 MCP 连接 ──► 返回状态报告
```

### config.py - 配置管理

集中管理配置项，包括数据路径、API Key、MCP 服务器配置等。

**配置项：**

| 常量 | 说明 | 默认值 |
|------|------|--------|
| `FUND_ADVISOR_DATA_PATH` | 数据目录环境变量名 | - |
| `QIEMAN_API_KEY` | API Key 环境变量名 | - |
| `DB_FILENAME` | 数据库文件名 | `fund_portfolio_v1.db` |

**辅助函数：**

| 函数 | 说明 |
|------|------|
| `get_data_path()` | 获取数据目录（支持环境变量覆盖） |
| `get_db_path()` | 获取数据库完整路径 |
| `get_api_key()` | 从环境变量获取 API Key |
| `is_api_key_configured()` | 检查 API Key 是否有效配置 |
| `get_qieman_mcp_config()` | 生成 qieman-mcp 服务器配置 |

**数据目录优先级：**

1. 环境变量 `FUND_ADVISOR_DATA_PATH`
2. 默认路径 `$HOME/.fund-advisor`

## 数据模型

### 三张核心数据表

| 表名 | 说明 | 主键 |
|------|------|------|
| `fund_holdings` | 用户持仓数据 | `(fund_account, trade_account, fund_code)` |
| `fund_info` | 基金基础信息 | `fund_code` |
| `fund_holdings_detail` | 基金持仓详情（股票/债券） | `fund_code` |

### 核心数据类

- `FundHolding` - 用户持仓记录
- `FundInfo` - 基金基础信息（净值、规模、经理等）
- `FundHoldingsDetail` - 基金持仓详情（重仓股、重仓债）
- `StockHolding` / `BondHolding` - 持仓明细

## 快速开始

### 1. 环境准备

```bash
# 配置 API Key 环境变量
export QIEMAN_API_KEY="your-api-key-here"

# 可选：自定义数据目录
export FUND_ADVISOR_DATA_PATH="/path/to/data"
```

### 2. 初始化

```bash
# 初始化环境（检查 mcporter + 配置 qieman-mcp）
bash scripts/fund-cli.sh init
```

### 3. 导入持仓

```bash
# 从 CSV 文件导入持仓数据
bash scripts/fund-cli.sh import-csv tools/data/holdings.csv
```

### 4. 同步数据

```bash
# 同步基金基础信息和持仓详情
bash scripts/fund-cli.sh sync --all
```

## CLI 命令

### 环境管理

```bash
# 初始化环境
bash scripts/fund-cli.sh init

# 仅检查环境状态
bash scripts/fund-cli.sh init --check

# 强制重新配置
bash scripts/fund-cli.sh init --force
```

### 持仓管理

```bash
# 导入 CSV 持仓文件
bash scripts/fund-cli.sh import-csv <csv_path>

# 清空所有持仓记录
bash scripts/fund-cli.sh reset
```

### 数据同步

```bash
# 同步基金基础信息
bash scripts/fund-cli.sh sync --info

# 同步基金持仓详情（重仓股、重仓债）
bash scripts/fund-cli.sh sync --detail

# 同步全部数据
bash scripts/fund-cli.sh sync --all
```

### 统计查询

```bash
# 查看基金详情
bash scripts/fund-cli.sh detail 004137

# 按列分组统计
bash scripts/fund-cli.sh group -c fund_manager    # 按基金管理人
bash scripts/fund-cli.sh group -c sales_agency    # 按销售机构
bash scripts/fund-cli.sh group -c invest_type     # 按投资类型
bash scripts/fund-cli.sh group -c currency         # 按结算币种

# 分组统计支持 JSON 格式输出
bash scripts/fund-cli.sh group -c fund_manager -f json

# 按条件查询持仓
bash scripts/fund-cli.sh query -c fund_manager -v "易方达"
bash scripts/fund-cli.sh query -c invest_type -v "股票型"
bash scripts/fund-cli.sh query -c fund_name -v "红利"

# 查询支持 JSON 格式输出
bash scripts/fund-cli.sh query -c fund_name -v "红利" -f json
```

支持的分组/查询列：
- `fund_code` - 基金代码
- `fund_name` - 基金名称
- `fund_manager` - 基金管理人
- `fund_account` - 基金账户
- `trade_account` - 交易账户
- `sales_agency` - 销售机构
- `invest_type` - 投资类型（需 sync --info 后）
- `currency` - 结算币种
- `dividend_method` - 分红方式

## MCP 工具调用

通过 `mcporter` CLI 直接调用 qieman-mcp 服务：

### 基金信息查询

```bash
# 查询单只基金详情
mcporter call qieman-mcp.BatchGetFundsDetail \
  --args '{"fundCodes":["004137"]}' --output json

# 批量查询多只基金
mcporter call qieman-mcp.BatchGetFundsDetail \
  --args '{"fundCodes":["004137","000001","110022"]}' --output json

# 查询基金持仓明细
mcporter call qieman-mcp.BatchGetFundsHolding \
  --args '{"fundCodes":["004137"]}' --output json
```

### 投研分析

```bash
# 基金筛选
mcporter call qieman-mcp.SearchFunds \
  --args '{"keyword":"红利","limit":10}' --output json

# 相关性分析
mcporter call qieman-mcp.GetFundsCorrelation \
  --args '{"fundCodes":["005094","320007"]}' --output json

# 组合回测
mcporter call qieman-mcp.GetFundsBackTest \
  --args '{"fundCodes":["005094","320007"],"weights":[0.5,0.5]}' --output json
```

### 市场资讯

```bash
# 热点话题
mcporter call qieman-mcp.SearchHotTopic \
  --args '{"limit":10}' --output json

# 基金经理观点
mcporter call qieman-mcp.SearchManagerViewpoint \
  --args '{"industry":"科技","limit":5}' --output json
```

## CSV 导入格式

必需列（支持中文名称）：

| 列名 | 说明 | 示例 |
|------|------|------|
| 基金代码 | 6位基金代码 | 004137 |
| 基金名称 | 基金全称 | 易方达中证红利ETF联接A |
| 基金账户 | 基金账户号 | 12345678 |
| 交易账户 | 交易账号 | 87654321 |
| 持有份额 | 份额数量 | 1000.00 |
| 份额日期 | 份额确认日 | 2024/01/15 |
| 基金净值 | 单位净值 | 1.2345 |
| 净值日期 | 净值日期 | 2024/01/15 |
| 资产情况（结算币种） | 资产价值 | 1234.56 |

可选列：份额类别、基金管理人、销售机构、结算币种、分红方式

支持的编码：utf-8, utf-8-sig, gbk, gb18030

## 环境要求

- Python 3.10+
- mcporter CLI（用于调用 MCP 服务）
- qieman-mcp API Key（[申请地址](https://qieman.com/mcp/account)）

## 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `QIEMAN_API_KEY` | 且慢 MCP API Key | 必需 |
| `FUND_ADVISOR_DATA_PATH` | 数据存储目录 | `$HOME/.fund-advisor` |

## 数据存储

默认数据目录：`$HOME/.fund-advisor/`

```
.fund-advisor/
└── fund_portfolio_v1.db    # SQLite 数据库
```

## 开发

### 运行测试

```bash
cd tools
./venv/bin/python -m pytest tests/ -v
```

### 代码风格

- Python 3.10+ 特性
- PEP 8 命名规范
- dataclass 数据模型
- Click CLI 框架
- Rich 终端输出

## 参考文档

- [MCP工具完整清单](references/mcp-tools-full.md)
- [MCP工具基础文档](references/mcp-tools.md)
- [CSV导入格式规范](references/csv-format.md)
- [项目架构说明](references/REFERENCE.md)

## 许可证

MIT License