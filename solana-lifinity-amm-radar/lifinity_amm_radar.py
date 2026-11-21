"""
Solana Lifinity Protocol Concentrated AMM & Asymmetric Spread Radar
Autonomous Mathematical Simulation Engine
Calculates Pyth oracle-guided proactive market making, dynamic spread anti-LVR defense,
and true net LP yield cashflows on Solana.
"""

from typing import Dict, Any

def calculate_dynamic_spread(
    base_spread_bps: float = 10.0,
    volatility_index_pct: float = 2.5,
    rebalancing_factor: float = 1.0
) -> Dict[str, Any]:
    """
    Computes proactive dynamic bid-ask spread on Lifinity based on Pyth oracle volatility
    and pool inventory skew.
    
    Formula:
    dynamic_spread_bps = base_spread_bps + (volatility_index_pct * 2.0) + (rebalancing_factor * 1.5)
    """
    if base_spread_bps < 0 or volatility_index_pct < 0 or rebalancing_factor < 0:
        raise ValueError("Parameters must be non-negative")
        
    volatility_markup_bps = volatility_index_pct * 2.0
    inventory_markup_bps = rebalancing_factor * 1.5
    dynamic_spread_bps = base_spread_bps + volatility_markup_bps + inventory_markup_bps
    effective_spread_pct = dynamic_spread_bps / 100.0
    
    return {
        "base_spread_bps": round(base_spread_bps, 2),
        "volatility_index_pct": round(volatility_index_pct, 2),
        "volatility_markup_bps": round(volatility_markup_bps, 2),
        "inventory_markup_bps": round(inventory_markup_bps, 2),
        "dynamic_spread_bps": round(dynamic_spread_bps, 2),
        "effective_spread_pct": round(effective_spread_pct, 4)
    }

def calculate_lvr_reduction_savings(
    pool_daily_volume_usd: float,
    standard_amm_lvr_bps: float = 25.0,
    lifinity_lvr_reduction_pct: float = 75.0,
    user_lp_share_pct: float = 1.0
) -> Dict[str, Any]:
    """
    Computes Loss-Versus-Rebalancing (LVR) savings achieved by oracle price re-centering
    over standard passive AMMs (Uniswap v3 / Raydium CLMM).
    """
    if pool_daily_volume_usd < 0 or user_lp_share_pct < 0:
        raise ValueError("Volume and share must be non-negative")
        
    standard_pool_daily_lvr_usd = pool_daily_volume_usd * (standard_amm_lvr_bps / 10000.0)
    saved_pool_daily_lvr_usd = standard_pool_daily_lvr_usd * (lifinity_lvr_reduction_pct / 100.0)
    
    user_daily_saved_lvr_usd = saved_pool_daily_lvr_usd * (user_lp_share_pct / 100.0)
    user_annual_saved_lvr_usd = user_daily_saved_lvr_usd * 365.0
    
    return {
        "pool_daily_volume_usd": round(pool_daily_volume_usd, 2),
        "standard_pool_daily_lvr_usd": round(standard_pool_daily_lvr_usd, 2),
        "saved_pool_daily_lvr_usd": round(saved_pool_daily_lvr_usd, 2),
        "user_daily_saved_lvr_usd": round(user_daily_saved_lvr_usd, 2),
        "user_annual_saved_lvr_usd": round(user_annual_saved_lvr_usd, 2)
    }

def calculate_lifinity_lp_yield(
    user_liquidity_usd: float,
    pool_daily_volume_usd: float,
    dynamic_spread_bps: float,
    pool_total_liquidity_usd: float = 1000000.0,
    user_annual_saved_lvr_usd: float = 0.0
) -> Dict[str, Any]:
    """
    Calculates combined LP yield: trading fee cashflow + LVR loss prevention alpha.
    """
    if user_liquidity_usd <= 0 or pool_total_liquidity_usd <= 0:
        raise ValueError("Liquidity must be positive")
        
    user_share_ratio = min(1.0, user_liquidity_usd / pool_total_liquidity_usd)
    pool_daily_fee_usd = pool_daily_volume_usd * (dynamic_spread_bps / 10000.0)
    user_daily_fee_usd = pool_daily_fee_usd * user_share_ratio
    user_annual_fee_usd = user_daily_fee_usd * 365.0
    
    fee_apy_pct = (user_annual_fee_usd / user_liquidity_usd) * 100.0
    lvr_alpha_apy_pct = (user_annual_saved_lvr_usd / user_liquidity_usd) * 100.0
    true_net_apy_pct = fee_apy_pct + lvr_alpha_apy_pct
    
    return {
        "user_liquidity_usd": round(user_liquidity_usd, 2),
        "user_share_pct": round(user_share_ratio * 100.0, 4),
        "pool_daily_fee_usd": round(pool_daily_fee_usd, 2),
        "user_daily_fee_usd": round(user_daily_fee_usd, 2),
        "user_annual_fee_usd": round(user_annual_fee_usd, 2),
        "fee_apy_pct": round(fee_apy_pct, 2),
        "lvr_alpha_apy_pct": round(lvr_alpha_apy_pct, 2),
        "true_net_apy_pct": round(true_net_apy_pct, 2)
    }

def evaluate_lifinity_market(
    user_liquidity_usd: float,
    pool_daily_volume_usd: float,
    base_spread_bps: float,
    volatility_index_pct: float,
    rebalancing_factor: float,
    pool_total_liquidity_usd: float = 1000000.0
) -> Dict[str, Any]:
    """
    Synthesizes spread expansion, LVR savings, and true net LP yield.
    """
    spread = calculate_dynamic_spread(base_spread_bps, volatility_index_pct, rebalancing_factor)
    user_share_pct = (user_liquidity_usd / pool_total_liquidity_usd) * 100.0
    lvr = calculate_lvr_reduction_savings(pool_daily_volume_usd, user_lp_share_pct=user_share_pct)
    yield_data = calculate_lifinity_lp_yield(
        user_liquidity_usd, pool_daily_volume_usd, spread["dynamic_spread_bps"],
        pool_total_liquidity_usd, lvr["user_annual_saved_lvr_usd"]
    )
    
    if yield_data["true_net_apy_pct"] >= 25.0:
        recommendation = "PRIME_PMM_LP_ACCUMULATION"
    elif yield_data["true_net_apy_pct"] >= 10.0:
        recommendation = "HEALTHY_ORACLE_GUIDED_YIELD"
    else:
        recommendation = "LOW_VOLATILITY_MONITORING"
        
    return {
        "recommendation": recommendation,
        "spread_data": spread,
        "lvr_savings": lvr,
        "yield_data": yield_data
    }
