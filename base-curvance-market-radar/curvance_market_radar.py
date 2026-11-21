"""
Base Curvance Modular Money Market & Yield-Bearing Collateral Radar
Autonomous Mathematical Simulation Engine
Calculates Curvance yield-bearing collateral looping carry APY, Dutch auction liquidation discount decay,
and isolated risk containment on Base L2.
"""

from typing import Dict, Any

def calculate_curvance_leveraged_carry(
    deposit_amount_usd: float,
    target_leverage: float,
    collateral_yield_apy: float,
    borrow_rate_apy: float
) -> Dict[str, Any]:
    """
    Computes net leveraged carry APY and daily cashflow for yield-bearing collateral loops.
    
    Formula:
    total_supplied = deposit * leverage
    debt_borrowed = deposit * (leverage - 1.0)
    gross_supply = total_supplied * (collateral_yield / 100.0)
    borrow_cost = debt_borrowed * (borrow_rate / 100.0)
    net_profit = gross_supply - borrow_cost
    net_apy = (net_profit / deposit) * 100.0
    """
    if deposit_amount_usd <= 0 or target_leverage < 1.0:
        raise ValueError("Deposit must be positive and leverage >= 1.0")
        
    total_supplied_usd = deposit_amount_usd * target_leverage
    debt_borrowed_usd = deposit_amount_usd * (target_leverage - 1.0)
    
    gross_supply_usd = total_supplied_usd * (collateral_yield_apy / 100.0)
    borrow_cost_usd = debt_borrowed_usd * (borrow_rate_apy / 100.0)
    net_annual_profit_usd = gross_supply_usd - borrow_cost_usd
    net_leveraged_apy = (net_annual_profit_usd / deposit_amount_usd) * 100.0
    daily_cashflow_usd = net_annual_profit_usd / 365.0
    
    return {
        "deposit_amount_usd": round(deposit_amount_usd, 2),
        "target_leverage": round(target_leverage, 2),
        "total_supplied_usd": round(total_supplied_usd, 2),
        "debt_borrowed_usd": round(debt_borrowed_usd, 2),
        "gross_supply_usd": round(gross_supply_usd, 2),
        "borrow_cost_usd": round(borrow_cost_usd, 2),
        "net_annual_profit_usd": round(net_annual_profit_usd, 2),
        "net_leveraged_apy": round(net_leveraged_apy, 2),
        "daily_cashflow_usd": round(daily_cashflow_usd, 2)
    }

def calculate_dutch_auction_liquidation(
    repaid_debt_usd: float,
    elapsed_seconds: float,
    auction_duration_seconds: float = 1800.0,
    start_discount_pct: float = 10.0,
    end_discount_pct: float = 2.0,
    base_l2_gas_usd: float = 0.04
) -> Dict[str, Any]:
    """
    Computes descending Dutch auction liquidation discount and liquidator net profit.
    """
    if repaid_debt_usd <= 0 or auction_duration_seconds <= 0:
        raise ValueError("Invalid parameters for Dutch auction")
        
    progress = min(1.0, max(0.0, elapsed_seconds / auction_duration_seconds))
    current_discount_pct = start_discount_pct - (progress * (start_discount_pct - end_discount_pct))
    
    seized_collateral_usd = repaid_debt_usd * (1.0 + (current_discount_pct / 100.0))
    gross_profit_usd = seized_collateral_usd - repaid_debt_usd
    net_profit_usd = max(0.0, gross_profit_usd - base_l2_gas_usd)
    roi_pct = (net_profit_usd / repaid_debt_usd) * 100.0
    
    return {
        "repaid_debt_usd": round(repaid_debt_usd, 2),
        "elapsed_seconds": round(elapsed_seconds, 1),
        "auction_duration_seconds": round(auction_duration_seconds, 1),
        "current_discount_pct": round(current_discount_pct, 2),
        "seized_collateral_usd": round(seized_collateral_usd, 2),
        "gross_profit_usd": round(gross_profit_usd, 2),
        "net_profit_usd": round(net_profit_usd, 2),
        "roi_pct": round(roi_pct, 2)
    }

def calculate_account_safety_buffer(
    collateral_usd: float,
    debt_usd: float,
    liquidation_threshold_pct: float = 85.0
) -> Dict[str, Any]:
    """
    Computes health factor and maximum collateral value drawdown before liquidation.
    """
    if collateral_usd <= 0 or debt_usd < 0:
        raise ValueError("Invalid collateral or debt")
        
    if debt_usd == 0:
        return {
            "health_factor": 999.0,
            "max_drawdown_pct": 100.0,
            "is_liquidatable": False,
            "status": "ZERO_DEBT_RISK_FREE"
        }
        
    effective_collateral = collateral_usd * (liquidation_threshold_pct / 100.0)
    health_factor = effective_collateral / debt_usd
    max_drawdown_pct = max(0.0, (1.0 - (debt_usd / effective_collateral)) * 100.0)
    is_liquidatable = health_factor < 1.0
    
    return {
        "collateral_usd": round(collateral_usd, 2),
        "debt_usd": round(debt_usd, 2),
        "health_factor": round(health_factor, 4),
        "max_drawdown_pct": round(max_drawdown_pct, 2),
        "is_liquidatable": is_liquidatable,
        "status": "LIQUIDATABLE" if is_liquidatable else ("MARGIN_WARNING" if max_drawdown_pct < 5.0 else "HEALTHY")
    }

def evaluate_curvance_market(
    deposit_usd: float,
    leverage: float,
    collateral_yield: float,
    borrow_rate: float,
    elapsed_seconds: float
) -> Dict[str, Any]:
    """
    Synthesizes carry yields, Dutch auction liquidation entry, and risk buffer.
    """
    carry = calculate_curvance_leveraged_carry(deposit_usd, leverage, collateral_yield, borrow_rate)
    buffer = calculate_account_safety_buffer(carry["total_supplied_usd"], carry["debt_borrowed_usd"])
    auction = calculate_dutch_auction_liquidation(repaid_debt_usd=5000.0, elapsed_seconds=elapsed_seconds)
    
    if carry["net_leveraged_apy"] >= 15.0 and buffer["health_factor"] >= 1.15:
        tier = "PRIME_CURVANCE_CARRY_LOOP"
    elif buffer["is_liquidatable"]:
        tier = "DUTCH_AUCTION_LIQUIDATION_ACTIVE"
    else:
        tier = "STANDARD_MONEY_MARKET_MONITOR"
        
    return {
        "tier": tier,
        "carry": carry,
        "buffer": buffer,
        "auction": auction
    }
