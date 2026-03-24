#!/usr/bin/env python3
"""
基金分析技能 - 核心代码
基于 AkShare 的全市场基金分析工具
"""

import akshare as ak
import pandas as pd
import numpy as np
import warnings
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Tuple
warnings.filterwarnings('ignore')

# 默认无风险利率（年化），参考当前10年期国债收益率水平
# 更新日期: 2025-02，中国10年期国债收益率约1.6%-1.8%
RISK_FREE_RATE = 0.018

# 默认指标计算窗口（交易日数），约3年
METRICS_WINDOW_DAYS = 756

# 共享缓存：fund_manager_em 数据（避免 get_fund_scale 和 get_fund_manager_info 各自独立请求）
_manager_cache = {'data': None, 'time': 0}

# 共享缓存：股票代码 → 申万行业映射
_industry_cache = {'data': None, 'time': 0}


def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = RISK_FREE_RATE) -> float:
    """
    计算夏普比率
    
    Args:
        returns: 日收益率序列
        risk_free_rate: 无风险利率（年化）
    
    Returns:
        夏普比率，值越大表示风险调整后收益越好
    """
    if len(returns) < 2 or returns.std() == 0:
        return np.nan
    excess_returns = returns - risk_free_rate / 252
    return np.sqrt(252) * excess_returns.mean() / returns.std()


def calculate_max_drawdown(nav_values: pd.Series) -> float:
    """
    计算最大回撤
    
    Args:
        nav_values: 净值序列
    
    Returns:
        最大回撤比例（负数），如 -0.15 表示最大回撤15%
    """
    if len(nav_values) < 2:
        return np.nan
    peak = nav_values.expanding(min_periods=1).max()
    drawdown = (nav_values - peak) / peak
    return drawdown.min()


def calculate_annualized_return(nav_values: pd.Series, days: int = 252) -> float:
    """
    计算年化收益率
    
    Args:
        nav_values: 净值序列
        days: 每年交易日数量
    
    Returns:
        年化收益率
    """
    if len(nav_values) < 2:
        return np.nan
    total_return = (nav_values.iloc[-1] / nav_values.iloc[0]) - 1
    n_years = len(nav_values) / days
    if n_years <= 0:
        return np.nan
    return (1 + total_return) ** (1 / n_years) - 1


def calculate_calmar_ratio(annual_return: float, max_drawdown: float) -> float:
    """
    计算卡玛比率 (Calmar Ratio)
    
    公式：年化收益率 / |最大回撤|
    用于评估收益与回撤的平衡，值越大越好
    
    Args:
        annual_return: 年化收益率（小数）
        max_drawdown: 最大回撤（负数，如-0.15）
    
    Returns:
        卡玛比率
    """
    if max_drawdown >= 0 or abs(max_drawdown) < 0.001:
        return np.nan
    return annual_return / abs(max_drawdown)


def calculate_sortino_ratio(returns: pd.Series, risk_free_rate: float = RISK_FREE_RATE) -> float:
    """
    计算索提诺比率 (Sortino Ratio)

    公式：(年化收益 - 无风险利率) / 下行偏差(DD)
    下行偏差：DD = sqrt( (1/N) * Σ min(0, r_i - MAR)^2 ) * sqrt(252)
    其中 MAR = 最小可接受收益率（日化无风险利率）

    与夏普比率的区别：只惩罚低于MAR的波动，不惩罚上行波动
    更适合评估固收+基金（投资者喜欢上涨，只厌恶下跌）

    Args:
        returns: 日收益率序列
        risk_free_rate: 无风险利率（年化）

    Returns:
        索提诺比率，值越大越好
    """
    if len(returns) < 2:
        return np.nan

    # 最小可接受收益率（日化）
    mar_daily = risk_free_rate / 252

    # 年化收益率
    annual_return = returns.mean() * 252

    # 下行偏差（Downside Deviation）：对全部交易日计算
    downside_diff = np.minimum(0, returns.values - mar_daily)
    downside_deviation = np.sqrt(np.mean(downside_diff ** 2)) * np.sqrt(252)

    if downside_deviation == 0:
        return np.nan

    # 索提诺比率
    excess_return = annual_return - risk_free_rate
    return excess_return / downside_deviation


def calculate_information_ratio(returns: pd.Series, benchmark_returns: pd.Series) -> float:
    """
    计算信息比率 (Information Ratio)
    
    公式：超额收益 / 跟踪误差
    衡量基金经理相对于基准的超额收益能力
    
    Args:
        returns: 基金日收益率序列
        benchmark_returns: 基准指数日收益率序列
    
    Returns:
        信息比率，>0.5表示有稳定的超额收益能力
    """
    if len(returns) < 2 or len(benchmark_returns) < 2:
        return np.nan
    
    # 计算超额收益
    excess_returns = returns - benchmark_returns
    
    # 跟踪误差（年化）
    tracking_error = excess_returns.std() * np.sqrt(252)
    
    if tracking_error == 0:
        return np.nan
    
    # 信息比率
    return excess_returns.mean() * 252 / tracking_error


def calculate_style_drift_score(holdings_history: List[Dict]) -> float:
    """
    计算风格漂移分数
    
    通过分析历史持仓的行业集中度变化来评估风格一致性
    分数越低表示风格越稳定
    
    Args:
        holdings_history: 历史持仓数据列表
    
    Returns:
        风格漂移分数（0-1之间，越小越好）
    """
    if len(holdings_history) < 3:
        return 0.5  # 数据不足，返回中等分数
    
    try:
        # 计算每个报告期的行业集中度（前3大行业占比）
        concentrations = []
        for holding in holdings_history:
            if '行业分布' in holding:
                industries = holding['行业分布']
                if len(industries) > 0:
                    top3_ratio = sum(sorted(industries.values(), reverse=True)[:3])
                    concentrations.append(top3_ratio)
        
        if len(concentrations) < 3:
            return 0.5
        
        # 计算集中度的标准差（变异系数）
        mean_conc = np.mean(concentrations)
        std_conc = np.std(concentrations)
        
        if mean_conc == 0:
            return 0.5
        
        cv = std_conc / mean_conc
        # 归一化到0-1范围
        drift_score = min(1.0, cv / 0.5)
        
        return drift_score
    except Exception:
        return 0.5


def _find_nav_by_date(df: pd.DataFrame, target_date: datetime, date_col: str = '净值日期', nav_col: str = '单位净值') -> Optional[float]:
    """
    按日期查找最近的净值，向前查找最近的交易日

    Args:
        df: 含净值日期和单位净值的DataFrame（需已排序）
        target_date: 目标日期
        date_col: 日期列名
        nav_col: 净值列名

    Returns:
        最近交易日的净值，找不到返回None
    """
    mask = df[date_col] <= target_date
    if mask.any():
        return df.loc[mask, nav_col].iloc[-1]
    return None


def _calc_period_return(df: pd.DataFrame, years: float, date_col: str = '净值日期', nav_col: str = '单位净值') -> Optional[float]:
    """
    计算近N年的年化收益率（按日期，CAGR）

    Args:
        df: 含净值日期和单位净值的DataFrame（需已按日期升序排序）
        years: 年数（如1, 2, 3）
        date_col: 日期列名
        nav_col: 净值列名

    Returns:
        年化收益率(%)，数据不足返回None
    """
    if len(df) < 2:
        return None
    latest_date = df[date_col].iloc[-1]
    target_date = latest_date - timedelta(days=int(years * 365))
    start_nav = _find_nav_by_date(df, target_date, date_col, nav_col)
    if start_nav is None or start_nav <= 0:
        return None
    end_nav = df[nav_col].iloc[-1]
    if years <= 1:
        # 不满1年用简单收益
        return (end_nav / start_nav - 1) * 100
    return ((end_nav / start_nav) ** (1 / years) - 1) * 100


def get_fund_metrics(fund_code: str, fund_name: str, min_days: int = 750) -> Optional[Dict]:
    """
    获取基金风险指标（基于近3年数据）

    Args:
        fund_code: 基金代码
        fund_name: 基金名称
        min_days: 最小数据天数要求（默认750，约3年交易日）

    Returns:
        包含各项指标的字典，失败返回 None
    """
    try:
        df = ak.fund_open_fund_info_em(symbol=fund_code, indicator="单位净值走势")

        if df is None or len(df) < min_days:
            return None

        df['净值日期'] = pd.to_datetime(df['净值日期'])
        df = df.sort_values('净值日期')
        df['日收益率'] = df['单位净值'].pct_change()

        # 使用近3年窗口计算核心指标（数据不足3年则用全部）
        window_df = df.tail(METRICS_WINDOW_DAYS)
        returns = window_df['日收益率'].dropna()
        sharpe = calculate_sharpe_ratio(returns)
        max_dd = calculate_max_drawdown(window_df['单位净值'])
        annual_return = calculate_annualized_return(window_df['单位净值'])
        volatility = returns.std() * np.sqrt(252)

        # 按日期计算各期收益（CAGR）
        return_1y = _calc_period_return(df, 1)
        return_2y = _calc_period_return(df, 2)

        return {
            '基金代码': fund_code,
            '基金名称': fund_name,
            '夏普比率': round(sharpe, 2) if not np.isnan(sharpe) else None,
            '最大回撤(%)': round(max_dd * 100, 2) if not np.isnan(max_dd) else None,
            '年化收益率(%)': round(annual_return * 100, 2) if not np.isnan(annual_return) else None,
            '年化波动率(%)': round(volatility * 100, 2) if not np.isnan(volatility) else None,
            '近1年收益(%)': round(return_1y, 2) if return_1y is not None else None,
            '近2年年化(%)': round(return_2y, 2) if return_2y is not None else None,
            '数据天数': len(df)
        }
    except Exception as e:
        return None


def get_fund_scale(fund_code: str) -> Dict:
    """
    获取基金规模

    优先尝试获取单只基金规模，失败则回退到基金经理总管理规模（标注来源）。

    Args:
        fund_code: 基金代码

    Returns:
        包含基金规模的字典
    """
    # 方法1：尝试通过基金个体信息获取单只基金规模
    try:
        individual_df = ak.fund_individual_detail_info_xq(symbol=fund_code)
        if individual_df is not None and len(individual_df) > 0:
            for _, row in individual_df.iterrows():
                item_name = str(row.iloc[0]) if len(row) > 0 else ''
                item_value = str(row.iloc[1]) if len(row) > 1 else ''
                if '规模' in item_name or '资产' in item_name:
                    # 提取数字部分（如 "11.09亿" -> "11.09"）
                    import re
                    match = re.search(r'([\d.]+)', item_value)
                    if match:
                        return {'基金规模(亿元)': match.group(1)}
    except Exception:
        pass

    # 方法2：回退到基金经理总管理规模
    try:
        import time as time_module
        if _manager_cache['data'] is None or time_module.time() - _manager_cache['time'] > 600:
            _manager_cache['data'] = ak.fund_manager_em()
            _manager_cache['time'] = time_module.time()

        mgr_df = _manager_cache['data']
        fund_info = mgr_df[mgr_df['现任基金代码'] == fund_code]

        if len(fund_info) > 0:
            scale_str = fund_info.iloc[0]['现任基金资产总规模']
            return {'基金规模(亿元)': scale_str}
    except Exception:
        pass
    return {'基金规模(亿元)': None}


def get_fund_asset_allocation(fund_code: str) -> Dict:
    """
    获取基金资产配置（从股票持仓推算）
    
    Args:
        fund_code: 基金代码
    
    Returns:
        包含股票仓位、债券仓位的字典
    """
    try:
        hold_df = ak.fund_portfolio_hold_em(symbol=fund_code, date="")
        if hold_df is not None and len(hold_df) > 0:
            latest_quarter = hold_df['季度'].iloc[0]
            latest_hold = hold_df[hold_df['季度'] == latest_quarter]
            
            # 计算股票总仓位
            stock_ratio = latest_hold['占净值比例'].astype(float).sum()
            bond_ratio = max(0, 100 - stock_ratio - 5)
            
            return {
                '股票仓位(%)': round(stock_ratio, 1),
                '估算债券仓位(%)': round(bond_ratio, 1),
                '报告期': latest_quarter
            }
    except Exception:
        pass
    return {'股票仓位(%)': None, '估算债券仓位(%)': None, '报告期': None}


def analyze_funds(fund_list: List[Tuple[str, str, str]], 
                  min_sharpe: float = 0.3,
                  max_drawdown: float = -25,
                  min_return: float = 2,
                  delay: float = 0.3) -> pd.DataFrame:
    """
    批量分析基金
    
    Args:
        fund_list: 基金列表，格式 [(代码, 名称, 类型), ...]
        min_sharpe: 最小夏普比率
        max_drawdown: 最大回撤限制（负数）
        min_return: 最小年化收益率
        delay: 请求间隔（秒）
    
    Returns:
        分析结果 DataFrame
    """
    print(f"开始分析 {len(fund_list)} 只基金...")
    print("-" * 100)
    
    results = []
    for idx, (code, name, ftype) in enumerate(fund_list, 1):
        print(f"[{idx:3d}/{len(fund_list)}] {code} {name[:30]}", end=" ")
        
        metrics = get_fund_metrics(code, name)
        if not metrics:
            print("✗ 无数据")
            continue
        
        metrics['类型'] = ftype
        
        # 获取规模（每5个基金请求一次）
        if idx % 5 == 1:
            scale_info = get_fund_scale(code)
            metrics.update(scale_info)
        else:
            metrics['基金规模(亿元)'] = None
        
        # 获取资产配置
        asset_info = get_fund_asset_allocation(code)
        metrics.update(asset_info)
        
        results.append(metrics)
        print(f"✓ 夏普:{metrics['夏普比率']:.2f} 回撤:{metrics['最大回撤(%)']:.1f}%")
        
        time.sleep(delay)
    
    if not results:
        return pd.DataFrame()
    
    df = pd.DataFrame(results)
    df = df.sort_values('夏普比率', ascending=False)
    
    return df


def filter_quality_funds(df: pd.DataFrame,
                         min_sharpe: float = 0.5,
                         max_drawdown: float = -15,
                         min_return: float = 3) -> pd.DataFrame:
    """
    筛选优质基金
    
    Args:
        df: 分析结果 DataFrame
        min_sharpe: 最小夏普比率
        max_drawdown: 最大回撤限制
        min_return: 最小年化收益率
    
    Returns:
        筛选后的 DataFrame
    """
    return df[
        (df['夏普比率'] >= min_sharpe) & 
        (df['最大回撤(%)'] >= max_drawdown) &
        (df['年化收益率(%)'] > min_return)
    ].copy()


