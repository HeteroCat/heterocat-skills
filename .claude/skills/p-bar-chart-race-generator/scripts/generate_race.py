#!/usr/bin/env python3
"""
Bar Chart Race Generator - D3风格复现版

根据CSV数据生成包含D3.js动态柱状图的HTML文件，
完全复现Observable案例的动画效果和样式。

使用方式:
    python3 generate_race.py --input data.csv --output output.html
"""

import csv
import argparse
import json
from datetime import datetime
from collections import defaultdict


def validate_csv_structure(headers):
    """验证CSV表头结构"""
    required_fields = {'date', 'name', 'category', 'value'}
    header_set = set([h.strip().lower() for h in headers])
    
    if not required_fields.issubset(header_set):
        missing = required_fields - header_set
        raise ValueError(f"CSV文件缺少必需字段: {missing}")
    
    header_lower = [h.strip().lower() for h in headers]
    return {
        'date': header_lower.index('date'),
        'name': header_lower.index('name'),
        'category': header_lower.index('category'),
        'value': header_lower.index('value')
    }


def parse_csv_data(filepath, field_indices):
    """解析CSV数据"""
    data = []
    seen = set()
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)
        
        for row in reader:
            if len(row) != 4:
                raise ValueError(f"数据行格式错误: {row}")
            
            date = row[field_indices['date']].strip()
            name = row[field_indices['name']].strip()
            category = row[field_indices['category']].strip()
            value_str = row[field_indices['value']].strip()
            
            key = (date, name)
            if key in seen:
                raise ValueError(f"数据重复: date={date}, name={name}")
            seen.add(key)
            
            try:
                value = float(value_str)
            except ValueError:
                raise ValueError(f"无效的数值: {value_str}")
            
            try:
                datetime.strptime(date, '%Y-%m-%d')
            except ValueError:
                raise ValueError(f"无效的日期格式: {date}")
            
            data.append({
                'date': date,
                'name': name,
                'category': category,
                'value': value
            })
    
    return data


def process_timeline_data(raw_data):
    """处理时序数据，按日期分组"""
    timeline = defaultdict(list)
    for entry in raw_data:
        timeline[entry['date']].append({
            'name': entry['name'],
            'category': entry['category'],
            'value': entry['value']
        })
    
    sorted_dates = sorted(timeline.keys())
    processed_timeline = []
    for date in sorted_dates:
        sorted_entries = sorted(timeline[date], key=lambda x: x['value'], reverse=True)
        processed_timeline.append({
            'date': date,
            'entries': sorted_entries
        })
    
    return processed_timeline


