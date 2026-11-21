#!/usr/bin/env python3
"""
Base Pendle Finance PT/YT Yield Stripping & Fixed-Rate APY Locking Radar
Calculates Principal Token (PT) fixed APY lock schedules, Yield Token (YT) leverage returns,
and Pendle v2 AMM pull-to-par convergence on Base.
"""

from typing import Dict, Any


def calculate_pt_fixed_apy(
    pt_price: float = 0.940,
    days_to_maturity: int = 90,
    deposit_amount_usd: float = 10000.0
) -> Dict[str, Any]:
    """
    Calculates fixed APY locked by purchasing Principal Tokens (PT).
    At maturity, 1 PT redeems for exactly 1.0 unit of underlying collateral.
    """
    if pt_price <= 0.0 or pt_price >= 1.0:
        raise ValueError("pt_price must be between 0.0 and 1.0 exclusive")
    if days_to_maturity <= 0:
        raise ValueError("days_to_maturity must be positive")
    if deposit_amount_usd <= 0.0:
        raise ValueError("deposit_amount_usd must be positive")

    time_fraction_years = days_to_maturity / 365.0
    # Annualized fixed APY: (1 / pt_price)^(1 / time_fraction) - 1
    fixed_apy = ((1.0 / pt_price) ** (1.0 / time_fraction_years)) - 1.0
    pt_tokens_purchased = deposit_amount_usd / pt_price
    maturity_value_usd = pt_tokens_purchased * 1.0
    net_profit_usd = maturity_value_usd - deposit_amount_usd
    net_roi_pct = (net_profit_usd / deposit_amount_usd) * 100.0

    return {
        "pt_price": pt_price,
        "days_to_maturity": days_to_maturity,
        "deposit_amount_usd": deposit_amount_usd,
        "pt_tokens_purchased": round(pt_tokens_purchased, 4),
        "maturity_value_usd": round(maturity_value_usd, 2),
        "net_profit_usd": round(net_profit_usd, 2),
        "net_roi_pct": round(net_roi_pct, 2),
        "fixed_apy_pct": round(fixed_apy * 100.0, 2)
    }


def calculate_yt_leveraged_carry(
    underlying_price: float = 1.0,
    yt_price: float = 0.060,
    actual_variable_apr: float = 0.16,
    implied_yield_apr: float = 0.12,
    days_held: int = 90,
    capital_usd: float = 10000.0
) -> Dict[str, Any]:
    """
    Calculates Yield Token (YT) leverage multiplier and net return if variable yield
    exceeds implied yield over holding period.
    """
    if yt_price <= 0.0 or underlying_price <= 0.0:
        raise ValueError("Prices must be positive")
    if days_held <= 0 or capital_usd <= 0.0:
        raise ValueError("Days held and capital must be positive")

    leverage_ratio = underlying_price / yt_price
    yt_tokens_purchased = capital_usd / yt_price
    time_fraction_years = days_held / 365.0

    # Yield cashflow earned = yt_tokens * underlying_price * actual_variable_apr * time_fraction
    accrued_yield_usd = yt_tokens_purchased * underlying_price * actual_variable_apr * time_fraction_years
    net_profit_usd = accrued_yield_usd - capital_usd
    net_roi_pct = (net_profit_usd / capital_usd) * 100.0

    # Breakeven variable APR required over time_fraction: capital = yt_tokens * 1.0 * APR * time_fraction
    # APR_breakeven = yt_price / time_fraction
    breakeven_variable_apr = (yt_price / time_fraction_years)

    return {
        "yt_price": yt_price,
        "leverage_ratio": round(leverage_ratio, 2),
        "actual_variable_apr_pct": round(actual_variable_apr * 100.0, 2),
        "breakeven_variable_apr_pct": round(breakeven_variable_apr * 100.0, 2),
        "yt_tokens_purchased": round(yt_tokens_purchased, 4),
        "accrued_yield_usd": round(accrued_yield_usd, 2),
        "net_profit_usd": round(net_profit_usd, 2),
        "net_roi_pct": round(net_roi_pct, 2)
    }


def calculate_pendle_amm_pull_to_par(
    initial_pt_price: float = 0.940,
    days_elapsed: int = 45,
    total_days: int = 90
) -> Dict[str, Any]:
    """
    Models Pendle v2 AMM pull-to-par convergence as expiration approaches.
    PT price converges toward 1.0 asymptotically according to scalar logit curve.
    """
    if days_elapsed < 0 or days_elapsed > total_days or total_days <= 0:
        raise ValueError("Invalid days parameters")

    remaining_days = total_days - days_elapsed
    progress_ratio = days_elapsed / float(total_days)

    # Linear pull-to-par baseline with convex acceleration near maturity
    discount = 1.0 - initial_pt_price
    remaining_discount = discount * ((remaining_days / float(total_days)) ** 0.85)
    current_pt_price = round(1.0 - remaining_discount, 4)

    return {
        "initial_pt_price": initial_pt_price,
        "current_pt_price": current_pt_price,
        "days_elapsed": days_elapsed,
        "remaining_days": remaining_days,
        "progress_pct": round(progress_ratio * 100.0, 1),
        "discount_captured_pct": round(((current_pt_price - initial_pt_price) / discount) * 100.0, 2)
    }


def evaluate_pendle_trade_signal(
    fixed_apy: float,
    current_variable_apr: float,
    pt_price: float
) -> Dict[str, Any]:
    """
    Evaluates market regime to provide institutional yield strategy recommendations.
    """
    spread_bps = round((fixed_apy - (current_variable_apr * 100.0)) * 100.0, 1)

    if spread_bps > 200.0:
        recommendation = "STRONG_BUY_PT"
        summary = "Fixed APY is higher than current variable yield by >200 bps. Lock guaranteed fixed returns."
    elif spread_bps < -200.0:
        recommendation = "STRONG_BUY_YT"
        summary = "Variable yield is outpacing implied yield by >200 bps. Exploit leveraged yield expansion."
    else:
        recommendation = "NEUTRAL_LP_DEPOSIT"
        summary = "Yields are fairly priced. Provide liquidity to earn pool trading fees + base rewards."

    return {
        "fixed_apy_pct": fixed_apy,
        "current_variable_apr_pct": round(current_variable_apr * 100.0, 2),
        "spread_bps": spread_bps,
        "recommendation": recommendation,
        "summary": summary
    }


if __name__ == "__main__":
    pt_res = calculate_pt_fixed_apy()
    print("PT Fixed APY:", pt_res)
    yt_res = calculate_yt_leveraged_carry()
    print("YT Leveraged Carry:", yt_res)
    par_res = calculate_pendle_amm_pull_to_par()
    print("Pull to Par:", par_res)
    sig = evaluate_pendle_trade_signal(28.6, 0.16, 0.940)
    print("Signal:", sig)
