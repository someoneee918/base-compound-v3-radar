"""
Solana Flash Trade Multi-Asset FLP Liquidity Pool & Funding Rate Radar
Autonomous Mathematical Simulation Engine
Calculates FLP target weight dynamic entry/exit fees, trader borrow interest rates,
and FLP real staking APR on Solana.
"""

from typing import Dict, Any

def calculate_flp_dynamic_fee(
    deposit_amount_usd: float,
    actual_weight_pct: float,
    target_weight_pct: float = 40.0,
    base_fee_bps: float = 20.0,
    penalty_slope: float = 5.0
) -> Dict[str, Any]:
    """
    Computes dynamic deposit fee based on FLP pool asset balance relative to target weight.
    
    Formula:
    weight_delta = actual_weight - target_weight
    If actual < target (underweight): fee is discounted (down to min 5.0 bps).
    If actual > target (overweight): fee has slippage penalty added.
    """
    if deposit_amount_usd <= 0 or actual_weight_pct < 0 or target_weight_pct <= 0:
        raise ValueError("Invalid parameters for dynamic fee calculation")
        
    weight_delta_pct = actual_weight_pct - target_weight_pct
    
    if weight_delta_pct <= 0:
        # Rebalancing reward discount
        fee_bps = max(5.0, base_fee_bps + (weight_delta_pct * penalty_slope))
        action_type = "REBALANCING_DEPOSIT_DISCOUNT"
    else:
        # Overweight penalty
        fee_bps = base_fee_bps + (weight_delta_pct * penalty_slope)
        action_type = "OVERWEIGHT_PENALTY_SURGE"
        
    fee_cost_usd = deposit_amount_usd * (fee_bps / 10000.0)
    
    return {
        "deposit_amount_usd": round(deposit_amount_usd, 2),
        "actual_weight_pct": round(actual_weight_pct, 2),
        "target_weight_pct": round(target_weight_pct, 2),
        "weight_delta_pct": round(weight_delta_pct, 2),
        "fee_bps": round(fee_bps, 2),
        "fee_cost_usd": round(fee_cost_usd, 2),
        "action_type": action_type
    }

def calculate_trader_borrow_fee(
    position_size_usd: float,
    pool_utilization_pct: float,
    base_hourly_rate_bps: float = 0.5
) -> Dict[str, Any]:
    """
    Computes hourly and annualized borrow fees charged to perpetual traders.
    """
    if position_size_usd <= 0 or pool_utilization_pct < 0 or pool_utilization_pct > 100.0:
        raise ValueError("Invalid position or utilization")
        
    hourly_rate_bps = base_hourly_rate_bps * (1.0 + (pool_utilization_pct / 100.0) * 2.0)
    hourly_fee_usd = position_size_usd * (hourly_rate_bps / 10000.0)
    daily_fee_usd = hourly_fee_usd * 24.0
    annual_fee_usd = daily_fee_usd * 365.0
    borrow_apr_pct = (annual_fee_usd / position_size_usd) * 100.0
    
    return {
        "position_size_usd": round(position_size_usd, 2),
        "pool_utilization_pct": round(pool_utilization_pct, 2),
        "hourly_rate_bps": round(hourly_rate_bps, 4),
        "hourly_fee_usd": round(hourly_fee_usd, 2),
        "daily_fee_usd": round(daily_fee_usd, 2),
        "annual_fee_usd": round(annual_fee_usd, 2),
        "borrow_apr_pct": round(borrow_apr_pct, 2)
    }

def calculate_flp_staking_apr(
    user_flp_deposit_usd: float,
    pool_daily_volume_usd: float,
    trading_fee_bps: float = 6.0,
    flp_fee_share_pct: float = 70.0,
    pool_flp_tvl_usd: float = 5000000.0
) -> Dict[str, Any]:
    """
    Computes FLP liquidity provider daily real yield cashflow and staking APR.
    """
    if user_flp_deposit_usd <= 0 or pool_flp_tvl_usd <= 0 or pool_daily_volume_usd < 0:
        raise ValueError("Invalid parameters for FLP staking calculation")
        
    pool_daily_trading_fees_usd = pool_daily_volume_usd * (trading_fee_bps / 10000.0)
    flp_daily_fee_pool_usd = pool_daily_trading_fees_usd * (flp_fee_share_pct / 100.0)
    
    user_share_ratio = min(1.0, user_flp_deposit_usd / pool_flp_tvl_usd)
    user_daily_income_usd = flp_daily_fee_pool_usd * user_share_ratio
    user_annual_income_usd = user_daily_income_usd * 365.0
    flp_staking_apr_pct = (user_annual_income_usd / user_flp_deposit_usd) * 100.0
    
    return {
        "user_flp_deposit_usd": round(user_flp_deposit_usd, 2),
        "pool_daily_volume_usd": round(pool_daily_volume_usd, 2),
        "pool_daily_trading_fees_usd": round(pool_daily_trading_fees_usd, 2),
        "user_share_pct": round(user_share_ratio * 100.0, 4),
        "user_daily_income_usd": round(user_daily_income_usd, 2),
        "user_annual_income_usd": round(user_annual_income_usd, 2),
        "flp_staking_apr_pct": round(flp_staking_apr_pct, 2)
    }

def evaluate_flash_trade_market(
    deposit_amount_usd: float,
    actual_weight: float,
    target_weight: float,
    pool_daily_volume_usd: float,
    pool_utilization_pct: float
) -> Dict[str, Any]:
    """
    Synthesizes pool rebalancing incentives, trader borrow costs, and real yield APR.
    """
    dynamic_fee = calculate_flp_dynamic_fee(deposit_amount_usd, actual_weight, target_weight)
    borrow = calculate_trader_borrow_fee(position_size_usd=25000.0, pool_utilization_pct=pool_utilization_pct)
    staking = calculate_flp_staking_apr(deposit_amount_usd, pool_daily_volume_usd)
    
    if dynamic_fee["action_type"] == "REBALANCING_DEPOSIT_DISCOUNT" and staking["flp_staking_apr_pct"] >= 20.0:
        tier = "PRIME_FLP_REBALANCE_ACCUMULATION"
    elif staking["flp_staking_apr_pct"] >= 15.0:
        tier = "STRONG_REAL_YIELD_FARMING"
    else:
        tier = "STANDARD_POOL_MONITORING"
        
    return {
        "tier": tier,
        "dynamic_fee": dynamic_fee,
        "trader_borrow": borrow,
        "flp_staking": staking
    }
