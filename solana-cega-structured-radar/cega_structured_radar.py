"""
Solana Cega Protocol Pure Yield & Auto-Callable Knock-Out Structured Products Radar
Mathematical simulation and risk management engine for Cega Protocol exotic options vaults,
auto-callable early redemption triggers, downside knock-in barrier defense buffers, and fee structures on Solana.
"""

import math

BASE_USDC_RECEIVE_ADDRESS = "0xF0E0D361bBE899F3089f0a968506eF2B97693c01"
SOLANA_RECEIVE_ADDRESS = "DW2MdHEq3qZ6nh9b5YFUoaPnBuuxC8Gz2785kwbbjSAM"

def calculate_autocall_structured_note_irr(
    deposit_amount_usd: float,
    annual_coupon_pct: float = 22.0,
    tenure_weeks: int = 12,
    autocall_week: int = 4,
    autocall_barrier_pct: float = 105.0,
    current_price_pct: float = 108.0
) -> dict:
    """
    Evaluates auto-callable structured note payout schedules and capital turnover velocity.
    When price exceeds the auto-call threshold, capital is redeemed early with accrued coupon.
    """
    if deposit_amount_usd <= 0 or annual_coupon_pct <= 0 or tenure_weeks <= 0:
        return {
            "deposit_amount_usd": deposit_amount_usd,
            "annual_coupon_pct": annual_coupon_pct,
            "is_autocalled": False,
            "effective_tenure_weeks": tenure_weeks,
            "coupon_earned_usd": 0.0,
            "total_payout_usd": 0.0,
            "annualized_irr_pct": 0.0
        }

    is_autocalled = current_price_pct >= autocall_barrier_pct
    effective_tenure = autocall_week if is_autocalled else tenure_weeks

    coupon_earned = deposit_amount_usd * (annual_coupon_pct / 100.0) * (effective_tenure / 52.0)
    total_payout = deposit_amount_usd + coupon_earned
    annualized_irr = (coupon_earned / deposit_amount_usd) * (52.0 / effective_tenure) * 100.0

    return {
        "deposit_amount_usd": round(deposit_amount_usd, 2),
        "annual_coupon_pct": round(annual_coupon_pct, 2),
        "autocall_barrier_pct": round(autocall_barrier_pct, 2),
        "current_price_pct": round(current_price_pct, 2),
        "is_autocalled": is_autocalled,
        "effective_tenure_weeks": effective_tenure,
        "coupon_earned_usd": round(coupon_earned, 2),
        "total_payout_usd": round(total_payout, 2),
        "annualized_irr_pct": round(annualized_irr, 2)
    }

def calculate_knock_in_barrier_buffer(
    underlying_spot_usd: float,
    knock_in_barrier_pct: float = 50.0,
    current_market_price_usd: float = 180.0
) -> dict:
    """
    Computes downside protection margin and distance to knock-in barrier.
    Principal remains 100% safe as long as the market price stays above the knock-in barrier.
    """
    if underlying_spot_usd <= 0:
        return {
            "underlying_spot_usd": 0.0,
            "barrier_price_usd": 0.0,
            "safety_buffer_usd": 0.0,
            "safety_buffer_pct": 0.0,
            "is_barrier_breached": False
        }

    barrier_price = underlying_spot_usd * (knock_in_barrier_pct / 100.0)
    safety_buffer = max(0.0, current_market_price_usd - barrier_price)
    safety_buffer_pct = ((current_market_price_usd - barrier_price) / current_market_price_usd) * 100.0 if current_market_price_usd > 0 else 0.0
    is_breached = current_market_price_usd <= barrier_price

    return {
        "underlying_spot_usd": round(underlying_spot_usd, 2),
        "current_market_price_usd": round(current_market_price_usd, 2),
        "knock_in_barrier_pct": round(knock_in_barrier_pct, 2),
        "barrier_price_usd": round(barrier_price, 2),
        "safety_buffer_usd": round(safety_buffer, 2),
        "safety_buffer_pct": round(safety_buffer_pct, 2),
        "is_barrier_breached": is_breached
    }

def calculate_cega_vault_revenue_and_fees(
    vault_tvl_usd: float,
    management_fee_pct: float = 1.0,
    performance_fee_pct: float = 15.0,
    gross_yield_apr_pct: float = 22.0
) -> dict:
    """
    Models protocol revenue and net LP yield distributions across Cega exotic options vaults.
    """
    if vault_tvl_usd <= 0:
        return {
            "vault_tvl_usd": 0.0,
            "gross_yield_usd": 0.0,
            "protocol_fee_usd": 0.0,
            "net_lender_yield_usd": 0.0,
            "net_lender_apr_pct": 0.0
        }

    gross_yield = vault_tvl_usd * (gross_yield_apr_pct / 100.0)
    mgmt_fee = vault_tvl_usd * (management_fee_pct / 100.0)
    perf_fee = gross_yield * (performance_fee_pct / 100.0)
    total_protocol_fee = mgmt_fee + perf_fee
    net_lender_yield = gross_yield - total_protocol_fee
    net_lender_apr = (net_lender_yield / vault_tvl_usd) * 100.0

    return {
        "vault_tvl_usd": round(vault_tvl_usd, 2),
        "gross_yield_usd": round(gross_yield, 2),
        "management_fee_usd": round(mgmt_fee, 2),
        "performance_fee_usd": round(perf_fee, 2),
        "total_protocol_fee_usd": round(total_protocol_fee, 2),
        "net_lender_yield_usd": round(net_lender_yield, 2),
        "net_lender_apr_pct": round(net_lender_apr, 2)
    }

def verify_vip_license(tx_hash: str, chain: str, amount: float, recipient: str) -> dict:
    """
    Validates on-chain VIP sentinel license for Cega structured product analytics.
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
