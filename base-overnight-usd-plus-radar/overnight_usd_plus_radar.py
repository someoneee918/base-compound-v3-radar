"""
Base Overnight.fi USD+ Daily Rebase & Peg Arbitrage Radar
Autonomous Mathematical Simulation Engine
Calculates USD+ daily rebasing yield compounding, secondary DEX peg discount redemptions,
and delta-neutral ETS carry on Base L2.
"""

from typing import Dict, Any

def calculate_usd_plus_rebase_yield(
    deposit_usd: float,
    gross_protocol_apy: float = 11.5,
    protocol_fee_pct: float = 10.0
) -> Dict[str, Any]:
    """
    Computes net rebasing APY and daily yield for holding USD+ on Base.
    
    Formula:
    net_apy = gross_apy * (1.0 - (protocol_fee / 100.0))
    daily_rate = (1.0 + (net_apy / 100.0))^(1/365) - 1.0
    daily_cashflow = deposit * daily_rate
    annual_profit = deposit * (net_apy / 100.0)
    """
    if deposit_usd <= 0 or gross_protocol_apy < 0:
        raise ValueError("Invalid parameters for rebase yield")
        
    net_apy_pct = gross_protocol_apy * (1.0 - (protocol_fee_pct / 100.0))
    daily_rate = ((1.0 + (net_apy_pct / 100.0)) ** (1.0 / 365.0)) - 1.0
    daily_cashflow_usd = deposit_usd * daily_rate
    annual_profit_usd = deposit_usd * (net_apy_pct / 100.0)
    
    return {
        "deposit_usd": round(deposit_usd, 2),
        "gross_protocol_apy": round(gross_protocol_apy, 2),
        "net_apy_pct": round(net_apy_pct, 2),
        "daily_rate_bps": round(daily_rate * 10000.0, 4),
        "daily_cashflow_usd": round(daily_cashflow_usd, 2),
        "annual_profit_usd": round(annual_profit_usd, 2)
    }

def calculate_peg_discount_arbitrage(
    secondary_dex_price: float,
    trade_size_usd: float = 10000.0,
    redeem_fee_pct: float = 0.04,
    base_l2_gas_usd: float = 0.04
) -> Dict[str, Any]:
    """
    Computes secondary DEX depeg redemption arbitrage profit (buying USD+ at discount,
    redeeming 1:1 with protocol for USDC).
    """
    if secondary_dex_price <= 0 or trade_size_usd <= 0:
        raise ValueError("Price and trade size must be positive")
        
    discount_pct = max(0.0, (1.0 - secondary_dex_price) * 100.0)
    
    if secondary_dex_price >= 1.0:
        return {
            "secondary_dex_price": round(secondary_dex_price, 4),
            "discount_pct": 0.0,
            "tokens_bought": 0.0,
            "gross_usdc_received": 0.0,
            "net_profit_usd": 0.0,
            "roi_pct": 0.0,
            "is_profitable": False
        }
        
    tokens_bought = trade_size_usd / secondary_dex_price
    gross_usdc_received = tokens_bought * 1.0  # 1:1 on-chain redemption
    redeem_fee_usd = gross_usdc_received * (redeem_fee_pct / 100.0)
    net_usdc_received = gross_usdc_received - redeem_fee_usd - base_l2_gas_usd
    net_profit_usd = max(0.0, net_usdc_received - trade_size_usd)
    roi_pct = (net_profit_usd / trade_size_usd) * 100.0
    is_profitable = net_profit_usd > 1.0 and discount_pct >= 0.10
    
    return {
        "secondary_dex_price": round(secondary_dex_price, 4),
        "discount_pct": round(discount_pct, 4),
        "tokens_bought": round(tokens_bought, 2),
        "gross_usdc_received": round(gross_usdc_received, 2),
        "redeem_fee_usd": round(redeem_fee_usd, 2),
        "net_profit_usd": round(net_profit_usd, 2),
        "roi_pct": round(roi_pct, 2),
        "is_profitable": is_profitable
    }

def calculate_ets_delta_neutral_carry(
    lp_yield_apr: float = 18.5,
    hedge_funding_apr: float = 8.0,
    capital_allocated_usd: float = 25000.0,
    management_fee_pct: float = 1.5
) -> Dict[str, Any]:
    """
    Computes delta-neutral Exchange-Traded Strategy (ETS) carry combining DEX LP yield
    with short perpetual futures funding rates.
    """
    if capital_allocated_usd <= 0:
        raise ValueError("Capital must be positive")
        
    net_ets_apr_pct = max(0.0, lp_yield_apr + hedge_funding_apr - management_fee_pct)
    annual_cashflow_usd = capital_allocated_usd * (net_ets_apr_pct / 100.0)
    daily_cashflow_usd = annual_cashflow_usd / 365.0
    
    return {
        "capital_allocated_usd": round(capital_allocated_usd, 2),
        "lp_yield_apr": round(lp_yield_apr, 2),
        "hedge_funding_apr": round(hedge_funding_apr, 2),
        "management_fee_pct": round(management_fee_pct, 2),
        "net_ets_apr_pct": round(net_ets_apr_pct, 2),
        "daily_cashflow_usd": round(daily_cashflow_usd, 2),
        "annual_cashflow_usd": round(annual_cashflow_usd, 2)
    }

def evaluate_overnight_market(
    deposit_usd: float,
    secondary_price: float,
    gross_apy: float,
    lp_yield_apr: float
) -> Dict[str, Any]:
    """
    Synthesizes rebasing cashflow, peg arbitrage triggers, and ETS carry yields.
    """
    rebase = calculate_usd_plus_rebase_yield(deposit_usd, gross_apy)
    peg_arb = calculate_peg_discount_arbitrage(secondary_price, trade_size_usd=deposit_usd)
    ets = calculate_ets_delta_neutral_carry(lp_yield_apr)
    
    if peg_arb["is_profitable"] and peg_arb["discount_pct"] >= 0.30:
        tier = "HIGH_CONVICTION_PEG_ARBITRAGE"
    elif ets["net_ets_apr_pct"] >= 20.0:
        tier = "PRIME_DELTA_NEUTRAL_ETS_CARRY"
    else:
        tier = "PASSIVE_DAILY_REBASE_YIELD"
        
    return {
        "tier": tier,
        "rebase": rebase,
        "peg_arbitrage": peg_arb,
        "ets_carry": ets
    }
