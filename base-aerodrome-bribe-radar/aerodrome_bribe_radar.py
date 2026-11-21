"""
Base Aerodrome Finance veAERO Gauge Voting & Bribe ROI Radar
Autonomous Mathematical Simulation Engine
Calculates weekly epoch bribe yields, veAERO voter APR, and protocol emission multipliers
on Base's flagship liquidity engine.
"""

from typing import Dict, Any

def calculate_voter_bribe_apr(
    ve_aero_votes: float,
    gauge_total_votes: float,
    total_bribes_usd: float,
    aero_price_usd: float = 1.20
) -> Dict[str, Any]:
    """
    Computes annualized bribe APR for veAERO lockers voting on a specific pool gauge.
    
    Formula:
    vote_share = ve_aero_votes / gauge_total_votes
    weekly_payout = total_bribes_usd * vote_share
    annual_payout = weekly_payout * 52.0
    voter_value = ve_aero_votes * aero_price_usd
    voter_apr = (annual_payout / voter_value) * 100.0
    """
    if ve_aero_votes < 0 or gauge_total_votes <= 0 or aero_price_usd <= 0:
        raise ValueError("Invalid parameters for voter APR calculation")
        
    vote_share_ratio = min(1.0, ve_aero_votes / gauge_total_votes)
    user_weekly_bribe_usd = total_bribes_usd * vote_share_ratio
    user_annual_bribe_usd = user_weekly_bribe_usd * 52.0
    
    ve_aero_value_usd = ve_aero_votes * aero_price_usd
    voter_apr_pct = (user_annual_bribe_usd / ve_aero_value_usd * 100.0) if ve_aero_value_usd > 0 else 0.0
    
    bribe_per_1k_votes_usd = (total_bribes_usd / gauge_total_votes) * 1000.0
    
    return {
        "ve_aero_votes": round(ve_aero_votes, 2),
        "gauge_total_votes": round(gauge_total_votes, 2),
        "total_bribes_usd": round(total_bribes_usd, 2),
        "vote_share_pct": round(vote_share_ratio * 100.0, 4),
        "user_weekly_bribe_usd": round(user_weekly_bribe_usd, 2),
        "user_annual_bribe_usd": round(user_annual_bribe_usd, 2),
        "ve_aero_value_usd": round(ve_aero_value_usd, 2),
        "voter_apr_pct": round(voter_apr_pct, 2),
        "bribe_per_1k_votes_usd": round(bribe_per_1k_votes_usd, 4)
    }

def calculate_protocol_emission_multiplier(
    bribe_amount_usd: float,
    votes_attracted: float,
    epoch_total_votes: float = 100000000.0,
    weekly_aero_emissions: float = 10000000.0,
    aero_price_usd: float = 1.20
) -> Dict[str, Any]:
    """
    Computes protocol capital efficiency multiplier (dollar value of emissions directed
    per dollar of bribe deposited into the gauge).
    """
    if bribe_amount_usd <= 0 or epoch_total_votes <= 0:
        raise ValueError("Bribe and epoch votes must be positive")
        
    gauge_vote_share = min(1.0, votes_attracted / epoch_total_votes)
    aero_emissions_directed = weekly_aero_emissions * gauge_vote_share
    emission_value_usd = aero_emissions_directed * aero_price_usd
    
    multiplier = emission_value_usd / bribe_amount_usd
    net_subsidy_profit_usd = emission_value_usd - bribe_amount_usd
    
    return {
        "bribe_amount_usd": round(bribe_amount_usd, 2),
        "votes_attracted": round(votes_attracted, 2),
        "gauge_vote_share_pct": round(gauge_vote_share * 100.0, 4),
        "aero_emissions_directed": round(aero_emissions_directed, 2),
        "emission_value_usd": round(emission_value_usd, 2),
        "multiplier": round(multiplier, 2),
        "net_subsidy_profit_usd": round(net_subsidy_profit_usd, 2)
    }

def evaluate_gauge_opportunity(
    voter_apr_pct: float,
    emission_multiplier: float
) -> Dict[str, Any]:
    """
    Synthesizes voter yield and protocol bribe efficiency.
    """
    if voter_apr_pct >= 40.0 and emission_multiplier >= 1.5:
        tier = "HYPER_EFFICIENT_BRIBE_OPPORTUNITY"
    elif voter_apr_pct >= 20.0:
        tier = "STRONG_YIELD_GAUGE"
    elif voter_apr_pct >= 10.0:
        tier = "MODERATE_GAUGE_YIELD"
    else:
        tier = "DILUTED_VOTE_MONITOR"
        
    return {
        "tier": tier,
        "voter_apr_pct": voter_apr_pct,
        "emission_multiplier": emission_multiplier
    }
