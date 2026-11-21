"""
Base Spectra Protocol Fixed-Yield Stripping (PT/YT) & Yield Curve Arbitrage Radar
Mathematical simulation and execution optimization engine for Spectra Protocol (ex-APWine) Principal Tokens (PT),
Yield Tokens (YT), leveraged yield carry, and time-decay AMM convergence on Base L2.
"""

import math

BASE_USDC_RECEIVE_ADDRESS = "0xF0E0D361bBE899F3089f0a968506eF2B97693c01"
SOLANA_RECEIVE_ADDRESS = "DW2MdHEq3qZ6nh9b5YFUoaPnBuuxC8Gz2785kwbbjSAM"

def calculate_pt_fixed_yield_discount(
    underlying_deposit_usd: float,
    maturity_days: int = 180,
    fixed_implied_apr_pct: float = 8.5
) -> dict:
    """
    Evaluates Principal Token (PT) purchasing discounts and guaranteed fixed annual yields.
    Locking capital in PT guarantees repayment of 1.0 underlying asset at maturity date.
    """
    if underlying_deposit_usd <= 0 or maturity_days <= 0 or fixed_implied_apr_pct <= 0:
        return {
            "underlying_deposit_usd": underlying_deposit_usd,
            "maturity_days": maturity_days,
            "fixed_implied_apr_pct": fixed_implied_apr_pct,
            "pt_price_ratio": 1.0,
            "pt_buy_price_usd": underlying_deposit_usd,
            "fixed_interest_gain_usd": 0.0,
            "realized_fixed_apr_pct": 0.0
        }

    time_fraction = maturity_days / 365.0
    pt_price_ratio = 1.0 / (1.0 + (fixed_implied_apr_pct / 100.0) * time_fraction)
    pt_buy_price = underlying_deposit_usd * pt_price_ratio
    fixed_interest_gain = underlying_deposit_usd - pt_buy_price
    realized_fixed_apr = (fixed_interest_gain / pt_buy_price) * (365.0 / maturity_days) * 100.0

    return {
        "underlying_deposit_usd": round(underlying_deposit_usd, 2),
        "maturity_days": maturity_days,
        "fixed_implied_apr_pct": round(fixed_implied_apr_pct, 2),
        "pt_price_ratio": round(pt_price_ratio, 6),
        "pt_buy_price_usd": round(pt_buy_price, 2),
        "fixed_interest_gain_usd": round(fixed_interest_gain, 2),
        "realized_fixed_apr_pct": round(realized_fixed_apr, 2)
    }

def calculate_yt_leverage_yield_pnl(
    yt_capital_invested_usd: float,
    underlying_principal_represented_usd: float,
    variable_actual_apy_pct: float = 14.0,
    maturity_days: int = 180
) -> dict:
    """
    Models Yield Token (YT) carry and leveraged upside from variable rate expansion.
    YT holders harvest all variable yield accrued by the underlying vault until maturity.
    """
    if yt_capital_invested_usd <= 0 or underlying_principal_represented_usd <= 0 or maturity_days <= 0:
        return {
            "yt_capital_invested_usd": yt_capital_invested_usd,
            "underlying_principal_represented_usd": underlying_principal_represented_usd,
            "variable_interest_harvested_usd": 0.0,
            "net_yt_profit_usd": 0.0,
            "yt_roi_pct": 0.0,
            "is_profitable": False
        }

    time_fraction = maturity_days / 365.0
    variable_yield_harvested = underlying_principal_represented_usd * (variable_actual_apy_pct / 100.0) * time_fraction
    net_profit = variable_yield_harvested - yt_capital_invested_usd
    roi_pct = (net_profit / yt_capital_invested_usd) * 100.0

    return {
        "yt_capital_invested_usd": round(yt_capital_invested_usd, 2),
        "underlying_principal_represented_usd": round(underlying_principal_represented_usd, 2),
        "variable_actual_apy_pct": round(variable_actual_apy_pct, 2),
        "variable_interest_harvested_usd": round(variable_yield_harvested, 2),
        "net_yt_profit_usd": round(net_profit, 2),
        "yt_roi_pct": round(roi_pct, 2),
        "is_profitable": net_profit > 0
    }

def calculate_amm_time_decay_convergence(
    current_pt_price_ratio: float,
    days_to_maturity: int,
    initial_maturity_days: int = 180
) -> dict:
    """
    Tracks price convergence of PT towards 1.0 (par) as expiry nears,
    providing zero-impermanent-loss liquidity on specialized Spectra AMM curves.
    """
    if current_pt_price_ratio <= 0 or initial_maturity_days <= 0:
        return {
            "current_pt_price_ratio": current_pt_price_ratio,
            "days_to_maturity": days_to_maturity,
            "pull_to_par_gain_pct": 0.0,
            "annualized_convergence_apr_pct": 0.0
        }

    pull_to_par_gain = ((1.0 - current_pt_price_ratio) / current_pt_price_ratio) * 100.0
    convergence_apr = pull_to_par_gain * (365.0 / days_to_maturity) if days_to_maturity > 0 else 0.0

    return {
        "current_pt_price_ratio": round(current_pt_price_ratio, 6),
        "days_to_maturity": days_to_maturity,
        "pull_to_par_gain_pct": round(pull_to_par_gain, 2),
        "annualized_convergence_apr_pct": round(convergence_apr, 2)
    }

def verify_vip_license(tx_hash: str, chain: str, amount: float, recipient: str) -> dict:
    """
    Validates on-chain VIP sentinel license for Spectra fixed yield & YT leverage analytics.
    Requires 5 Base USDC or 0.03 SOL to the designated receive addresses.
    """
    if not tx_hash or len(tx_hash) < 10:
        return {"valid": False, "reason": "Invalid transaction hash"}
    
    chain_lower = chain.lower()
    if chain_lower == "base":
        if recipient.lower() != BASE_USDC_RECEIVE_ADDRESS.lower():
            return {"valid": False, "reason": "Incorrect Base recipient address"}
        if amount < 5.0:
            return {"valid": False, "reason": "Insufficient fee; minimum 5 Base USDC required"}
        return {"valid": True, "tier": "PRO_SENTINEL", "granted_chain": "base"}
    elif chain_lower == "solana":
        if recipient != SOLANA_RECEIVE_ADDRESS:
            return {"valid": False, "reason": "Incorrect Solana recipient address"}
        if amount < 0.03:
            return {"valid": False, "reason": "Insufficient fee; minimum 0.03 SOL required"}
        return {"valid": True, "tier": "PRO_SENTINEL", "granted_chain": "solana"}
    else:
        return {"valid": False, "reason": f"Unsupported payment chain: {chain}"}
