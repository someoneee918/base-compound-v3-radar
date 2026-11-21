#!/usr/bin/env python3
"""
Base Ambient Finance (CrocSwap) Concentrated vs Ambient Liquidity & Knock-Out Order Radar
Calculates concentrated vs ambient LP capital efficiency multipliers, knock-out limit order fill margins,
and single-contract internal vault gas savings on Base.
"""

import math
from typing import Dict, Any


def calculate_concentrated_vs_ambient_efficiency(
    current_price: float = 3000.0,
    lower_tick_price: float = 2700.0,
    upper_tick_price: float = 3300.0,
    deposit_usd: float = 10000.0,
    annual_volume_usd: float = 100000000.0,
    fee_tier_pct: float = 0.05
) -> Dict[str, Any]:
    """
    Computes capital efficiency multiplier of concentrated liquidity vs ambient liquidity
    and projected fee earnings over 365 days.
    """
    if lower_tick_price <= 0.0 or upper_tick_price <= lower_tick_price:
        raise ValueError("Invalid tick price bounds")
    if current_price < lower_tick_price or current_price > upper_tick_price:
        raise ValueError("Current price must be within range")
    if deposit_usd <= 0.0:
        raise ValueError("Deposit amount must be positive")

    # Uniswap v3 / Ambient concentrated capital efficiency multiplier
    sqrt_p = math.sqrt(current_price)
    sqrt_pa = math.sqrt(lower_tick_price)
    sqrt_pb = math.sqrt(upper_tick_price)

    # Relative capital required for identical depth
    cap_eff_multiplier = 1.0 / (1.0 - math.sqrt(sqrt_pa / sqrt_pb)) if sqrt_pb > sqrt_pa else 1.0
    cap_eff_multiplier = round(max(1.0, min(50.0, cap_eff_multiplier)), 2)

    total_pool_fees_usd = annual_volume_usd * (fee_tier_pct / 100.0)
    # Ambient baseline APR (e.g. on $10M ambient depth)
    ambient_depth_usd = 10000000.0
    ambient_share = deposit_usd / (ambient_depth_usd + deposit_usd)
    ambient_fee_yield_usd = total_pool_fees_usd * ambient_share
    ambient_apr_pct = (ambient_fee_yield_usd / deposit_usd) * 100.0

    # Concentrated effective depth = deposit * multiplier
    concentrated_effective_depth = deposit_usd * cap_eff_multiplier
    concentrated_share = concentrated_effective_depth / (ambient_depth_usd + concentrated_effective_depth)
    concentrated_fee_yield_usd = total_pool_fees_usd * concentrated_share
    concentrated_apr_pct = (concentrated_fee_yield_usd / deposit_usd) * 100.0

    return {
        "current_price": current_price,
        "lower_tick_price": lower_tick_price,
        "upper_tick_price": upper_tick_price,
        "deposit_usd": deposit_usd,
        "capital_efficiency_multiplier": cap_eff_multiplier,
        "ambient_fee_yield_usd": round(ambient_fee_yield_usd, 2),
        "ambient_apr_pct": round(ambient_apr_pct, 2),
        "concentrated_fee_yield_usd": round(concentrated_fee_yield_usd, 2),
        "concentrated_apr_pct": round(concentrated_apr_pct, 2),
        "fee_boost_factor": round(concentrated_fee_yield_usd / ambient_fee_yield_usd, 2) if ambient_fee_yield_usd > 0 else 1.0
    }