def get_default_fund_pool() -> List[Tuple[str, str, str]]:
    """
    获取默认基金池
    
    Returns:
        基金列表 [(代码, 名称, 类型), ...]
    """
    return [
        # 华泰柏瑞
        ('004010', '华泰柏瑞鼎利混合A', '偏债混合'),
        ('004011', '华泰柏瑞鼎利混合C', '偏债混合'),
        ('001822', '华泰柏瑞惠利混合A', '偏债混合'),
        ('002340', '华泰柏瑞享利混合A', '偏债混合'),
        
        # 南方
        ('002015', '南方荣光A', '偏债混合'),
        ('014681', '南方誉稳一年持有混合A', '偏债混合'),
        ('016927', '南方誉泰稳健6个月持有混合A', '偏债混合'),
        
        # 华夏
        ('000047', '华夏鼎泓债券A', '二级债基'),
        ('002459', '华夏鼎利债券A', '二级债基'),
        ('000121', '华夏永福混合A', '偏债混合'),
        
        # 招商
        ('002657', '招商安本增利债券C', '二级债基'),
        ('217008', '招商安本增利债券A', '二级债基'),
        ('003859', '招商招旭纯债A', '纯债'),
        
        # 易方达
        ('000171', '易方达裕丰回报债券', '二级债基'),
        ('002351', '易方达裕祥回报债券', '二级债基'),
        ('001316', '安信稳健增值混合A', '偏债混合'),
        ('001182', '易方达安心回馈混合', '偏债混合'),
        ('110007', '易方达稳健收益债券A', '二级债基'),
        ('110027', '易方达安心回报债券A', '二级债基'),
        
        # 景顺长城
        ('000385', '景顺长城景颐双利债券A', '二级债基'),
        ('000386', '景顺长城景颐双利债券C', '二级债基'),
        
        # 广发
        ('270002', '广发稳健增长混合A', '偏债混合'),
        ('270006', '广发策略优选混合', '偏债混合'),
        ('000215', '广发趋势优选灵活配置混合A', '偏债混合'),
        
        # 富国
        ('100035', '富国优化增强债券A', '二级债基'),
        ('100036', '富国优化增强债券B', '二级债基'),
        
        # 交银施罗德
        ('004225', '交银增利增强债券A', '二级债基'),
        ('519682', '交银增利债券A', '二级债基'),
        ('519732', '交银定期支付双息平衡混合', '股债平衡'),
        
        # 工银瑞信
        ('485111', '工银瑞信双利债券A', '二级债基'),
        ('485011', '工银瑞信双利债券B', '二级债基'),
        
        # 博时
        ('050011', '博时信用债券A', '二级债基'),
        ('050111', '博时信用债券C', '二级债基'),
        
        # 鹏华
        ('000297', '鹏华可转债债券A', '可转债'),
        ('206013', '鹏华宏泰灵活配置混合', '偏债混合'),
        ('002018', '鹏华弘盛混合A', '偏债混合'),
        
        # 嘉实
        ('070009', '嘉实超短债债券C', '纯债'),
        ('000009', '嘉实超短债债券', '纯债'),
        
        # 其他
        ('002961', '蜂巢恒利债券A', '二级债基'),
        ('002440', '金鹰鑫瑞混合A', '偏债混合'),
        ('005833', '华泰保兴尊合债券A', '二级债基'),
        ('001711', '安信新趋势混合A', '偏债混合'),
        ('000190', '中银新回报混合A', '偏债混合'),
        ('002364', '华安安康灵活配置混合A', '偏债混合'),
        ('110017', '易方达增强回报债券A', '二级债基'),
        ('001717', '天弘精选混合', '偏债混合'),
        ('519069', '汇添富价值精选混合A', '偏债混合'),
        ('166006', '中欧行业成长混合(LOF)A', '偏债混合'),
        ('166005', '中欧价值发现混合A', '偏债混合'),
        ('163406', '兴全合润混合(LOF)', '偏债混合'),
        ('163407', '兴全合宜混合(LOF)A', '偏债混合'),
    ]


def get_fund_manager_info(fund_code: str) -> Dict:
    """获取基金经理信息"""
    try:
        import time as time_module
        if _manager_cache['data'] is None or time_module.time() - _manager_cache['time'] > 600:
            _manager_cache['data'] = ak.fund_manager_em()
            _manager_cache['time'] = time_module.time()

        mgr_df = _manager_cache['data']
        fund_info = mgr_df[mgr_df['现任基金代码'] == fund_code]

        if len(fund_info) > 0:
            info = fund_info.iloc[0]
            years = int(info['累计从业时间']) / 365
            return {
                '基金经理': info['姓名'],
                '所属公司': info['所属公司'],
                '从业年限': f"{years:.1f}年",
                '管理规模': f"{info['现任基金资产总规模']}亿元",
                '最佳回报': f"{info['现任基金最佳回报']}%"
            }
    except Exception:
        pass
    return {}


def get_fund_holding(fund_code: str) -> Dict:
    """获取基金持仓信息"""
    try:
        hold_df = ak.fund_portfolio_hold_em(symbol=fund_code, date=str(datetime.now().year))
        if hold_df is not None and len(hold_df) > 0:
            latest_quarter = hold_df['季度'].iloc[0]
            latest_hold = hold_df[hold_df['季度'] == latest_quarter]
            
            # 计算股票总仓位
            stock_ratio = latest_hold['占净值比例'].astype(float).sum()
            
            return {
                '报告期': latest_quarter,
                '持仓数量': len(latest_hold),
                '股票仓位': f"{stock_ratio:.1f}%",
                '前10大重仓': latest_hold.head(10)[['股票代码', '股票名称', '占净值比例']].to_dict('records')
            }
    except Exception:
        pass
    return {}


def build_industry_mapping() -> Dict[str, str]:
    """
    构建股票代码 → 申万行业映射（带缓存）

    遍历申万行业分类，获取每个行业的成分股，建立映射关系。
    结果缓存到 _industry_cache，有效期 1 小时。

    Returns:
        {股票代码: 行业名称} 字典
    """
    import time as time_module

    # 缓存有效期 1 小时
    if _industry_cache['data'] is not None and time_module.time() - _industry_cache['time'] < 3600:
        return _industry_cache['data']

    print("  构建申万行业映射（首次执行，约20秒）...")
    stock_to_industry = {}

    try:
        industry_df = ak.stock_board_industry_name_em()
        industry_names = industry_df['板块名称'].tolist()

        for idx, ind_name in enumerate(industry_names):
            try:
                cons = ak.stock_board_industry_cons_em(symbol=ind_name)
                if cons is not None and len(cons) > 0:
                    for _, row in cons.iterrows():
                        stock_code = str(row.get('代码', ''))
                        if stock_code:
                            stock_to_industry[stock_code] = ind_name
                if (idx + 1) % 50 == 0:
                    print(f"    已处理 {idx+1}/{len(industry_names)} 个行业...")
            except Exception:
                pass
            time.sleep(0.12)

        print(f"  行业映射完成: {len(stock_to_industry)} 只股票")
        _industry_cache['data'] = stock_to_industry
        _industry_cache['time'] = time_module.time()
    except Exception as e:
        print(f"  行业映射构建失败: {e}")
        _industry_cache['data'] = stock_to_industry
        _industry_cache['time'] = time_module.time()

    return stock_to_industry


def get_fund_holdings_by_quarter(fund_code: str, years: List[str] = None) -> List[Dict]:
    """
    获取基金多个季度的持仓数据

    Args:
        fund_code: 基金代码
        years: 年份列表，如 ['2024', '2023']

    Returns:
        [{'季度': str, '持仓': [{'股票代码': str, '股票名称': str, '占净值比例': float}]}]
    """
    if years is None:
        current_year = datetime.now().year
        years = [str(current_year), str(current_year - 1)]

    quarters = []
    for year in years:
        try:
            df = ak.fund_portfolio_hold_em(symbol=fund_code, date=year)
            if df is not None and len(df) > 0:
                for q_name in df['季度'].unique():
                    q_df = df[df['季度'] == q_name].head(10)
                    holdings = []
                    for _, row in q_df.iterrows():
                        pct = 0
                        try:
                            pct = float(str(row.get('占净值比例', 0)).replace('%', ''))
                        except (ValueError, TypeError):
                            pass
                        holdings.append({
                            '股票代码': str(row.get('股票代码', '')),
                            '股票名称': str(row.get('股票名称', '')),
                            '占净值比例': pct,
                        })
                    quarters.append({'季度': q_name, '持仓': holdings})
        except Exception:
            pass

    return quarters


def calculate_style_drift_from_holdings(quarters_data: List[Dict],
                                         stock_to_industry: Dict[str, str]) -> Tuple[float, str]:
    """
    基于多季度持仓数据计算风格漂移分数

    对每个季度的前10大持仓映射到行业，计算前3大行业在各季度之间的变化系数。

    Args:
        quarters_data: get_fund_holdings_by_quarter() 返回的季度持仓列表
        stock_to_industry: 股票代码→行业映射

    Returns:
        (drift_score, drift_label)
        drift_score: 0-1，越小越稳定
        drift_label: "稳定"/"轻微漂移"/"严重漂移"
    """
    if len(quarters_data) < 3:
        return 0.5, "数据不足"

    # 计算每季度的行业权重分布
    quarter_top3 = []
    for q in quarters_data:
        industry_weights = {}
        for h in q['持仓']:
            ind = stock_to_industry.get(h['股票代码'], '其他')
            if ind not in industry_weights:
                industry_weights[ind] = 0
            industry_weights[ind] += h['占净值比例']

        # 取前3大行业（不含"其他"）
        sorted_ind = sorted(
            [(k, v) for k, v in industry_weights.items() if k != '其他'],
            key=lambda x: x[1], reverse=True
        )[:3]
        quarter_top3.append(set(k for k, v in sorted_ind))

    if len(quarter_top3) < 3:
        return 0.5, "数据不足"

    # 方法：计算相邻季度之间 top3 行业的 Jaccard 相似度
    similarities = []
    for i in range(1, len(quarter_top3)):
        if len(quarter_top3[i]) == 0 or len(quarter_top3[i-1]) == 0:
            continue
        intersection = len(quarter_top3[i] & quarter_top3[i-1])
        union = len(quarter_top3[i] | quarter_top3[i-1])
        if union > 0:
            similarities.append(intersection / union)

    if len(similarities) == 0:
        return 0.5, "数据不足"

    # 平均 Jaccard 相似度越高越稳定
    avg_sim = np.mean(similarities)
    drift_score = 1.0 - avg_sim  # 转换：相似度高→漂移分数低

    if drift_score <= 0.3:
        label = "稳定"
    elif drift_score <= 0.5:
        label = "轻微漂移"
    else:
        label = "严重漂移"

    return round(drift_score, 2), label


def classify_fund_style(holdings: List[Dict], stock_to_industry: Dict[str, str]) -> str:
    """
    根据持仓的行业分布，将基金分类为 价值/红利型、成长型 或 均衡型

    Args:
        holdings: 最近一期的前10大持仓
        stock_to_industry: 股票代码→行业映射

    Returns:
        "价值/红利型" / "成长型" / "均衡型"
    """
    # 定义行业归属
    # 注意：申万行业分类有一级/二级/三级，持仓数据中可能出现各级名称
    value_industries = {
        # 申万一级 — 典型价值/周期/资源板块
        '银行', '煤炭', '石油石化', '电力', '交通运输', '钢铁', '房地产',
        '建筑装饰', '建筑材料', '公用事业', '纺织服饰', '农林牧渔',
        '有色金属', '基础化工', '环保', '综合',
        # 申万二级/三级 — 资源/有色金属
        '铜', '贵金属', '白银', '黄金', '工业金属', '小金属', '能源金属',
        '磁性材料', '稀土', '铝', '锌', '铅', '锡', '镍', '钴', '锂',
        '钨', '钼', '钛', '锰',
        # 申万二级/三级 — 煤炭/石油
        '焦煤', '动力煤', '焦炭', '油气开采', '油服工程', '炼油化工',
        # 申万二级/三级 — 钢铁
        '普钢', '特钢', '特钢Ⅱ',
        # 申万二级/三级 — 电力/公用事业
        '火电', '水电', '核电', '风电', '光伏发电', '热力',
        # 申万二级/三级 — 交通运输
        '铁路运输', '高速公路', '航运', '港口', '物流', '航空',
        '公交', '机场',
        # 申万二级/三级 — 银行
        '国有大型银行Ⅲ', '股份制银行Ⅲ', '城商行Ⅲ', '农商行Ⅲ',
        # 申万二级/三级 — 化工
        '氟化工', '氯碱', '纯碱', '磷化工', '钾肥', '农药',
        '涤纶', '粘胶', '氨纶', '碳纤维',
        # 申万二级/三级 — 农林牧渔
        '养殖业', '种植业', '饲料', '渔业', '林业', '动物保健',
        # 申万二级/三级 — 其他价值/消费
        '钟表珠宝', '轮胎轮毂', '综合Ⅱ', '纺织制造', '服装家纺',
    }

    growth_industries = {
        # 申万一级 — 典型成长板块
        '电子', '计算机', '医药生物', '电力设备', '通信', '传媒', '机械设备',
        '国防军工', '汽车', '食品饮料', '美容护理', '家用电器',
        # 申万二级/三级 — 半导体/电子
        '半导体', '数字芯片设计', '集成电路制造', '集成电路封测',
        '消费电子', '面板', '光学元件', '元件', '其他电子Ⅱ',
        '模拟芯片设计', '存储', 'LED',
        # 申万二级/三级 — 计算机/软件
        'IT服务Ⅲ', '垂直应用软件', '通用应用软件', '基础软件',
        # 申万二级/三级 — 通信
        '通信网络设备及器件', '通信服务',
        # 申万二级/三级 — 医药
        '医疗器械', '化学制药', '化学制剂', '中药', '生物制品',
        '医药商业', '医疗服务', '医疗耗材',
        # 申万二级/三级 — 电力设备/新能源
        '新能源动力系统', '光伏设备', '风电设备', '储能设备',
        '电池', '逆变器',
        # 申万二级/三级 — 家电
        '白色家电', '空调', '小家电', '厨卫电器',
        # 申万二级/三级 — 军工
        '军工电子Ⅱ', '航空装备', '航天装备', '地面兵装',
        # 申万二级/三级 — 机械
        '专用设备', '通用设备', '工程机械', '自动化设备',
    }

    # 统计前5大行业中属于各类的数量
    industry_weights = {}
    for h in holdings[:10]:
        ind = stock_to_industry.get(h['股票代码'], '其他')
        if ind not in industry_weights:
            industry_weights[ind] = 0
        industry_weights[ind] += h['占净值比例']

    sorted_ind = sorted(
        [(k, v) for k, v in industry_weights.items() if k != '其他'],
        key=lambda x: x[1], reverse=True
    )[:5]

    top_names = [k for k, v in sorted_ind]

    value_count = sum(1 for name in top_names[:3]
                      if any(vi in name for vi in value_industries))
    growth_count = sum(1 for name in top_names[:3]
                       if any(gi in name for gi in growth_industries))

    if value_count >= 2:
        return "价值/红利型"
    elif growth_count >= 2:
        return "成长型"
    else:
        return "均衡型"


