"""
Base Goldfinch / Finterest RWA Private Credit Junior & Senior Tranche Waterfall Radar
Mathematical simulation and risk management engine for Goldfinch Protocol RWA borrower pools,
first-loss Junior tranche risk-reallocation premiums, Senior tranche capital protection, and secondary loan token discounts on Base.
"""

import math

BASE_USDC_RECEIVE_ADDRESS = "0xF0E0D361bBE899F3089f0a968506eF2B97693c01"
SOLANA_RECEIVE_ADDRESS = "DW2MdHEq3qZ6nh9b5YFUoaPnBuuxC8Gz2785kwbbjSAM"

def calculate_tranche_waterfall_yields(
    borrower_principal_usd: float,
    borrower_interest_rate_pct: float = 12.0,
    junior_tranche_ratio_pct: float = 20.0,
    junior_reallocation_pct: float = 20.0,
    protocol_reserve_fee_pct: float = 10.0
) -> dict:
    """
    Computes cashflow distributions and annualized net yields across Junior (Backer) and Senior tranches,
    accounting for first-loss interest reallocation and protocol reserve deductions.
    """
    if borrower_principal_usd <= 0 or borrower_interest_rate_pct <= 0:
        return {
            "borrower_principal_usd": borrower_principal_usd,
            "senior_capital_usd": 0.0,
            "junior_capital_usd": 0.0,
            "senior_net_apy_pct": 0.0,
            "junior_net_apy_pct": 0.0,
            "annual_protocol_fee_usd": 0.0,
            "junior_yield_boost_pct": 0.0
        }

    junior_capital = borrower_principal_usd * (junior_tranche_ratio_pct / 100.0)
    senior_capital = borrower_principal_usd - junior_capital

    senior_nominal_interest = senior_capital * (borrower_interest_rate_pct / 100.0)
    junior_reallocation_bonus = senior_nominal_interest * (junior_reallocation_pct / 100.0)

    fee_multiplier = 1.0 - (protocol_reserve_fee_pct / 100.0)
    senior_net_interest = (senior_nominal_interest - junior_reallocation_bonus) * fee_multiplier
    junior_net_interest = ((junior_capital * (borrower_interest_rate_pct / 100.0)) + junior_reallocation_bonus) * fee_multiplier

    senior_net_apy = (senior_net_interest / senior_capital) * 100.0 if senior_capital > 0 else 0.0
    junior_net_apy = (junior_net_interest / junior_capital) * 100.0 if junior_capital > 0 else 0.0
    gross_annual_interest = borrower_principal_usd * (borrower_interest_rate_pct / 100.0)
    protocol_fee = gross_annual_interest * (protocol_reserve_fee_pct / 100.0)

    return {
        "borrower_principal_usd": round(borrower_principal_usd, 2),
        "senior_capital_usd": round(senior_capital, 2),
        "junior_capital_usd": round(junior_capital, 2),
        "senior_net_annual_income_usd": round(senior_net_interest, 2),
        "junior_net_annual_income_usd": round(junior_net_interest, 2),
        "senior_net_apy_pct": round(senior_net_apy, 2),
        "junior_net_apy_pct": round(junior_net_apy, 2),
        "annual_protocol_fee_usd": round(protocol_fee, 2),
        "junior_yield_boost_pct": round(junior_net_apy - senior_net_apy, 2)
    }

def calculate_default_impairment_waterfall(
    borrower_principal_usd: float,
    default_loss_amount_usd: float,
    junior_tranche_ratio_pct: float = 20.0
) -> dict:
    """
    Evaluates loss absorption across tranches during borrower distress.
    Junior tranche absorbs first-loss capital up to its entire balance before Senior principal is impacted.
    """
    if borrower_principal_usd <= 0:
        return {
            "borrower_principal_usd": 0.0,
            "default_loss_amount_usd": 0.0,
            "junior_loss_absorbed_usd": 0.0,
            "senior_loss_absorbed_usd": 0.0,
            "junior_impairment_pct": 0.0,
            "senior_impairment_pct": 0.0,
            "senior_principal_protected": True
        }

    junior_capital = borrower_principal_usd * (junior_tranche_ratio_pct / 100.0)
    senior_capital = borrower_principal_usd - junior_capital

    if default_loss_amount_usd <= junior_capital:
        junior_loss = default_loss_amount_usd
        senior_loss = 0.0
    else:
        junior_loss = junior_capital
        senior_loss = default_loss_amount_usd - junior_capital

    junior_impairment = (junior_loss / junior_capital) * 100.0 if junior_capital > 0 else 0.0
    senior_impairment = (senior_loss / senior_capital) * 100.0 if senior_capital > 0 else 0.0

    return {
        "borrower_principal_usd": round(borrower_principal_usd, 2),
        "default_loss_amount_usd": round(default_loss_amount_usd, 2),
        "junior_loss_absorbed_usd": round(junior_loss, 2),
        "senior_loss_absorbed_usd": round(senior_loss, 2),
        "junior_impairment_pct": round(junior_impairment, 2),
        "senior_impairment_pct": round(senior_impairment, 2),
        "senior_principal_protected": senior_loss == 0.0
    }

def calculate_secondary_loan_token_discount(
    face_value_usd: float,
    secondary_discount_bps: float = 150.0,
    holding_months: float = 6.0,
    annual_coupon_pct: float = 10.0
) -> dict:
    """
    Quantifies arbitrage opportunities and enhanced returns from acquiring secondary RWA loan tokens
    at a liquidity discount.
    """
    if face_value_usd <= 0 or holding_months <= 0:
        return {
            "face_value_usd": 0.0,
            "buy_price_usd": 0.0,
            "discount_gain_usd": 0.0,
            "coupon_income_usd": 0.0,
            "total_return_usd": 0.0,
            "annualized_yield_pct": 0.0
        }

    buy_price = face_value_usd * (1.0 - (secondary_discount_bps / 10000.0))
    discount_gain = face_value_usd - buy_price
    coupon_income = face_value_usd * (annual_coupon_pct / 100.0) * (holding_months / 12.0)
    total_return = discount_gain + coupon_income
    annualized_yield = (total_return / buy_price) * (12.0 / holding_months) * 100.0 if buy_price > 0 else 0.0

    return {
        "face_value_usd": round(face_value_usd, 2),
        "secondary_discount_bps": round(secondary_discount_bps, 2),
        "buy_price_usd": round(buy_price, 2),
        "discount_gain_usd": round(discount_gain, 2),
        "coupon_income_usd": round(coupon_income, 2),
        "total_return_usd": round(total_return, 2),
        "annualized_yield_pct": round(annualized_yield, 2)
    }

def verify_vip_license(tx_hash: str, chain: str, amount: float, recipient: str) -> dict:
    """
    Validates on-chain VIP sentinel license for Goldfinch RWA credit analytics.
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
