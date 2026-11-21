"""
Base Seamless Protocol Integrated Liquidity Market (ILM) & Deleveraging Radar
Autonomous Mathematical Simulation Engine
Calculates ILM leveraged carry yields, automated flash-rebalance liquidation savings,
and keeper rebalance bounty economics on Base L2.
"""

from typing import Dict, Any

def calculate_ilm_looping_yield(
    deposit_amount_usd: float,
    target_leverage: float,
    base_supply_apy: float,
    borrow_apy: float,
    ilm_reward_apr: float
) -> Dict[str, Any]:
    """
    Computes net leveraged carry yield for an Integrated Liquidity Market (ILM) strategy.
    
    Formula:
    total_supplied = deposit * leverage
    borrowed_debt = deposit * (leverage - 1.0)
    gross_supply = total_supplied * (base_supply_apy / 100.0)
    borrow_cost = borrowed_debt * (borrow_apy / 100.0)
    rewards = total_supplied * (ilm_reward_apr / 100.0)
    net_profit = gross_supply - borrow_cost + rewards
    net_apy = (net_profit / deposit) * 100.0
    """
    if deposit_amount_usd <= 0 or target_leverage < 1.0:
        raise ValueError("Deposit must be positive and leverage >= 1.0")
        
    total_supplied_usd = deposit_amount_usd * target_leverage
    borrowed_debt_usd = deposit_amount_usd * (target_leverage - 1.0)
    
    gross_supply_yield_usd = total_supplied_usd * (base_supply_apy / 100.0)
    borrow_cost_usd = borrowed_debt_usd * (borrow_apy / 100.0)
    ilm_rewards_usd = total_supplied_usd * (ilm_reward_apr / 100.0)
    
    net_annual_profit_usd = gross_supply_yield_usd - borrow_cost_usd + ilm_rewards_usd
    net_leveraged_apy = (net_annual_profit_usd / deposit_amount_usd) * 100.0
    daily_cashflow_usd = net_annual_profit_usd / 365.0
    
    return {
        "deposit_amount_usd": round(deposit_amount_usd, 2),
        "target_leverage": round(target_leverage, 2),
        "total_supplied_usd": round(total_supplied_usd, 2),
        "borrowed_debt_usd": round(borrowed_debt_usd, 2),
        "gross_supply_yield_usd": round(gross_supply_yield_usd, 2),
        "borrow_cost_usd": round(borrow_cost_usd, 2),
        "ilm_rewards_usd": round(ilm_rewards_usd, 2),
        "net_annual_profit_usd": round(net_annual_profit_usd, 2),
        "net_leveraged_apy": round(net_leveraged_apy, 2),
        "daily_cashflow_usd": round(daily_cashflow_usd, 2)
    }

def calculate_deleveraging_boundaries(
    collateral_usd: float,
    debt_usd: float,
    liquidation_threshold_pct: float = 85.0,
    emergency_unwind_buffer_pct: float = 3.0
) -> Dict[str, Any]:
    """
    Computes account health factor, maximum drawdown before liquidation,
    and flash-loan deleveraging savings vs standard 5.0% liquidation penalty.
    """
    if collateral_usd <= 0 or debt_usd < 0:
        raise ValueError("Collateral must be positive and debt non-negative")
        
    if debt_usd == 0:
        return {
            "health_factor": 999.0,
            "max_drawdown_pct": 100.0,
            "liquidation_price_ratio": 0.0,
            "penalty_savings_usd": 0.0,
            "status": "ZERO_DEBT_RISK_FREE"
        }
        
    effective_collateral = collateral_usd * (liquidation_threshold_pct / 100.0)
    health_factor = effective_collateral / debt_usd
    
    # Maximum percentage collateral value can drop before HF reaches 1.0
    max_drawdown_pct = max(0.0, (1.0 - (debt_usd / effective_collateral)) * 100.0)
    
    # Liquidation penalty is 5.0% of seized collateral in Seamless
    standard_liquidation_penalty_usd = collateral_usd * 0.05
    
    # Flash loan rebalance fee (0.05% flash fee + 0.10% swap cost = 0.15%)
    flash_rebalance_cost_usd = collateral_usd * 0.0015
    penalty_savings_usd = max(0.0, standard_liquidation_penalty_usd - flash_rebalance_cost_usd)
    
    is_emergency_triggered = health_factor <= 1.05 or max_drawdown_pct <= emergency_unwind_buffer_pct
    
    return {
        "collateral_usd": round(collateral_usd, 2),
        "debt_usd": round(debt_usd, 2),
        "liquidation_threshold_pct": round(liquidation_threshold_pct, 2),
        "health_factor": round(health_factor, 4),
        "max_drawdown_pct": round(max_drawdown_pct, 2),
        "standard_liquidation_penalty_usd": round(standard_liquidation_penalty_usd, 2),
        "flash_rebalance_cost_usd": round(flash_rebalance_cost_usd, 2),
        "penalty_savings_usd": round(penalty_savings_usd, 2),
        "is_emergency_triggered": is_emergency_triggered
    }

def calculate_keeper_rebalance_bounty(
    unwind_volume_usd: float,
    keeper_bounty_pct: float = 1.25,
    base_l2_gas_usd: float = 0.04
) -> Dict[str, Any]:
    """
    Computes keeper bot profitability for executing rebalancing or liquidation unwinds.
    """
    if unwind_volume_usd < 0:
        raise ValueError("Volume must be non-negative")
        
    gross_bounty_usd = unwind_volume_usd * (keeper_bounty_pct / 100.0)
    net_keeper_profit_usd = max(0.0, gross_bounty_usd - base_l2_gas_usd)
    profit_margin_pct = (net_keeper_profit_usd / gross_bounty_usd * 100.0) if gross_bounty_usd > 0 else 0.0
    
    return {
        "unwind_volume_usd": round(unwind_volume_usd, 2),
        "keeper_bounty_pct": round(keeper_bounty_pct, 2),
        "base_l2_gas_usd": round(base_l2_gas_usd, 4),
        "gross_bounty_usd": round(gross_bounty_usd, 2),
        "net_keeper_profit_usd": round(net_keeper_profit_usd, 2),
        "profit_margin_pct": round(profit_margin_pct, 2)
    }

def evaluate_seamless_opportunity(
    deposit_amount_usd: float,
    target_leverage: float,
    base_supply_apy: float,
    borrow_apy: float,
    ilm_reward_apr: float,
    liquidation_threshold_pct: float = 85.0
) -> Dict[str, Any]:
    """
    Comprehensive evaluation linking carry yield, risk boundary, and keeper defense.
    """
    carry = calculate_ilm_looping_yield(
        deposit_amount_usd, target_leverage, base_supply_apy, borrow_apy, ilm_reward_apr
    )
    
    collateral = carry["total_supplied_usd"]
    debt = carry["borrowed_debt_usd"]
    
    boundaries = calculate_deleveraging_boundaries(collateral, debt, liquidation_threshold_pct)
    
    hf = boundaries["health_factor"]
    net_apy = carry["net_leveraged_apy"]
    
    if hf < 1.05:
        tier = "URGENT_DELEVERAGING_REQUIRED"
    elif net_apy >= 15.0 and hf >= 1.15:
        tier = "EXCEPTIONAL_CARRY_OPPORTUNITY"
    elif net_apy >= 8.0:
        tier = "HEALTHY_LEVERAGED_CARRY"
    else:
        tier = "LOW_MARGIN_MONITOR"
        
    return {
        "tier": tier,
        "carry_metrics": carry,
        "risk_boundaries": boundaries
    }