def analyze_single_fund(fund_code: str, fund_name: Optional[str] = None) -> Dict:
    """
    深度分析单个基金

    Args:
        fund_code: 基金代码
        fund_name: 基金名称（可选，如果不提供会自动查找）
    
    Returns:
        完整的基金分析报告字典
    """
    # 获取基金列表信息（同时用于查名称和最新净值，避免重复请求）
    fund_list = None
    try:
        fund_list = ak.fund_open_fund_daily_em()
    except Exception:
        pass

    # 如果未提供基金名称，尝试查找
    if fund_name is None:
        if fund_list is not None:
            info = fund_list[fund_list['基金代码'] == fund_code]
            if len(info) > 0:
                fund_name = info.iloc[0]['基金简称']
            else:
                fund_name = fund_code
        else:
            fund_name = fund_code

    # 获取最新净值信息
    try:
        if fund_list is not None:
            info = fund_list[fund_list['基金代码'] == fund_code]
        else:
            info = pd.DataFrame()
        if len(info) > 0:
            # 动态获取最新的净值日期列
            # 查找包含"单位净值"的列
            nav_columns = [col for col in info.columns if '单位净值' in col and '累计' not in col]
            accum_columns = [col for col in info.columns if '累计净值' in col]
            
            # 获取最新净值（取第一个匹配的列）
            latest_nav = info.iloc[0].get(nav_columns[0], 'N/A') if nav_columns else 'N/A'
            accum_nav = info.iloc[0].get(accum_columns[0], 'N/A') if accum_columns else 'N/A'
            
            # 提取日期（从列名中）
            latest_date = nav_columns[0].split('-单位净值')[0] if nav_columns else '未知日期'
            
            daily_change = info.iloc[0].get('日增长率', 'N/A')
            fee = info.iloc[0].get('手续费', 'N/A')
            purchase_status = info.iloc[0].get('申购状态', 'N/A')
            redeem_status = info.iloc[0].get('赎回状态', 'N/A')
        else:
            latest_nav = accum_nav = daily_change = fee = purchase_status = redeem_status = 'N/A'
            latest_date = '未知日期'
    except Exception as e:
        latest_nav = accum_nav = daily_change = fee = purchase_status = redeem_status = 'N/A'
        latest_date = '未知日期'
    
    # 获取历史数据用于计算各项指标
    try:
        df = ak.fund_open_fund_info_em(symbol=fund_code, indicator="单位净值走势")
        if df is not None and len(df) >= 250:
            df['净值日期'] = pd.to_datetime(df['净值日期'])
            df = df.sort_values('净值日期')
            df['日收益率'] = df['单位净值'].pct_change()

            # 使用近3年窗口计算核心指标
            window_df = df.tail(METRICS_WINDOW_DAYS)
            returns = window_df['日收益率'].dropna()
            sharpe = calculate_sharpe_ratio(returns)
            max_dd = calculate_max_drawdown(window_df['单位净值'])
            annual_return = calculate_annualized_return(window_df['单位净值'])
            volatility = returns.std() * np.sqrt(252)

            # 按日期计算阶段收益
            periods = {}
            r1 = _calc_period_return(df, 1)
            if r1 is not None:
                periods['近1年'] = round(r1, 2)
            r2 = _calc_period_return(df, 2)
            if r2 is not None:
                periods['近2年年化'] = round(r2, 2)
            r3 = _calc_period_return(df, 3)
            if r3 is not None:
                periods['近3年年化'] = round(r3, 2)

            # 年度收益（用上年末净值作为起始值）
            df['年份'] = df['净值日期'].dt.year
            annual_returns = {}
            years_sorted = sorted(df['年份'].unique())
            for i, year in enumerate(years_sorted):
                if year not in [y for y in years_sorted[-5:]]:
                    continue
                year_df = df[df['年份'] == year]
                if len(year_df) > 50:
                    # 用上年末净值（如果有的话）
                    if i > 0:
                        prev_year_df = df[df['年份'] == years_sorted[i - 1]]
                        start_nav = prev_year_df['单位净值'].iloc[-1]
                    else:
                        start_nav = year_df['单位净值'].iloc[0]
                    end_nav = year_df['单位净值'].iloc[-1]
                    year_return = (end_nav / start_nav - 1) * 100
                    annual_returns[str(year)] = round(year_return, 2)
        else:
            sharpe = max_dd = annual_return = volatility = None
            periods = {}
            annual_returns = {}
    except Exception:
        sharpe = max_dd = annual_return = volatility = None
        periods = {}
        annual_returns = {}
    
    # 获取资产配置
    allocation = get_fund_asset_allocation(fund_code)
    
    # 获取基金经理信息
    manager = get_fund_manager_info(fund_code)
    
    # 获取持仓信息
    holding = get_fund_holding(fund_code)
    
    return {
        '基本信息': {
            '基金代码': fund_code,
            '基金名称': fund_name,
            '最新净值': latest_nav,
            '累计净值': accum_nav,
            '日增长率': daily_change,
            '手续费': fee,
            '申购状态': purchase_status,
            '赎回状态': redeem_status
        },
        '风险指标': {
            '夏普比率': round(sharpe, 2) if sharpe is not None else None,
            '最大回撤(%)': round(max_dd * 100, 2) if max_dd is not None else None,
            '年化收益率(%)': round(annual_return * 100, 2) if annual_return is not None else None,
            '年化波动率(%)': round(volatility * 100, 2) if volatility is not None else None
        },
        '阶段收益': periods,
        '年度收益': annual_returns,
        '资产配置': allocation,
        '基金经理': manager,
        '持仓信息': holding
    }


def print_fund_analysis(analysis: Dict):
    """打印基金分析报告"""
    print("=" * 80)
    print(" " * 25 + "基金深度分析报告")
    print("=" * 80)
    print()
    
    # 1. 基本信息
    print("【1. 基本信息】")
    print("-" * 80)
    basic = analysis['基本信息']
    for key, value in basic.items():
        print(f"{key}: {value}")
    print()
    
    # 2. 风险指标
    if analysis['风险指标'].get('夏普比率'):
        print("【2. 风险指标】")
        print("-" * 80)
        risk = analysis['风险指标']
        for key, value in risk.items():
            if value is not None:
                print(f"{key}: {value}")
        
        # 风险评级
        sharpe = risk.get('夏普比率', 0)
        max_dd = risk.get('最大回撤(%)', 0)
        if sharpe > 1.0 and max_dd > -10:
            risk_level = '低风险（优秀）'
        elif sharpe > 0.5 and max_dd > -20:
            risk_level = '中等风险（良好）'
        else:
            risk_level = '较高风险（需谨慎）'
        print(f"风险评级: {risk_level}")
        print()
    
    # 3. 阶段收益
    if analysis['阶段收益']:
        print("【3. 阶段收益】")
        print("-" * 80)
        for period, return_pct in analysis['阶段收益'].items():
            print(f"{period}: {return_pct}%")
        print()
    
    # 4. 年度收益
    if analysis['年度收益']:
        print("【4. 年度收益表现】")
        print("-" * 80)
        for year, return_pct in analysis['年度收益'].items():
            print(f"{year}年: {return_pct:+.2f}%")
        print()
    
    # 5. 资产配置
    if analysis['资产配置']:
        print("【5. 资产配置】")
        print("-" * 80)
        alloc = analysis['资产配置']
        for key, value in alloc.items():
            if value is not None:
                print(f"{key}: {value}")
        print()
    
    # 6. 基金经理
    if analysis['基金经理']:
        print("【6. 基金经理】")
        print("-" * 80)
        mgr = analysis['基金经理']
        for key, value in mgr.items():
            print(f"{key}: {value}")
        print()
    
    # 7. 持仓信息
    if analysis['持仓信息']:
        print("【7. 持仓信息】")
        print("-" * 80)
        hold = analysis['持仓信息']
        print(f"报告期: {hold.get('报告期', 'N/A')}")
        print(f"持仓数量: {hold.get('持仓数量', 'N/A')}只")
        print(f"股票仓位: {hold.get('股票仓位', 'N/A')}")
        
        if hold.get('前10大重仓'):
            print()
            print("前10大重仓股:")
            for i, stock in enumerate(hold['前10大重仓'][:10], 1):
                print(f"  {i}. {stock['股票名称']}({stock['股票代码']}) - {stock['占净值比例']}%")
        print()
    
    # 8. 综合评价
    print("【8. 综合评价】")
    print("-" * 80)
    
    # 优点
    print("✅ 优点:")
    stock_pos = analysis['资产配置'].get('股票仓位(%)')
    if stock_pos is not None and stock_pos < 20:
        print(f"  • 股票仓位适中({stock_pos}%)，风险可控")
    bond_pos = analysis['资产配置'].get('估算债券仓位(%)')
    if bond_pos is not None and bond_pos > 70:
        print(f"  • 债券仓位较高({bond_pos}%)，收益稳定")
    sharpe = analysis['风险指标'].get('夏普比率')
    if sharpe is not None and sharpe > 0.5:
        print(f"  • 夏普比率良好({sharpe})，风险调整后收益较好")
    
    # 注意
    print()
    print("⚠️  注意:")
    max_dd = analysis['风险指标'].get('最大回撤(%)')
    if max_dd is not None and max_dd < -15:
        print(f"  • 最大回撤{max_dd}%较大，需关注风险控制")
    if sharpe is not None and sharpe < 0.5:
        print(f"  • 夏普比率{sharpe}处于中等水平，风险调整后收益一般")
    
    print()
    print("=" * 80)


# 基金分类常量
class FundType:
    """基金类型枚举"""
    MONEY_MARKET = "货币型"      # 股票仓位 = 0%
    PURE_BOND = "纯债型"          # 股票仓位 < 10%
    BOND_PLUS = "固收+"           # 股票仓位 10-30%
    HYBRID_BOND = "偏债混合"      # 股票仓位 30-50%
    BALANCED = "平衡型"            # 股票仓位 50-70%
    HYBRID_STOCK = "偏股混合"     # 股票仓位 70-90%
    STOCK = "股票型"              # 股票仓位 > 90%
    INDEX = "指数型"               # 指数基金
    QDII = "QDII"                # 海外基金
    FOF = "FOF"                  # 基金中的基金
    OTHER = "其他"


def get_fund_real_type(fund_code: str) -> Dict:
    """
    获取基金的真实类型和基本信息
    
    Args:
        fund_code: 基金代码
    
    Returns:
        包含基金类型、名称等信息的字典
    """
    try:
        # 获取基金列表信息
        fund_list = ak.fund_open_fund_daily_em()
        info = fund_list[fund_list['基金代码'] == fund_code]
        
        if len(info) == 0:
            return {'类型': FundType.OTHER, '基金代码': fund_code}
        
        row = info.iloc[0]
        
        # 从基金简称中提取类型信息
        fund_name = row.get('基金简称', '')
        fund_type_str = row.get('基金类型', '')
        
        # 判断基金真实类型
        fund_type = _classify_fund_type(fund_name, fund_type_str)
        
        return {
            '基金代码': fund_code,
            '基金名称': fund_name,
            '类型': fund_type,
            '基金类型字符串': fund_type_str
        }
        
    except Exception as e:
        return {'类型': FundType.OTHER, '基金代码': fund_code}


def _classify_fund_type(fund_name: str, fund_type_str: str) -> str:
    """
    根据基金名称和类型字符串分类基金
    
    Args:
        fund_name: 基金简称
        fund_type_str: 基金类型字符串（来自API）
    
    Returns:
        基金类型
    """
    name = fund_name.upper()
    type_str = fund_type_str.upper() if fund_type_str else ""
    
    # FOF优先判断
    if 'FOF' in name or '基金中基金' in fund_type_str:
        return FundType.FOF
    
    # QDII判断
    if 'QDII' in name or 'QDII' in type_str:
        return FundType.QDII
    
    # 指数型判断
    if '指数' in name or 'ETF' in name or 'ETF联接' in name:
        return FundType.INDEX
    
    # 货币型判断
    if '货币' in name or type_str == '货币型':
        return FundType.MONEY_MARKET
    
    # 纯债型判断
    if '纯债' in name or '短债' in name or '中短债' in name or '中低债' in name:
        return FundType.PURE_BOND
    
    # 可转债判断
    if '可转债' in name or '转债' in name:
        return "可转债"
    
    # 债券型判断
    if '债券' in name or '债基' in name:
        if '二级债' in name or '混合债' in name:
            return "二级债基"
        return FundType.PURE_BOND
    
    # 根据基金类型字符串判断
    if '混合' in type_str:
        if '偏债' in type_str:
            return FundType.HYBRID_BOND
        elif '偏股' in type_str:
            return FundType.HYBRID_STOCK
        elif '平衡' in type_str:
            return FundType.BALANCED
        else:
            return FundType.HYBRID_BOND  # 默认归类为偏债
    
    # 根据名称关键词判断（使用至少2字词组避免误匹配）
    if any(kw in name for kw in ['稳健', '安心', '安康', '增利', '回报', '增强', '固收']):
        return FundType.BOND_PLUS
    
    return FundType.OTHER


def get_funds_by_type(fund_type: str, max_funds: int = 200, 
                      min_stock_pct: float = None, max_stock_pct: float = None) -> List[Tuple[str, str, str]]:
    """
    按基金类型筛选基金
    
    Args:
        fund_type: 基金类型（使用FundType常量）
        max_funds: 最大数量
        min_stock_pct: 最小股票仓位（可选）
        max_stock_pct: 最大股票仓位（可选）
    
    Returns:
        基金列表 [(代码, 名称, 类型), ...]
    """
    print(f"\n正在筛选 {fund_type} 类型基金...")
    print("-" * 80)
    
    try:
        # 获取基金排名数据
        fund_rank = ak.fund_open_fund_rank_em()
        print(f"✓ 获取到 {len(fund_rank)} 只开放式基金")
        
        # 根据类型筛选
        if fund_type == FundType.PURE_BOND:
            # 纯债型：排除混合、股票、指数、可转债
            filtered = fund_rank[
                ~fund_rank['基金简称'].str.contains('混合|股票|指数|ETF|LOF|可转债|转债', na=False, case=False) &
                fund_rank['基金简称'].str.contains('债|债券|纯债|短债', na=False, case=False)
            ]
        elif fund_type == FundType.BOND_PLUS:
            # 固收+：偏债混合、二级债基、灵活配置（排除纯债和股票型）
            filtered = fund_rank[
                fund_rank['基金简称'].str.contains('混合|二级债|灵活配置|固收+|稳健|增强', na=False, case=False) &
                ~fund_rank['基金简称'].str.contains('纯债|短债|中短债|股票|指数|ETF|LOF|QDII|医药|科技|新能源|光伏|半导体|芯片', na=False, case=False)
            ]
        elif fund_type == FundType.HYBRID_BOND:
            # 偏债混合
            filtered = fund_rank[
                fund_rank['基金简称'].str.contains('偏债|灵活配置', na=False, case=False)
            ]
        elif fund_type == FundType.STOCK:
            # 股票型
            filtered = fund_rank[
                fund_rank['基金简称'].str.contains('股票|偏股', na=False, case=False) &
                ~fund_rank['基金简称'].str.contains('ETF|指数|联接', na=False, case=False)
            ]
        elif fund_type == FundType.INDEX:
            # 指数型
            filtered = fund_rank[
                fund_rank['基金简称'].str.contains('指数|ETF', na=False, case=False)
            ]
        else:
            filtered = fund_rank.head(0)  # 空结果
        
        print(f"✓ 按类型筛选后剩余: {len(filtered)} 只")
        
        # 按近1年收益排序
        filtered['近1年'] = pd.to_numeric(filtered['近1年'], errors='coerce')
        filtered = filtered.sort_values('近1年', ascending=False)
        
        # 限制数量
        selected = filtered.head(max_funds)
        
        result = []
        for idx, row in selected.iterrows():
            result.append((
                str(row['基金代码']).zfill(6),
                row['基金简称'],
                fund_type
            ))
        
        print(f"✓ 将分析 {len(result)} 只{fund_type}基金\n")
        return result
        
    except Exception as e:
        print(f"✗ 筛选失败: {e}")
        return []


