"""
Solana Save Finance (ex-Solend) Isolated Pool & Liquidation Radar
Autonomous Mathematical Simulation Engine
Calculates multi-tier collateral liquidation boundaries, piecewise utilization kink rates,
and flash liquidator seizure economics on Solana Save Finance.
"""

from typing import Dict, Any

def calculate_account_health_factor(
    collateral_usd: float,
    borrowed_usd: float,
    liquidation_threshold_pct: float = 80.0
) -> Dict[str, Any]:
    """
    Computes account health factor and maximum asset drawdown before liquidation.
    
    Formula:
    liq_threshold_usd = collateral_usd * (liquidation_threshold_pct / 100.0)
    health_factor = liq_threshold_usd / borrowed_usd
    max_drawdown = (1.0 - (borrowed_usd / liq_threshold_usd)) * 100.0
    """
    if collateral_usd <= 0 or borrowed_usd < 0:
        raise ValueError("Collateral must be positive and debt non-negative")
        
    if borrowed_usd == 0:
        return {
            "collateral_usd": round(collateral_usd, 2),
            "borrowed_usd": 0.0,
            "liquidation_threshold_usd": round(collateral_usd * (liquidation_threshold_pct / 100.0), 2),
            "health_factor": 999.0,
            "max_drawdown_pct": 100.0,
            "is_liquidatable": False,
            "status": "ZERO_DEBT_RISK_FREE"
        }
        
    liq_threshold_usd = collateral_usd * (liquidation_threshold_pct / 100.0)
    health_factor = liq_threshold_usd / borrowed_usd
    max_drawdown_pct = max(0.0, (1.0 - (borrowed_usd / liq_threshold_usd)) * 100.0)
    is_liquidatable = health_factor < 1.0
    
    return {
        "collateral_usd": round(collateral_usd, 2),
        "borrowed_usd": round(borrowed_usd, 2),
        "liquidation_threshold_usd": round(liq_threshold_usd, 2),
        "health_factor": round(health_factor, 4),
        "max_drawdown_pct": round(max_drawdown_pct, 2),
        "is_liquidatable": is_liquidatable,
        "status": "LIQUIDATABLE" if is_liquidatable else ("MARGIN_WARNING" if max_drawdown_pct < 5.0 else "HEALTHY")
    }

def calculate_save_kink_borrow_rate(
    utilization_pct: float,
    base_rate_pct: float = 2.0,
    kink_utilization_pct: float = 80.0,
    slope1_pct: float = 6.0,
    slope2_pct: float = 50.0,
    reserve_fee_pct: float = 10.0
) -> Dict[str, Any]:
    """
    Computes piecewise kinked borrow rate and lender supply APY on Save pools.
    """
    if utilization_pct < 0 or utilization_pct > 100.0:
        raise ValueError("Utilization must be between 0% and 100%")
        
    if utilization_pct <= kink_utilization_pct:
        borrow_rate_pct = base_rate_pct + (utilization_pct / kink_utilization_pct) * slope1_pct
    else:
        excess_ratio = (utilization_pct - kink_utilization_pct) / (100.0 - kink_utilization_pct)
        borrow_rate_pct = base_rate_pct + slope1_pct + (excess_ratio * slope2_pct)
        
    lender_supply_apy_pct = (borrow_rate_pct * (utilization_pct / 100.0)) * (1.0 - (reserve_fee_pct / 100.0))
    
    return {
        "utilization_pct": round(utilization_pct, 2),
        "kink_utilization_pct": round(kink_utilization_pct, 2),
        "borrow_rate_pct": round(borrow_rate_pct, 2),
        "lender_supply_apy_pct": round(lender_supply_apy_pct, 2),
        "is_above_kink": utilization_pct > kink_utilization_pct
    }

def calculate_liquidator_seizure_profit(
    borrowed_usd: float,
    close_factor_pct: float = 20.0,
    liquidation_bonus_pct: float = 8.0,
    priority_fee_sol: float = 0.005,
    sol_price_usd: float = 180.0
) -> Dict[str, Any]:
    """
    Computes net liquidator flash repayment and seizure profit.
    """
    if borrowed_usd <= 0:
        raise ValueError("Borrowed debt must be positive")
        
    repaid_usd = borrowed_usd * (close_factor_pct / 100.0)
    seized_usd = repaid_usd * (1.0 + (liquidation_bonus_pct / 100.0))
    gross_profit_usd = seized_usd - repaid_usd
    gas_cost_usd = priority_fee_sol * sol_price_usd
    net_profit_usd = max(0.0, gross_profit_usd - gas_cost_usd)
    roi_pct = (net_profit_usd / repaid_usd) * 100.0
    
    return {
        "borrowed_usd": round(borrowed_usd, 2),
        "close_factor_pct": round(close_factor_pct, 2),
        "repaid_usd": round(repaid_usd, 2),
        "seized_usd": round(seized_usd, 2),
        "gross_profit_usd": round(gross_profit_usd, 2),
        "gas_cost_usd": round(gas_cost_usd, 4),
        "net_profit_usd": round(net_profit_usd, 2),
        "roi_pct": round(roi_pct, 2)
    }

def evaluate_save_position(
    collateral_usd: float,
    borrowed_usd: float,
    utilization_pct: float,
    liquidation_threshold_pct: float = 80.0
) -> Dict[str, Any]:
    """
    Synthesizes position health, interest rate curve status, and liquidator triggers.
    """
    health = calculate_account_health_factor(collateral_usd, borrowed_usd, liquidation_threshold_pct)
    rates = calculate_save_kink_borrow_rate(utilization_pct)
    
    liquidator = None
    if health["is_liquidatable"]:
        liquidator = calculate_liquidator_seizure_profit(borrowed_usd)
        tier = "LIQUIDATION_ACTIVE_REPAY_CHUNK"
    elif health["max_drawdown_pct"] <= 5.0:
        tier = "CRITICAL_COLLATERAL_WARNING"
    elif rates["is_above_kink"]:
        tier = "HIGH_INTEREST_RATE_SURGE"
    else:
        tier = "HEALTHY_BORROW_POSITION"
        
    return {
        "tier": tier,
        "health": health,
        "rates": rates,
        "liquidator": liquidator
    }
