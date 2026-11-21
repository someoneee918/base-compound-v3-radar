"""
Base Alien Base Area 51 Concentrated Liquidity & StableSwap Radar
Autonomous Mathematical Simulation Engine
Calculates Area 51 concentrated tick capital efficiency, StableSwap low-slippage amplification curves,
and atomic DEX arbitrage on Base L2.
"""

from typing import Dict, Any
import math

def calculate_area51_concentrated_efficiency(
    lower_tick_price: float,
    upper_tick_price: float,
    current_price: float = 1.0
) -> Dict[str, Any]:
    """
    Computes concentrated liquidity capital efficiency multiplier for Area 51 pools.
    
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

def calculate_stableswap_slippage(
    trade_amount_usd: float,
    pool_liquidity_usd: float,
    amplification_coefficient: float = 100.0
) -> Dict[str, Any]:
    """
    Computes StableSwap amplification-curve slippage and savings vs constant-product AMM.
    """
    if trade_amount_usd <= 0 or pool_liquidity_usd <= 0 or amplification_coefficient <= 0:
        raise ValueError("Parameters must be positive")
        
    trade_ratio = trade_amount_usd / pool_liquidity_usd
    # StableSwap slippage is compressed by amplification factor A
    slippage_pct = (trade_ratio * (100.0 / amplification_coefficient)) * 0.10
    slippage_cost_usd = trade_amount_usd * (slippage_pct / 100.0)
    
    # Standard Uniswap v2 constant-product slippage for comparison
    v2_slippage_pct = trade_ratio * 100.0
    v2_slippage_cost_usd = trade_amount_usd * (v2_slippage_pct / 100.0)
    slippage_savings_usd = max(0.0, v2_slippage_cost_usd - slippage_cost_usd)
    
    return {
        "trade_amount_usd": round(trade_amount_usd, 2),
        "pool_liquidity_usd": round(pool_liquidity_usd, 2),
        "amplification_coefficient": round(amplification_coefficient, 2),
        "slippage_pct": round(slippage_pct, 4),
        "slippage_cost_usd": round(slippage_cost_usd, 2),
        "v2_slippage_cost_usd": round(v2_slippage_cost_usd, 2),
        "slippage_savings_usd": round(slippage_savings_usd, 2)
    }

def calculate_atomic_dex_arbitrage(
    alien_price: float,
    aerodrome_price: float,
    trade_size_usd: float = 10000.0,
    base_l2_gas_usd: float = 0.04
) -> Dict[str, Any]:
    """
    Computes cross-DEX atomic arbitrage between Alien Base and Aerodrome/Uniswap.
    """
    if alien_price <= 0 or aerodrome_price <= 0 or trade_size_usd <= 0:
        raise ValueError("Prices and trade size must be positive")
        
    spread_pct = abs(alien_price - aerodrome_price) / aerodrome_price * 100.0
    gross_profit_usd = trade_size_usd * (spread_pct / 100.0)
    net_profit_usd = max(0.0, gross_profit_usd - base_l2_gas_usd)
    is_profitable = net_profit_usd > 1.0 and spread_pct >= 0.15
    
    return {
        "alien_price": round(alien_price, 4),
        "aerodrome_price": round(aerodrome_price, 4),
        "spread_pct": round(spread_pct, 4),
        "trade_size_usd": round(trade_size_usd, 2),
        "gross_profit_usd": round(gross_profit_usd, 2),
        "base_l2_gas_usd": round(base_l2_gas_usd, 4),
        "net_profit_usd": round(net_profit_usd, 2),
        "is_profitable": is_profitable
    }

def evaluate_alien_base_market(
    lower_tick: float,
    upper_tick: float,
    current_price: float,
    trade_amount_usd: float,
    alien_price: float,
    aerodrome_price: float
) -> Dict[str, Any]:
    """
    Synthesizes tick concentration, StableSwap efficiency, and cross-DEX arbitrage.
    """
    conc = calculate_area51_concentrated_efficiency(lower_tick, upper_tick, current_price)
    stable = calculate_stableswap_slippage(trade_amount_usd, pool_liquidity_usd=1000000.0)
    arb = calculate_atomic_dex_arbitrage(alien_price, aerodrome_price, trade_size_usd=trade_amount_usd)
    
    if arb["is_profitable"] and arb["net_profit_usd"] >= 25.0:
        tier = "HIGH_CONVICTION_CROSS_DEX_ARBITRAGE"
    elif conc["is_in_range"] and conc["capital_multiplier"] >= 40.0:
        tier = "PRIME_AREA51_TICK_FARMING"
    else:
        tier = "STANDARD_LIQUIDITY_MONITOR"
        
    return {
        "tier": tier,
        "concentration": conc,
        "stableswap": stable,
        "arbitrage": arb
    }
