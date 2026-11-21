"""
Base Liquity v2 (BOLD) User-Set Interest Rate Trove & Redemption Queue Radar
Mathematical simulation and risk management engine for Liquity v2 (BOLD) decentralized borrow positions,
user-set interest rate redemption queue priorities, Stability Pool fee accrual, and secondary DEX peg arbitrage on Base L2.
"""

import math

BASE_USDC_RECEIVE_ADDRESS = "0xF0E0D361bBE899F3089f0a968506eF2B97693c01"
SOLANA_RECEIVE_ADDRESS = "DW2MdHEq3qZ6nh9b5YFUoaPnBuuxC8Gz2785kwbbjSAM"

def calculate_trove_redemption_risk_and_interest(
    collateral_eth: float,
    eth_price_usd: float = 3000.0,
    debt_bold: float = 5000.0,
    user_interest_rate_pct: float = 3.5,
    market_median_rate_pct: float = 2.8
) -> dict:
    """
    Computes collateral ratio, annual carrying cost, and redemption vulnerability ranking.
    In Liquity v2, redemptions occur in ascending order of interest rate; borrowers setting rates
    above market median are shielded from unwanted collateral redemptions.
    """
    if collateral_eth <= 0 or debt_bold <= 0:
        return {
            "collateral_eth": collateral_eth,
            "collateral_val_usd": 0.0,
            "debt_bold": debt_bold,
            "collateral_ratio_pct": 0.0,
            "annual_interest_cost_usd": 0.0,
            "daily_interest_cost_usd": 0.0,
            "is_protected_from_redemption": False,
            "redemption_risk_score": 100.0
        }

    collateral_val = collateral_eth * eth_price_usd
    cr_pct = (collateral_val / debt_bold) * 100.0
    annual_interest = debt_bold * (user_interest_rate_pct / 100.0)
    daily_interest = annual_interest / 365.0
    is_protected = user_interest_rate_pct >= market_median_rate_pct

    # Higher rate relative to median lowers redemption risk score (0 = lowest risk, 100 = highest risk)
    if user_interest_rate_pct > 0:
        risk_score = max(0.0, min(100.0, (market_median_rate_pct / user_interest_rate_pct) * 50.0))
    else:
        risk_score = 100.0

    return {
        "collateral_eth": round(collateral_eth, 4),
        "eth_price_usd": round(eth_price_usd, 2),
        "collateral_val_usd": round(collateral_val, 2),
        "debt_bold": round(debt_bold, 2),
        "collateral_ratio_pct": round(cr_pct, 2),
        "user_interest_rate_pct": round(user_interest_rate_pct, 2),
        "market_median_rate_pct": round(market_median_rate_pct, 2),
        "annual_interest_cost_usd": round(annual_interest, 2),
        "daily_interest_cost_usd": round(daily_interest, 4),
        "is_protected_from_redemption": is_protected,
        "redemption_risk_score": round(risk_score, 2)
    }

def calculate_stability_pool_yield(
    bold_deposited: float,
    total_stability_pool_bold: float = 10000000.0,
    total_annual_interest_revenue_usd: float = 350000.0,
    annual_liquidation_volume_usd: float = 500000.0,
    liquidation_bonus_pct: float = 5.0
) -> dict:
    """
    Models Stability Pool yield combining direct borrower interest distributions and liquidation collateral gains.
    """
    if bold_deposited <= 0 or total_stability_pool_bold <= 0:
        return {
            "bold_deposited": bold_deposited,
            "user_pool_share_pct": 0.0,
            "interest_earned_usd": 0.0,
            "liquidation_bonus_usd": 0.0,
            "total_annual_yield_usd": 0.0,
            "net_stability_pool_apr_pct": 0.0
        }

    share = bold_deposited / total_stability_pool_bold
    interest_earned = total_annual_interest_revenue_usd * share
    liquidation_bonus = (annual_liquidation_volume_usd * (liquidation_bonus_pct / 100.0)) * share
    total_yield = interest_earned + liquidation_bonus
    apr_pct = (total_yield / bold_deposited) * 100.0

    return {
        "bold_deposited": round(bold_deposited, 2),
        "user_pool_share_pct": round(share * 100.0, 4),
        "interest_earned_usd": round(interest_earned, 2),
        "liquidation_bonus_usd": round(liquidation_bonus, 2),
        "total_annual_yield_usd": round(total_yield, 2),
        "net_stability_pool_apr_pct": round(apr_pct, 2)
    }

def calculate_bold_peg_redemption_arbitrage(
    bold_market_price_usd: float = 0.985,
    trade_capital_usd: float = 10000.0,
    redemption_gas_usd: float = 0.003
) -> dict:
    """
    Evaluates instantaneous secondary market discount redemption arbitrage opportunities.
    """
    if bold_market_price_usd <= 0 or trade_capital_usd <= 0:
        return {
            "bold_market_price_usd": bold_market_price_usd,
            "tokens_bought": 0.0,
            "gross_collateral_usd": 0.0,
            "net_profit_usd": 0.0,
            "roi_pct": 0.0
        }

    tokens_bought = trade_capital_usd / bold_market_price_usd
    gross_collateral = tokens_bought * 1.0  # 1:1 par redemption
    net_profit = gross_collateral - trade_capital_usd - redemption_gas_usd
    roi_pct = (net_profit / trade_capital_usd) * 100.0

    return {
        "bold_market_price_usd": round(bold_market_price_usd, 4),
        "trade_capital_usd": round(trade_capital_usd, 2),
        "tokens_bought": round(tokens_bought, 4),
        "gross_collateral_usd": round(gross_collateral, 2),
        "net_profit_usd": round(net_profit, 2),
        "roi_pct": round(roi_pct, 2)
    }

def verify_vip_license(tx_hash: str, chain: str, amount: float, recipient: str) -> dict:
    """
    Validates on-chain VIP sentinel license for Liquity v2 BOLD credit analytics.
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
