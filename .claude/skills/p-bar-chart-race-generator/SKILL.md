---
name: bar-chart-race-generator
description: 根据用户上传的CSV数据生成D3动态柱状图可视化HTML文件；适用于展示随时间变化的排名数据、历史趋势分析、竞争格局演变等场景
---

# Bar Chart Race Generator

## 任务目标
- 本 Skill 用于：将CSV格式的时序排名数据转换为可交互的动态柱状图可视化
- 能力包含：数据格式验证、自动生成HTML可视化文件、提供查看指导
- 触发条件：用户需要展示随时间变化的排名数据、历史趋势、竞争格局演变时

## 前置准备
- 依赖说明：无额外依赖，使用Python标准库

## 操作步骤

### 1. 数据准备
- 确认用户已上传CSV数据文件，格式要求见 [references/data-format.md](references/data-format.md)
- 智能体验证CSV文件格式，确保包含必需的四个字段：date, name, category, value

### 2. 生成可视化
- 调用脚本生成HTML文件：
  ```bash
  python3 .claude/skills/bar-chart-race-generator/scripts/generate_race.py --input ./data.csv --output ./bar_chart_race.html
  ```
- 脚本参数：
  - `--input`：输入CSV文件路径（必需）
  - `--output`：输出HTML文件路径（可选，默认为./bar_chart_race.html）
  - `--title`：图表标题（可选，默认为"Bar Chart Race"）
  - `--duration`：每帧持续时间（可选，单位毫秒，默认为250）
  - `--n`：显示的柱状图数量（可选，默认为12）

### 3. 结果查看
- 指导用户在浏览器中打开生成的HTML文件
- 说明交互功能：
  - **Replay**：重新播放动画
  - **速度控制**：可选Normal/Slow/Fast三种速度
  - **数值动画**：柱状图右侧数值会平滑过渡

## 可视化特性

本Skill完全复现D3官方案例的视觉效果和动画特性：

### 动画特性
- ✅ **数值平滑过渡**：使用 `d3.interpolateNumber` 实现数值的逐帧变化动画
- ✅ **流畅的柱状图移动**：每个时间点之间插入10帧过渡（k=10），使用线性缓动
- ✅ **进入/退出动画**：新条目从底部进入，退出条目平滑消失

### 样式细节
- ✅ **颜色编码**：使用 `d3.schemeTableau10` 调色板，按category着色
- ✅ **字体样式**：使用系统字体栈，数值采用等宽数字格式（tabular-nums）
- ✅ **布局精确**：完全复现原始案例的边距、间距和比例

### 交互功能
- ✅ **重播控制**：随时重新播放完整动画
- ✅ **速度调节**：支持三种播放速度
- ✅ **响应式设计**：自适应不同屏幕宽度

## 资源索引
- 必要脚本：见 [scripts/generate_race.py](scripts/generate_race.py)（用途：读取CSV数据并生成包含完整D3.js代码的HTML文件）
- 数据格式说明：见 [references/data-format.md](references/data-format.md)（何时读取：准备数据或验证格式时）
- 示例数据：见 [assets/sample-data.csv](assets/sample-data.csv)（用途：提供参考格式）

## 注意事项
- CSV文件必须包含UTF-8编码
- date字段格式应为YYYY-MM-DD
- value字段必须为数值类型
- 同一date下同一name不应重复
- 智能体应利用其自然语言能力与用户交互，帮助用户理解数据格式要求和结果含义
- 生成的HTML文件依赖D3.js CDN，需要网络连接才能加载

## 使用示例

### 示例1：品牌价值排名变化
- 功能说明：展示品牌价值随年份变化的排名
- 执行方式：脚本自动生成
- 关键参数：用户上传CSV文件
- 示例命令：
  ```bash
  python3 .claude/skills/bar-chart-race-generator/scripts/generate_race.py \
    --input ./brand_rankings.csv \
    --output ./brand_race.html \
    --title "Brand Value Rankings"
  ```

### 示例2：国家GDP排名演变
- 功能说明：展示各国GDP排名的历史变化
- 执行方式：脚本自动生成
- 关键参数：CSV包含国家、年份、GDP数据
- 示例命令：
  ```bash
  python3 .claude/skills/bar-chart-race-generator/scripts/generate_race.py \
    --input ./gdp_data.csv \
    --output ./gdp_race.html \
    --duration 500 \
    --n 15
  ```

### 示例3：慢速播放用于演示
- 功能说明：降低动画速度，方便详细观察变化
- 执行方式：脚本自动生成
- 关键参数：设置较长的duration
- 示例命令：
  ```bash
  python3 .claude/skills/bar-chart-race-generator/scripts/generate_race.py \
    --input ./data.csv \
    --output ./slow_race.html \
    --duration 1000
  ```
