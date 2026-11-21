"""
Solana Zeta Markets Perps & Options Cross-Margin Liquidation Radar
Autonomous Mathematical Simulation Engine
Calculates dynamic MMR maintenance margin boundaries, passive maker rebate yields,
and liquidator penalty economics on Solana Zeta Markets.
"""

from typing import Dict, Any
import math

def calculate_zeta_margin_requirements(
    position_notional_usd: float,
    base_imr_pct: float = 10.0,
    dynamic_factor: float = 0.005
) -> Dict[str, Any]:
    """
    Computes Initial Margin Ratio (IMR) and Maintenance Margin Ratio (MMR)
    incorporating position size dynamic scaling.
    
    Formula:
    imr_pct = base_imr_pct + (dynamic_factor * sqrt(position_notional_usd))
    mmr_pct = imr_pct / 2.0
    """
    if position_notional_usd < 0:
        raise ValueError("Position notional must be non-negative")
        
    if position_notional_usd == 0:
        return {
            "position_notional_usd": 0.0,
            "imr_pct": base_imr_pct,
            "mmr_pct": base_imr_pct / 2.0,
            "required_imr_usd": 0.0,
            "required_mmr_usd": 0.0
        }
        
    scaling = dynamic_factor * math.sqrt(position_notional_usd)
    imr_pct = base_imr_pct + scaling
    mmr_pct = imr_pct / 2.0
    
    required_imr_usd = position_notional_usd * (imr_pct / 100.0)
    required_mmr_usd = position_notional_usd * (mmr_pct / 100.0)
    
    return {
        "position_notional_usd": round(position_notional_usd, 2),
        "imr_pct": round(imr_pct, 4),
        "mmr_pct": round(mmr_pct, 4),
        "required_imr_usd": round(required_imr_usd, 2),
        "required_mmr_usd": round(required_mmr_usd, 2)
    }

def calculate_account_liquidation_health(
    collateral_usd: float,
    unrealized_pnl_usd: float,
    position_notional_usd: float,
    mmr_pct: float = 5.5
) -> Dict[str, Any]:
    """
    Evaluates account health, margin ratio, liquidation threshold, and penalty.
    
    Formula:
    equity = collateral + unrealized_pnl
    margin_ratio = (equity / notional) * 100.0
    is_liquidatable = margin_ratio <= mmr_pct
    """
    if position_notional_usd < 0:
        raise ValueError("Notional must be non-negative")
        
    equity_usd = collateral_usd + unrealized_pnl_usd
    
    if position_notional_usd == 0:
        return {
            "equity_usd": round(equity_usd, 2),
            "margin_ratio_pct": 999.0,
            "distance_to_liq_pct": 999.0,
            "is_liquidatable": False,
            "liquidation_penalty_usd": 0.0,
            "status": "NO_OPEN_POSITIONS"
        }
        
    margin_ratio_pct = (equity_usd / position_notional_usd) * 100.0
    distance_to_liq_pct = max(0.0, margin_ratio_pct - mmr_pct)
    is_liquidatable = margin_ratio_pct <= mmr_pct
    
    # 2.5% liquidation fee on position notional
    liquidation_penalty_usd = position_notional_usd * 0.025
    liquidator_reward_usd = position_notional_usd * 0.0125  # 50% of penalty to liquidator
    
    return {
        "collateral_usd": round(collateral_usd, 2),
        "unrealized_pnl_usd": round(unrealized_pnl_usd, 2),
        "equity_usd": round(equity_usd, 2),
        "margin_ratio_pct": round(margin_ratio_pct, 2),
        "mmr_pct": round(mmr_pct, 2),
        "distance_to_liq_pct": round(distance_to_liq_pct, 2),
        "is_liquidatable": is_liquidatable,
        "liquidation_penalty_usd": round(liquidation_penalty_usd, 2),
        "liquidator_reward_usd": round(liquidator_reward_usd, 2)
    }

def calculate_maker_rebate_yield(
    daily_maker_volume_usd: float,
    base_maker_rebate_bps: float = 1.0,
    zx_stake_boost_pct: float = 50.0,
    capital_allocated_usd: float = 10000.0
) -> Dict[str, Any]:
    """
    Calculates passive market maker rebate cashflow and annualized return.
    """
    if daily_maker_volume_usd < 0 or capital_allocated_usd <= 0:
        raise ValueError("Volume must be non-negative and capital positive")
        
    effective_rebate_bps = base_maker_rebate_bps * (1.0 + (zx_stake_boost_pct / 100.0))
    daily_rebate_usd = daily_maker_volume_usd * (effective_rebate_bps / 10000.0)
    annual_rebate_usd = daily_rebate_usd * 365.0
    rebate_apy_pct = (annual_rebate_usd / capital_allocated_usd) * 100.0
    
    return {
        "daily_maker_volume_usd": round(daily_maker_volume_usd, 2),
        "base_maker_rebate_bps": round(base_maker_rebate_bps, 2),
        "effective_rebate_bps": round(effective_rebate_bps, 3),
        "daily_rebate_usd": round(daily_rebate_usd, 2),
        "annual_rebate_usd": round(annual_rebate_usd, 2),
        "rebate_apy_pct": round(rebate_apy_pct, 2)
    }

def evaluate_zeta_profile(
    collateral_usd: float,
    unrealized_pnl_usd: float,
    position_notional_usd: float,
    daily_maker_volume_usd: float,
    capital_allocated_usd: float = 10000.0
) -> Dict[str, Any]:
    """
    Synthesizes margin health, liquidator risk, and maker rebate opportunities.
    """
    margin_req = calculate_zeta_margin_requirements(position_notional_usd)
    health = calculate_account_liquidation_health(
        collateral_usd, unrealized_pnl_usd, position_notional_usd, margin_req["mmr_pct"]
    )
    maker = calculate_maker_rebate_yield(
        daily_maker_volume_usd, capital_allocated_usd=capital_allocated_usd
    )
    
    if health["is_liquidatable"]:
        recommendation = "LIQUIDATION_ACTIVE_EXECUTE_CHUNKS"
    elif health["distance_to_liq_pct"] < 3.0:
        recommendation = "CRITICAL_MARGIN_CALL_ADD_COLLATERAL"
    elif maker["rebate_apy_pct"] >= 20.0:
        recommendation = "HIGH_YIELD_MAKER_REBATE_FARMING"
    else:
        recommendation = "STANDARD_MARGIN_MONITORING"
        
    return {
        "recommendation": recommendation,
        "margin_requirements": margin_req,
        "liquidation_health": health,
        "maker_rebates": maker
    }
