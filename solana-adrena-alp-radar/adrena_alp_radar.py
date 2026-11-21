"""
Solana Adrena Protocol (ADX) Multi-Asset ALP Liquidity & Funding Carry Radar
Autonomous Mathematical Simulation Engine
Calculates ALP target weight dynamic rebalancing fees, skew-based trader funding velocity,
and ALP real yield staking APR on Solana.
"""

from typing import Dict, Any

def calculate_alp_rebalancing_fee(
    deposit_amount_usd: float,
    actual_weight_pct: float,
    target_weight_pct: float = 35.0,
    base_fee_bps: float = 15.0,
    slope: float = 4.0
) -> Dict[str, Any]:
    """
    Computes dynamic deposit fee based on ALP pool asset skew.
    
    Formula:
    delta = actual_weight - target_weight
    If delta < 0: fee discounted down to 0.0 bps (free deposit for rebalancing).
    If delta > 0: fee surcharge added.
    """
    if deposit_amount_usd <= 0 or actual_weight_pct < 0 or target_weight_pct <= 0:
        raise ValueError("Invalid parameters for ALP fee calculation")
        
    delta_pct = actual_weight_pct - target_weight_pct
    
    if delta_pct <= 0:
        fee_bps = max(0.0, base_fee_bps + (delta_pct * slope))
        status = "ZERO_FEE_REBALANCE_BONUS" if fee_bps == 0.0 else "DISCOUNTED_REBALANCE"
    else:
        fee_bps = base_fee_bps + (delta_pct * slope)
        status = "OVERWEIGHT_SURCHARGE"
        
    fee_cost_usd = deposit_amount_usd * (fee_bps / 10000.0)
    
    return {
        "deposit_amount_usd": round(deposit_amount_usd, 2),
        "actual_weight_pct": round(actual_weight_pct, 2),
        "target_weight_pct": round(target_weight_pct, 2),
        "delta_pct": round(delta_pct, 2),
        "fee_bps": round(fee_bps, 2),
        "fee_cost_usd": round(fee_cost_usd, 2),
        "status": status
    }

def calculate_skew_funding_rate(
    long_oi_usd: float,
    short_oi_usd: float,
    pool_liquidity_usd: float = 10000000.0,
    velocity_factor: float = 0.05
) -> Dict[str, Any]:
    """
    Computes continuous funding rate velocity driven by open interest skew.
    """
    if pool_liquidity_usd <= 0 or long_oi_usd < 0 or short_oi_usd < 0:
        raise ValueError("Invalid parameters for funding rate")
        
    skew_usd = long_oi_usd - short_oi_usd
    skew_ratio = skew_usd / pool_liquidity_usd
    hourly_funding_bps = skew_ratio * velocity_factor * 100.0
    daily_funding_bps = hourly_funding_bps * 24.0
    annual_funding_apr_pct = (daily_funding_bps * 365.0) / 100.0
    
    return {
        "long_oi_usd": round(long_oi_usd, 2),
        "short_oi_usd": round(short_oi_usd, 2),
        "skew_usd": round(skew_usd, 2),
        "skew_ratio_pct": round(skew_ratio * 100.0, 2),
        "hourly_funding_bps": round(hourly_funding_bps, 4),
        "annual_funding_apr_pct": round(annual_funding_apr_pct, 2)
    }

def calculate_alp_real_yield_apr(
    user_deposit_usd: float,
    pool_daily_volume_usd: float,
    trading_fee_bps: float = 8.0,
    protocol_revenue_share_pct: float = 70.0,
    pool_alp_tvl_usd: float = 8000000.0
) -> Dict[str, Any]:
    """
    Computes user daily cashflow and annualized return for staking ALP tokens.
    """
    if user_deposit_usd <= 0 or pool_alp_tvl_usd <= 0 or pool_daily_volume_usd < 0:
        raise ValueError("Invalid parameters for ALP yield")
        
    pool_daily_trading_fees_usd = pool_daily_volume_usd * (trading_fee_bps / 10000.0)
    alp_daily_pool_usd = pool_daily_trading_fees_usd * (protocol_revenue_share_pct / 100.0)
    
    user_share_ratio = min(1.0, user_deposit_usd / pool_alp_tvl_usd)
    user_daily_income_usd = alp_daily_pool_usd * user_share_ratio
    user_annual_income_usd = user_daily_income_usd * 365.0
    alp_staking_apr_pct = (user_annual_income_usd / user_deposit_usd) * 100.0
    
    return {
        "user_deposit_usd": round(user_deposit_usd, 2),
        "pool_daily_volume_usd": round(pool_daily_volume_usd, 2),
        "pool_daily_trading_fees_usd": round(pool_daily_trading_fees_usd, 2),
        "user_share_pct": round(user_share_ratio * 100.0, 4),
        "user_daily_income_usd": round(user_daily_income_usd, 2),
        "user_annual_income_usd": round(user_annual_income_usd, 2),
        "alp_staking_apr_pct": round(alp_staking_apr_pct, 2)
    }

def evaluate_adrena_market(
    deposit_usd: float,
    actual_weight: float,
    target_weight: float,
    long_oi: float,
    short_oi: float,
    volume: float
) -> Dict[str, Any]:
    """
    Synthesizes rebalance fee savings, funding carry velocity, and ALP real yields.
    """
    fee = calculate_alp_rebalancing_fee(deposit_usd, actual_weight, target_weight)
    funding = calculate_skew_funding_rate(long_oi, short_oi)
    yield_data = calculate_alp_real_yield_apr(deposit_usd, volume)
    
    if fee["fee_bps"] == 0.0 and yield_data["alp_staking_apr_pct"] >= 20.0:
        tier = "PRIME_ZERO_FEE_ALP_ACCUMULATION"
    elif yield_data["alp_staking_apr_pct"] >= 15.0:
        tier = "STRONG_ALP_REAL_YIELD"
    else:
        tier = "STANDARD_PERPS_MONITORING"
        
    return {
        "tier": tier,
        "rebalancing_fee": fee,
        "skew_funding": funding,
        "alp_yield": yield_data
    }
