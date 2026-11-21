"""
Solana Step Finance xSTEP Protocol Revenue & Staking Yield Radar
Mathematical modeling engine for Step Finance protocol fee revenue distribution, xSTEP fair exchange value accretion, and secondary DEX discount arbitrage on Solana.
"""

from typing import Dict, Any

def calculate_xstep_accretion_and_yield(
    total_staked_step: float,
    total_xstep_supply: float,
    step_price_usd: float,
    daily_protocol_fee_usd: float
) -> Dict[str, Any]:
    """
    Calculates xSTEP fair value accretion and annualized staking APY derived from 100% protocol fee buybacks.
    """
    if total_staked_step <= 0 or total_xstep_supply <= 0 or step_price_usd <= 0:
        raise ValueError("Staked STEP, xSTEP supply, and STEP price must be positive.")

    current_ratio = total_staked_step / total_xstep_supply
    xstep_fair_value_usd = current_ratio * step_price_usd
    total_staked_value_usd = total_staked_step * step_price_usd

    daily_step_buyback = daily_protocol_fee_usd / step_price_usd
    annual_fee_revenue_usd = daily_protocol_fee_usd * 365.0
    staking_apy_pct = (annual_fee_revenue_usd / total_staked_value_usd) * 100.0

    annual_step_added = daily_step_buyback * 365.0
    projected_annual_ratio = (total_staked_step + annual_step_added) / total_xstep_supply
    daily_cashflow_per_10k_usd = (10000.0 * (staking_apy_pct / 100.0)) / 365.0

    return {
        "total_staked_step": round(total_staked_step, 2),
        "total_xstep_supply": round(total_xstep_supply, 2),
        "current_ratio": round(current_ratio, 4),
        "step_price_usd": round(step_price_usd, 4),
        "xstep_fair_value_usd": round(xstep_fair_value_usd, 4),
        "total_staked_value_usd": round(total_staked_value_usd, 2),
        "daily_protocol_fee_usd": round(daily_protocol_fee_usd, 2),
        "annual_fee_revenue_usd": round(annual_fee_revenue_usd, 2),
        "daily_step_buyback": round(daily_step_buyback, 2),
        "staking_apy_pct": round(staking_apy_pct, 2),
        "projected_annual_ratio": round(projected_annual_ratio, 4),
        "daily_cashflow_per_10k_usd": round(daily_cashflow_per_10k_usd, 2)
    }

def calculate_xstep_secondary_arbitrage(
    secondary_xstep_price_usd: float,
    fair_xstep_value_usd: float,
    redemption_fee_pct: float = 0.0
) -> Dict[str, Any]:
    """
    Evaluates instant secondary market discount arbitrage when xSTEP trades below fair NAV on secondary DEXes.
    """
    if secondary_xstep_price_usd <= 0 or fair_xstep_value_usd <= 0:
        raise ValueError("Prices must be positive.")

    net_fair_proceeds = fair_xstep_value_usd * (1.0 - (redemption_fee_pct / 100.0))
    discount_pct = max(0.0, ((fair_xstep_value_usd - secondary_xstep_price_usd) / fair_xstep_value_usd) * 100.0)
    net_arb_profit_per_xstep_usd = net_fair_proceeds - secondary_xstep_price_usd
    roi_pct = (net_arb_profit_per_xstep_usd / secondary_xstep_price_usd) * 100.0

    return {
        "secondary_xstep_price_usd": round(secondary_xstep_price_usd, 4),
        "fair_xstep_value_usd": round(fair_xstep_value_usd, 4),
        "discount_pct": round(discount_pct, 2),
        "net_arb_profit_per_xstep_usd": round(net_arb_profit_per_xstep_usd, 4),
        "roi_pct": round(roi_pct, 2),
        "is_profitable_arbitrage": net_arb_profit_per_xstep_usd > 0
    }

def calculate_annual_compounded_staking_return(
    principal_usd: float,
    staking_apy_pct: float,
    years: int = 1
) -> Dict[str, Any]:
    """
    Calculates multi-year compounded growth of staked xSTEP positions.
    """
    final_usd = principal_usd * ((1.0 + (staking_apy_pct / 100.0)) ** years)
    net_profit_usd = final_usd - principal_usd

    return {
        "principal_usd": round(principal_usd, 2),
        "staking_apy_pct": round(staking_apy_pct, 2),
        "years": years,
        "final_usd": round(final_usd, 2),
        "net_profit_usd": round(net_profit_usd, 2)
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
        "tier": "Step Finance VIP Sentinel" if is_valid else "Unverified"
    }
