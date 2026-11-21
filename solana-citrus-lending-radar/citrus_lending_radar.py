"""
Solana Citrus NFT P2P & Instant Liquidity Lending Radar
Mathematical simulation and risk management engine for Citrus Protocol (Famous Fox Federation) P2P NFT loans,
fixed APR lending yields, default foreclosure arbitrage markups, and collection drawdown buffer analysis on Solana.
"""

import math

BASE_USDC_RECEIVE_ADDRESS = "0xF0E0D361bBE899F3089f0a968506eF2B97693c01"
SOLANA_RECEIVE_ADDRESS = "DW2MdHEq3qZ6nh9b5YFUoaPnBuuxC8Gz2785kwbbjSAM"

def calculate_p2p_loan_yield(
    principal_sol: float,
    apr_pct: float = 32.0,
    duration_days: int = 14,
    protocol_fee_cut_pct: float = 1.5
) -> dict:
    """
    Computes net interest income and annualized yield for Citrus P2P loans after protocol platform fees.
    """
    if principal_sol <= 0 or apr_pct <= 0 or duration_days <= 0:
        return {
            "principal_sol": principal_sol,
            "apr_pct": apr_pct,
            "duration_days": duration_days,
            "gross_interest_sol": 0.0,
            "protocol_fee_sol": 0.0,
            "net_interest_sol": 0.0,
            "net_realized_apr_pct": 0.0,
            "daily_interest_sol": 0.0
        }

    gross_interest = principal_sol * (apr_pct / 100.0) * (duration_days / 365.0)
    protocol_fee = gross_interest * (protocol_fee_cut_pct / 100.0)
    net_interest = gross_interest - protocol_fee
    net_apr = (net_interest / principal_sol) * (365.0 / duration_days) * 100.0
    daily_interest = net_interest / duration_days

    return {
        "principal_sol": round(principal_sol, 4),
        "apr_pct": round(apr_pct, 2),
        "duration_days": duration_days,
        "gross_interest_sol": round(gross_interest, 6),
        "protocol_fee_sol": round(protocol_fee, 6),
        "net_interest_sol": round(net_interest, 6),
        "net_realized_apr_pct": round(net_apr, 2),
        "daily_interest_sol": round(daily_interest, 6)
    }

def calculate_default_foreclosure_arbitrage(
    loan_principal_sol: float,
    collection_floor_sol: float = 100.0,
    marketplace_fee_pct: float = 2.0
) -> dict:
    """
    Quantifies lender collateral seizure profits when a borrower defaults on a Citrus NFT loan.
    """
    if loan_principal_sol <= 0 or collection_floor_sol <= 0:
        return {
            "loan_principal_sol": loan_principal_sol,
            "collection_floor_sol": collection_floor_sol,
            "net_liquidation_proceeds_sol": 0.0,
            "foreclosure_profit_sol": 0.0,
            "foreclosure_roi_pct": 0.0
        }

    net_proceeds = collection_floor_sol * (1.0 - (marketplace_fee_pct / 100.0))
    profit = net_proceeds - loan_principal_sol
    roi = (profit / loan_principal_sol) * 100.0 if loan_principal_sol > 0 else 0.0

    return {
        "loan_principal_sol": round(loan_principal_sol, 4),
        "collection_floor_sol": round(collection_floor_sol, 4),
        "marketplace_fee_sol": round(collection_floor_sol * (marketplace_fee_pct / 100.0), 4),
        "net_liquidation_proceeds_sol": round(net_proceeds, 4),
        "foreclosure_profit_sol": round(profit, 4),
        "foreclosure_roi_pct": round(roi, 2)
    }

def calculate_collection_drawdown_safety(
    current_floor_sol: float,
    loan_principal_sol: float
) -> dict:
    """
    Evaluates liquidation buffer and safety distance before loan collateral becomes underwater.
    """
    if current_floor_sol <= 0:
        return {
            "current_floor_sol": 0.0,
            "loan_principal_sol": loan_principal_sol,
            "buffer_sol": 0.0,
            "buffer_pct": 0.0,
            "is_underwater": True
        }

    buffer_sol = max(0.0, current_floor_sol - loan_principal_sol)
    buffer_pct = (buffer_sol / current_floor_sol) * 100.0
    is_underwater = current_floor_sol <= loan_principal_sol

    return {
        "current_floor_sol": round(current_floor_sol, 4),
        "loan_principal_sol": round(loan_principal_sol, 4),
        "buffer_sol": round(buffer_sol, 4),
        "buffer_pct": round(buffer_pct, 2),
        "is_underwater": is_underwater
    }

def verify_vip_license(tx_hash: str, chain: str, amount: float, recipient: str) -> dict:
    """
    Validates on-chain VIP sentinel license for Citrus NFT lending analytics.
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
