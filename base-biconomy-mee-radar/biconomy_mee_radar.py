"""
Base Biconomy Modular Execution Environment (MEE) Cross-Chain UserOp & Gas Sponsorship Radar
Mathematical modeling engine for Biconomy ERC-4337 Account Abstraction Paymaster sponsorship margins, UserOp bundling economics, EntryPoint treasury runway, and cross-chain MEE intent execution on Base L2.
"""

from typing import Dict, Any

def calculate_biconomy_userop_bundling_profit(
    userop_count: int,
    avg_execution_gas: int = 150000,
    base_l2_fee_gwei: float = 0.005,
    l1_data_fee_usd: float = 0.0008,
    eth_price_usd: float = 3000.0,
    paymaster_markup_pct: float = 10.0
) -> Dict[str, Any]:
    """
    Calculates cost decomposition and bundler/paymaster profit for sponsoring & executing UserOps on Base L2:
    - Base L2 Gas Cost = avg_execution_gas * base_l2_fee_gwei * 1e-9 * eth_price_usd
    - Total Cost Per Op = L2 Gas Cost + L1 Data Fee
    - Revenue Per Op = Total Cost Per Op * (1 + paymaster_markup_pct / 100)
    - Net Profit = Revenue - Cost
    """
    if userop_count <= 0 or avg_execution_gas <= 0 or eth_price_usd <= 0:
        raise ValueError("UserOp count, gas, and ETH price must be positive.")

    l2_gas_cost_usd = avg_execution_gas * (base_l2_fee_gwei * 1e-9) * eth_price_usd
    actual_cost_per_op_usd = l2_gas_cost_usd + l1_data_fee_usd

    markup_ratio = 1.0 + (paymaster_markup_pct / 100.0)
    revenue_per_op_usd = actual_cost_per_op_usd * markup_ratio
    profit_per_op_usd = revenue_per_op_usd - actual_cost_per_op_usd

    total_bundle_cost_usd = actual_cost_per_op_usd * userop_count
    total_bundle_revenue_usd = revenue_per_op_usd * userop_count
    total_bundle_profit_usd = profit_per_op_usd * userop_count

    return {
        "userop_count": userop_count,
        "l2_gas_cost_usd": round(l2_gas_cost_usd, 6),
        "l1_data_fee_usd": round(l1_data_fee_usd, 6),
        "actual_cost_per_op_usd": round(actual_cost_per_op_usd, 6),
        "paymaster_markup_pct": round(paymaster_markup_pct, 2),
        "revenue_per_op_usd": round(revenue_per_op_usd, 6),
        "profit_per_op_usd": round(profit_per_op_usd, 6),
        "total_bundle_cost_usd": round(total_bundle_cost_usd, 4),
        "total_bundle_revenue_usd": round(total_bundle_revenue_usd, 4),
        "total_bundle_profit_usd": round(total_bundle_profit_usd, 4)
    }

def calculate_paymaster_treasury_runway_and_alerts(
    entrypoint_deposit_usd: float,
    daily_userop_volume: int,
    actual_cost_per_op_usd: float,
    low_runway_alert_days: float = 3.0
) -> Dict[str, Any]:
    """
    Tracks Paymaster balance in EntryPoint contract on Base and calculates runway days.
    """
    if entrypoint_deposit_usd <= 0 or daily_userop_volume <= 0 or actual_cost_per_op_usd <= 0:
        raise ValueError("Deposit, volume, and cost must be positive.")

    daily_burn_usd = daily_userop_volume * actual_cost_per_op_usd
    runway_days = entrypoint_deposit_usd / daily_burn_usd if daily_burn_usd > 0 else 999.0
    is_runway_critical = runway_days <= low_runway_alert_days

    suggested_topup_usd = max(0.0, (7.0 - runway_days) * daily_burn_usd) if is_runway_critical else 0.0

    return {
        "entrypoint_deposit_usd": round(entrypoint_deposit_usd, 2),
        "daily_userop_volume": daily_userop_volume,
        "daily_burn_usd": round(daily_burn_usd, 2),
        "runway_days": round(runway_days, 1),
        "is_runway_critical": is_runway_critical,
        "suggested_topup_usd": round(suggested_topup_usd, 2)
    }

def calculate_mee_cross_chain_intent_settlement(
    intent_volume_usd: float,
    solver_quote_spread_bps: float = 8.0,
    bridging_gas_cost_usd: float = 0.15
) -> Dict[str, Any]:
    """
    Models Modular Execution Environment (MEE) cross-chain intent settlement profit for relayers/solvers.
    """
    if intent_volume_usd <= 0:
        raise ValueError("Intent volume must be positive.")

    gross_solver_spread_usd = intent_volume_usd * (solver_quote_spread_bps / 10000.0)
    net_solver_profit_usd = max(0.0, gross_solver_spread_usd - bridging_gas_cost_usd)
    net_margin_bps = (net_solver_profit_usd / intent_volume_usd) * 10000.0

    return {
        "intent_volume_usd": round(intent_volume_usd, 2),
        "solver_quote_spread_bps": round(solver_quote_spread_bps, 2),
        "bridging_gas_cost_usd": round(bridging_gas_cost_usd, 4),
        "gross_solver_spread_usd": round(gross_solver_spread_usd, 4),
        "net_solver_profit_usd": round(net_solver_profit_usd, 4),
        "net_margin_bps": round(net_margin_bps, 2)
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
        "tier": "Biconomy MEE VIP Sentinel" if is_valid else "Unverified"
    }