def generate_html(data, options):
    """生成包含D3.js代码的HTML文件，完全复现原始风格"""
    
    # 提取所有唯一的category
    categories = set()
    for entry in data:
        for item in entry['entries']:
            categories.add(item['category'])
    categories = sorted(list(categories))
    
    # 原始案例的参数
    barSize = 48
    marginTop = 16
    marginRight = 6
    marginBottom = 6
    marginLeft = 0
    n = options.get('n', 12)
    k = 10  # 每个时间点之间的过渡帧数
    duration = options.get('duration', 250)
    
    # 构建颜色映射
    categories_json = json.dumps(categories)
    color_scale_code = f"""
    const categoryByName = new Map(data.flatMap(d => d.entries.map(e => [e.name, e.category])));
    const scale = d3.scaleOrdinal(d3.schemeTableau10);
    scale.domain({categories_json});
    const color = d => scale(categoryByName.get(d.name));
    """
    
    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{options['title']}</title>
    <script src="https://d3js.org/d3.v7.min.js" onerror="this.src='https://cdn.bootcdn.net/ajax/libs/d3/7.9.0/d3.min.js'"></script>
    <style>
        :root {{
            --sans-serif: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }}
        body {{
            font-family: var(--sans-serif);
            margin: 0;
            padding: 40px;
            background-color: #fff;
        }}
        .chart {{
            max-width: 100%;
            margin: 0 auto;
        }}
        .header {{
            margin-bottom: 30px;
        }}
        .header h1 {{
            margin: 0;
            font-size: 32px;
            color: #1b1e23;
        }}
        .header p {{
            margin: 10px 0 0 0;
            color: #666;
            font-size: 14px;
        }}
        .controls {{
            margin-bottom: 20px;
        }}
        .controls button {{
            padding: 8px 16px;
            font-family: var(--sans-serif);
            font-size: 14px;
            cursor: pointer;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 4px;
            transition: background-color 0.2s;
        }}
        .controls button:hover {{
            background-color: #45a049;
        }}
        .controls select {{
            padding: 8px;
            font-size: 14px;
            border-radius: 4px;
            border: 1px solid #ddd;
            margin-left: 10px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{options['title']}</h1>
        <p>Color indicates category. Hover for details.</p>
    </div>
    
    <div class="controls">
        <button id="replayBtn">Replay</button>
        <select id="speedSelect">
            <option value="500">Normal</option>
            <option value="1000">Slow</option>
            <option value="125">Fast</option>
        </select>
    </div>
    
    <div class="chart" id="chart"></div>

    <script>
        // 原始数据
        const rawData = {json.dumps(data)};
        
        // 参数配置
        const barSize = {barSize};
        const marginTop = {marginTop};
        const marginRight = {marginRight};
        const marginBottom = {marginBottom};
        const marginLeft = {marginLeft};
        const n = {n};
        const k = {k};
        let duration = {duration};
        
        // 计算尺寸
        const width = 1000;
        const height = marginTop + barSize * n + marginBottom;
        
        // 数据预处理
        const data = rawData;
        const names = new Set(data.flatMap(d => d.entries.map(e => e.name)));
        
        // 将数据转换为date -> name -> value的映射
        const flatData = data.flatMap(d => d.entries.map(e => ({{...e, date: d.date}})));
        const datevalues = Array.from(
            d3.rollup(
                flatData,
                v => v[0].value,
                d => +new Date(d.date),
                d => d.name
            )
        )
        .map(([date, data]) => [new Date(date), data])
        .sort(([a], [b]) => d3.ascending(a, b));
        
        // 计算排名的函数
        function rank(value) {{
            const data = Array.from(names, name => ({{name, value: value(name)}}));
            data.sort((a, b) => d3.descending(a.value, b.value));
            for (let i = 0; i < data.length; ++i) data[i].rank = Math.min(n, i);
            return data;
        }}
        
        // 生成关键帧
        let ka, a, kb, b;
        const keyframes = [];
        for ([[ka, a], [kb, b]] of d3.pairs(datevalues)) {{
            for (let i = 0; i < k; ++i) {{
                const t = i / k;
                keyframes.push([
                    new Date(ka * (1 - t) + kb * t),
                    rank(name => (a.get(name) || 0) * (1 - t) + (b.get(name) || 0) * t)
                ]);
            }}
        }}
        keyframes.push([new Date(kb), rank(name => b.get(name) || 0)]);
        
        // 构建nameframes
        const nameframes = d3.groups(keyframes.flatMap(([, data]) => data), d => d.name);
        
        // 构建prev和next映射
        const prev = new Map(nameframes.flatMap(([, data]) => d3.pairs(data, (a, b) => [b, a])));
        const next = new Map(nameframes.flatMap(([, data]) => d3.pairs(data)));
        
        // 创建比例尺
        const x = d3.scaleLinear([0, 1], [marginLeft, width - marginRight]);
        const y = d3.scaleBand()
            .domain(d3.range(n + 1))
            .rangeRound([marginTop, marginTop + barSize * (n + 1 + 0.1)])
            .padding(0.1);
        
        // 颜色映射
        {color_scale_code}
        
        // 数值格式化
        function textTween(a, b) {{
            const i = d3.interpolateNumber(a, b);
            return function(t) {{
                this.textContent = d3.format(",.0f")(i(t));
            }};
        }}
        
        // 日期格式化
        function formatDate(date) {{
            return d3.utcFormat("%Y")(date);
        }}
        
        // 创建SVG
        const svg = d3.select("#chart")
            .append("svg")
            .attr("viewBox", [0, 0, width, height])
            .attr("width", width)
            .attr("height", height)
            .attr("style", "max-width: 100%; height: auto;");
        
        // 创建条形图更新函数
        const updateBars = bars(svg);
        const updateAxis = axis(svg);
        const updateLabels = labels(svg);
        const updateTicker = ticker(svg);
        
        // 辅助函数：创建条形图
        function bars(svg) {{
            let bar = svg.append("g")
                .attr("fill-opacity", 0.6)
                .selectAll("rect");
            
            return ([date, data], transition) => bar = bar
                .data(data.slice(0, n), d => d.name)
                .join(
                    enter => enter.append("rect")
                        .attr("fill", color)
                        .attr("height", y.bandwidth())
                        .attr("x", x(0))
                        .attr("y", d => y((prev.get(d) || d).rank))
                        .attr("width", d => x((prev.get(d) || d).value) - x(0)),
                    update => update,
                    exit => exit.transition(transition).remove()
                        .attr("y", d => y((next.get(d) || d).rank))
                        .attr("width", d => x((next.get(d) || d).value) - x(0))
                )
                .call(bar => bar.transition(transition)
                    .attr("y", d => y(d.rank))
                    .attr("width", d => x(d.value) - x(0)));
        }}
        
        // 辅助函数：创建标签
        function labels(svg) {{
            let label = svg.append("g")
                .style("font", "bold 12px var(--sans-serif)")
                .style("font-variant-numeric", "tabular-nums")
                .attr("text-anchor", "end")
                .selectAll("text");
            
            return ([date, data], transition) => label = label
                .data(data.slice(0, n), d => d.name)
                .join(
                    enter => enter.append("text")
                        .attr("transform", d => `translate(${{x((prev.get(d) || d).value)}},${{y((prev.get(d) || d).rank)}})`)
                        .attr("y", y.bandwidth() / 2)
                        .attr("x", -6)
                        .attr("dy", "-0.25em")
                        .text(d => d.name)
                        .call(text => text.append("tspan")
                            .attr("fill-opacity", 0.7)
                            .attr("font-weight", "normal")
                            .attr("x", -6)
                            .attr("dy", "1.15em")),
                    update => update,
                    exit => exit.transition(transition).remove()
                        .attr("transform", d => `translate(${{x((next.get(d) || d).value)}},${{y((next.get(d) || d).rank)}})`)
                        .call(g => g.select("tspan").tween("text", d => textTween(d.value, (next.get(d) || d).value)))
                )
                .call(bar => bar.transition(transition)
                    .attr("transform", d => `translate(${{x(d.value)}},${{y(d.rank)}})`)
                    .call(g => g.select("tspan").tween("text", d => textTween((prev.get(d) || d).value, d.value))));
        }}
        
        // 辅助函数：创建坐标轴
        function axis(svg) {{
            const g = svg.append("g")
                .attr("transform", `translate(0,${{marginTop}})`);
            
            const axis = d3.axisTop(x)
                .ticks(width / 160)
                .tickSizeOuter(0)
                .tickSizeInner(-barSize * (n + y.padding()));
            
            return (_, transition) => {{
                g.transition(transition).call(axis);
                g.select(".tick:first-of-type text").remove();
                g.selectAll(".tick:not(:first-of-type) line").attr("stroke", "white");
                g.select(".domain").remove();
            }};
        }}
        
        // 辅助函数：创建时间显示
        function ticker(svg) {{
            const now = svg.append("text")
                .style("font", `bold ${{barSize}}px var(--sans-serif)`)
                .style("font-variant-numeric", "tabular-nums")
                .attr("text-anchor", "end")
                .attr("x", width - 6)
                .attr("y", marginTop + barSize * (n - 0.45))
                .attr("dy", "0.32em")
                .text(formatDate(keyframes[0][0]));
            
            return ([date], transition) => {{
                transition.end().then(() => now.text(formatDate(date)));
            }};
        }}
        
        // 动画控制变量
        let animation = null;
        let currentKeyframeIndex = 0;
        
        // 执行动画
        async function runAnimation() {{
            if (animation) {{
                animation.stop();
                animation = null;
            }}
            
            svg.node().innerHTML = '';
            
            const updateBars = bars(svg);
            const updateAxis = axis(svg);
            const updateLabels = labels(svg);
            const updateTicker = ticker(svg);
            
            svg.node();
            
            for (const keyframe of keyframes) {{
                const transition = svg.transition()
                    .duration(duration)
                    .ease(d3.easeLinear);
                
                // 更新X轴域
                x.domain([0, keyframe[1][0].value]);
                
                updateAxis(keyframe, transition);
                updateBars(keyframe, transition);
                updateLabels(keyframe, transition);
                updateTicker(keyframe, transition);
                
                await transition.end();
            }}
        }}
        
        // 重播按钮
        document.getElementById("replayBtn").addEventListener("click", () => {{
            runAnimation();
        }});
        
        // 速度选择
        document.getElementById("speedSelect").addEventListener("change", function() {{
            duration = parseInt(this.value);
            runAnimation();
        }});
        
        // 初始运行
        runAnimation();
    </script>
</body>
</html>
"""
    
    return html_template


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='生成D3风格动态柱状图HTML文件')
    parser.add_argument('--input', required=True, help='输入CSV文件路径')
    parser.add_argument('--output', default='./bar_chart_race.html', help='输出HTML文件路径')
    parser.add_argument('--title', default='Bar Chart Race', help='图表标题')
    parser.add_argument('--duration', type=int, default=250, help='每帧持续时间（毫秒）')
    parser.add_argument('--n', type=int, default=12, help='显示的柱状图数量')
    
    args = parser.parse_args()
    
    # 验证并解析CSV
    with open(args.input, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)
        field_indices = validate_csv_structure(headers)
    
    # 读取数据
    data = parse_csv_data(args.input, field_indices)
    print(f"已读取 {len(data)} 条数据记录")
    
    # 处理时序数据
    timeline_data = process_timeline_data(data)
    print(f"包含 {len(timeline_data)} 个时间点")
    
    # 生成HTML
    html_content = generate_html(timeline_data, {
        'title': args.title,
        'duration': args.duration,
        'n': args.n
    })
    
    # 写入输出文件
    with open(args.output, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✓ 动态柱状图已生成: {args.output}")
    print(f"✓ 请在浏览器中打开此文件查看可视化效果")


if __name__ == '__main__':
    main()
