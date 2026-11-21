"""
Solana Dual Finance Staking Options & Dual Investment Product (DIP) Radar
Mathematical modeling engine for Dual Finance structured products on Solana: Dual Investment Products (Sell-High / Buy-Low DIP), Staking Options (SO) intrinsic valuation, and treasury dilution prevention.
"""

import math
from typing import Dict, Any, List

def calculate_dip_yield_and_assignment_outcomes(
    deposit_asset: str, # "SOL" or "USDC"
    deposit_amount: float,
    strike_price_usd: float,
    spot_price_at_expiry_usd: float,
    dip_type: str, # "sell_high" (call) or "buy_low" (put)
    tenor_days: int,
    apr_pct: float
) -> Dict[str, Any]:
    """
    Calculates guaranteed premium yield and settlement asset outcome at expiry for Dual Investment Products (DIP).
    """
    if deposit_amount <= 0 or strike_price_usd <= 0 or spot_price_at_expiry_usd <= 0 or tenor_days <= 0 or apr_pct <= 0:
        raise ValueError("Inputs must be positive numbers.")

    tenor_fraction = tenor_days / 365.0
    period_yield_pct = apr_pct * tenor_fraction
    guaranteed_yield_amount = deposit_amount * (period_yield_pct / 100.0)
    total_repaid_nominal = deposit_amount + guaranteed_yield_amount

    dip_type_clean = dip_type.strip().lower()
    if dip_type_clean == "sell_high":
        # User deposits SOL, sells Covered Call at strike_price_usd
        is_assigned = spot_price_at_expiry_usd >= strike_price_usd
        if is_assigned:
            settlement_asset = "USDC"
            settlement_amount = total_repaid_nominal * strike_price_usd
        else:
            settlement_asset = "SOL"
            settlement_amount = total_repaid_nominal
    elif dip_type_clean == "buy_low":
        # User deposits USDC, sells Cash-Secured Put at strike_price_usd
        is_assigned = spot_price_at_expiry_usd <= strike_price_usd
        if is_assigned:
            settlement_asset = "SOL"
            settlement_amount = total_repaid_nominal / strike_price_usd
        else:
            settlement_asset = "USDC"
            settlement_amount = total_repaid_nominal
    else:
        raise ValueError("dip_type must be 'sell_high' or 'buy_low'")

    effective_total_value_usd = (
        settlement_amount if settlement_asset == "USDC" else settlement_amount * spot_price_at_expiry_usd
    )

    return {
        "deposit_asset": deposit_asset.upper(),
        "deposit_amount": round(deposit_amount, 4),
        "strike_price_usd": round(strike_price_usd, 2),
        "spot_price_at_expiry_usd": round(spot_price_at_expiry_usd, 2),
        "dip_type": dip_type_clean,
        "tenor_days": tenor_days,
        "apr_pct": round(apr_pct, 2),
        "guaranteed_yield_amount": round(guaranteed_yield_amount, 4),
        "is_assigned": is_assigned,
        "settlement_asset": settlement_asset,
        "settlement_amount": round(settlement_amount, 4),
        "effective_total_value_usd": round(effective_total_value_usd, 2)
    }

def calculate_staking_options_fair_value_and_dilution(
    token_grant_count: float,
    strike_usd: float,
    current_token_price_usd: float,
    implied_vol_pct: float = 80.0
) -> Dict[str, Any]:
    """
    Evaluates Staking Options (SO) intrinsic value and DAO treasury protection:
    If market price is above strike, option has intrinsic value.
    Exercise infuses cash into DAO treasury equal to grant_count * strike_usd.
    """
    if token_grant_count <= 0 or strike_usd <= 0 or current_token_price_usd <= 0:
        raise ValueError("Token grant, strike, and price must be positive.")

    intrinsic_per_token_usd = max(0.0, current_token_price_usd - strike_usd)
    total_intrinsic_value_usd = intrinsic_per_token_usd * token_grant_count

    # Capital infused into DAO treasury upon exercise
    treasury_cash_inflow_usd = token_grant_count * strike_usd

    # Unconditional raw grant cost to DAO
    raw_grant_market_value_usd = token_grant_count * current_token_price_usd
    dao_treasury_savings_usd = raw_grant_market_value_usd - total_intrinsic_value_usd

    is_in_the_money = current_token_price_usd > strike_usd

    return {
        "token_grant_count": round(token_grant_count, 2),
        "strike_usd": round(strike_usd, 2),
        "current_token_price_usd": round(current_token_price_usd, 2),
        "is_in_the_money": is_in_the_money,
        "intrinsic_per_token_usd": round(intrinsic_per_token_usd, 4),
        "total_intrinsic_value_usd": round(total_intrinsic_value_usd, 2),
        "treasury_cash_inflow_usd": round(treasury_cash_inflow_usd, 2),
        "raw_grant_market_value_usd": round(raw_grant_market_value_usd, 2),
        "dao_treasury_savings_usd": round(dao_treasury_savings_usd, 2)
    }

def calculate_optimal_dip_strike_risk_adjusted_roi(
    spot_price_usd: float,
    strikes: List[Dict[str, Any]], # List of {"strike": float, "apr_pct": float}
    tenor_days: int = 7
) -> Dict[str, Any]:
    """
    Ranks DIP strikes by annualized yield and calculates buffer against spot price.
    """
    if spot_price_usd <= 0 or not strikes:
        raise ValueError("Spot price must be positive and strikes list non-empty.")

    ranked_strikes = []
    for s in strikes:
        strike = s["strike"]
        apr = s["apr_pct"]
        buffer_pct = ((strike - spot_price_usd) / spot_price_usd) * 100.0
        daily_yield_pct = apr / 365.0
        period_yield_pct = daily_yield_pct * tenor_days

        ranked_strikes.append({
            "strike": round(strike, 2),
            "apr_pct": round(apr, 2),
            "buffer_pct": round(buffer_pct, 2),
            "period_yield_pct": round(period_yield_pct, 4)
        })

    # Sort by APR descending
    ranked_strikes.sort(key=lambda x: x["apr_pct"], reverse=True)

    return {
        "spot_price_usd": round(spot_price_usd, 2),
        "tenor_days": tenor_days,
        "best_strike": ranked_strikes[0],
        "all_strikes": ranked_strikes
    }

def verify_vip_license(tx_hash: str, chain: str, recipient: str, amount: float) -> Dict[str, Any]:
    """
    Verifies on-chain payment for VIP Access (5 Base USDC or 0.03 SOL).
    """
    valid_base_wallet = "0xF0E0D361bBE899F3089f0a968506eF2B97693c01"
    valid_sol_wallet = "DW2MdHEq3qZ6nh9b5YFUoaPnBuuxC8Gz2785kwbbjSAM"

    chain_clean = chain.strip().lower()
    if chain_clean == "base":
        is_valid = (
            recipient.lower() == valid_base_wallet.lower() and
            amount >= 5.0 and
            len(tx_hash) >= 64
        )
    elif chain_clean == "solana":
        is_valid = (
            recipient == valid_sol_wallet and
            amount >= 0.03 and
            len(tx_hash) >= 64
        )
    else:
        is_valid = False

    return {
        "verified": is_valid,
        "chain": chain,
        "tx_hash": tx_hash,
        "amount": amount,
        "recipient": recipient,
        "tier": "Dual Finance VIP Sentinel" if is_valid else "Unverified"
    }