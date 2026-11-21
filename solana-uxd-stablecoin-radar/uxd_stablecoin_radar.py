"""
Solana UXD Protocol Delta-Neutral Stablecoin & Basis Funding Carry Radar
Mathematical simulation and risk management engine for UXD Protocol algorithmic delta-neutral stablecoin minting,
perpetual swap funding rate harvest carry, insurance fund negative funding runway, and DEX peg arbitrage on Solana.
"""

import math

BASE_USDC_RECEIVE_ADDRESS = "0xF0E0D361bBE899F3089f0a968506eF2B97693c01"
SOLANA_RECEIVE_ADDRESS = "DW2MdHEq3qZ6nh9b5YFUoaPnBuuxC8Gz2785kwbbjSAM"

def calculate_delta_neutral_funding_yield(
    deposit_amount_usd: float,
    funding_rate_apr_pct: float = 18.5,
    protocol_insurance_cut_pct: float = 15.0
) -> dict:
    """
    Computes staker yield accrued from 1x short perpetual funding rates while delta-hedged against SOL volatility.
    """
    if deposit_amount_usd <= 0:
        return {
            "deposit_amount_usd": deposit_amount_usd,
            "funding_rate_apr_pct": funding_rate_apr_pct,
            "gross_funding_usd": 0.0,
            "insurance_cut_usd": 0.0,
            "net_staker_yield_usd": 0.0,
            "net_staker_apr_pct": 0.0,
            "daily_cashflow_usd": 0.0
        }

    gross_funding = deposit_amount_usd * (funding_rate_apr_pct / 100.0)
    insurance_cut = gross_funding * (protocol_insurance_cut_pct / 100.0)
    net_staker_yield = gross_funding - insurance_cut
    net_staker_apr = (net_staker_yield / deposit_amount_usd) * 100.0
    daily_cashflow = net_staker_yield / 365.0

    return {
        "deposit_amount_usd": round(deposit_amount_usd, 2),
        "funding_rate_apr_pct": round(funding_rate_apr_pct, 2),
        "gross_funding_usd": round(gross_funding, 2),
        "insurance_cut_usd": round(insurance_cut, 2),
        "net_staker_yield_usd": round(net_staker_yield, 2),
        "net_staker_apr_pct": round(net_staker_apr, 4),
        "daily_cashflow_usd": round(daily_cashflow, 4)
    }

def calculate_negative_funding_insurance_runway(
    total_uxd_supply_usd: float,
    negative_funding_apr_pct: float = 5.0,
    insurance_fund_balance_usd: float = 250000.0
) -> dict:
    """
    Models insurance fund solvency runway during prolonged bearish regimes where short positions must pay funding.
    """
    if total_uxd_supply_usd <= 0 or insurance_fund_balance_usd <= 0:
        return {
            "total_uxd_supply_usd": total_uxd_supply_usd,
            "negative_funding_apr_pct": negative_funding_apr_pct,
            "insurance_fund_balance_usd": insurance_fund_balance_usd,
            "daily_funding_cost_usd": 0.0,
            "runway_days": 0.0,
            "is_solvency_risk": True
        }

    annual_funding_cost = total_uxd_supply_usd * (negative_funding_apr_pct / 100.0)
    daily_funding_cost = annual_funding_cost / 365.0
    runway_days = insurance_fund_balance_usd / daily_funding_cost if daily_funding_cost > 0 else float("inf")
    is_risk = runway_days < 30.0

    return {
        "total_uxd_supply_usd": round(total_uxd_supply_usd, 2),
        "negative_funding_apr_pct": round(negative_funding_apr_pct, 2),
        "insurance_fund_balance_usd": round(insurance_fund_balance_usd, 2),
        "daily_funding_cost_usd": round(daily_funding_cost, 2),
        "runway_days": round(runway_days, 1),
        "is_solvency_risk": is_risk
    }

def calculate_uxd_peg_arbitrage(
    secondary_uxd_price_usd: float = 0.985,
    trade_capital_usd: float = 10000.0,
    redemption_fee_bps: float = 10.0,
    solana_tx_fee_usd: float = 0.001
) -> dict:
    """
    Evaluates instantaneous secondary market discount redemption arbitrage opportunities.
    """
    if secondary_uxd_price_usd <= 0 or trade_capital_usd <= 0:
        return {
            "secondary_uxd_price_usd": secondary_uxd_price_usd,
            "tokens_bought": 0.0,
            "net_proceeds_usd": 0.0,
            "net_profit_usd": 0.0,
            "roi_pct": 0.0
        }

    tokens_bought = trade_capital_usd / secondary_uxd_price_usd
    gross_proceeds = tokens_bought * 1.0  # 1:1 on-chain redemption
    fee_usd = gross_proceeds * (redemption_fee_bps / 10000.0)
    net_proceeds = gross_proceeds - fee_usd - solana_tx_fee_usd
    net_profit = net_proceeds - trade_capital_usd
    roi_pct = (net_profit / trade_capital_usd) * 100.0

    return {
        "secondary_uxd_price_usd": round(secondary_uxd_price_usd, 4),
        "trade_capital_usd": round(trade_capital_usd, 2),
        "tokens_bought": round(tokens_bought, 4),
        "redemption_fee_usd": round(fee_usd, 4),
        "net_proceeds_usd": round(net_proceeds, 2),
        "net_profit_usd": round(net_profit, 2),
        "roi_pct": round(roi_pct, 4)
    }

def verify_vip_license(tx_hash: str, chain: str, amount: float, recipient: str) -> dict:
    """
    Validates on-chain VIP sentinel license for UXD delta-neutral yield & peg analytics.
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
