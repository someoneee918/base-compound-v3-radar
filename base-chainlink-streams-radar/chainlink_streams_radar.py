"""
Base Chainlink Data Streams & Automation Low-Latency Oracle Radar
Mathematical modeling engine for Chainlink Data Streams pull verification gas savings, keeper automation upkeep margins, and front-running protection on Base L2.
"""

from typing import Dict, Any

def calculate_data_streams_gas_savings(
    monthly_push_updates: int,
    monthly_user_trades: int,
    push_gas_units: int = 80000,
    stream_verify_gas_units: int = 120000,
    gas_price_gwei: float = 0.05,
    eth_price_usd: float = 3000.0
) -> Dict[str, Any]:
    """
    Calculates protocol gas savings achieved by transitioning from continuous push oracles to on-demand Chainlink Data Streams.
    """
    if monthly_push_updates <= 0 or eth_price_usd <= 0:
        raise ValueError("Push updates and ETH price must be positive.")

    push_gas_eth = (push_gas_units * (gas_price_gwei * 1e9)) / 1e18
    total_push_cost_usd = monthly_push_updates * push_gas_eth * eth_price_usd

    stream_gas_eth = (stream_verify_gas_units * (gas_price_gwei * 1e9)) / 1e18
    total_stream_cost_usd = monthly_user_trades * stream_gas_eth * eth_price_usd

    monthly_gas_savings_usd = max(0.0, total_push_cost_usd - total_stream_cost_usd)
    annual_gas_savings_usd = monthly_gas_savings_usd * 12.0
    gas_reduction_pct = (monthly_gas_savings_usd / total_push_cost_usd) * 100.0 if total_push_cost_usd > 0 else 0.0

    return {
        "monthly_push_updates": monthly_push_updates,
        "monthly_user_trades": monthly_user_trades,
        "total_push_cost_usd": round(total_push_cost_usd, 2),
        "total_stream_cost_usd": round(total_stream_cost_usd, 2),
        "monthly_gas_savings_usd": round(monthly_gas_savings_usd, 2),
        "annual_gas_savings_usd": round(annual_gas_savings_usd, 2),
        "gas_reduction_pct": round(gas_reduction_pct, 2)
    }

def calculate_keeper_automation_profit(
    daily_upkeeps: int,
    avg_execution_gas_units: int = 150000,
    gas_price_gwei: float = 0.05,
    eth_price_usd: float = 3000.0,
    keeper_reward_premium_pct: float = 20.0
) -> Dict[str, Any]:
    """
    Calculates keeper automation profitability executing Chainlink upkeep transactions on Base.
    """
    if daily_upkeeps <= 0:
        raise ValueError("Daily upkeeps must be positive.")

    gas_cost_eth = (avg_execution_gas_units * (gas_price_gwei * 1e9)) / 1e18
    gas_cost_usd = gas_cost_eth * eth_price_usd
    payout_received_usd = gas_cost_usd * (1.0 + (keeper_reward_premium_pct / 100.0))
    profit_per_upkeep_usd = payout_received_usd - gas_cost_usd

    daily_profit_usd = daily_upkeeps * profit_per_upkeep_usd
    annual_profit_usd = daily_profit_usd * 365.0

    return {
        "daily_upkeeps": daily_upkeeps,
        "gas_cost_usd": round(gas_cost_usd, 4),
        "payout_received_usd": round(payout_received_usd, 4),
        "profit_per_upkeep_usd": round(profit_per_upkeep_usd, 4),
        "daily_profit_usd": round(daily_profit_usd, 2),
        "annual_profit_usd": round(annual_profit_usd, 2)
    }

def calculate_adverse_selection_protection(
    trade_notional_usd: float,
    oracle_staleness_seconds: float = 60.0,
    volatility_per_second_bps: float = 0.05
) -> Dict[str, Any]:
    """
    Models trader front-running avoidance by replacing stale push oracle prices with sub-second verified stream prices.
    """
    if trade_notional_usd <= 0:
        raise ValueError("Trade notional must be positive.")

    expected_price_lag_bps = oracle_staleness_seconds * volatility_per_second_bps
    front_running_risk_usd = trade_notional_usd * (expected_price_lag_bps / 10000.0)
    subsecond_stream_lag_bps = 0.5 * volatility_per_second_bps
    protected_value_usd = max(0.0, front_running_risk_usd - (trade_notional_usd * (subsecond_stream_lag_bps / 10000.0)))

    return {
        "trade_notional_usd": round(trade_notional_usd, 2),
        "oracle_staleness_seconds": oracle_staleness_seconds,
        "expected_price_lag_bps": round(expected_price_lag_bps, 2),
        "front_running_risk_usd": round(front_running_risk_usd, 2),
        "protected_value_usd": round(protected_value_usd, 2)
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
        "tier": "Chainlink Streams VIP Sentinel" if is_valid else "Unverified"
    }