def calculate_knockout_limit_order_savings(
    order_size_usd: float = 25000.0,
    standard_taker_fee_pct: float = 0.30,
    slippage_cost_pct: float = 0.15,
    knockout_maker_fee_pct: float = 0.0
) -> Dict[str, Any]:
    """
    Calculates cost savings of executing via Ambient knock-out liquidity limit orders
    versus aggressive market taker swaps on Base DEXes.
    """
    if order_size_usd <= 0.0:
        raise ValueError("Order size must be positive")

    market_swap_fee_usd = order_size_usd * (standard_taker_fee_pct / 100.0)
    market_slippage_usd = order_size_usd * (slippage_cost_pct / 100.0)
    total_market_swap_cost_usd = market_swap_fee_usd + market_slippage_usd

    knockout_fee_usd = order_size_usd * (knockout_maker_fee_pct / 100.0)
    net_savings_usd = total_market_swap_cost_usd - knockout_fee_usd
    savings_pct = (net_savings_usd / total_market_swap_cost_usd) * 100.0 if total_market_swap_cost_usd > 0 else 0.0

    return {
        "order_size_usd": order_size_usd,
        "market_swap_fee_usd": round(market_swap_fee_usd, 2),
        "market_slippage_usd": round(market_slippage_usd, 2),
        "total_market_cost_usd": round(total_market_swap_cost_usd, 2),
        "knockout_fee_usd": round(knockout_fee_usd, 2),
        "net_savings_usd": round(net_savings_usd, 2),
        "savings_pct": round(savings_pct, 2)
    }


def calculate_single_contract_vault_gas_savings(
    num_hops: int = 3,
    standard_multicall_gas_units: int = 185000,
    ambient_vault_gas_units: int = 78000,
    base_l2_gas_price_gwei: float = 0.05,
    eth_price_usd: float = 3000.0
) -> Dict[str, Any]:
    """
    Computes gas reduction enabled by Ambient's single-contract architecture that eliminates
    redundant intermediate ERC-20 token transfers in multi-hop routings.
    """
    if num_hops <= 0 or standard_multicall_gas_units <= ambient_vault_gas_units:
        raise ValueError("Invalid gas parameters")

    gas_units_saved = standard_multicall_gas_units - ambient_vault_gas_units
    gas_reduction_pct = (gas_units_saved / standard_multicall_gas_units) * 100.0

    standard_cost_eth = (standard_multicall_gas_units * base_l2_gas_price_gwei) / 1e9
    ambient_cost_eth = (ambient_vault_gas_units * base_l2_gas_price_gwei) / 1e9
    standard_cost_usd = standard_cost_eth * eth_price_usd
    ambient_cost_usd = ambient_cost_eth * eth_price_usd
    usd_saved = standard_cost_usd - ambient_cost_usd

    return {
        "num_hops": num_hops,
        "standard_gas_units": standard_multicall_gas_units,
        "ambient_gas_units": ambient_vault_gas_units,
        "gas_units_saved": gas_units_saved,
        "gas_reduction_pct": round(gas_reduction_pct, 2),
        "standard_cost_usd": round(standard_cost_usd, 4),
        "ambient_cost_usd": round(ambient_cost_usd, 4),
        "usd_saved_per_swap": round(usd_saved, 4)
    }


def evaluate_ambient_lp_strategy(
    price_volatility_pct: float,
    current_fee_apr: float,
    range_width_pct: float
) -> Dict[str, Any]:
    """
    Evaluates whether an LP should deploy Ambient (full range) or Concentrated liquidity.
    """
    if price_volatility_pct < 0.0 or range_width_pct <= 0.0:
        raise ValueError("Invalid volatility or range width")

    if price_volatility_pct > 60.0 or range_width_pct > 50.0:
        recommendation = "AMBIENT_FULL_RANGE"
        reason = "High market volatility. Ambient liquidity eliminates out-of-range fee starvation and active rebalance gas drag."
    else:
        recommendation = "CONCENTRATED_TIGHT_BAND"
        reason = "Stable or trending market with low volatility. Concentrated liquidity yields 5x-15x higher capital efficiency."

    return {
        "price_volatility_pct": price_volatility_pct,
        "range_width_pct": range_width_pct,
        "recommendation": recommendation,
        "reason": reason
    }


if __name__ == "__main__":
    eff_res = calculate_concentrated_vs_ambient_efficiency()
    print("Concentrated vs Ambient:", eff_res)
    ko_res = calculate_knockout_limit_order_savings()
    print("Knockout Savings:", ko_res)
    gas_res = calculate_single_contract_vault_gas_savings()
    print("Vault Gas Savings:", gas_res)
    strat = evaluate_ambient_lp_strategy(30.0, 15.0, 20.0)
    print("Strategy:", strat)
