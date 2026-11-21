#!/usr/bin/env python3
"""
Solana Sharky.fi NFT Lending Collection APR & Default Seizure Radar
Calculates Sharky.fi loan offer yields, borrower default foreclosure arbitrage profits,
and collection floor price drawdown solvency buffers.
"""

from typing import Dict, Any


def calculate_sharky_loan_yield(
    principal_sol: float = 100.0,
    stated_apr: float = 0.40,
    duration_days: int = 14,
    protocol_fee_pct: float = 1.5
) -> Dict[str, Any]:
    """
    Computes net realized interest and annualized return for Sharky.fi loan offers.
    Protocol fee is charged as a percentage of generated interest.
    """
    if principal_sol <= 0.0 or stated_apr <= 0.0:
        raise ValueError("Principal and stated APR must be positive")
    if duration_days <= 0 or not (0.0 <= protocol_fee_pct < 100.0):
        raise ValueError("Invalid duration or protocol fee")

    time_fraction = duration_days / 365.0
    gross_interest_sol = principal_sol * stated_apr * time_fraction
    protocol_fee_sol = gross_interest_sol * (protocol_fee_pct / 100.0)
    net_interest_sol = gross_interest_sol - protocol_fee_sol
    net_realized_apr = (net_interest_sol / principal_sol) / time_fraction

    return {
        "principal_sol": principal_sol,
        "stated_apr_pct": round(stated_apr * 100.0, 2),
        "duration_days": duration_days,
        "gross_interest_sol": round(gross_interest_sol, 4),
        "protocol_fee_sol": round(protocol_fee_sol, 4),
        "net_interest_sol": round(net_interest_sol, 4),
        "net_realized_apr_pct": round(net_realized_apr * 100.0, 2)
    }


def calculate_default_foreclosure_profit(
    floor_price_sol: float = 150.0,
    loan_principal_sol: float = 97.5,
    marketplace_taker_fee_pct: float = 2.0
) -> Dict[str, Any]:
    """
    Calculates lender net profit and ROI if borrower defaults and the underlying NFT is seized.
    """
    if floor_price_sol <= 0.0 or loan_principal_sol <= 0.0:
        raise ValueError("Floor price and loan principal must be positive")

    ltv_ratio = loan_principal_sol / floor_price_sol
    net_liquidation_value_sol = floor_price_sol * (1.0 - (marketplace_taker_fee_pct / 100.0))
    net_profit_sol = net_liquidation_value_sol - loan_principal_sol
    net_roi_pct = (net_profit_sol / loan_principal_sol) * 100.0

    return {
        "floor_price_sol": floor_price_sol,
        "loan_principal_sol": loan_principal_sol,
        "ltv_pct": round(ltv_ratio * 100.0, 2),
        "net_liquidation_value_sol": round(net_liquidation_value_sol, 4),
        "net_profit_sol": round(net_profit_sol, 4),
        "net_roi_pct": round(net_roi_pct, 2)
    }


def calculate_floor_drawdown_buffer(
    floor_price_sol: float = 150.0,
    loan_principal_sol: float = 97.5
) -> Dict[str, Any]:
    """
    Computes safe collection floor price drawdown before loan collateral is underwater.
    """
    if floor_price_sol <= 0.0 or loan_principal_sol <= 0.0:
        raise ValueError("Values must be positive")

    breakeven_floor_sol = loan_principal_sol
    drawdown_buffer_sol = floor_price_sol - breakeven_floor_sol
    drawdown_buffer_pct = (drawdown_buffer_sol / floor_price_sol) * 100.0

    return {
        "current_floor_sol": floor_price_sol,
        "breakeven_floor_sol": breakeven_floor_sol,
        "drawdown_buffer_sol": round(drawdown_buffer_sol, 4),
        "drawdown_buffer_pct": round(drawdown_buffer_pct, 2)
    }


def evaluate_sharky_collection_risk(
    ltv_pct: float,
    stated_apr_pct: float,
    drawdown_buffer_pct: float
) -> Dict[str, Any]:
    """
    Evaluates loan offer risk rating (0-100 score) and provides underwriting guidance.
    """
    # Healthy loans have LTV <= 65% and drawdown buffer >= 35%
    ltv_risk_penalty = max(0.0, (ltv_pct - 50.0) * 1.5)
    buffer_reward = min(40.0, drawdown_buffer_pct * 0.8)
    yield_factor = min(20.0, stated_apr_pct * 0.4)

    safety_score = round(max(0.0, min(100.0, 70.0 - ltv_risk_penalty + buffer_reward + yield_factor)), 1)

    if safety_score >= 80.0:
        status = "PRIME_UNDERWRITING"
        recommendation = "Low LTV with deep collection floor buffer. Highly attractive risk-adjusted yield."
    elif safety_score >= 50.0:
        status = "MODERATE_RISK"
        recommendation = "Monitor collection floor velocity. Consider reducing loan offer duration to 7 days."
    else:
        status = "HIGH_DEFAULT_EXPOSURE"
        recommendation = "Excessive LTV. Risk of toxic floor decay exceeding loan principal upon default."

    return {
        "safety_score": safety_score,
        "status": status,
        "recommendation": recommendation
    }


if __name__ == "__main__":
    y_res = calculate_sharky_loan_yield()
    print("Sharky Yield:", y_res)
    d_res = calculate_default_foreclosure_profit()
    print("Foreclosure Profit:", d_res)
    b_res = calculate_floor_drawdown_buffer()
    print("Drawdown Buffer:", b_res)
    risk = evaluate_sharky_collection_risk(65.0, 40.0, 35.0)
    print("Risk:", risk)
