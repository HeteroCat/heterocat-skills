"""
基金分析技能 (Mutual Fund Skills)

基于 Python + AkShare 的全市场基金分析工具
"""

from .fund_screener import (
    calculate_sharpe_ratio,
    calculate_max_drawdown,
    calculate_annualized_return,
    calculate_calmar_ratio,
    calculate_sortino_ratio,
    calculate_information_ratio,
    get_fund_metrics,
    get_fund_scale,
    get_fund_asset_allocation,
    get_fund_manager_info,
    analyze_funds,
    analyze_single_fund,
    analyze_gushou_plus_funds_advanced,
    analyze_stock_funds_advanced,
    filter_quality_funds,
    filter_quality_stock_funds,
    filter_quality_gushou_plus_funds,
    get_default_fund_pool,
    main
)

__version__ = '1.3.0'
__all__ = [
    'calculate_sharpe_ratio',
    'calculate_max_drawdown',
    'calculate_annualized_return',
    'calculate_calmar_ratio',
    'calculate_sortino_ratio',
    'calculate_information_ratio',
    'get_fund_metrics',
    'get_fund_scale',
    'get_fund_asset_allocation',
    'get_fund_manager_info',
    'analyze_funds',
    'analyze_single_fund',
    'analyze_gushou_plus_funds_advanced',
    'analyze_stock_funds_advanced',
    'filter_quality_funds',
    'filter_quality_stock_funds',
    'filter_quality_gushou_plus_funds',
    'get_default_fund_pool',
    'main'
]
