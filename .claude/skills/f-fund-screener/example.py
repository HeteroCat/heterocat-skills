#!/usr/bin/env python3
"""
基金分析技能 使用示例
展示如何调用各个功能函数
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fund_screener import (
    get_fund_metrics,
    get_fund_asset_allocation,
    get_fund_scale,
    analyze_funds,
    filter_quality_funds,
    get_default_fund_pool
)

# 示例1: 分析单只基金
print("=" * 80)
print("示例1: 分析单只基金")
print("=" * 80)

fund_code = '004010'
fund_name = '华泰柏瑞鼎利混合A'

print(f"\n分析基金: {fund_code} {fund_name}")
metrics = get_fund_metrics(fund_code, fund_name)

if metrics:
    print("\n风险指标:")
    print(f"  夏普比率: {metrics['夏普比率']}")
    print(f"  最大回撤: {metrics['最大回撤(%)']}%")
    print(f"  年化收益: {metrics['年化收益率(%)']}%")
    print(f"  波动率: {metrics['年化波动率(%)']}%")
    print(f"  近1年收益: {metrics['近1年收益(%)']}%")
else:
    print("  获取数据失败")

# 示例2: 获取资产配置
print("\n" + "=" * 80)
print("示例2: 获取资产配置")
print("=" * 80)

allocation = get_fund_asset_allocation(fund_code)
print(f"\n{fund_name} 资产配置:")
for key, value in allocation.items():
    print(f"  {key}: {value}")

# 示例3: 自定义基金池分析
print("\n" + "=" * 80)
print("示例3: 自定义基金池分析")
print("=" * 80)

# 定义要分析的基金列表
custom_funds = [
    ('002015', '南方荣光A', '偏债混合'),
    ('001316', '安信稳健增值混合A', '偏债混合'),
    ('000385', '景顺长城景颐双利债券A', '二级债基'),
]

print(f"\n分析 {len(custom_funds)} 只基金...")
results_df = analyze_funds(custom_funds, delay=0.5)

if len(results_df) > 0:
    print("\n结果:")
    print(results_df[['基金代码', '基金名称', '夏普比率', '最大回撤(%)', '年化收益率(%)']].to_string(index=False))

# 示例4: 筛选优质基金
print("\n" + "=" * 80)
print("示例4: 筛选优质基金")
print("=" * 80)

if len(results_df) > 0:
    # 筛选夏普>0.5且回撤>-15%的基金
    quality_funds = filter_quality_funds(
        results_df, 
        min_sharpe=0.5,
        max_drawdown=-15
    )
    
    print(f"\n筛选条件: 夏普>=0.5, 回撤>-15%")
    print(f"找到 {len(quality_funds)} 只优质基金:")
    
    if len(quality_funds) > 0:
        print(quality_funds[['基金代码', '基金名称', '夏普比率', '最大回撤(%)']].to_string(index=False))

# 示例5: 使用默认基金池
print("\n" + "=" * 80)
print("示例5: 获取默认基金池")
print("=" * 80)

default_pool = get_default_fund_pool()
print(f"\n默认基金池包含 {len(default_pool)} 只基金")
print("\n前10只基金:")
for code, name, ftype in default_pool[:10]:
    print(f"  {code} {name} ({ftype})")

print("\n" + "=" * 80)
print("示例运行完成!")
print("=" * 80)
