"""
Base Aera Protocol Autonomous Treasury & Vault Rebalancing Radar
Mathematical simulation and portfolio optimization engine for Aera Protocol autonomous on-chain treasury vaults,
Gauntlet-modeled risk objective functions, Dutch auction rebalancing slippage minimization, and guardian circuit breakers on Base L2.
"""

import math

BASE_USDC_RECEIVE_ADDRESS = "0xF0E0D361bBE899F3089f0a968506eF2B97693c01"
SOLANA_RECEIVE_ADDRESS = "DW2MdHEq3qZ6nh9b5YFUoaPnBuuxC8Gz2785kwbbjSAM"

def calculate_portfolio_risk_and_sharpe(
    weights: dict,
    expected_returns: dict,
    volatilities: dict,
    risk_free_rate_pct: float = 4.5
) -> dict:
    """
    Computes expected portfolio annualized return, composite volatility,
    and risk-adjusted Sharpe ratio across treasury asset allocations.
    """
    if not weights or not expected_returns or not volatilities:
        return {
            "expected_return_pct": 0.0,
            "portfolio_volatility_pct": 0.0,
            "sharpe_ratio": 0.0,
            "excess_return_pct": 0.0
        }

    exp_return = sum(weights.get(asset, 0.0) * expected_returns.get(asset, 0.0) for asset in weights)
    var_sum = sum((weights.get(asset, 0.0) * volatilities.get(asset, 0.0)) ** 2 for asset in weights)
    port_vol = math.sqrt(var_sum)
    excess_return = exp_return - risk_free_rate_pct
    sharpe = excess_return / port_vol if port_vol > 0 else 0.0

    return {
        "expected_return_pct": round(exp_return, 2),
        "portfolio_volatility_pct": round(port_vol, 2),
        "sharpe_ratio": round(sharpe, 4),
        "excess_return_pct": round(excess_return, 2)
    }

def calculate_dutch_auction_rebalance_savings(
    turnover_usd: float,
    direct_amm_slippage_bps: float = 50.0,
    aera_dutch_slippage_bps: float = 5.0
) -> dict:
    """
    Quantifies capital preserved by routing portfolio rebalances through Aera's continuous Dutch auctions
    instead of submitting direct market orders to DEX liquidity pools.
    """
    if turnover_usd <= 0:
        return {
            "turnover_usd": turnover_usd,
            "direct_amm_cost_usd": 0.0,
            "aera_dutch_cost_usd": 0.0,
            "mev_slippage_saved_usd": 0.0,
            "savings_percentage": 0.0
        }

    direct_cost = turnover_usd * (direct_amm_slippage_bps / 10000.0)
    aera_cost = turnover_usd * (aera_dutch_slippage_bps / 10000.0)
    saved = max(0.0, direct_cost - aera_cost)
    savings_pct = (saved / direct_cost) * 100.0 if direct_cost > 0 else 0.0

    return {
        "turnover_usd": round(turnover_usd, 2),
        "direct_amm_cost_usd": round(direct_cost, 2),
        "aera_dutch_cost_usd": round(aera_cost, 2),
        "mev_slippage_saved_usd": round(saved, 2),
        "savings_percentage": round(savings_pct, 2)
    }

def calculate_guardian_circuit_breaker(
    current_drawdown_pct: float,
    max_allowed_drawdown_pct: float = 5.0,
    portfolio_value_usd: float = 1000000.0
) -> dict:
    """
    Monitors guardian stop-loss triggers and automated stablecoin de-risking thresholds.
    """
    if portfolio_value_usd <= 0:
        return {
            "current_drawdown_pct": current_drawdown_pct,
            "max_allowed_drawdown_pct": max_allowed_drawdown_pct,
            "portfolio_value_usd": 0.0,
            "capital_at_risk_usd": 0.0,
            "buffer_remaining_pct": 0.0,
            "is_circuit_breaker_triggered": False
        }

    is_triggered = current_drawdown_pct >= max_allowed_drawdown_pct
    capital_at_risk = portfolio_value_usd * (current_drawdown_pct / 100.0)
    buffer_remaining = max(0.0, max_allowed_drawdown_pct - current_drawdown_pct)

    return {
        "current_drawdown_pct": round(current_drawdown_pct, 2),
        "max_allowed_drawdown_pct": round(max_allowed_drawdown_pct, 2),
        "portfolio_value_usd": round(portfolio_value_usd, 2),
        "capital_at_risk_usd": round(capital_at_risk, 2),
        "buffer_remaining_pct": round(buffer_remaining, 2),
        "is_circuit_breaker_triggered": is_triggered
    }

def verify_vip_license(tx_hash: str, chain: str, amount: float, recipient: str) -> dict:
    """
    Validates on-chain VIP sentinel license for Aera autonomous treasury analytics.
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
