"""
Solana BlazeStake (bSOL) Fair NAV & Gauge Directed Stake Radar
Autonomous Mathematical Simulation Engine
Calculates bSOL true fair NAV backing vs secondary DEX market discount arbitrage,
custom validator gauge directed stake yields, and epoch redemption sentinels on Solana.
"""

from typing import Dict, Any

def calculate_bsol_nav_accretion(
    staked_sol_reserves: float,
    bsol_supply: float,
    network_staking_apy_pct: float = 7.20
) -> Dict[str, Any]:
    """
    Computes bSOL fair NAV per token and forward accretion schedule based on Solana staking rewards.
    
    Formula:
    fair_nav_sol = staked_sol_reserves / bsol_supply
    daily_rate = (1 + APY)^(1/365) - 1
    projected_nav_1y = fair_nav_sol * (1 + APY/100)
    """
    if staked_sol_reserves <= 0 or bsol_supply <= 0:
        raise ValueError("Reserves and supply must be positive")
        
    fair_nav_sol = staked_sol_reserves / bsol_supply
    daily_rate = ((1.0 + (network_staking_apy_pct / 100.0)) ** (1.0 / 365.0)) - 1.0
    projected_nav_30d = fair_nav_sol * (1.0 + (daily_rate * 30.0))
    projected_nav_1y = fair_nav_sol * (1.0 + (network_staking_apy_pct / 100.0))
    
    return {
        "staked_sol_reserves": round(staked_sol_reserves, 4),
        "bsol_supply": round(bsol_supply, 4),
        "fair_nav_sol": round(fair_nav_sol, 6),
        "network_staking_apy_pct": round(network_staking_apy_pct, 2),
        "daily_accretion_bps": round(daily_rate * 10000.0, 4),
        "projected_nav_30d": round(projected_nav_30d, 6),
        "projected_nav_1y": round(projected_nav_1y, 6)
    }

def calculate_secondary_dex_discount_arbitrage(
    fair_nav_sol: float,
    secondary_dex_price_sol: float,
    trade_size_sol: float = 50.0,
    sol_price_usd: float = 180.0
) -> Dict[str, Any]:
    """
    Computes atomic or delayed unstake arbitrage profit when bSOL trades at a discount on DEXs.
    """
    if fair_nav_sol <= 0 or secondary_dex_price_sol <= 0 or trade_size_sol <= 0:
        raise ValueError("Prices and trade size must be positive")
        
    discount_sol = max(0.0, fair_nav_sol - secondary_dex_price_sol)
    discount_pct = (discount_sol / fair_nav_sol) * 100.0
    
    if secondary_dex_price_sol >= fair_nav_sol:
        return {
            "fair_nav_sol": round(fair_nav_sol, 6),
            "secondary_dex_price_sol": round(secondary_dex_price_sol, 6),
            "discount_pct": 0.0,
            "gross_profit_sol": 0.0,
            "net_profit_usd": 0.0,
            "roi_pct": 0.0,
            "is_profitable": False
        }
        
    bsol_acquired = trade_size_sol / secondary_dex_price_sol
    sol_redeemed = bsol_acquired * fair_nav_sol
    gross_profit_sol = sol_redeemed - trade_size_sol
    gross_profit_usd = gross_profit_sol * sol_price_usd
    roi_pct = (gross_profit_sol / trade_size_sol) * 100.0
    is_profitable = discount_pct >= 0.20 and gross_profit_usd >= 10.0
    
    return {
        "fair_nav_sol": round(fair_nav_sol, 6),
        "secondary_dex_price_sol": round(secondary_dex_price_sol, 6),
        "discount_pct": round(discount_pct, 4),
        "bsol_acquired": round(bsol_acquired, 4),
        "sol_redeemed": round(sol_redeemed, 4),
        "gross_profit_sol": round(gross_profit_sol, 4),
        "net_profit_usd": round(gross_profit_usd, 2),
        "roi_pct": round(roi_pct, 2),
        "is_profitable": is_profitable
    }

def calculate_validator_gauge_yield(
    blze_votes: float,
    total_gauge_votes: float = 10000000.0,
    epoch_sol_directed: float = 50000.0,
    validator_mev_commission_pct: float = 0.0
) -> Dict[str, Any]:
    """
    Computes stake directed to community validators via BLZE gauge voting.
    """
    if blze_votes <= 0 or total_gauge_votes <= 0:
        raise ValueError("Votes must be positive")
        
    vote_share_ratio = min(1.0, blze_votes / total_gauge_votes)
    sol_directed = epoch_sol_directed * vote_share_ratio
    
    return {
        "blze_votes": round(blze_votes, 2),
        "total_gauge_votes": round(total_gauge_votes, 2),
        "vote_share_pct": round(vote_share_ratio * 100.0, 4),
        "sol_directed": round(sol_directed, 2),
        "validator_mev_commission_pct": round(validator_mev_commission_pct, 2)
    }

def evaluate_blazestake_market(
    reserves: float,
    supply: float,
    secondary_price: float,
    trade_size_sol: float
) -> Dict[str, Any]:
    """
    Synthesizes NAV accretion, discount arbitrage signals, and gauge stake mechanics.
    """
    nav = calculate_bsol_nav_accretion(reserves, supply)
    arb = calculate_secondary_dex_discount_arbitrage(nav["fair_nav_sol"], secondary_price, trade_size_sol)
    gauge = calculate_validator_gauge_yield(blze_votes=100000.0)
    
    if arb["is_profitable"] and arb["discount_pct"] >= 0.40:
        tier = "HIGH_CONVICTION_BSOL_ARBITRAGE"
    elif arb["is_profitable"]:
        tier = "MODERATE_DISCOUNT_ACCUMULATION"
    else:
        tier = "STANDARD_LST_ACCRETION"
        
    return {
        "tier": tier,
        "nav": nav,
        "arbitrage": arb,
        "gauge": gauge
    }
