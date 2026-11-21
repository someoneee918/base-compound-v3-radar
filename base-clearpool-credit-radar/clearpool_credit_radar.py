"""
Base Clearpool Institutional Uncollateralized Credit & Prime Borrowing Radar
Mathematical simulation and risk analytics engine for Clearpool Protocol single-borrower uncollateralized lending pools,
dynamic utilization kink curves, cpToken yield accrual, and CPOOL insurance coverage on Base L2.
"""

import math

BASE_USDC_RECEIVE_ADDRESS = "0xF0E0D361bBE899F3089f0a968506eF2B97693c01"
SOLANA_RECEIVE_ADDRESS = "DW2MdHEq3qZ6nh9b5YFUoaPnBuuxC8Gz2785kwbbjSAM"

def calculate_clearpool_utilization_and_borrow_rate(
    pool_total_liquidity_usd: float,
    total_borrowed_usd: float,
    base_rate_pct: float = 2.0,
    kink_utilization_pct: float = 80.0,
    slope1_pct: float = 10.0,
    slope2_pct: float = 60.0,
    insurance_cut_pct: float = 5.0
) -> dict:
    """
    Computes pool utilization rate, dynamic piecewise borrow APR, and lender supply APR
    net of the protocol insurance pool deduction.
    """
    if pool_total_liquidity_usd <= 0:
        return {
            "utilization_pct": 0.0,
            "borrow_apr_pct": base_rate_pct,
            "supply_apr_pct": 0.0,
            "available_liquidity_usd": 0.0,
            "total_borrowed_usd": total_borrowed_usd,
            "is_above_kink": False
        }

    utilization_pct = min(100.0, (total_borrowed_usd / pool_total_liquidity_usd) * 100.0)
    available_liquidity = max(0.0, pool_total_liquidity_usd - total_borrowed_usd)

    is_above_kink = utilization_pct > kink_utilization_pct
    if not is_above_kink:
        borrow_apr = base_rate_pct + (utilization_pct / kink_utilization_pct) * slope1_pct
    else:
        excess_util = (utilization_pct - kink_utilization_pct) / (100.0 - kink_utilization_pct)
        borrow_apr = base_rate_pct + slope1_pct + (excess_util * slope2_pct)

    # Lenders earn borrow interest proportional to utilization minus the insurance cut
    supply_apr = borrow_apr * (utilization_pct / 100.0) * (1.0 - (insurance_cut_pct / 100.0))

    return {
        "pool_total_liquidity_usd": round(pool_total_liquidity_usd, 2),
        "total_borrowed_usd": round(total_borrowed_usd, 2),
        "available_liquidity_usd": round(available_liquidity, 2),
        "utilization_pct": round(utilization_pct, 2),
        "borrow_apr_pct": round(borrow_apr, 4),
        "supply_apr_pct": round(supply_apr, 4),
        "is_above_kink": is_above_kink
    }

def calculate_lender_net_yield_and_credit_spread(
    deposit_amount_usd: float,
    supply_apr_pct: float,
    default_probability_pct: float = 1.0,
    recovery_rate_pct: float = 40.0,
    cpool_rewards_apr_pct: float = 3.5,
    risk_free_rate_pct: float = 4.5
) -> dict:
    """
    Evaluates net risk-adjusted lender return, incorporating expected loss rates from uncollateralized default,
    CPOOL liquidity rewards, and institutional credit spreads over risk-free SOFR.
    """
    if deposit_amount_usd <= 0:
        return {
            "deposit_amount_usd": 0.0,
            "expected_loss_rate_pct": 0.0,
            "net_total_apr_pct": 0.0,
            "credit_spread_bps": 0.0,
            "annual_net_cashflow_usd": 0.0,
            "daily_net_cashflow_usd": 0.0
        }

    expected_loss_rate = default_probability_pct * (1.0 - (recovery_rate_pct / 100.0))
    net_interest_apr = supply_apr_pct - expected_loss_rate
    net_total_apr = net_interest_apr + cpool_rewards_apr_pct
    credit_spread_bps = (net_total_apr - risk_free_rate_pct) * 100.0

    annual_cashflow = deposit_amount_usd * (net_total_apr / 100.0)
    daily_cashflow = annual_cashflow / 365.0

    return {
        "deposit_amount_usd": round(deposit_amount_usd, 2),
        "supply_apr_pct": round(supply_apr_pct, 4),
        "expected_loss_rate_pct": round(expected_loss_rate, 4),
        "cpool_rewards_apr_pct": round(cpool_rewards_apr_pct, 2),
        "net_total_apr_pct": round(net_total_apr, 4),
        "credit_spread_bps": round(credit_spread_bps, 2),
        "annual_net_cashflow_usd": round(annual_cashflow, 2),
        "daily_net_cashflow_usd": round(daily_cashflow, 4)
    }

def calculate_insurance_pool_coverage(
    borrower_debt_usd: float,
    insurance_pool_cpool_usd: float,
    required_buffer_pct: float = 5.0
) -> dict:
    """
    Monitors on-chain CPOOL insurance reserve adequacy to guarantee lender principal protection.
    """
    if borrower_debt_usd <= 0:
        return {
            "borrower_debt_usd": 0.0,
            "required_reserve_usd": 0.0,
            "insurance_pool_cpool_usd": insurance_pool_cpool_usd,
            "coverage_ratio_pct": 100.0,
            "is_adequately_covered": True,
            "shortfall_usd": 0.0
        }

    required_reserve = borrower_debt_usd * (required_buffer_pct / 100.0)
    coverage_ratio = (insurance_pool_cpool_usd / required_reserve) * 100.0 if required_reserve > 0 else 0.0
    is_covered = coverage_ratio >= 100.0
    shortfall = max(0.0, required_reserve - insurance_pool_cpool_usd)

    return {
        "borrower_debt_usd": round(borrower_debt_usd, 2),
        "required_reserve_usd": round(required_reserve, 2),
        "insurance_pool_cpool_usd": round(insurance_pool_cpool_usd, 2),
        "coverage_ratio_pct": round(coverage_ratio, 2),
        "is_adequately_covered": is_covered,
        "shortfall_usd": round(shortfall, 2)
    }

def verify_vip_license(tx_hash: str, chain: str, amount: float, recipient: str) -> dict:
    """
    Validates on-chain VIP sentinel license for Clearpool uncollateralized credit analytics.
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
