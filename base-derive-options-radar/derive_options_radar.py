"""
Base Derive (ex-Lyra v2) Sub-Account Portfolio Margin & Variance Risk Premium (VRP) Options Radar
Mathematical modeling engine for Derive sub-account cross-margin requirements, options expiration settlement payoffs, Variance Risk Premium (VRP) volatility harvesting yields, and delta-hedged margin safety on Base L2.
"""

from typing import Dict, Any

def calculate_options_payoff_and_settlement_pnl(
    strike_price: float,
    underlying_spot_at_expiry: float,
    option_type: str, # "call" or "put"
    is_long: bool,
    option_premium_usd: float,
    contracts_count: float = 1.0
) -> Dict[str, Any]:
    """
    Calculates settlement payoff and net PnL at expiry for European options on Derive.
    """
    if strike_price <= 0 or underlying_spot_at_expiry <= 0 or option_premium_usd < 0 or contracts_count <= 0:
        raise ValueError("Prices, premium, and contracts must be valid positive numbers.")

    opt_type_clean = option_type.strip().lower()
    if opt_type_clean == "call":
        intrinsic_value = max(0.0, underlying_spot_at_expiry - strike_price)
    elif opt_type_clean == "put":
        intrinsic_value = max(0.0, strike_price - underlying_spot_at_expiry)
    else:
        raise ValueError("option_type must be 'call' or 'put'")

    gross_payout_per_contract = intrinsic_value
    gross_total_payout_usd = gross_payout_per_contract * contracts_count
    total_premium_paid_usd = option_premium_usd * contracts_count

    if is_long:
        net_pnl_usd = gross_total_payout_usd - total_premium_paid_usd
        roi_pct = (net_pnl_usd / total_premium_paid_usd * 100.0) if total_premium_paid_usd > 0 else 0.0
    else:
        # Short position: receives premium upfront, pays gross settlement
        net_pnl_usd = total_premium_paid_usd - gross_total_payout_usd
        # Capital at risk approximation = strike * contracts
        capital_at_risk = strike_price * contracts_count
        roi_pct = (net_pnl_usd / capital_at_risk * 100.0) if capital_at_risk > 0 else 0.0

    is_in_the_money = intrinsic_value > 0

    return {
        "strike_price": round(strike_price, 2),
        "underlying_spot_at_expiry": round(underlying_spot_at_expiry, 2),
        "option_type": opt_type_clean,
        "is_long": is_long,
        "is_in_the_money": is_in_the_money,
        "intrinsic_value": round(intrinsic_value, 2),
        "total_premium_paid_usd": round(total_premium_paid_usd, 2),
        "gross_total_payout_usd": round(gross_total_payout_usd, 2),
        "net_pnl_usd": round(net_pnl_usd, 2),
        "roi_pct": round(roi_pct, 2)
    }

def calculate_variance_risk_premium_and_harvest_roi(
    implied_vol_pct: float,
    realized_vol_pct: float,
    option_premium_collected_usd: float,
    delta_hedged_capital_usd: float,
    days_to_expiry: int,
    hedging_cost_usd: float = 10.0
) -> Dict[str, Any]:
    """
    Models Variance Risk Premium (VRP) harvesting:
    Selling elevated IV against lower realized RV with dynamic delta-hedging.
    Net profit captures IV - RV theta decay surplus minus hedging transaction costs.
    """
    if delta_hedged_capital_usd <= 0 or days_to_expiry <= 0:
        raise ValueError("Capital and days to expiry must be positive.")

    vrp_spread_pct = implied_vol_pct - realized_vol_pct
    is_vrp_positive = vrp_spread_pct > 0

    # Theoretical decay capture proportion of premium based on VRP ratio
    if implied_vol_pct > 0 and is_vrp_positive:
        vrp_capture_ratio = min(1.0, max(0.0, vrp_spread_pct / implied_vol_pct))
    else:
        vrp_capture_ratio = 0.0

    gross_vrp_profit_usd = option_premium_collected_usd * vrp_capture_ratio
    net_vrp_profit_usd = max(0.0, gross_vrp_profit_usd - hedging_cost_usd)

    # Annualized yield on allocated delta-hedged capital
    period_fraction = days_to_expiry / 365.0
    period_yield_pct = (net_vrp_profit_usd / delta_hedged_capital_usd) * 100.0
    annualized_vrp_apr_pct = (period_yield_pct / period_fraction) if period_fraction > 0 else 0.0

    return {
        "implied_vol_pct": round(implied_vol_pct, 2),
        "realized_vol_pct": round(realized_vol_pct, 2),
        "vrp_spread_pct": round(vrp_spread_pct, 2),
        "is_vrp_positive": is_vrp_positive,
        "option_premium_collected_usd": round(option_premium_collected_usd, 2),
        "hedging_cost_usd": round(hedging_cost_usd, 2),
        "net_vrp_profit_usd": round(net_vrp_profit_usd, 2),
        "period_yield_pct": round(period_yield_pct, 2),
        "annualized_vrp_apr_pct": round(annualized_vrp_apr_pct, 2)
    }

def calculate_subaccount_portfolio_margin_requirement(
    subaccount_collateral_usd: float,
    long_perps_notional_usd: float,
    short_calls_notional_usd: float,
    short_puts_notional_usd: float,
    base_margin_rate_pct: float = 10.0,
    offset_discount_pct: float = 40.0
) -> Dict[str, Any]:
    """
    Calculates sub-account portfolio margin requirements on Derive:
    Correlated positions (e.g. Long Perps + Short Calls covered yield) receive cross-margin offset discounts.
    """
    if subaccount_collateral_usd <= 0:
        raise ValueError("Subaccount collateral must be positive.")

    total_gross_notional = long_perps_notional_usd + short_calls_notional_usd + short_puts_notional_usd
    base_required_margin_usd = total_gross_notional * (base_margin_rate_pct / 100.0)

    # Offset discount applied between Long Perps and Short Calls (covered call offset)
    hedged_pair_notional = min(long_perps_notional_usd, short_calls_notional_usd)
    margin_discount_usd = hedged_pair_notional * (base_margin_rate_pct / 100.0) * (offset_discount_pct / 100.0)

    net_required_margin_usd = max(100.0, base_required_margin_usd - margin_discount_usd)
    margin_utilization_pct = (net_required_margin_usd / subaccount_collateral_usd) * 100.0
    free_collateral_usd = max(0.0, subaccount_collateral_usd - net_required_margin_usd)
    is_margin_safe = margin_utilization_pct < 85.0

    return {
        "subaccount_collateral_usd": round(subaccount_collateral_usd, 2),
        "total_gross_notional": round(total_gross_notional, 2),
        "base_required_margin_usd": round(base_required_margin_usd, 2),
        "margin_discount_usd": round(margin_discount_usd, 2),
        "net_required_margin_usd": round(net_required_margin_usd, 2),
        "free_collateral_usd": round(free_collateral_usd, 2),
        "margin_utilization_pct": round(margin_utilization_pct, 2),
        "is_margin_safe": is_margin_safe
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
        "tier": "Derive Options VIP Sentinel" if is_valid else "Unverified"
    }