def get_gushou_plus_funds(max_funds: int = 0,
                          min_scale: float = 20.0,
                          max_scale: float = 80.0) -> List[Tuple[str, str, str]]:
    """
    获取真正的固收+基金（二级债基、偏债混合、一级债基）

    筛选策略（低成本指标初筛 → 全量深度分析）：
    1. 基金类型精确匹配：债券型-混合二级 / 混合型-偏债 / 债券型-混合一级
    2. 规模筛选：默认 20-80 亿（排除迷你基金和船大难掉头的超大基金）
    3. 成立满 3 年：通过"近3年收益"字段是否有值来判断
    4. 近 1 年收益合理范围 -5%~15%：排除高波动偏股产品
    5. 按近 3 年收益排序，全量输出（max_funds=0）或取 top N 只

    Args:
        max_funds: 最大筛选数量（0=不限制，全量输出，默认0）
        min_scale: 最小规模（亿元，默认20）
        max_scale: 最大规模（亿元，默认80）

    Returns:
        基金列表 [(代码, 名称, 类型), ...]
    """
    print("\n正在从全市场基金中智能筛选固收+产品...")
    print("-" * 100)

    try:
        # === 第一步：获取基金分类数据（精确匹配固收+类型） ===
        name_df = ak.fund_name_em()
        gushou_types = ['债券型-混合二级', '混合型-偏债', '债券型-混合一级']
        type_df = name_df[name_df['基金类型'].isin(gushou_types)][['基金代码', '基金简称', '基金类型']].copy()
        print(f"✓ 固收+类型基金（二级债基/偏债混合/一级债基）: {len(type_df)} 只")

        # === 第二步：获取规模数据，筛选 min_scale ~ max_scale 亿 ===
        import time as time_module
        if _manager_cache['data'] is None or time_module.time() - _manager_cache['time'] > 600:
            _manager_cache['data'] = ak.fund_manager_em()
            _manager_cache['time'] = time_module.time()
        mgr_df = _manager_cache['data']

        # 一只基金可能有多个经理，取第一条（规模是经理维度的总规模，此处用于粗筛）
        mgr_unique = mgr_df.drop_duplicates(subset='现任基金代码', keep='first')[
            ['现任基金代码', '现任基金资产总规模']
        ].rename(columns={'现任基金代码': '基金代码', '现任基金资产总规模': '规模_亿'})

        merged = type_df.merge(mgr_unique, on='基金代码', how='left')
        scale_filtered = merged[
            (merged['规模_亿'] >= min_scale) & (merged['规模_亿'] <= max_scale)
        ].copy()
        print(f"✓ 规模 {min_scale}-{max_scale} 亿筛选后: {len(scale_filtered)} 只")

        # === 第三步：获取业绩数据，筛选成立满3年 + 收益率合理范围 ===
        rank_df = ak.fund_open_fund_rank_em()
        rank_df['近1年'] = pd.to_numeric(rank_df['近1年'], errors='coerce')
        rank_df['近3年'] = pd.to_numeric(rank_df['近3年'], errors='coerce')
        rank_cols = rank_df[['基金代码', '近1年', '近3年']].copy()

        result_df = scale_filtered.merge(rank_cols, on='基金代码', how='left')

        # 成立满3年（近3年数据有值）
        result_df = result_df[result_df['近3年'].notna()].copy()
        print(f"✓ 成立满3年筛选后: {len(result_df)} 只")

        # 近1年收益合理范围
        result_df = result_df[
            (result_df['近1年'] >= -5) & (result_df['近1年'] <= 15)
        ].copy()
        print(f"✓ 近1年收益 -5%~15% 筛选后: {len(result_df)} 只")

        # === 第四步：按近3年收益排序 ===
        result_df = result_df.sort_values('近3年', ascending=False)
        if max_funds > 0:
            selected = result_df.head(max_funds)
        else:
            selected = result_df
        print(f"✓ 按近3年收益排序，共 {len(selected)} 只将进行深度分析\n")

        # 各类型分布
        for t in gushou_types:
            cnt = len(selected[selected['基金类型'] == t])
            if cnt > 0:
                print(f"  {t}: {cnt} 只")

        # === 转换为输出格式 ===
        # 基金类型映射
        type_map = {
            '债券型-混合二级': '二级债基',
            '混合型-偏债': '偏债混合',
            '债券型-混合一级': '一级债基',
        }

        result = []
        for _, row in selected.iterrows():
            code = str(row['基金代码']).zfill(6)
            name = row['基金简称']
            ftype = type_map.get(row['基金类型'], '固收+')
            result.append((code, name, ftype))

        return result

    except Exception as e:
        print(f"✗ 获取基金列表失败: {e}")
        print("将使用备选固收+基金池...")
        # 备选固收+基金池（经典的固收+产品）
        return [
            ('002015', '南方荣光A', '偏债混合'),
            ('004010', '华泰柏瑞鼎利混合A', '偏债混合'),
            ('001822', '华泰柏瑞惠利混合A', '偏债混合'),
            ('001316', '安信稳健增值混合A', '偏债混合'),
            ('000047', '华夏鼎泓债券A', '二级债基'),
            ('003859', '招商招旭纯债A', '纯债'),
            ('000171', '易方达裕丰回报债券', '二级债基'),
            ('002351', '易方达裕祥回报债券', '二级债基'),
            ('000385', '景顺长城景颐双利债券A', '二级债基'),
            ('270002', '广发稳健增长混合A', '偏债混合'),
        ]


def get_smart_active_funds(max_funds: int = 0,
                           min_scale: float = 10.0,
                           max_scale: float = 200.0,
                           min_career_years: float = 5.0) -> List[Tuple[str, str, str]]:
    """
    智选主动管理基金 —— 选"每次考试都在前20%、且不偏科作弊"的基金

    筛选策略（低成本指标初筛 → 全量深度分析）：
    1. 基金类型精确匹配：股票型 / 混合型-偏股 / 混合型-灵活（排除一切指数型）
    2. 规模筛选：默认 10-200 亿
    3. 基金经理从业年限 ≥ 5 年（经历过至少一轮牛熊）
    4. 业绩一致性检验：近1年/近2年/近3年 均需进入同类前40%/35%/30%
    5. 按综合一致性得分排序输出

    Args:
        max_funds: 最大筛选数量（0=不限制）
        min_scale: 最小规模（亿元，默认10）
        max_scale: 最大规模（亿元，默认200）
        min_career_years: 最低基金经理从业年限（默认5年）

    Returns:
        基金列表 [(代码, 名称, 类型), ...]
    """
    print("\n正在从全市场主动基金中智能筛选...")
    print("-" * 100)

    try:
        # === Step 1：精确类型匹配，排除指数基金 ===
        name_df = ak.fund_name_em()
        active_types = ['股票型', '混合型-偏股', '混合型-灵活']
        type_df = name_df[name_df['基金类型'].isin(active_types)][['基金代码', '基金简称', '基金类型']].copy()
        print(f"✓ 主动管理型基金（股票型/偏股/灵活配置）: {len(type_df)} 只")

        # === Step 2：规模筛选 ===
        import time as time_module
        if _manager_cache['data'] is None or time_module.time() - _manager_cache['time'] > 600:
            _manager_cache['data'] = ak.fund_manager_em()
            _manager_cache['time'] = time_module.time()
        mgr_df = _manager_cache['data']

        mgr_unique = mgr_df.drop_duplicates(subset='现任基金代码', keep='first')[
            ['现任基金代码', '现任基金资产总规模', '累计从业时间']
        ].rename(columns={
            '现任基金代码': '基金代码',
            '现任基金资产总规模': '规模_亿',
            '累计从业时间': '从业天数'
        })

        merged = type_df.merge(mgr_unique, on='基金代码', how='left')
        scale_filtered = merged[
            (merged['规模_亿'] >= min_scale) & (merged['规模_亿'] <= max_scale)
        ].copy()
        print(f"✓ 规模 {min_scale}-{max_scale} 亿筛选后: {len(scale_filtered)} 只")

        # === Step 3：基金经理从业年限筛选 ===
        min_career_days = min_career_years * 365
        career_filtered = scale_filtered[
            scale_filtered['从业天数'].notna() &
            (scale_filtered['从业天数'] >= min_career_days)
        ].copy()
        print(f"✓ 经理从业 ≥{min_career_years}年 筛选后: {len(career_filtered)} 只")

        # === Step 4：业绩一致性检验 ===
        rank_df = ak.fund_open_fund_rank_em()
        rank_df['近1年'] = pd.to_numeric(rank_df['近1年'], errors='coerce')
        rank_df['近2年'] = pd.to_numeric(rank_df['近2年'], errors='coerce')
        rank_df['近3年'] = pd.to_numeric(rank_df['近3年'], errors='coerce')
        rank_cols = rank_df[['基金代码', '近1年', '近2年', '近3年']].copy()

        result_df = career_filtered.merge(rank_cols, on='基金代码', how='left')

        # 必须成立满3年
        result_df = result_df[result_df['近3年'].notna()].copy()
        print(f"✓ 成立满3年: {len(result_df)} 只")

        # 分类型计算百分位排名（在同类型基金中比较）
        # 百分位越低越好：0% = 最好，100% = 最差
        for period in ['近1年', '近2年', '近3年']:
            result_df[f'{period}_pct'] = result_df.groupby('基金类型')[period].rank(
                method='min', ascending=False, pct=True
            )

        # 一致性要求：每个时期都在同类前N%
        consistent = result_df[
            (result_df['近1年_pct'] <= 0.40) &   # 近1年前40%
            (result_df['近2年_pct'] <= 0.35) &   # 近2年前35%
            (result_df['近3年_pct'] <= 0.30)     # 近3年前30%
        ].copy()
        print(f"✓ 业绩一致性检验（1Y前40%+2Y前35%+3Y前30%）: {len(consistent)} 只")

        if len(consistent) == 0:
            print("  放宽条件重试...")
            consistent = result_df[
                (result_df['近1年_pct'] <= 0.50) &
                (result_df['近2年_pct'] <= 0.45) &
                (result_df['近3年_pct'] <= 0.40)
            ].copy()
            print(f"  放宽后: {len(consistent)} 只")

        # === Step 5：综合得分排序 ===
        # 得分越低越好（百分位排名越靠前）
        consistent['综合得分'] = (
            0.4 * consistent['近3年_pct'] +
            0.3 * consistent['近2年_pct'] +
            0.3 * consistent['近1年_pct']
        )
        consistent = consistent.sort_values('综合得分', ascending=True)

        if max_funds > 0:
            selected = consistent.head(max_funds)
        else:
            selected = consistent

        print(f"✓ 按一致性综合得分排序，共 {len(selected)} 只将进行深度分析\n")

        # 各类型分布
        for t in active_types:
            cnt = len(selected[selected['基金类型'] == t])
            if cnt > 0:
                print(f"  {t}: {cnt} 只")

        # === 转换为输出格式 ===
        type_map = {
            '股票型': '股票型',
            '混合型-偏股': '偏股混合',
            '混合型-灵活': '灵活配置',
        }

        result = []
        for _, row in selected.iterrows():
            code = str(row['基金代码']).zfill(6)
            name = row['基金简称']
            ftype = type_map.get(row['基金类型'], '主动管理')
            result.append((code, name, ftype))

        return result

    except Exception as e:
        print(f"✗ 获取基金列表失败: {e}")
        import traceback
        traceback.print_exc()
        return []


def get_dividend_funds(min_scale: float = 5.0,
                       max_scale: float = 500.0,
                       min_career_years: float = 3.0) -> List[Tuple[str, str, str]]:
    """
    筛选重仓红利/高股息的主动管理型基金

    双通道筛选：
    通道A: 名称包含红利/高股息/价值等关键词的基金（直接入池）
    通道B: 全量主动基金中，通过持仓分析确认重仓高股息板块的

    放宽标准：规模5-500亿，经理从业≥3年，业绩一致性放宽

    Returns:
        [(代码, 名称, 类型), ...]
    """
    try:
        print("\n正在从全市场筛选红利/高股息主动基金...")
        print("-" * 100)

        # Step 1: 获取全量基金名称和类型
        name_df = ak.fund_name_em()

        # 只要主动管理的类型
        active_types = ['股票型', '混合型-偏股', '混合型-灵活']
        exclude_types = ['指数型-股票', '指数型-海外股票', '指数型-固收', '指数型-其他']
        type_df = name_df[name_df['基金类型'].isin(active_types)].copy()
        # 排除名称中含指数特征的
        idx_kw = ['指数', 'ETF', 'LOF联接', '被动', '跟踪', '增强指数']
        for kw in idx_kw:
            type_df = type_df[~type_df['基金简称'].str.contains(kw, na=False)]
        print(f"✓ 主动管理型基金（股票型/偏股/灵活配置）: {len(type_df)} 只")

        # Step 2: 标记红利关键词基金（通道A）
        dividend_keywords = ['红利', '高股息', '股息', '价值精选', '央企回报', '国企红利',
                           '高分红', '低估值', '深度价值', '价值回报', '红利低波',
                           '红利优选', '红利增长', '红利策略']
        type_df['is_dividend_name'] = False
        for kw in dividend_keywords:
            type_df.loc[type_df['基金简称'].str.contains(kw, na=False), 'is_dividend_name'] = True

        dividend_name_count = type_df['is_dividend_name'].sum()
        print(f"  其中名称含红利/高股息关键词: {dividend_name_count} 只")

        # Step 3: 规模筛选（放宽到 5-500 亿）
        import time as time_module
        if _manager_cache['data'] is None or time_module.time() - _manager_cache['time'] > 600:
            _manager_cache['data'] = ak.fund_manager_em()
            _manager_cache['time'] = time_module.time()
        mgr_df = _manager_cache['data']

        # 构建经理数据（统一列名）
        mgr_unique = mgr_df.drop_duplicates(subset='现任基金代码', keep='first')[
            ['现任基金代码', '现任基金资产总规模', '累计从业时间']
        ].rename(columns={
            '现任基金代码': '基金代码',
            '现任基金资产总规模': '规模_亿',
            '累计从业时间': '从业天数'
        })
        mgr_unique['规模_亿'] = pd.to_numeric(mgr_unique['规模_亿'], errors='coerce')
        mgr_unique['从业天数'] = pd.to_numeric(mgr_unique['从业天数'], errors='coerce')

        merged = type_df.merge(mgr_unique, on='基金代码', how='left')
        merged = merged[
            (merged['规模_亿'] >= min_scale) & (merged['规模_亿'] <= max_scale)
        ].copy()
        print(f"✓ 规模 {min_scale}-{max_scale} 亿筛选后: {len(merged)} 只")

        # Step 4: 经理从业年限 ≥ 3年（放宽）
        min_career_days = min_career_years * 365
        merged = merged[
            merged['从业天数'].notna() & (merged['从业天数'] >= min_career_days)
        ].copy()
        print(f"✓ 经理从业 ≥{min_career_years}年 筛选后: {len(merged)} 只")

        # Step 5: 业绩排名检验（放宽：只要求近3年有数据 + 近1年前60%）
        rank_df = ak.fund_open_fund_rank_em()

        if '近1年' in rank_df.columns:
            for col in ['近1年', '近2年', '近3年']:
                if col in rank_df.columns:
                    rank_df[col] = pd.to_numeric(rank_df[col], errors='coerce')

            rank_df = rank_df[rank_df['基金代码'].isin(merged['基金代码'])]

            # 分通道处理
            # 通道A（名称匹配）: 只要求近1年收益为正
            dividend_codes = set(merged[merged['is_dividend_name'] == True]['基金代码'])
            rank_a = rank_df[rank_df['基金代码'].isin(dividend_codes)].copy()
            if '近1年' in rank_a.columns:
                rank_a = rank_a[rank_a['近1年'] > 0]  # 只要求正收益

            # 通道B（非名称匹配）: 放宽的一致性检验
            rank_b = rank_df[~rank_df['基金代码'].isin(dividend_codes)].copy()

            # 要求近3年有数据
            if '近3年' in rank_b.columns:
                rank_b = rank_b.dropna(subset=['近3年'])

            # 按同类型计算百分位排名
            if '基金类型' in merged.columns:
                rank_b = rank_b.merge(
                    merged[['基金代码', '基金类型']].drop_duplicates(),
                    on='基金代码', how='left'
                )
            else:
                rank_b['基金类型'] = '混合型'

            for col in ['近1年', '近2年', '近3年']:
                if col in rank_b.columns:
                    rank_b[f'{col}_pct'] = rank_b.groupby('基金类型')[col].rank(
                        pct=True, ascending=False
                    )

            # 放宽条件: 近1年前60%, 近2年前55%, 近3年前50%
            if '近1年_pct' in rank_b.columns:
                rank_b = rank_b[rank_b['近1年_pct'] <= 0.60]
            if '近2年_pct' in rank_b.columns:
                rank_b = rank_b[rank_b['近2年_pct'] <= 0.55]
            if '近3年_pct' in rank_b.columns:
                rank_b = rank_b[rank_b['近3年_pct'] <= 0.50]

            passed_codes = set(rank_a['基金代码'].tolist() + rank_b['基金代码'].tolist())
            merged = merged[merged['基金代码'].isin(passed_codes)]

        print(f"✓ 业绩筛选后: {len(merged)} 只（通道A名称匹配 + 通道B放宽一致性）")

        # Step 6: 综合排序
        # 通道A优先（名称匹配的红利基金排在前面），然后按规模降序
        merged['channel'] = merged['is_dividend_name'].apply(lambda x: 0 if x else 1)
        merged = merged.sort_values(['channel', '规模_亿'], ascending=[True, False])

        # 构建输出
        type_map = {
            '股票型': '股票型',
            '混合型-偏股': '偏股混合',
            '混合型-灵活': '灵活配置',
        }

        result = []
        for _, row in merged.iterrows():
            code = str(row['基金代码']).zfill(6)
            name = str(row['基金简称'])
            fund_type = type_map.get(str(row.get('基金类型', '')), '混合型')
            result.append((code, name, fund_type))

        a_count = len(merged[merged['is_dividend_name'] == True])
        b_count = len(merged[merged['is_dividend_name'] == False])
        print(f"✓ 共 {len(result)} 只候选")
        print(f"  通道A（名称匹配红利/高股息）: {a_count} 只")
        print(f"  通道B（全量筛选待持仓验证）: {b_count} 只")

        return result

    except Exception as e:
        print(f"\n筛选出错: {e}")
        import traceback
        traceback.print_exc()
        return []


