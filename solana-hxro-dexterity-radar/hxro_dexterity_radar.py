"""
Solana Hxro Network / Dexterity Institutional Derivatives & Risk Engine Radar
Mathematical modeling engine for Hxro Dexterity SPAN-like cross-collateral portfolio margin, trader funding carry, and liquidator seizure bounties on Solana.
"""

from typing import Dict, Any

def calculate_portfolio_margin_health(
    collateral_deposits: Dict[str, Dict[str, float]],
    position_notional_usd: float,
    base_mmr_pct: float = 5.0,
    concentration_factor: float = 1.0
) -> Dict[str, Any]:
    """
    Calculates portfolio margin account equity, haircut-adjusted collateral, and health factor.
    Health Factor = Haircut-Adjusted Equity / Scaled MMR
    Liquidation triggered when Health Factor < 1.0.
    """
    if position_notional_usd < 0:
        raise ValueError("Position notional cannot be negative.")

    total_effective_collateral = 0.0
    gross_collateral_usd = 0.0

    for asset, details in collateral_deposits.items():
        amount = details.get("amount", 0.0)
        price = details.get("price", 0.0)
        haircut = details.get("haircut_pct", 0.0)

        val = amount * price
        gross_collateral_usd += val
        total_effective_collateral += val * (1.0 - (haircut / 100.0))

    scaled_mmr_pct = base_mmr_pct + (concentration_factor * (position_notional_usd / 100000.0))
    mmr_required_usd = position_notional_usd * (scaled_mmr_pct / 100.0)

    if mmr_required_usd > 0:
        health_factor = total_effective_collateral / mmr_required_usd
        drawdown_buffer_pct = max(0.0, (1.0 - (mmr_required_usd / total_effective_collateral)) * 100.0) if total_effective_collateral > 0 else 0.0
    else:
        health_factor = 999.0
        drawdown_buffer_pct = 100.0

    return {
        "gross_collateral_usd": round(gross_collateral_usd, 2),
        "total_effective_collateral": round(total_effective_collateral, 2),
        "position_notional_usd": round(position_notional_usd, 2),
        "scaled_mmr_pct": round(scaled_mmr_pct, 2),
        "mmr_required_usd": round(mmr_required_usd, 2),
        "health_factor": round(health_factor, 3),
        "drawdown_buffer_pct": round(drawdown_buffer_pct, 2),
        "is_safe": health_factor >= 1.0
    }

def calculate_funding_carry_yield(
    position_size_usd: float,
    mark_price: float,
    index_price: float,
    funding_interval_hours: float = 8.0,
    is_long: bool = False
) -> Dict[str, Any]:
    """
    Calculates funding velocity and annualized carry yield.
    Short positions receive positive funding when mark price > index price.
    """
    if index_price <= 0:
        raise ValueError("Index price must be positive.")

    premium_pct = ((mark_price - index_price) / index_price) * 100.0
    # Clamped at ±0.75% per 8h interval
    funding_rate_8h_pct = max(-0.75, min(0.75, premium_pct * 0.10))
    intervals_per_year = 8760.0 / funding_interval_hours
    annualized_funding_apr_pct = funding_rate_8h_pct * intervals_per_year

    net_carry_apr_pct = -annualized_funding_apr_pct if is_long else annualized_funding_apr_pct
    daily_cashflow_usd = (position_size_usd * (net_carry_apr_pct / 100.0)) / 365.0

    return {
        "position_size_usd": round(position_size_usd, 2),
        "mark_price": round(mark_price, 4),
        "index_price": round(index_price, 4),
        "premium_pct": round(premium_pct, 4),
        "funding_rate_8h_pct": round(funding_rate_8h_pct, 4),
        "net_carry_apr_pct": round(net_carry_apr_pct, 2),
        "daily_cashflow_usd": round(daily_cashflow_usd, 2),
        "is_profitable_carry": net_carry_apr_pct > 0
    }

def calculate_liquidator_seizure_profit(
    insolvent_notional_usd: float,
    liquidation_bonus_pct: float = 3.5,
    sol_priority_fee_usd: float = 0.05,
    jito_tip_usd: float = 2.50
) -> Dict[str, Any]:
    """
    Calculates liquidator net profit from seizing and liquidating an underwater position on Hxro Dexterity.
    """
    if insolvent_notional_usd <= 0:
        raise ValueError("Insolvent notional must be positive.")

    gross_seizure_bounty_usd = insolvent_notional_usd * (liquidation_bonus_pct / 100.0)
    tx_cost_usd = sol_priority_fee_usd + jito_tip_usd
    net_profit_usd = gross_seizure_bounty_usd - tx_cost_usd
    roi_pct = (net_profit_usd / tx_cost_usd) * 100.0 if tx_cost_usd > 0 else 0.0

    return {
        "insolvent_notional_usd": round(insolvent_notional_usd, 2),
        "liquidation_bonus_pct": round(liquidation_bonus_pct, 2),
        "gross_seizure_bounty_usd": round(gross_seizure_bounty_usd, 2),
        "tx_cost_usd": round(tx_cost_usd, 2),
        "net_profit_usd": round(net_profit_usd, 2),
        "roi_pct": round(roi_pct, 2),
        "is_profitable": net_profit_usd > 0
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
        "tier": "Hxro Dexterity VIP Sentinel" if is_valid else "Unverified"
    }
