"""
Solana Dialect Actions & Blinks Creator Fee & Compute Unit Radar
Mathematical modeling engine for Solana Actions and Blockchain Links (Blinks) creator affiliate monetization, priority compute unit (CU) landing rates, and dropped conversion mitigation.
"""

from typing import Dict, Any

def calculate_blink_creator_revenue(
    daily_impressions: int,
    conversion_rate_pct: float,
    avg_tx_volume_usd: float,
    creator_fee_pct: float
) -> Dict[str, Any]:
    """
    Calculates creator and affiliate revenue from shareable Solana Blinks across social media (X, Discord, Telegram).
    """
    if daily_impressions <= 0 or conversion_rate_pct <= 0 or avg_tx_volume_usd <= 0:
        raise ValueError("Impressions, conversion rate, and volume must be positive.")

    daily_executed_txs = int(daily_impressions * (conversion_rate_pct / 100.0))
    total_daily_volume_usd = daily_executed_txs * avg_tx_volume_usd
    daily_creator_revenue_usd = total_daily_volume_usd * (creator_fee_pct / 100.0)
    monthly_revenue_usd = daily_creator_revenue_usd * 30.0
    annual_revenue_usd = daily_creator_revenue_usd * 365.0

    return {
        "daily_impressions": daily_impressions,
        "conversion_rate_pct": round(conversion_rate_pct, 2),
        "daily_executed_txs": daily_executed_txs,
        "avg_tx_volume_usd": round(avg_tx_volume_usd, 2),
        "total_daily_volume_usd": round(total_daily_volume_usd, 2),
        "creator_fee_pct": round(creator_fee_pct, 2),
        "daily_creator_revenue_usd": round(daily_creator_revenue_usd, 2),
        "monthly_revenue_usd": round(monthly_revenue_usd, 2),
        "annual_revenue_usd": round(annual_revenue_usd, 2)
    }

def calculate_compute_unit_landing_rate(
    cu_limit: int,
    micro_lamports_per_cu: int,
    current_p75_micro_lamports: int = 30000
) -> Dict[str, Any]:
    """
    Calculates transaction landing probability and fee breakdown for Solana Action/Blink execution.
    """
    if cu_limit <= 0:
        raise ValueError("CU limit must be positive.")

    base_fee_lamports = 5000
    priority_fee_lamports = int((cu_limit * micro_lamports_per_cu) / 1_000_000)
    total_tx_fee_lamports = base_fee_lamports + priority_fee_lamports
    total_tx_fee_sol = total_tx_fee_lamports / 1e9

    if micro_lamports_per_cu >= current_p75_micro_lamports * 1.5:
        landing_rate_pct = 98.5
        tier = "High Priority (Immediate Next Block)"
    elif micro_lamports_per_cu >= current_p75_micro_lamports:
        landing_rate_pct = 92.0
        tier = "Standard Competitive (1-2 Blocks)"
    else:
        landing_rate_pct = 65.0
        tier = "Low / Dropped under Congestion"

    return {
        "cu_limit": cu_limit,
        "micro_lamports_per_cu": micro_lamports_per_cu,
        "base_fee_lamports": base_fee_lamports,
        "priority_fee_lamports": priority_fee_lamports,
        "total_tx_fee_lamports": total_tx_fee_lamports,
        "total_tx_fee_sol": round(total_tx_fee_sol, 8),
        "landing_rate_pct": landing_rate_pct,
        "priority_tier": tier
    }

def calculate_conversion_loss_due_to_drops(
    daily_impressions: int,
    conversion_rate_pct: float,
    avg_revenue_per_tx_usd: float,
    landing_rate_pct: float
) -> Dict[str, Any]:
    """
    Quantifies revenue lost due to transaction drops from inadequate priority fees on social Blinks.
    """
    potential_txs = daily_impressions * (conversion_rate_pct / 100.0)
    failed_txs = potential_txs * ((100.0 - landing_rate_pct) / 100.0)
    daily_lost_revenue_usd = failed_txs * avg_revenue_per_tx_usd
    annual_lost_revenue_usd = daily_lost_revenue_usd * 365.0

    return {
        "potential_daily_txs": round(potential_txs, 1),
        "failed_daily_txs": round(failed_txs, 1),
        "daily_lost_revenue_usd": round(daily_lost_revenue_usd, 2),
        "annual_lost_revenue_usd": round(annual_lost_revenue_usd, 2)
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
        "tier": "Dialect Blinks Creator VIP Sentinel" if is_valid else "Unverified"
    }