def get_all_gushou_funds(max_funds: int = 200) -> List[Tuple[str, str, str]]:
    """
    从所有基金中智能筛选优质基金
    
    筛选逻辑：
    1. 从所有开放式基金中筛选
    2. 排除明显股票型、指数型、行业主题型
    3. 保留债券型、稳健型、混合型中风险较低的
    4. 按近1年收益率排序，优先分析表现稳定的
    
    Args:
        max_funds: 最大筛选数量（默认200，避免耗时过长）
    
    Returns:
        基金列表 [(代码, 名称, 类型), ...]
    """
    print("\n正在从全市场基金中智能筛选优质产品...")
    print("-" * 100)
    
    try:
        # 获取所有开放式基金排名
        fund_rank = ak.fund_open_fund_rank_em()
        total = len(fund_rank)
        print(f"✓ 获取到 {total} 只开放式基金")
        
        # 第一步：排除明显股票型/行业主题型基金
        exclude_keywords = [
            '股票', '指数', 'ETF', 'ETF联接', 'LOF', '分级', '医药', '医疗', '科技', 
            '新能源', '半导体', '芯片', '军工', '传媒', '光伏', '白酒', '消费', 
            '制造', '高端制造', '先进制造', '材料', '化工', '有色', '稀土', '煤炭',
            '钢铁', '地产', '银行', '证券', '保险', '金融', '互联网', '传媒', '游戏',
            '生物医药', '医疗器械', '电子', '计算机', '通信', '5G', '人工智能',
            '大数据', '云计算', '新能源', '电动车', '新能源汽车', '碳中和',
            '价值', '成长', '红利', '量化', '对冲', '绝对收益'
        ]
        
        # 先排除明显股票型和行业主题型
        filtered = fund_rank[
            ~fund_rank['基金简称'].str.contains('|'.join(exclude_keywords), na=False, case=False)
        ].copy()
        
        print(f"✓ 排除股票型/行业主题型后剩余: {len(filtered)} 只")
        
        # 第二步：筛选稳健型基金特征
        include_keywords = ['债券', '债基', '稳健', '增利', '鼎利', '丰利', '裕丰',
                           '添利', '回报', '精选', '增强', '双债', '强债', '信用债',
                           '可转债', '纯债', '短债', '安心', '安康', '恒利', '盛利',
                           '混合', '偏债', '灵活配置', '固收']
        
        # 包含稳健型基金特征的基金
        gushou_funds = filtered[
            filtered['基金简称'].str.contains('|'.join(include_keywords), na=False, case=False)
        ].copy()
        
        print(f"✓ 筛选出稳健型特征基金: {len(gushou_funds)} 只")
        
        # 第三步：通过收益率筛选，保留风险适中的
        gushou_funds['近1年'] = pd.to_numeric(gushou_funds['近1年'], errors='coerce')
        
        # 稳健型基金特征：近1年收益通常在 -5% 到 30% 之间
        # 太低可能是纯债，太高可能是股票型
        gushou_funds = gushou_funds[
            (gushou_funds['近1年'] >= -5) & 
            (gushou_funds['近1年'] <= 30)
        ].sort_values('近1年', ascending=False)  # 按收益排序，优先分析表现好的
        
        print(f"✓ 收益率筛选后剩余: {len(gushou_funds)} 只")
        
        # 限制数量
        selected = gushou_funds.head(max_funds)
        print(f"✓ 将分析前 {len(selected)} 只基金\n")
        
        # 转换为需要的格式
        result = []
        for idx, row in selected.iterrows():
            name = row['基金简称']
            # 更精确地判断基金类型
            if '纯债' in name or '短债' in name or '中短债' in name:
                ftype = '纯债型'
            elif '可转债' in name:
                ftype = '可转债'
            elif '债' in name or '债券' in name:
                ftype = '债券型'
            elif '混合' in name:
                ftype = '混合型'
            else:
                ftype = '其他'
            
            result.append((str(row['基金代码']).zfill(6), name, ftype))
        
        return result
        
    except Exception as e:
        print(f"✗ 获取基金列表失败: {e}")
        print("将使用备选基金池...")
        # 如果失败，返回一个小的备选池
        return [
            ('004010', '华泰柏瑞鼎利混合A', '混合型'),
            ('002015', '南方荣光A', '混合型'),
            ('000047', '华夏鼎泓债券A', '债券型'),
            ('003859', '招商招旭纯债A', '纯债型'),
            ('001316', '安信稳健增值混合A', '混合型'),
        ]


def get_stock_funds(max_funds: int = 100) -> List[Tuple[str, str, str]]:
    """
    获取股票类基金（包括股票型、偏股混合型、指数基金等）
    
    筛选逻辑：
    1. 从所有开放式基金中筛选
    2. 优先选择股票型、偏股混合型、指数基金
    3. 排除明显债券型、货币型产品
    4. 按近1年收益率排序，优先分析表现好的
    
    Args:
        max_funds: 最大筛选数量（默认100）
    
    Returns:
        基金列表 [(代码, 名称, 类型), ...]
    """
    print("\n正在从全市场基金中智能筛选股票类产品...")
    print("-" * 100)
    
    try:
        # 获取所有开放式基金排名
        fund_rank = ak.fund_open_fund_rank_em()
        total = len(fund_rank)
        print(f"✓ 获取到 {total} 只开放式基金")
        
        # 股票型基金关键词
        stock_keywords = [
            '股票', '偏股', '成长', '价值', '精选', '优势', '领先', '新锐',
            '蓝筹', '红利', '量化', '指数', 'ETF', '沪深300', '中证500',
            '创业板', '科创板', '新能源', '科技', '医药', '消费', '白酒',
            '半导体', '芯片', '军工', '光伏', '制造', '创新', '新兴'
        ]
        
        # 排除债券型关键词
        exclude_keywords = [
            '债', '债券', '纯债', '短债', '中短债', '可转债', '货币', '理财',
            '稳健', '保守', '保本', '安', '稳', '盈', '丰', '鼎', '裕'
        ]
        
        # 第一步：筛选包含股票型特征的基金
        stock_funds = fund_rank[
            fund_rank['基金简称'].str.contains('|'.join(stock_keywords), na=False, case=False)
        ].copy()
        
        print(f"✓ 筛选出股票型特征基金: {len(stock_funds)} 只")
        
        # 第二步：排除债券型特征基金
        stock_funds = stock_funds[
            ~stock_funds['基金简称'].str.contains('|'.join(exclude_keywords), na=False, case=False)
        ].copy()
        
        print(f"✓ 排除债券型后剩余: {len(stock_funds)} 只")
        
        # 第三步：通过收益率筛选（股票型基金收益通常较高）
        stock_funds['近1年'] = pd.to_numeric(stock_funds['近1年'], errors='coerce')
        
        # 股票型基金特征：近1年收益通常在 -20% 到 100% 之间
        stock_funds = stock_funds[
            (stock_funds['近1年'] >= -20) & 
            (stock_funds['近1年'] <= 100)
        ].sort_values('近1年', ascending=False)
        
        print(f"✓ 收益率筛选后剩余: {len(stock_funds)} 只")
        
        # 限制数量
        selected = stock_funds.head(max_funds)
        print(f"✓ 将分析前 {len(selected)} 只股票类基金\n")
        
        # 转换为需要的格式
        result = []
        for idx, row in selected.iterrows():
            name = row['基金简称']
            # 判断基金类型
            if '指数' in name or 'ETF' in name:
                ftype = '指数型'
            elif '股票' in name:
                ftype = '股票型'
            elif '混合' in name:
                ftype = '混合型-偏股'
            else:
                ftype = '股票型'
            
            result.append((str(row['基金代码']).zfill(6), name, ftype))
        
        return result
        
    except Exception as e:
        print(f"✗ 获取基金列表失败: {e}")
        print("将使用备选股票基金池...")
        # 备选股票基金池
        return [
            ('110022', '易方达消费行业股票', '股票型'),
            ('161725', '招商中证白酒指数A', '指数型'),
            ('005911', '广发双擎升级混合A', '混合型-偏股'),
            ('002190', '农银新能源主题A', '混合型-偏股'),
            ('004997', '广发高端制造股票A', '股票型'),
        ]


def filter_quality_stock_funds(df: pd.DataFrame,
                                min_calmar: float = 1.2,
                                min_info_ratio: float = 0.5,
                                max_drawdown_limit: float = -30,
                                min_annual_return: float = 0.10) -> pd.DataFrame:
    """
    使用专业标准筛选优质股票型基金

    筛选标准（基于Alpha策略）：
    1. 卡玛比率 > 1.2：收益回撤比优秀
    2. 信息比率 > 0.5：有稳定超额收益能力
    3. 最大回撤 < 30%：风险控制良好
    4. 年化收益 > 10%：进攻能力充足
    
    Args:
        df: 分析结果 DataFrame
        min_calmar: 最小卡玛比率
        min_info_ratio: 最小信息比率
        max_drawdown_limit: 最大回撤限制
        min_annual_return: 最小年化收益率
    
    Returns:
        筛选后的 DataFrame
    """
    # 计算卡玛比率（如果还没有）
    if '卡玛比率' not in df.columns:
        df['卡玛比率'] = df.apply(
            lambda row: calculate_calmar_ratio(
                row['年化收益率(%)'] / 100 if pd.notna(row['年化收益率(%)']) else 0,
                row['最大回撤(%)'] / 100 if pd.notna(row['最大回撤(%)']) else -0.5
            ), axis=1
        )
    
    # 专业筛选条件
    quality_funds = df[
        (df['卡玛比率'] >= min_calmar) & 
        (df['最大回撤(%)'] >= max_drawdown_limit) &
        (df['年化收益率(%)'] >= min_annual_return * 100)
    ].copy()
    
    # 按卡玛比率排序
    quality_funds = quality_funds.sort_values('卡玛比率', ascending=False)
    
    return quality_funds


def filter_quality_gushou_plus_funds(df: pd.DataFrame,
                                      min_sharpe: float = 0.8,
                                      min_sortino: float = 1.2,
                                      max_drawdown_limit: float = -5.0,
                                      min_annual_return: float = 3.5) -> pd.DataFrame:
    """
    筛选优质固收+基金

    固收+基金筛选标准：
    1. 夏普比率 > 0.8：风险收益性价比良好
    2. 索提诺比率 > 1.2：下行风险控制优秀
    3. 最大回撤 < 5%：底线防守（固收+的防守底色）
    4. 年化收益 > 3.5%：超越纯债收益（体现"+"的价值）

    为什么用索提诺替代/补充夏普：
    - 夏普惩罚所有波动（包括上涨），对固收+不公平
    - 索提诺只惩罚下行波动，更符合固收+投资者偏好
    - 优秀固收+的索提诺通常显著高于夏普

    Args:
        df: 分析结果 DataFrame
        min_sharpe: 最小夏普比率（默认0.8）
        min_sortino: 最小索提诺比率（默认1.2）
        max_drawdown_limit: 最大回撤限制（默认-5%）
        min_annual_return: 最小年化收益率（默认3.5%）
    
    Returns:
        筛选后的 DataFrame
    """
    # 确保有必要列
    required_cols = ['夏普比率', '最大回撤(%)', '年化收益率(%)']
    for col in required_cols:
        if col not in df.columns:
            print(f"警告: 缺少列 {col}")
            return pd.DataFrame()
    
    # 铁三角筛选条件
    quality_funds = df[
        (df['夏普比率'] >= min_sharpe) & 
        (df['最大回撤(%)'] >= max_drawdown_limit) &
        (df['年化收益率(%)'] >= min_annual_return)
    ].copy()
    
    # 如果有索提诺比率，加入筛选
    if '索提诺比率' in df.columns:
        quality_funds = quality_funds[quality_funds['索提诺比率'] >= min_sortino]
        # 按索提诺比率排序（优先）
        quality_funds = quality_funds.sort_values(['索提诺比率', '夏普比率'], ascending=[False, False])
    else:
        # 按夏普比率排序
        quality_funds = quality_funds.sort_values('夏普比率', ascending=False)
    
    return quality_funds


