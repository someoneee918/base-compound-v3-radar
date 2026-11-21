"""
Base DackieSwap Concentrated AMM v3 & Fee APR Radar
Autonomous Mathematical Simulation Engine
Calculates DackieSwap v3 concentrated tick capital multipliers, multi-tier fee yields,
and cross-DEX atomic arbitrage on Base L2.
"""

from typing import Dict, Any
import math

def calculate_v3_tick_efficiency(
    lower_tick_price: float,
    upper_tick_price: float,
    current_price: float = 1.0
) -> Dict[str, Any]:
    """
    Computes concentrated liquidity capital efficiency multiplier for DackieSwap v3 pools.
    
    Formula:
    multiplier = 1.0 / (1.0 - sqrt(lower_tick / upper_tick))
    """
    if lower_tick_price <= 0 or upper_tick_price <= lower_tick_price or current_price <= 0:
        raise ValueError("Invalid tick range or current price")
        
    ratio = lower_tick_price / upper_tick_price
    multiplier = min(500.0, 1.0 / (1.0 - math.sqrt(ratio)))
    is_in_range = lower_tick_price <= current_price <= upper_tick_price
    
    return {
        "lower_tick_price": round(lower_tick_price, 4),
        "upper_tick_price": round(upper_tick_price, 4),
        "current_price": round(current_price, 4),
        "capital_multiplier": round(multiplier, 2),
        "is_in_range": is_in_range,
        "status": "ACTIVE_FEE_HARVEST" if is_in_range else "OUT_OF_RANGE_DORMANT"
    }

def calculate_lp_fee_revenue(
    liquidity_usd: float,
    pool_daily_volume_usd: float,
    fee_tier_pct: float = 0.25,
    effective_multiplier: float = 50.48,
    pool_tvl_usd: float = 1000000.0
) -> Dict[str, Any]:
    """
    Computes daily fee cashflow and annualized return for concentrated LPs.
    """
    if liquidity_usd <= 0 or pool_daily_volume_usd < 0 or pool_tvl_usd <= 0:
        raise ValueError("Invalid parameters for fee revenue")
        
    virtual_liquidity = liquidity_usd * effective_multiplier
    effective_total_tvl = pool_tvl_usd + virtual_liquidity
    fee_share_ratio = min(1.0, virtual_liquidity / effective_total_tvl)
    
    pool_daily_fees_usd = pool_daily_volume_usd * (fee_tier_pct / 100.0)
    user_daily_fees_usd = pool_daily_fees_usd * fee_share_ratio
    user_annual_fees_usd = user_daily_fees_usd * 365.0
    fee_apy_pct = (user_annual_fees_usd / liquidity_usd) * 100.0
    
    return {
        "liquidity_usd": round(liquidity_usd, 2),
        "pool_daily_volume_usd": round(pool_daily_volume_usd, 2),
        "fee_tier_pct": round(fee_tier_pct, 4),
        "fee_share_pct": round(fee_share_ratio * 100.0, 4),
        "user_daily_fees_usd": round(user_daily_fees_usd, 2),
        "user_annual_fees_usd": round(user_annual_fees_usd, 2),
        "fee_apy_pct": round(fee_apy_pct, 2)
    }

def calculate_atomic_cross_dex_arbitrage(
    dackie_price: float,
    external_dex_price: float,
    trade_size_usd: float = 10000.0,
    base_l2_gas_usd: float = 0.04
) -> Dict[str, Any]:
    """
    Computes cross-DEX atomic arbitrage profit between DackieSwap and Aerodrome/Uniswap.
    """
    if dackie_price <= 0 or external_dex_price <= 0 or trade_size_usd <= 0:
        raise ValueError("Prices and trade size must be positive")
        
    spread_pct = abs(dackie_price - external_dex_price) / external_dex_price * 100.0
    gross_profit_usd = trade_size_usd * (spread_pct / 100.0)
    net_profit_usd = max(0.0, gross_profit_usd - base_l2_gas_usd)
    is_profitable = net_profit_usd > 1.0 and spread_pct >= 0.15
    
    return {
        "dackie_price": round(dackie_price, 4),
        "external_dex_price": round(external_dex_price, 4),
        "spread_pct": round(spread_pct, 4),
        "trade_size_usd": round(trade_size_usd, 2),
        "gross_profit_usd": round(gross_profit_usd, 2),
        "base_l2_gas_usd": round(base_l2_gas_usd, 4),
        "net_profit_usd": round(net_profit_usd, 2),
        "is_profitable": is_profitable
    }

def evaluate_dackieswap_market(
    lower_tick: float,
    upper_tick: float,
    current_price: float,
    liquidity_usd: float,
    volume: float,
    fee_tier: float,
    dackie_price: float,
    external_price: float
) -> Dict[str, Any]:
    """
    Synthesizes tick concentration efficiency, fee yield cashflow, and cross-DEX arbitrage.
    """
    eff = calculate_v3_tick_efficiency(lower_tick, upper_tick, current_price)
    fees = calculate_lp_fee_revenue(liquidity_usd, volume, fee_tier, effective_multiplier=eff["capital_multiplier"])
    arb = calculate_atomic_cross_dex_arbitrage(dackie_price, external_price, trade_size_usd=liquidity_usd)
    
    if arb["is_profitable"] and arb["net_profit_usd"] >= 20.0:
        tier = "HIGH_CONVICTION_CROSS_DEX_ARBITRAGE"
    elif eff["is_in_range"] and fees["fee_apy_pct"] >= 25.0:
        tier = "PRIME_CONCENTRATED_FEE_FARMING"
    else:
        tier = "STANDARD_TICK_MONITORING"
        
    return {
        "tier": tier,
        "efficiency": eff,
        "fees": fees,
        "arbitrage": arb
    }
