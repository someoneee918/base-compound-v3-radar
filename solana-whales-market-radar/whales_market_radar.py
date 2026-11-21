"""
Solana Whales Market Pre-Market OTC Collateral & Default Slashing Radar
Autonomous Mathematical Simulation Engine
Calculates Whales Market pre-TGE escrow collateralization, seller default slashing seizures
(100% collateral bonus), and implied FDV basis arbitrage on Solana.
"""

from typing import Dict, Any

def calculate_premarket_implied_fdv(
    premarket_price_usd: float,
    total_supply: float = 1000000000.0,
    comparable_live_fdv_usd: float = 500000000.0
) -> Dict[str, Any]:
    """
    Computes implied fully diluted valuation (FDV) and basis spread vs comparable live benchmarks.
    
    Formula:
    implied_fdv = premarket_price * total_supply
    fdv_basis_pct = ((implied_fdv - comparable_live_fdv) / comparable_live_fdv) * 100.0
    """
    if premarket_price_usd <= 0 or total_supply <= 0 or comparable_live_fdv_usd <= 0:
        raise ValueError("Invalid parameters for implied FDV calculation")
        
    implied_fdv_usd = premarket_price_usd * total_supply
    fdv_basis_pct = ((implied_fdv_usd - comparable_live_fdv_usd) / comparable_live_fdv_usd) * 100.0
    
    if fdv_basis_pct >= 30.0:
        recommendation = "OVERVALUED_HEDGE_SHORT_BASIS"
    elif fdv_basis_pct <= -20.0:
        recommendation = "UNDERVALUED_BUY_DISCOUNT_ALLOCATION"
    else:
        recommendation = "FAIR_VALUATION_RANGE"
        
    return {
        "premarket_price_usd": round(premarket_price_usd, 4),
        "total_supply": round(total_supply, 0),
        "implied_fdv_usd": round(implied_fdv_usd, 2),
        "comparable_live_fdv_usd": round(comparable_live_fdv_usd, 2),
        "fdv_basis_pct": round(fdv_basis_pct, 2),
        "recommendation": recommendation
    }

def calculate_seller_default_slashing_payout(
    order_size_usd: float,
    seller_collateral_ratio_pct: float = 100.0,
    protocol_fee_pct: float = 2.5
) -> Dict[str, Any]:
    """
    Computes buyer compensation and net windfall profit if the seller defaults past the 24h TGE cutoff.
    """
    if order_size_usd <= 0 or seller_collateral_ratio_pct <= 0:
        raise ValueError("Order size and collateral ratio must be positive")
        
    seller_collateral_usd = order_size_usd * (seller_collateral_ratio_pct / 100.0)
    protocol_cut_usd = seller_collateral_usd * (protocol_fee_pct / 100.0)
    buyer_slashed_collateral_received = seller_collateral_usd - protocol_cut_usd
    total_buyer_payout_usd = order_size_usd + buyer_slashed_collateral_received
    net_windfall_profit_usd = buyer_slashed_collateral_received
    windfall_roi_pct = (net_windfall_profit_usd / order_size_usd) * 100.0
    
    return {
        "order_size_usd": round(order_size_usd, 2),
        "seller_collateral_usd": round(seller_collateral_usd, 2),
        "protocol_cut_usd": round(protocol_cut_usd, 2),
        "buyer_slashed_collateral_received": round(buyer_slashed_collateral_received, 2),
        "total_buyer_payout_usd": round(total_buyer_payout_usd, 2),
        "net_windfall_profit_usd": round(net_windfall_profit_usd, 2),
        "windfall_roi_pct": round(windfall_roi_pct, 2)
    }

def calculate_otc_settlement_timeline(
    tge_timestamp: float,
    current_timestamp: float,
    settlement_window_hours: float = 24.0
) -> Dict[str, Any]:
    """
    Computes hours remaining in the TGE settlement window and flags default status.
    """
    if current_timestamp < tge_timestamp:
        return {
            "hours_elapsed": 0.0,
            "hours_remaining": settlement_window_hours,
            "is_defaulted": False,
            "status": "PRE_TGE_LOCKED"
        }
        
    hours_elapsed = (current_timestamp - tge_timestamp) / 3600.0
    hours_remaining = max(0.0, settlement_window_hours - hours_elapsed)
    is_defaulted = hours_remaining == 0.0
    
    status = "DEFAULT_SLASH_CLAIMABLE" if is_defaulted else "ACTIVE_SETTLEMENT_WINDOW"
    
    return {
        "hours_elapsed": round(hours_elapsed, 2),
        "hours_remaining": round(hours_remaining, 2),
        "is_defaulted": is_defaulted,
        "status": status
    }

def evaluate_whales_market_opportunity(
    premarket_price: float,
    order_size_usd: float,
    tge_time: float,
    current_time: float,
    comparable_fdv: float = 500000000.0
) -> Dict[str, Any]:
    """
    Synthesizes implied valuation basis, settlement timeline, and default compensation.
    """
    fdv = calculate_premarket_implied_fdv(premarket_price, comparable_live_fdv_usd=comparable_fdv)
    default = calculate_seller_default_slashing_payout(order_size_usd)
    timeline = calculate_otc_settlement_timeline(tge_time, current_time)
    
    if timeline["is_defaulted"]:
        tier = "IMMEDIATE_COLLATERAL_SLASH_EXECUTION"
    elif fdv["recommendation"] == "UNDERVALUED_BUY_DISCOUNT_ALLOCATION":
        tier = "PRIME_OTC_DISCOUNT_ACCUMULATION"
    else:
        tier = "STANDARD_PREMARKET_MONITORING"
        
    return {
        "tier": tier,
        "fdv_metrics": fdv,
        "slashing_payout": default,
        "timeline": timeline
    }