def analyze_gushou_plus_funds_advanced(fund_list: List[Tuple[str, str, str]],
                                        min_sharpe: float = 0.8,
                                        min_sortino: float = 1.2,
                                        max_drawdown: float = -5.0,
                                        min_return: float = 3.5,
                                        delay: float = 0.3) -> pd.DataFrame:
    """
    使用"铁三角"标准批量分析固收+基金

    核心指标：
    - 夏普比率 (Sharpe Ratio) >= 0.8
    - 索提诺比率 (Sortino Ratio) >= 1.2
    - 最大回撤 < 5%
    - 年化收益 > 3.5%

    固收+基金特征：
    - 股票仓位通常在10%-20%
    - 债券仓位提供安全垫
    - 通过股票/可转债/打新增厚收益
    - 追求"稳中求进"

    Args:
        fund_list: 基金列表，格式 [(代码, 名称, 类型), ...]
        min_sharpe: 最小夏普比率
        min_sortino: 最小索提诺比率
        max_drawdown: 最大回撤限制（负数）
        min_return: 最小年化收益率
        delay: 请求间隔（秒）

    Returns:
        分析结果 DataFrame
    """
    print(f"\n开始专业分析 {len(fund_list)} 只固收+基金...")
    print("=" * 100)
    print("【固收+铁三角筛选标准】")
    print(f"  • 夏普比率 >= {min_sharpe}（风险收益性价比）")
    print(f"  • 索提诺比率 >= {min_sortino}（下行风险控制）")
    print(f"  • 最大回撤 >= {max_drawdown}%（底线防守）")
    print(f"  • 年化收益 >= {min_return}%（超越纯债）")
    print("=" * 100)
    print()
    
    results = []
    for idx, (code, name, ftype) in enumerate(fund_list, 1):
        print(f"[{idx:3d}/{len(fund_list)}] {code} {name[:30]}", end=" ")

        try:
            # 获取基金历史数据
            df = ak.fund_open_fund_info_em(symbol=code, indicator="单位净值走势")

            if df is None or len(df) < 750:
                print("✗ 数据不足")
                continue

            df['净值日期'] = pd.to_datetime(df['净值日期'])
            df = df.sort_values('净值日期')
            df['日收益率'] = df['单位净值'].pct_change()

            # 使用近3年窗口计算核心指标
            window_df = df.tail(METRICS_WINDOW_DAYS)
            returns = window_df['日收益率'].dropna()

            # 计算铁三角指标
            sharpe = calculate_sharpe_ratio(returns)
            sortino = calculate_sortino_ratio(returns)
            max_dd = calculate_max_drawdown(window_df['单位净值'])
            annual_return = calculate_annualized_return(window_df['单位净值'])
            volatility = returns.std() * np.sqrt(252)

            # 按日期计算阶段收益
            return_1y = _calc_period_return(df, 1)
            return_2y = _calc_period_return(df, 2)

            # 获取基金规模和资产配置
            scale_info = get_fund_scale(code)
            asset_info = get_fund_asset_allocation(code)

            metrics = {
                '基金代码': code,
                '基金名称': name,
                '类型': ftype,
                '夏普比率': round(sharpe, 2) if not np.isnan(sharpe) else None,
                '索提诺比率': round(sortino, 2) if not np.isnan(sortino) else None,
                '最大回撤(%)': round(max_dd * 100, 2) if not np.isnan(max_dd) else None,
                '年化收益率(%)': round(annual_return * 100, 2) if not np.isnan(annual_return) else None,
                '年化波动率(%)': round(volatility * 100, 2) if not np.isnan(volatility) else None,
                '近1年收益(%)': round(return_1y, 2) if return_1y is not None else None,
                '近2年年化(%)': round(return_2y, 2) if return_2y is not None else None,
                '数据天数': len(df),
                **scale_info,
                **asset_info
            }
            
            results.append(metrics)
            
            # 显示关键指标
            sharpe_str = f"{sharpe:.2f}" if not np.isnan(sharpe) else "N/A"
            sortino_str = f"{sortino:.2f}" if not np.isnan(sortino) else "N/A"
            dd_str = f"{max_dd*100:.1f}" if not np.isnan(max_dd) else "N/A"
            ret_str = f"{annual_return*100:.1f}" if not np.isnan(annual_return) else "N/A"
            print(f"✓ 夏普:{sharpe_str} 索提诺:{sortino_str} 回撤:{dd_str}% 收益:{ret_str}%")
            
        except Exception as e:
            print(f"✗ 错误: {str(e)[:30]}")
        
        time.sleep(delay)
    
    if not results:
        return pd.DataFrame()
    
    df = pd.DataFrame(results)
    
    # 按索提诺比率排序（固收+更看重下行风险）
    if '索提诺比率' in df.columns:
        df = df.sort_values('索提诺比率', ascending=False)
    elif '夏普比率' in df.columns:
        df = df.sort_values('夏普比率', ascending=False)
    
    return df


def analyze_stock_funds_advanced(fund_list: List[Tuple[str, str, str]], 
                                  min_calmar: float = 1.2,
                                  max_drawdown: float = -30,
                                  min_return: float = 0.15,
                                  delay: float = 0.3) -> pd.DataFrame:
    """
    使用专业标准批量分析股票型基金
    
    增加指标：
    - 卡玛比率 (Calmar Ratio)
    - 信息比率 (Information Ratio) - 需要基准数据
    - 风格一致性评分
    
    Args:
        fund_list: 基金列表，格式 [(代码, 名称, 类型), ...]
        min_calmar: 最小卡玛比率
        max_drawdown: 最大回撤限制
        min_return: 最小年化收益率
        delay: 请求间隔（秒）
    
    Returns:
        分析结果 DataFrame
    """
    print(f"开始专业分析 {len(fund_list)} 只股票型基金...")
    print("=" * 100)
    print("筛选标准：")
    print(f"  • 卡玛比率 >= {min_calmar}")
    print(f"  • 最大回撤 >= {max_drawdown}%")
    print(f"  • 年化收益 >= {min_return*100}%")
    print("=" * 100)
    print()
    
    results = []
    for idx, (code, name, ftype) in enumerate(fund_list, 1):
        print(f"[{idx:3d}/{len(fund_list)}] {code} {name[:30]}", end=" ")

        try:
            # 获取基金历史数据
            df = ak.fund_open_fund_info_em(symbol=code, indicator="单位净值走势")

            if df is None or len(df) < 750:
                print("✗ 数据不足")
                continue

            df['净值日期'] = pd.to_datetime(df['净值日期'])
            df = df.sort_values('净值日期')
            df['日收益率'] = df['单位净值'].pct_change()

            # 使用近3年窗口计算核心指标
            window_df = df.tail(METRICS_WINDOW_DAYS)
            returns = window_df['日收益率'].dropna()

            # 计算基础指标
            sharpe = calculate_sharpe_ratio(returns)
            max_dd = calculate_max_drawdown(window_df['单位净值'])
            annual_return = calculate_annualized_return(window_df['单位净值'])
            volatility = returns.std() * np.sqrt(252)

            # 计算卡玛比率（基于近3年窗口）
            calmar = calculate_calmar_ratio(annual_return, max_dd)

            # 按日期计算阶段收益
            return_1y = _calc_period_return(df, 1)
            return_2y = _calc_period_return(df, 2)

            # 获取基金规模
            scale_info = get_fund_scale(code)

            # 获取资产配置
            asset_info = get_fund_asset_allocation(code)

            metrics = {
                '基金代码': code,
                '基金名称': name,
                '类型': ftype,
                '夏普比率': round(sharpe, 2) if not np.isnan(sharpe) else None,
                '卡玛比率': round(calmar, 2) if not np.isnan(calmar) else None,
                '最大回撤(%)': round(max_dd * 100, 2) if not np.isnan(max_dd) else None,
                '年化收益率(%)': round(annual_return * 100, 2) if not np.isnan(annual_return) else None,
                '年化波动率(%)': round(volatility * 100, 2) if not np.isnan(volatility) else None,
                '近1年收益(%)': round(return_1y, 2) if return_1y is not None else None,
                '近2年年化(%)': round(return_2y, 2) if return_2y is not None else None,
                '数据天数': len(df),
                **scale_info,
                **asset_info
            }
            
            results.append(metrics)
            
            # 显示关键指标
            calmar_str = f"{calmar:.2f}" if not np.isnan(calmar) else "N/A"
            dd_str = f"{max_dd*100:.1f}" if not np.isnan(max_dd) else "N/A"
            ret_str = f"{annual_return*100:.1f}" if not np.isnan(annual_return) else "N/A"
            print(f"✓ 卡玛:{calmar_str} 回撤:{dd_str}% 收益:{ret_str}%")
            
        except Exception as e:
            print(f"✗ 错误: {str(e)[:30]}")
        
        time.sleep(delay)
    
    if not results:
        return pd.DataFrame()
    
    df = pd.DataFrame(results)
    
    # 按卡玛比率排序
    if '卡玛比率' in df.columns:
        df = df.sort_values('卡玛比率', ascending=False)

    return df


def analyze_smart_funds_advanced(fund_pool: List[Tuple[str, str, str]],
                                  delay: float = 0.3) -> pd.DataFrame:
    """
    智选主动基金深度分析 —— 在常规指标之上增加风格漂移检测和哑铃分类

    对每只基金：
    1. 计算 Sharpe/Sortino/MaxDD/AnnualReturn/Calmar（3年窗口）
    2. 获取近2年持仓，检测风格漂移
    3. 根据持仓行业分布进行 价值/红利 vs 成长 分类

    Args:
        fund_pool: [(代码, 名称, 类型), ...]
        delay: API 调用间隔秒数

    Returns:
        DataFrame，包含所有指标 + 风格漂移分数 + 哑铃分类 + 重点板块
    """
    if not fund_pool:
        return pd.DataFrame()

    total = len(fund_pool)
    print(f"\n开始深度分析 {total} 只主动基金（含风格漂移检测）...\n")

    # 预构建行业映射
    stock_to_industry = build_industry_mapping()

    results = []

    for idx, (code, name, ftype) in enumerate(fund_pool):
        print(f"[{idx+1:>3}/{total}] {code} {name} ... ", end="", flush=True)

        try:
            # === Part 1: 常规指标计算 ===
            df = ak.fund_open_fund_info_em(symbol=code, indicator="单位净值走势")

            if df is None or len(df) < 750:
                print("✗ 数据不足")
                continue

            df['净值日期'] = pd.to_datetime(df['净值日期'])
            df = df.sort_values('净值日期')
            df['日收益率'] = df['单位净值'].pct_change()

            window_df = df.tail(METRICS_WINDOW_DAYS)
            returns = window_df['日收益率'].dropna()

            sharpe = calculate_sharpe_ratio(returns)
            sortino = calculate_sortino_ratio(returns)
            max_dd = calculate_max_drawdown(window_df['单位净值'])
            annual_return = calculate_annualized_return(window_df['单位净值'])
            calmar = calculate_calmar_ratio(annual_return, max_dd)

            return_1y = _calc_period_return(df, 1)

            # 获取基金规模
            scale_info = get_fund_scale(code)

            # 获取基金经理信息
            mgr_info = get_fund_manager_info(code)

            # === Part 2: 风格漂移检测 ===
            quarters_data = get_fund_holdings_by_quarter(code, years=['2024', '2023'])
            drift_score, drift_label = calculate_style_drift_from_holdings(
                quarters_data, stock_to_industry
            )

            # === Part 3: 哑铃分类 + 重点板块 ===
            style_class = "均衡型"
            top_sectors_str = ""

            if quarters_data and quarters_data[0]['持仓']:
                latest_holdings = quarters_data[0]['持仓']
                style_class = classify_fund_style(latest_holdings, stock_to_industry)

                # 计算重点板块
                industry_weights = {}
                for h in latest_holdings[:10]:
                    ind = stock_to_industry.get(h['股票代码'], '其他')
                    if ind != '其他':
                        if ind not in industry_weights:
                            industry_weights[ind] = 0
                        industry_weights[ind] += h['占净值比例']

                sorted_ind = sorted(industry_weights.items(), key=lambda x: x[1], reverse=True)[:3]
                top_sectors_str = ', '.join(f"{k}({v:.1f}%)" for k, v in sorted_ind)

                # 前5大持仓名称
                top_names = ', '.join(h['股票名称'] for h in latest_holdings[:5])
            else:
                top_names = ""

            metrics = {
                '基金代码': code,
                '基金名称': name,
                '类型': ftype,
                '风格分类': style_class,
                '基金经理': mgr_info.get('基金经理', ''),
                '从业年限': mgr_info.get('从业年限', ''),
                '夏普比率': round(sharpe, 2) if not np.isnan(sharpe) else None,
                '索提诺比率': round(sortino, 2) if not np.isnan(sortino) else None,
                '卡玛比率': round(calmar, 2) if not np.isnan(calmar) else None,
                '最大回撤(%)': round(max_dd * 100, 2) if not np.isnan(max_dd) else None,
                '年化收益率(%)': round(annual_return * 100, 2) if not np.isnan(annual_return) else None,
                '近1年收益(%)': round(return_1y, 2) if return_1y is not None else None,
                '风格漂移': drift_score,
                '风格稳定度': drift_label,
                '重点板块': top_sectors_str,
                '前5大持仓': top_names,
                **scale_info,
            }

            results.append(metrics)

            calmar_str = f"{calmar:.2f}" if not np.isnan(calmar) else "N/A"
            dd_str = f"{max_dd*100:.1f}" if not np.isnan(max_dd) else "N/A"
            print(f"✓ [{style_class}] 卡玛:{calmar_str} 回撤:{dd_str}% 漂移:{drift_label}")

        except Exception as e:
            print(f"✗ 错误: {str(e)[:40]}")

        time.sleep(delay)

    if not results:
        return pd.DataFrame()

    result_df = pd.DataFrame(results)

    # 剔除严重漂移的基金
    before_count = len(result_df)
    result_df = result_df[result_df['风格漂移'] <= 0.5].copy()
    removed = before_count - len(result_df)
    if removed > 0:
        print(f"\n已剔除 {removed} 只风格严重漂移的基金")

    # 按卡玛比率排序
    if '卡玛比率' in result_df.columns:
        result_df = result_df.sort_values('卡玛比率', ascending=False)

    return result_df


