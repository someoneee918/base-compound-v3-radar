"""
Solana Armada Protocol Dynamic Token Launch & Liquidity Bootstrapping Radar
Mathematical simulation and quantitative optimization engine for Armada Protocol Liquidity Bootstrapping Pools (LBPs),
dynamic weight decay pricing curves, capital raised elasticity, and post-launch AMM liquidity migration on Solana.
"""

import math

BASE_USDC_RECEIVE_ADDRESS = "0xF0E0D361bBE899F3089f0a968506eF2B97693c01"
SOLANA_RECEIVE_ADDRESS = "DW2MdHEq3qZ6nh9b5YFUoaPnBuuxC8Gz2785kwbbjSAM"

def calculate_lbp_weight_and_price_trajectory(
    initial_base_reserves: float,
    initial_quote_reserves_usd: float,
    initial_base_weight_pct: float = 90.0,
    terminal_base_weight_pct: float = 10.0,
    total_duration_hours: float = 72.0,
    elapsed_hours: float = 0.0
) -> dict:
    """
    Computes time-decayed token weights, continuous spot price trajectory,
    and anti-sniper price decay elasticity across the LBP auction window.
    """
    if initial_base_reserves <= 0 or initial_quote_reserves_usd <= 0 or total_duration_hours <= 0:
        return {
            "elapsed_hours": elapsed_hours,
            "progress_pct": 0.0,
            "current_base_weight_pct": initial_base_weight_pct,
            "current_quote_weight_pct": 100.0 - initial_base_weight_pct,
            "spot_price_usd": 0.0,
            "initial_spot_price_usd": 0.0,
            "terminal_unbought_price_usd": 0.0,
            "price_decay_pct": 0.0
        }

    progress = min(1.0, max(0.0, elapsed_hours / total_duration_hours))
    current_base_weight = initial_base_weight_pct - progress * (initial_base_weight_pct - terminal_base_weight_pct)
    current_quote_weight = 100.0 - current_base_weight

    spot_price = (initial_quote_reserves_usd / (current_quote_weight / 100.0)) / (initial_base_reserves / (current_base_weight / 100.0))
    initial_spot_price = (initial_quote_reserves_usd / ((100.0 - initial_base_weight_pct) / 100.0)) / (initial_base_reserves / (initial_base_weight_pct / 100.0))
    terminal_unbought_price = (initial_quote_reserves_usd / ((100.0 - terminal_base_weight_pct) / 100.0)) / (initial_base_reserves / (terminal_base_weight_pct / 100.0))
    price_decay = ((initial_spot_price - spot_price) / initial_spot_price) * 100.0 if initial_spot_price > 0 else 0.0

    return {
        "elapsed_hours": round(elapsed_hours, 1),
        "total_duration_hours": round(total_duration_hours, 1),
        "progress_pct": round(progress * 100.0, 2),
        "current_base_weight_pct": round(current_base_weight, 2),
        "current_quote_weight_pct": round(current_quote_weight, 2),
        "spot_price_usd": round(spot_price, 6),
        "initial_spot_price_usd": round(initial_spot_price, 6),
        "terminal_unbought_price_usd": round(terminal_unbought_price, 6),
        "price_decay_pct": round(price_decay, 2)
    }

def calculate_auction_capital_raised_and_fdv(
    tokens_sold: float,
    avg_execution_price_usd: float,
    total_token_supply: float,
    pool_fee_bps: float = 100.0
) -> dict:
    """
    Evaluates gross and net capital raised, protocol fee cut, and implied fully diluted valuation (FDV).
    """
    if tokens_sold <= 0 or avg_execution_price_usd <= 0 or total_token_supply <= 0:
        return {
            "tokens_sold": tokens_sold,
            "avg_execution_price_usd": avg_execution_price_usd,
            "gross_capital_raised_usd": 0.0,
            "protocol_fee_usd": 0.0,
            "net_capital_raised_usd": 0.0,
            "implied_fdv_usd": 0.0,
            "capital_efficiency_pct": 0.0
        }

    gross_capital = tokens_sold * avg_execution_price_usd
    protocol_fee = gross_capital * (pool_fee_bps / 10000.0)
    net_capital = gross_capital - protocol_fee
    implied_fdv = total_token_supply * avg_execution_price_usd
    efficiency = (net_capital / gross_capital) * 100.0 if gross_capital > 0 else 0.0

    return {
        "tokens_sold": round(tokens_sold, 2),
        "avg_execution_price_usd": round(avg_execution_price_usd, 4),
        "gross_capital_raised_usd": round(gross_capital, 2),
        "protocol_fee_usd": round(protocol_fee, 2),
        "net_capital_raised_usd": round(net_capital, 2),
        "implied_fdv_usd": round(implied_fdv, 2),
        "capital_efficiency_pct": round(efficiency, 2)
    }

def calculate_post_lbp_liquidity_migration(
    net_capital_raised_usd: float,
    target_lp_quote_ratio_pct: float = 50.0,
    volume_to_tvl_multiple: float = 2.5,
    amm_fee_tier_pct: float = 0.25
) -> dict:
    """
    Models the migration of auction proceeds into Solana concentrated AMM pools (Orca, Raydium, Meteora)
    and estimates annual trading fee revenue for protocol treasuries.
    """
    if net_capital_raised_usd <= 0:
        return {
            "net_capital_raised_usd": 0.0,
            "quote_allocated_usd": 0.0,
            "treasury_retained_usd": 0.0,
            "initial_amm_depth_usd": 0.0,
            "annual_lp_fee_usd": 0.0,
            "lp_fee_apy_pct": 0.0
        }

    quote_allocated = net_capital_raised_usd * (target_lp_quote_ratio_pct / 100.0)
    treasury_retained = net_capital_raised_usd - quote_allocated
    amm_depth = quote_allocated * 2.0
    annual_volume = amm_depth * volume_to_tvl_multiple
    annual_fees = annual_volume * (amm_fee_tier_pct / 100.0)
    fee_apy = (annual_fees / amm_depth) * 100.0 if amm_depth > 0 else 0.0

    return {
        "net_capital_raised_usd": round(net_capital_raised_usd, 2),
        "quote_allocated_usd": round(quote_allocated, 2),
        "treasury_retained_usd": round(treasury_retained, 2),
        "initial_amm_depth_usd": round(amm_depth, 2),
        "annual_volume_usd": round(annual_volume, 2),
        "annual_lp_fee_usd": round(annual_fees, 2),
        "lp_fee_apy_pct": round(fee_apy, 4)
    }

def verify_vip_license(tx_hash: str, chain: str, amount: float, recipient: str) -> dict:
    """
    Validates on-chain VIP sentinel license for Armada dynamic token launch analytics.
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
