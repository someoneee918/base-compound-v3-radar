"""
Solana Switchboard On-Demand Oracles & Function VRF Radar
Mathematical modeling engine for Switchboard v3 On-Demand TEE oracle updates, verifiable randomness (VRF) fulfillment margins, attestation committee consensus variance, and push vs pull gas optimization on Solana.
"""

from typing import Dict, Any

def calculate_switchboard_ondemand_gas_savings(
    active_feeds_count: int = 5,
    daily_queries_per_feed: int = 10000,
    cost_per_ondemand_pull_usd: float = 0.0003,
    traditional_push_frequency_sec: int = 1,
    cost_per_push_tx_usd: float = 0.0005
) -> Dict[str, Any]:
    """
    Calculates cost decomposition and savings of Switchboard On-Demand pull feeds vs traditional push feeds:
    - Traditional push: 86,400 pushes / day per feed
    - Total Push Cost = active_feeds_count * 86,400 * cost_per_push_tx_usd
    - Total On-Demand Cost = active_feeds_count * daily_queries_per_feed * cost_per_ondemand_pull_usd
    """
    if active_feeds_count <= 0 or daily_queries_per_feed <= 0:
        raise ValueError("Feed count and queries must be positive.")

    daily_pushes_per_feed = 86400 / traditional_push_frequency_sec
    total_daily_push_cost_usd = active_feeds_count * daily_pushes_per_feed * cost_per_push_tx_usd
    total_daily_ondemand_cost_usd = active_feeds_count * daily_queries_per_feed * cost_per_ondemand_pull_usd

    daily_savings_usd = max(0.0, total_daily_push_cost_usd - total_daily_ondemand_cost_usd)
    annual_savings_usd = daily_savings_usd * 365.0
    savings_pct = (daily_savings_usd / total_daily_push_cost_usd * 100.0) if total_daily_push_cost_usd > 0 else 0.0

    return {
        "active_feeds_count": active_feeds_count,
        "daily_queries_per_feed": daily_queries_per_feed,
        "total_daily_push_cost_usd": round(total_daily_push_cost_usd, 2),
        "total_daily_ondemand_cost_usd": round(total_daily_ondemand_cost_usd, 2),
        "daily_savings_usd": round(daily_savings_usd, 2),
        "annual_savings_usd": round(annual_savings_usd, 2),
        "savings_pct": round(savings_pct, 2)
    }

def calculate_vrf_randomness_fulfillment_profit(
    daily_vrf_requests: int = 200,
    protocol_request_fee_sol: float = 0.002,
    execution_gas_sol: float = 0.000015,
    sol_price_usd: float = 150.0
) -> Dict[str, Any]:
    """
    Models relayer / crank profitability fulfilling Switchboard VRF randomness callbacks on Solana:
    - Net Profit Per Request = protocol_request_fee_sol - execution_gas_sol
    - Margin % = Net Profit / Fee
    """
    if daily_vrf_requests <= 0 or protocol_request_fee_sol <= 0 or sol_price_usd <= 0:
        raise ValueError("Requests, fee, and price must be positive.")

    net_profit_per_tx_sol = max(0.0, protocol_request_fee_sol - execution_gas_sol)
    net_profit_per_tx_usd = net_profit_per_tx_sol * sol_price_usd

    daily_profit_sol = net_profit_per_tx_sol * daily_vrf_requests
    daily_profit_usd = daily_profit_sol * sol_price_usd
    annual_profit_usd = daily_profit_usd * 365.0
    profit_margin_pct = (net_profit_per_tx_sol / protocol_request_fee_sol) * 100.0

    return {
        "daily_vrf_requests": daily_vrf_requests,
        "protocol_request_fee_sol": round(protocol_request_fee_sol, 6),
        "execution_gas_sol": round(execution_gas_sol, 6),
        "net_profit_per_tx_sol": round(net_profit_per_tx_sol, 6),
        "net_profit_per_tx_usd": round(net_profit_per_tx_usd, 4),
        "daily_profit_sol": round(daily_profit_sol, 4),
        "daily_profit_usd": round(daily_profit_usd, 2),
        "annual_profit_usd": round(annual_profit_usd, 2),
        "profit_margin_pct": round(profit_margin_pct, 2)
    }

def calculate_oracle_attestation_confidence_buffer(
    price_usd: float,
    tee_std_deviation_usd: float,
    max_safe_deviation_pct: float = 0.25
) -> Dict[str, Any]:
    """
    Evaluates Switchboard SGX TEE attestation consensus variance:
    Deviation Ratio = (std_dev / price) * 100
    Checks if oracle committee consensus variance is within safe operational bounds.
    """
    if price_usd <= 0 or tee_std_deviation_usd < 0:
        raise ValueError("Price must be positive and deviation non-negative.")

    deviation_ratio_pct = (tee_std_deviation_usd / price_usd) * 100.0
    is_consensus_healthy = deviation_ratio_pct <= max_safe_deviation_pct

    price_lower_bound = max(0.0, price_usd - (tee_std_deviation_usd * 2.0))
    price_upper_bound = price_usd + (tee_std_deviation_usd * 2.0)

    return {
        "price_usd": round(price_usd, 4),
        "tee_std_deviation_usd": round(tee_std_deviation_usd, 4),
        "deviation_ratio_pct": round(deviation_ratio_pct, 4),
        "is_consensus_healthy": is_consensus_healthy,
        "price_lower_bound": round(price_lower_bound, 4),
        "price_upper_bound": round(price_upper_bound, 4)
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
        "tier": "Switchboard On-Demand VIP Sentinel" if is_valid else "Unverified"
    }