def main():
    """主函数 - 默认从全基金池筛选"""
    import sys
    
    print("=" * 120)
    print(" " * 40 + "基金分析技能")
    print(" " * 35 + "全市场智能筛选 + 深度分析")
    print("=" * 120)
    
    # ===================== 自定义参数解析 =====================
    custom_params = {
        'min_sharpe': None,      # 最小夏普比率
        'max_drawdown': None,    # 最大回撤（负数）
        'min_return': None,      # 最小年化收益
        'min_calmar': None,      # 最小卡玛比率
        'min_sortino': None,     # 最小索提诺比率
    }
    
    # 解析自定义参数
    for i, arg in enumerate(sys.argv):
        if arg == '--min-sharpe' and i + 1 < len(sys.argv):
            try:
                custom_params['min_sharpe'] = float(sys.argv[i + 1])
            except ValueError:
                pass
        elif arg == '--max-dd' and i + 1 < len(sys.argv):
            try:
                custom_params['max_drawdown'] = -abs(float(sys.argv[i + 1]))
            except ValueError:
                pass
        elif arg == '--min-return' and i + 1 < len(sys.argv):
            try:
                custom_params['min_return'] = float(sys.argv[i + 1])
            except ValueError:
                pass
        elif arg == '--min-calmar' and i + 1 < len(sys.argv):
            try:
                custom_params['min_calmar'] = float(sys.argv[i + 1])
            except ValueError:
                pass
        elif arg == '--min-sortino' and i + 1 < len(sys.argv):
            try:
                custom_params['min_sortino'] = float(sys.argv[i + 1])
            except ValueError:
                pass
    
    # 检查是否有命令行参数（单个基金分析模式）
    if len(sys.argv) > 1 and not sys.argv[1].startswith('--'):
        # 单个基金分析模式
        fund_code = sys.argv[1]
        fund_name = sys.argv[2] if len(sys.argv) > 2 else None
        
        print(f"\n正在分析基金: {fund_code}\n")
        analysis = analyze_single_fund(fund_code, fund_name)
        print_fund_analysis(analysis)
        return
    
    # 批量筛选模式 - 默认从全市场筛选
    print("\n🚀 全市场基金智能筛选")
    print("-" * 120)
    print("将从所有开放式基金中智能筛选优质产品进行分析\n")
    
    # 解析参数
    max_funds = 200  # 默认200只
    fund_type = 'gushou'  # 默认为固收型
    
    if '--max' in sys.argv:
        idx = sys.argv.index('--max')
        if idx + 1 < len(sys.argv):
            try:
                max_funds = int(sys.argv[idx + 1])
                max_funds = max(50, min(max_funds, 500))  # 限制50-500
            except ValueError:
                pass
    
    # 检查是否使用红利/高股息基金筛选
    if '--dividend' in sys.argv:
        fund_type = 'dividend'

        print("\n" + "=" * 120)
        print(" " * 30 + "重仓红利/高股息主动基金筛选")
        print(" " * 20 + "寻找重仓银行、煤炭、电力、交运等高股息板块的基金")
        print("=" * 120)
        print("筛选理念：")
        print("  • 排除指数基金，只选主动管理")
        print("  • 双通道筛选：名称关键词匹配 + 全量持仓验证")
        print("  • 放宽标准：规模5-500亿，经理从业≥3年")
        print("  • 风格漂移检测，保留风格稳定的基金")
        print("  • 只保留持仓确认为高股息板块的基金")
        print("=" * 120)

        # 筛选候选基金
        fund_pool = get_dividend_funds()

        if not fund_pool:
            print("\n未获取到基金数据")
            return

        # 去重
        seen = set()
        unique_funds = []
        for fund in fund_pool:
            if fund[0] not in seen:
                seen.add(fund[0])
                unique_funds.append(fund)

        # 限制深度分析数量
        max_analyze = 200
        if len(unique_funds) > max_analyze:
            print(f"\n候选 {len(unique_funds)} 只，取前{max_analyze}只进行深度分析")
            unique_funds = unique_funds[:max_analyze]

        print(f"\n实际分析 {len(unique_funds)} 只基金\n")

        # 深度分析（含风格漂移检测 + 行业分类）
        df = analyze_smart_funds_advanced(unique_funds)

        if len(df) == 0:
            print("\n未获取到有效数据")
            return

        # 只保留 价值/红利型 的基金
        dividend_df = df[df['风格分类'] == '价值/红利型'].copy()

        # 定义纯红利/高股息的行业关键词（排除黄金、有色等资源周期）
        pure_dividend_kw = ['银行', '煤炭', '电力', '石油', '交通', '钢铁', '房地产',
                           '建筑', '公用事业', '火电', '水电', '核电', '高速公路',
                           '铁路', '航运', '港口']

        # 对每只基金检查重点板块是否以纯高股息行业为主
        def is_pure_dividend(row):
            """检查基金重点板块是否以纯高股息行业为主"""
            boards = str(row.get('重点板块', ''))
            if not boards:
                return False
            # 宽松判断：只要重点板块中至少有一个纯高股息行业就保留
            for kw in pure_dividend_kw:
                if kw in boards:
                    return True
            return False

        # 分两组：纯高股息 和 资源价值型
        pure_div = dividend_df[dividend_df.apply(is_pure_dividend, axis=1)].copy()
        resource_div = dividend_df[~dividend_df.apply(is_pure_dividend, axis=1)].copy()

        # 其他分类中名称含红利的也捞回来
        other_df = df[df['风格分类'] != '价值/红利型'].copy()
        name_rescued = other_df[other_df['基金名称'].apply(
            lambda x: any(kw in str(x) for kw in ['红利', '高股息', '股息', '价值'])
        )].copy()

        # 合并最终结果
        all_dividend = pd.concat([pure_div, resource_div, name_rescued], ignore_index=True)
        # 按卡玛比率降序
        all_dividend = all_dividend.sort_values('卡玛比率', ascending=False)

        # 保存CSV
        output_file = "红利高股息基金精选.csv"
        all_dividend.to_csv(output_file, index=False, encoding='utf-8-sig')

        # === 输出结果 ===
        print("\n" + "=" * 120)
        print(" " * 40 + "红利/高股息基金筛选结果")
        print("=" * 120)
        print(f"\n共分析 {len(unique_funds)} 只，{len(df)} 只通过风格漂移检验")
        print(f"其中红利/高股息相关: {len(all_dividend)} 只\n")

        display_cols = ['基金代码', '基金名称', '基金经理', '从业年限',
                       '卡玛比率', '夏普比率', '最大回撤(%)', '年化收益率(%)',
                       '近1年收益(%)', '风格稳定度', '重点板块']

        # 纯高股息板块基金
        if len(pure_div) > 0:
            print("\n" + "=" * 120)
            print(" " * 25 + "纯高股息板块基金（银行/煤电/交运/建筑等）")
            print("=" * 120)
            print(f"共 {len(pure_div)} 只\n")
            avail_cols = [c for c in display_cols if c in pure_div.columns]
            print(pure_div[avail_cols].to_string(index=False))

        # 资源价值型基金
        if len(resource_div) > 0:
            print("\n\n" + "=" * 120)
            print(" " * 25 + "资源价值型基金（贵金属/有色/化工等）")
            print("=" * 120)
            print(f"共 {len(resource_div)} 只\n")
            avail_cols = [c for c in display_cols if c in resource_div.columns]
            print(resource_div[avail_cols].to_string(index=False))

        # 名称含红利但持仓偏成长的
        if len(name_rescued) > 0:
            print("\n\n" + "=" * 120)
            print(" " * 25 + "名称含红利/价值但持仓偏其他风格")
            print("=" * 120)
            print(f"共 {len(name_rescued)} 只\n")
            avail_cols = [c for c in display_cols if c in name_rescued.columns]
            print(name_rescued[avail_cols].to_string(index=False))

        # 统计摘要
        print("\n\n" + "=" * 120)
        print(" " * 50 + "统计摘要")
        print("=" * 120)
        print(f"通过筛选基金总数: {len(all_dividend)}")
        if len(pure_div) > 0:
            print(f"  纯高股息板块: {len(pure_div)} 只")
        if len(resource_div) > 0:
            print(f"  资源价值型: {len(resource_div)} 只")
        if len(name_rescued) > 0:
            print(f"  名称含红利/持仓偏其他: {len(name_rescued)} 只")
        if len(all_dividend) > 0:
            print(f"卡玛比率: 均值 {all_dividend['卡玛比率'].mean():.2f}, 中位数 {all_dividend['卡玛比率'].median():.2f}")
            print(f"最大回撤: 均值 {all_dividend['最大回撤(%)'].mean():.1f}%, 中位数 {all_dividend['最大回撤(%)'].median():.1f}%")
            if '近1年收益(%)' in all_dividend.columns:
                print(f"近1年收益: 均值 {all_dividend['近1年收益(%)'].mean():.1f}%, 中位数 {all_dividend['近1年收益(%)'].median():.1f}%")

        print(f"\n结果已保存: {output_file}")

        return

    # 检查是否使用智选主动基金筛选
    if '--smart-pick' in sys.argv:
        fund_type = 'smart_pick'

        print("\n" + "=" * 120)
        print(" " * 30 + "智选主动基金 —— 哑铃结构配置")
        print(" " * 20 + "选'每次考试都在前20%、且绝对不偏科作弊'的基金")
        print("=" * 120)
        print("筛选理念：")
        print("  • 排除指数基金，只选主动管理")
        print("  • 基金经理从业 ≥5年，经历过牛熊考验")
        print("  • 近1年/2年/3年业绩一致性检验，拒绝'一次性考第一'")
        print("  • 风格漂移检测，剔除'挂羊头卖狗肉'的基金")
        print("  • 自动分类：价值/红利型 + 成长型 → 哑铃结构")
        print("=" * 120)
        print()

        # 获取智选基金池
        fund_pool = get_smart_active_funds()

        if len(fund_pool) == 0:
            print("\n未获取到基金数据")
            return

        # 去重
        seen = set()
        unique_funds = []
        for fund in fund_pool:
            if fund[0] not in seen:
                seen.add(fund[0])
                unique_funds.append(fund)

        # 限制深度分析数量（默认最多150只）
        if len(unique_funds) > 150:
            print(f"\n候选 {len(unique_funds)} 只，取综合得分最优的150只进行深度分析")
            unique_funds = unique_funds[:150]

        print(f"\n实际分析 {len(unique_funds)} 只基金\n")

        # 深度分析（含风格漂移检测 + 哑铃分类）
        df = analyze_smart_funds_advanced(unique_funds)

        if len(df) == 0:
            print("\n未获取到有效数据")
            return

        # 保存CSV
        output_file = "智选主动基金精选.csv"
        df.to_csv(output_file, index=False, encoding='utf-8-sig')

        # === 按哑铃结构分组输出 ===
        print("\n" + "=" * 120)
        print(" " * 40 + "智选主动基金筛选结果")
        print("=" * 120)
        print(f"\n共分析 {len(unique_funds)} 只，{len(df)} 只通过风格漂移检验\n")

        display_cols = ['基金代码', '基金名称', '基金经理', '从业年限',
                       '卡玛比率', '夏普比率', '最大回撤(%)', '年化收益率(%)',
                       '风格稳定度', '重点板块']

        # 价值/红利型
        value_df = df[df['风格分类'] == '价值/红利型'].copy()
        if len(value_df) > 0:
            print("\n" + "=" * 120)
            print(" " * 30 + "价值/红利型精选（对冲科技行业周期风险）")
            print("=" * 120)
            print(f"共 {len(value_df)} 只\n")
            avail_cols = [c for c in display_cols if c in value_df.columns]
            print(value_df[avail_cols].head(25).to_string(index=False))

        # 成长型
        growth_df = df[df['风格分类'] == '成长型'].copy()
        if len(growth_df) > 0:
            print("\n\n" + "=" * 120)
            print(" " * 30 + "高质量成长型精选（博取超额收益）")
            print("=" * 120)
            print(f"共 {len(growth_df)} 只\n")
            avail_cols = [c for c in display_cols if c in growth_df.columns]
            print(growth_df[avail_cols].head(25).to_string(index=False))

        # 均衡型
        balanced_df = df[df['风格分类'] == '均衡型'].copy()
        if len(balanced_df) > 0:
            print("\n\n" + "=" * 120)
            print(" " * 40 + "均衡型精选")
            print("=" * 120)
            print(f"共 {len(balanced_df)} 只\n")
            avail_cols = [c for c in display_cols if c in balanced_df.columns]
            print(balanced_df[avail_cols].head(15).to_string(index=False))

        # 统计摘要
        print("\n\n" + "=" * 120)
        print(" " * 50 + "统计摘要")
        print("=" * 120)
        print(f"通过筛选基金总数: {len(df)}")
        print(f"  价值/红利型: {len(value_df)} 只")
        print(f"  成长型: {len(growth_df)} 只")
        print(f"  均衡型: {len(balanced_df)} 只")
        if '卡玛比率' in df.columns:
            valid_calmar = df['卡玛比率'].dropna()
            if len(valid_calmar) > 0:
                print(f"卡玛比率: 均值 {valid_calmar.mean():.2f}, 中位数 {valid_calmar.median():.2f}")
        if '最大回撤(%)' in df.columns:
            valid_dd = df['最大回撤(%)'].dropna()
            if len(valid_dd) > 0:
                print(f"最大回撤: 均值 {valid_dd.mean():.1f}%, 中位数 {valid_dd.median():.1f}%")
        print(f"\n结果已保存: {output_file}")

        return

    # 检查是否使用专业股票型基金筛选
    if '--stock-alpha' in sys.argv:
        fund_type = 'stock_alpha'

        # 应用自定义参数，否则使用默认值
        min_calmar_val = custom_params['min_calmar'] if custom_params['min_calmar'] else 1.2
        max_dd_val = custom_params['max_drawdown'] if custom_params['max_drawdown'] else -30.0
        min_ret_val = custom_params['min_return'] if custom_params['min_return'] else 10.0

        print("\n🚀 专业股票型基金筛选（Alpha策略）")
        print("=" * 120)
        print("筛选标准：")
        print(f"  • 卡玛比率 >= {min_calmar_val}（收益回撤比优秀）")
        print(f"  • 最大回撤 <= {-max_dd_val}%（风险控制良好）")
        print(f"  • 年化收益 >= {min_ret_val}%（进攻能力充足）")
        print("=" * 120)
        print()

        print(f"📊 分析数量: {max_funds} 只股票类基金")
        print()
        
        # 从全市场获取股票型基金池
        fund_pool = get_stock_funds(max_funds=max_funds)
        
        if len(fund_pool) == 0:
            print("\n❌ 未获取到基金数据")
            return
        
        # 去重
        seen = set()
        unique_funds = []
        for fund in fund_pool:
            if fund[0] not in seen:
                seen.add(fund[0])
                unique_funds.append(fund)
        
        print(f"🎯 实际分析 {len(unique_funds)} 只基金\n")
        
        # 使用专业标准分析股票型基金
        df = analyze_stock_funds_advanced(unique_funds)
        
        if len(df) == 0:
            print("\n❌ 未获取到有效数据")
            return
        
        # 使用专业标准筛选
        high_quality = filter_quality_stock_funds(df, min_calmar=min_calmar_val, max_drawdown_limit=max_dd_val, min_annual_return=min_ret_val / 100)
        
        # 保存结果
        output_file = "股票型基金筛选结果.csv"
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        
        # 显示结果
        print("\n" + "=" * 120)
        print(" " * 45 + "🎉 专业股票型基金筛选结果")
        print("=" * 120)
        print(f"\n【分析 {len(df)} 只基金，{len(high_quality)} 只符合Alpha标准（卡玛>={min_calmar_val} & 回撤<{-max_dd_val}% & 收益>{min_ret_val}%）】\n")
        
        if len(high_quality) > 0:
            display_cols = ['基金代码', '基金名称', '类型', '卡玛比率', '夏普比率', '最大回撤(%)', 
                           '年化收益率(%)', '近1年收益(%)', '基金规模(亿元)']
            print("🏆 Alpha优质基金 TOP 20（推荐关注）：")
            print("-" * 120)
            print(high_quality[display_cols].head(20).to_string(index=False))
        else:
            print(f"⚠️  未找到符合Alpha标准（卡玛>={min_calmar_val} & 回撤<{-max_dd_val}% & 收益>{min_ret_val}%）的基金")
            print("   建议放宽条件查看全部结果\n")
        
        print("\n\n📊 全部基金按卡玛比率排序（TOP 30）：")
        print("-" * 120)
        display_cols2 = ['基金代码', '基金名称', '类型', '卡玛比率', '夏普比率', '最大回撤(%)', 
                        '年化收益率(%)', '股票仓位(%)', '基金规模(亿元)']
        print(df[display_cols2].head(30).to_string(index=False))
        
        # 统计
        print("\n\n" + "=" * 120)
        print(" " * 50 + "📈 统计摘要")
        print("=" * 120)
        print(f"分析基金总数: {len(df)}")
        print(f"卡玛比率>=2.0: {len(df[df['卡玛比率'] >= 2.0])} 只 (卓越)")
        print(f"卡玛比率>=1.5: {len(df[df['卡玛比率'] >= 1.5])} 只 (优秀)")
        print(f"卡玛比率>=1.2: {len(df[df['卡玛比率'] >= 1.2])} 只 (良好)")
        print(f"平均卡玛比率: {df['卡玛比率'].mean():.2f}")
        print(f"平均夏普比率: {df['夏普比率'].mean():.2f}")
        print(f"平均最大回撤: {df['最大回撤(%)'].mean():.2f}%")
        print(f"平均年化收益: {df['年化收益率(%)'].mean():.2f}%")
        
        # 按类型统计
        print("\n按类型统计：")
        type_stats = df.groupby('类型').agg({
            '卡玛比率': 'mean',
            '夏普比率': 'mean',
            '最大回撤(%)': 'mean',
            '年化收益率(%)': 'mean',
            '基金代码': 'count'
        }).round(2)
        type_stats.columns = ['平均卡玛', '平均夏普', '平均回撤', '平均收益', '数量']
        print(type_stats.to_string())
        
        print(f"\n✅ 详细结果已保存到: {output_file}")
        print("\n💡 使用建议:")
        print("   • 优先关注卡玛比率>1.2且回撤<30%的基金")
        print("   • 卡玛比率 = 年化收益 / |最大回撤|，衡量收益风险比")
        print("   • 可通过 'npx mutual-fund-skills <基金代码>' 进行单基金深度分析")
        print("=" * 120)
        return

    # ===================== 纯债基金筛选模式 =====================
    if '--bond' in sys.argv or '--pure-bond' in sys.argv:
        print("\n🚀 纯债基金筛选（低风险）")
        print("=" * 120)
        
        # 筛选标准（纯债要求更低回撤、更稳收益）
        min_sharpe_val = custom_params['min_sharpe'] if custom_params['min_sharpe'] else 1.0
        max_dd_val = custom_params['max_drawdown'] if custom_params['max_drawdown'] else -2.0
        min_ret_val = custom_params['min_return'] if custom_params['min_return'] else 2.5
        
        print("【筛选标准】")
        print(f"  • 夏普比率 >= {min_sharpe_val}（风险收益性价比）")
        print(f"  • 最大回撤 <= {-max_dd_val}%（底线防守）")
        print(f"  • 年化收益 >= {min_ret_val}%（稳定收益）")
        print("=" * 120)
        print()
        
        print(f"📊 分析数量: {max_funds} 只纯债基金")
        print()
        
        # 使用新的按类型筛选函数
        fund_pool = get_funds_by_type(FundType.PURE_BOND, max_funds=max_funds)
        
        if len(fund_pool) == 0:
            print("\n❌ 未获取到基金数据")
            return
        
        # 去重
        seen = set()
        unique_funds = []
        for fund in fund_pool:
            if fund[0] not in seen:
                seen.add(fund[0])
                unique_funds.append(fund)
        
        print(f"🎯 实际分析 {len(unique_funds)} 只纯债基金\n")
        
        # 使用固收+分析函数（但标准不同）
        df = analyze_gushou_plus_funds_advanced(
            unique_funds,
            min_sharpe=min_sharpe_val,
            max_drawdown=max_dd_val,
            min_return=min_ret_val
        )
        
        if len(df) == 0:
            print("\n❌ 未获取到有效数据")
            return
        
        # 筛选符合条件的基金
        quality_funds = df[
            (df['夏普比率'] >= min_sharpe_val) & 
            (df['最大回撤(%)'] >= max_dd_val) &
            (df['年化收益率(%)'] >= min_ret_val)
        ].copy()
        
        # 保存结果
        output_file = "纯债基金筛选结果.csv"
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        
        # 显示结果
        print("\n" + "=" * 120)
        print(" " * 50 + "🎉 纯债基金筛选结果")
        print("=" * 120)
        print(f"\n【分析 {len(df)} 只纯债基金，{len(quality_funds)} 只符合标准】\n")
        
        if len(quality_funds) > 0:
            display_cols = ['基金代码', '基金名称', '类型', '夏普比率', '最大回撤(%)', 
                           '年化收益率(%)', '近1年收益(%)', '基金规模(亿元)']
            print("🏆 优质纯债基金 TOP 20：")
            print("-" * 120)
            print(quality_funds[display_cols].head(20).to_string(index=False))
        
        print("\n\n📊 全部纯债基金按夏普比率排序（TOP 30）：")
        print("-" * 120)
        display_cols2 = ['基金代码', '基金名称', '类型', '夏普比率', '最大回撤(%)', 
                        '年化收益率(%)', '基金规模(亿元)']
        print(df[display_cols2].head(30).to_string(index=False))
        
        # 统计
        print("\n\n" + "=" * 120)
        print(" " * 50 + "📈 统计摘要")
        print("=" * 120)
        print(f"分析基金总数: {len(df)}")
        print(f"夏普比率>=1.0: {len(df[df['夏普比率'] >= 1.0])} 只 (优秀)")
        print(f"夏普比率>=0.8: {len(df[df['夏普比率'] >= 0.8])} 只 (良好)")
        print(f"平均夏普比率: {df['夏普比率'].mean():.2f}")
        print(f"平均最大回撤: {df['最大回撤(%)'].mean():.2f}%")
        print(f"平均年化收益: {df['年化收益率(%)'].mean():.2f}%")
        
        print(f"\n✅ 详细结果已保存到: {output_file}")
        print("\n💡 使用建议:")
        print("   • 纯债基金适合保守型投资者")
        print("   • 优先关注回撤<2%、夏普>1.0的产品")
        print("=" * 120)
        return
    
    # 检查是否使用固收+专业筛选模式
    if '--gushou-plus' in sys.argv:
        fund_type = 'gushou_plus'

        # 应用自定义参数，否则使用默认值
        min_sharpe_val = custom_params['min_sharpe'] if custom_params['min_sharpe'] else 0.8
        max_dd_val = custom_params['max_drawdown'] if custom_params['max_drawdown'] else -5.0
        min_ret_val = custom_params['min_return'] if custom_params['min_return'] else 3.5
        min_sortino_val = custom_params['min_sortino'] if custom_params['min_sortino'] else 1.2

        print("\n🚀 固收+基金专业筛选")
        print("=" * 120)
        print("【筛选标准】")
        print(f"  • 夏普比率 >= {min_sharpe_val}（风险收益性价比）")
        print(f"  • 索提诺比率 >= {min_sortino_val}（下行风险控制）")
        print(f"  • 最大回撤 <= {-max_dd_val}%（底线防守）")
        print(f"  • 年化收益 >= {min_ret_val}%（超越纯债）")
        print("=" * 120)
        print()

        print(f"📊 固收+基金全量筛选（规模20-80亿，成立满3年）")
        print()

        # 从全市场获取固收+基金池（全量初筛，不截断）
        fund_pool = get_gushou_plus_funds()

        if len(fund_pool) == 0:
            print("\n❌ 未获取到基金数据")
            return

        # 去重
        seen = set()
        unique_funds = []
        for fund in fund_pool:
            if fund[0] not in seen:
                seen.add(fund[0])
                unique_funds.append(fund)

        print(f"🎯 实际分析 {len(unique_funds)} 只基金\n")

        # 使用铁三角标准分析固收+基金
        df = analyze_gushou_plus_funds_advanced(unique_funds)

        if len(df) == 0:
            print("\n❌ 未获取到有效数据")
            return

        # 筛选 - 优先看回撤
        high_quality = df[
            (df['最大回撤(%)'] >= max_dd_val) &
            (df['年化收益率(%)'] >= min_ret_val) &
            (df['夏普比率'] >= min_sharpe_val)
        ].copy()

        # 如果有索提诺比率，加入筛选
        if '索提诺比率' in high_quality.columns:
            high_quality = high_quality[high_quality['索提诺比率'] >= min_sortino_val]

        # 按回撤排序（从小到大）
        high_quality = high_quality.sort_values('最大回撤(%)', ascending=False)

        # 保存结果
        output_file = "固收+基金筛选结果.csv"
        df.to_csv(output_file, index=False, encoding='utf-8-sig')

        # 显示结果 - 按回撤排序
        print("\n" + "=" * 120)
        print(" " * 45 + "🎉 固收+基金筛选结果")
        print("=" * 120)
        print(f"\n【分析 {len(df)} 只基金，{len(high_quality)} 只符合标准】\n")
        print(f"筛选标准：夏普>={min_sharpe_val} & 索提诺>={min_sortino_val} & 回撤<{-max_dd_val}% & 收益>{min_ret_val}%")
        print()
        
        if len(high_quality) > 0:
            display_cols = ['基金代码', '基金名称', '类型', '索提诺比率', '夏普比率', '最大回撤(%)', 
                           '年化收益率(%)', '近1年收益(%)', '基金规模(亿元)', '股票仓位(%)']
            print("🏆 铁三角优质基金 TOP 20（推荐关注）：")
            print("-" * 120)
            print(high_quality[display_cols].head(20).to_string(index=False))
        else:
            print("⚠️  未找到符合铁三角标准的基金")
            print("   建议放宽条件查看全部结果\n")
        
        print("\n\n📊 全部基金按索提诺比率排序（TOP 30）：")
        print("-" * 120)
        display_cols2 = ['基金代码', '基金名称', '类型', '索提诺比率', '夏普比率', '最大回撤(%)', 
                        '年化收益率(%)', '股票仓位(%)', '基金规模(亿元)']
        print(df[display_cols2].head(30).to_string(index=False))
        
        # 统计
        print("\n\n" + "=" * 120)
        print(" " * 50 + "📈 统计摘要")
        print("=" * 120)
        print(f"分析基金总数: {len(df)}")
        if '索提诺比率' in df.columns:
            print(f"索提诺比率>=2.0: {len(df[df['索提诺比率'] >= 2.0])} 只 (卓越)")
            print(f"索提诺比率>=1.5: {len(df[df['索提诺比率'] >= 1.5])} 只 (优秀)")
            print(f"平均索提诺比率: {df['索提诺比率'].mean():.2f}")
        print(f"夏普比率>=1.5: {len(df[df['夏普比率'] >= 1.5])} 只 (优秀)")
        print(f"夏普比率>=1.0: {len(df[df['夏普比率'] >= 1.0])} 只 (良好)")
        print(f"平均夏普比率: {df['夏普比率'].mean():.2f}")
        print(f"平均最大回撤: {df['最大回撤(%)'].mean():.2f}%")
        print(f"平均年化收益: {df['年化收益率(%)'].mean():.2f}%")
        
        # 按类型统计
        print("\n按类型统计：")
        type_stats = df.groupby('类型').agg({
            '索提诺比率': 'mean',
            '夏普比率': 'mean',
            '最大回撤(%)': 'mean',
            '年化收益率(%)': 'mean',
            '基金代码': 'count'
        }).round(2)
        type_stats.columns = ['平均索提诺', '平均夏普', '平均回撤', '平均收益', '数量']
        print(type_stats.to_string())
        
        print(f"\n✅ 详细结果已保存到: {output_file}")
        print("\n💡 使用建议:")
        print("   • 优先关注索提诺比率>1.2且回撤<5%的基金")
        print("   • 索提诺比率 = (年化收益-无风险利率) / 下行标准差")
        print("   • 固收+核心：夏普>0.8 + 索提诺>1.2 + 回撤<5%")
        print("   • 可通过 'npx mutual-fund-skills <基金代码>' 进行单基金深度分析")
        print("=" * 120)
        return
    
    # 检查是否筛选股票型基金（普通模式）
    # 应用自定义参数，否则使用默认值
    min_sharpe_val = custom_params['min_sharpe'] if custom_params['min_sharpe'] else 0.5
    max_dd_val = custom_params['max_drawdown'] if custom_params['max_drawdown'] else -15.0
    min_ret_val = custom_params['min_return'] if custom_params['min_return'] else 3.0

    if '--stock' in sys.argv:
        fund_type = 'stock'
        print(f"📊 分析数量: {max_funds} 只股票类基金")
        print()

        # 从全市场获取股票型基金池
        fund_pool = get_stock_funds(max_funds=max_funds)
    else:
        print(f"📊 分析数量: {max_funds} 只基金")
        print()

        # 从全市场获取基金池（默认固收型）
        fund_pool = get_all_gushou_funds(max_funds=max_funds)
    
    if len(fund_pool) == 0:
        print("\n❌ 未获取到基金数据")
        return
    
    # 去重
    seen = set()
    unique_funds = []
    for fund in fund_pool:
        if fund[0] not in seen:
            seen.add(fund[0])
            unique_funds.append(fund)
    
    print(f"🎯 实际分析 {len(unique_funds)} 只基金\n")
    
    # 分析基金
    df = analyze_funds(unique_funds)
    
    if len(df) == 0:
        print("\n❌ 未获取到有效数据")
        return
    
    # 筛选优质基金
    high_quality = filter_quality_funds(df, min_sharpe=min_sharpe_val, max_drawdown=max_dd_val, min_return=min_ret_val)
    
    # 保存结果
    output_file = "基金筛选结果.csv"
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    # 显示结果
    print("\n" + "=" * 120)
    print(" " * 50 + "🎉 筛选结果")
    print("=" * 120)
    print(f"\n【分析 {len(df)} 只基金，{len(high_quality)} 只优质基金（夏普>={min_sharpe_val} & 回撤<{-max_dd_val}%）】\n")
    
    if len(high_quality) > 0:
        display_cols = ['基金代码', '基金名称', '类型', '夏普比率', '最大回撤(%)', 
                       '年化收益率(%)', '近1年收益(%)', '基金规模(亿元)', '股票仓位(%)']
        print("🏆 优质基金 TOP 20（推荐关注）：")
        print("-" * 120)
        print(high_quality[display_cols].head(20).to_string(index=False))
    else:
        print(f"⚠️  未找到符合标准（夏普>={min_sharpe_val} & 回撤<{-max_dd_val}%）的基金")
        print("   建议放宽条件查看全部结果\n")
    
    print("\n\n📊 全部基金按夏普比率排序（TOP 30）：")
    print("-" * 120)
    display_cols2 = ['基金代码', '基金名称', '类型', '夏普比率', '最大回撤(%)', 
                     '年化收益率(%)', '股票仓位(%)', '基金规模(亿元)']
    print(df[display_cols2].head(30).to_string(index=False))
    
    # 统计
    print("\n\n" + "=" * 120)
    print(" " * 50 + "📈 统计摘要")
    print("=" * 120)
    print(f"分析基金总数: {len(df)}")
    print(f"夏普比率>=1.0: {len(df[df['夏普比率'] >= 1.0])} 只 (优秀)")
    print(f"夏普比率>=0.5: {len(df[df['夏普比率'] >= 0.5])} 只 (良好)")
    print(f"夏普比率>=0.3: {len(df[df['夏普比率'] >= 0.3])} 只 (可接受)")
    print(f"平均夏普比率: {df['夏普比率'].mean():.2f}")
    print(f"平均最大回撤: {df['最大回撤(%)'].mean():.2f}%")
    print(f"平均年化收益: {df['年化收益率(%)'].mean():.2f}%")
    
    # 按类型统计
    print("\n按类型统计：")
    type_stats = df.groupby('类型').agg({
        '夏普比率': 'mean',
        '最大回撤(%)': 'mean',
        '年化收益率(%)': 'mean',
        '基金代码': 'count'
    }).round(2)
    type_stats.columns = ['平均夏普', '平均回撤', '平均收益', '数量']
    print(type_stats.to_string())
    
    print(f"\n✅ 详细结果已保存到: {output_file}")
    print("\n💡 使用建议:")
    print("   • 优先关注夏普比率>0.5且回撤<15%的基金")
    print("   • 可通过 'npx mutual-fund-skills <基金代码>' 进行单基金深度分析")
    print("=" * 120)


if __name__ == "__main__":
    main()
