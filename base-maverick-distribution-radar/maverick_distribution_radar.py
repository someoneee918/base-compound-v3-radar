"""
Base Maverick Protocol Dynamic Distribution AMM & Directional Bin Radar
Autonomous Mathematical Simulation Engine
Calculates dynamic directional bin shift capital efficiency, fee cashflow APY,
and atomic DEX arbitrage profitability on Base L2.
"""

from typing import Dict, Any

def calculate_bin_capital_efficiency(
    bin_width_bps: float = 50.0,
    mode: str = "Mode_Right"
) -> Dict[str, Any]:
    """
    Computes concentrated bin capital efficiency and dynamic shift fee capture bonus.
    
    Modes:
    - Mode_Static: Fixed bin, no automated shifting.
    - Mode_Right: Liquidity shifts rightwards as price increases, locking profits.
    - Mode_Left: Liquidity shifts leftwards as price drops.
    - Mode_Both: Liquidity follows price in both directions, maximizing active time.
    """
    if bin_width_bps <= 0:
        raise ValueError("Bin width must be positive")
        
    width_pct = bin_width_bps / 100.0
    base_multiplier = min(500.0, 100.0 / width_pct)
    
    shift_bonuses = {
        "Mode_Static": 1.0,
        "Mode_Right": 1.35,
        "Mode_Left": 1.25,
        "Mode_Both": 1.60
    }
    
    bonus = shift_bonuses.get(mode, 1.0)
    effective_multiplier = base_multiplier * bonus
    
    return {
        "bin_width_bps": round(bin_width_bps, 2),
        "mode": mode,
        "base_multiplier": round(base_multiplier, 2),
        "mode_bonus_multiplier": round(bonus, 2),
        "effective_multiplier": round(effective_multiplier, 2)
    }

def calculate_lp_fee_cashflow(
    liquidity_usd: float,
    pool_daily_volume_usd: float,
    fee_tier_pct: float = 0.05,
    effective_multiplier: float = 270.0,
    pool_total_liquidity_usd: float = 1000000.0
) -> Dict[str, Any]:
    """
    Calculates LP daily fee earnings and annualized yield based on concentrated bin density.
    """
    if liquidity_usd <= 0 or pool_daily_volume_usd < 0 or pool_total_liquidity_usd <= 0:
        raise ValueError("Invalid parameters for fee calculation")
        
    virtual_liquidity = liquidity_usd * effective_multiplier
    effective_pool_liq = pool_total_liquidity_usd + virtual_liquidity
    fee_share_ratio = min(1.0, virtual_liquidity / effective_pool_liq)
    
    total_pool_daily_fees = pool_daily_volume_usd * (fee_tier_pct / 100.0)
    lp_daily_fees_usd = total_pool_daily_fees * fee_share_ratio
    annual_fees_usd = lp_daily_fees_usd * 365.0
    lp_fee_apy_pct = (annual_fees_usd / liquidity_usd) * 100.0
    
    return {
        "liquidity_usd": round(liquidity_usd, 2),
        "pool_daily_volume_usd": round(pool_daily_volume_usd, 2),
        "fee_tier_pct": round(fee_tier_pct, 4),
        "fee_share_pct": round(fee_share_ratio * 100.0, 4),
        "lp_daily_fees_usd": round(lp_daily_fees_usd, 2),
        "annual_fees_usd": round(annual_fees_usd, 2),
        "lp_fee_apy_pct": round(lp_fee_apy_pct, 2)
    }

def calculate_bin_dex_arbitrage(
    maverick_bin_price: float,
    external_dex_price: float,
    trade_size_usd: float,
    base_l2_gas_usd: float = 0.04
) -> Dict[str, Any]:
    """
    Calculates gross and net profit for atomic DEX arbitrage against Maverick active bins.
    """
    if maverick_bin_price <= 0 or external_dex_price <= 0 or trade_size_usd <= 0:
        raise ValueError("Prices and trade size must be positive")
        
    price_diff_pct = abs(maverick_bin_price - external_dex_price) / external_dex_price * 100.0
    gross_arbitrage_profit_usd = trade_size_usd * (price_diff_pct / 100.0)
    net_arbitrage_profit_usd = max(0.0, gross_arbitrage_profit_usd - base_l2_gas_usd)
    is_profitable = net_arbitrage_profit_usd > 1.0 and price_diff_pct >= 0.10
    
    return {
        "maverick_bin_price": round(maverick_bin_price, 4),
        "external_dex_price": round(external_dex_price, 4),
        "price_diff_pct": round(price_diff_pct, 4),
        "trade_size_usd": round(trade_size_usd, 2),
        "gross_arbitrage_profit_usd": round(gross_arbitrage_profit_usd, 2),
        "base_l2_gas_usd": round(base_l2_gas_usd, 4),
        "net_arbitrage_profit_usd": round(net_arbitrage_profit_usd, 2),
        "is_profitable": is_profitable
    }

def evaluate_maverick_market(
    liquidity_usd: float,
    pool_daily_volume_usd: float,
    bin_width_bps: float,
    mode: str,
    maverick_price: float,
    external_price: float
) -> Dict[str, Any]:
    """
    Synthesizes capital efficiency, fee yield, and atomic arbitrage signals.
    """
    eff = calculate_bin_capital_efficiency(bin_width_bps, mode)
    fees = calculate_lp_fee_cashflow(
        liquidity_usd, pool_daily_volume_usd, effective_multiplier=eff["effective_multiplier"]
    )
    arb = calculate_bin_dex_arbitrage(maverick_price, external_price, trade_size_usd=10000.0)
    
    if arb["is_profitable"] and arb["net_arbitrage_profit_usd"] >= 20.0:
        status = "HIGH_CONVICTION_ATOMIC_ARBITRAGE"
    elif fees["lp_fee_apy_pct"] >= 25.0:
        status = "PRIME_DYNAMIC_FEE_FARMING"
    else:
        status = "MODERATE_YIELD_MONITORING"
        
    return {
        "status": status,
        "efficiency": eff,
        "fee_cashflow": fees,
        "arbitrage": arb
    }
