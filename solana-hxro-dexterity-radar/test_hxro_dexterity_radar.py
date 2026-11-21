"""
Unit tests for Solana Hxro Network / Dexterity Institutional Derivatives & Risk Engine Radar.
"""

import unittest
from hxro_dexterity_radar import (
    calculate_portfolio_margin_health,
    calculate_funding_carry_yield,
    calculate_liquidator_seizure_profit,
    verify_vip_license
)

class TestHxroDexterityRadar(unittest.TestCase):
    def test_portfolio_margin_health_safe(self):
        collateral = {
            "USDC": {"amount": 5000.0, "price": 1.0, "haircut_pct": 0.0},
            "SOL": {"amount": 40.0, "price": 150.0, "haircut_pct": 15.0}
        }
        res = calculate_portfolio_margin_health(
            collateral_deposits=collateral,
            position_notional_usd=50000.0,
            base_mmr_pct=5.0,
            concentration_factor=1.0
        )
        self.assertTrue(res["is_safe"])
        self.assertEqual(res["gross_collateral_usd"], 11000.0)
        self.assertEqual(res["total_effective_collateral"], 10100.0)
        self.assertEqual(res["scaled_mmr_pct"], 5.5)
        self.assertEqual(res["mmr_required_usd"], 2750.0)
        self.assertEqual(res["health_factor"], 3.673)
        self.assertEqual(res["drawdown_buffer_pct"], 72.77)

    def test_portfolio_margin_health_insolvent(self):
        collateral = {
            "USDC": {"amount": 1000.0, "price": 1.0, "haircut_pct": 0.0}
        }
        res = calculate_portfolio_margin_health(
            collateral_deposits=collateral,
            position_notional_usd=50000.0,
            base_mmr_pct=5.0,
            concentration_factor=1.0
        )
        self.assertFalse(res["is_safe"])
        self.assertLess(res["health_factor"], 1.0)

    def test_funding_carry_yield_short(self):
        res = calculate_funding_carry_yield(
            position_size_usd=20000.0,
            mark_price=152.0,
            index_price=150.0,
            funding_interval_hours=8.0,
            is_long=False
        )
        self.assertTrue(res["is_profitable_carry"])
        self.assertEqual(res["premium_pct"], 1.3333)
        self.assertEqual(res["funding_rate_8h_pct"], 0.1333)
        self.assertEqual(res["net_carry_apr_pct"], 146.0)
        self.assertEqual(res["daily_cashflow_usd"], 80.0)

    def test_liquidator_seizure_profit(self):
        res = calculate_liquidator_seizure_profit(
            insolvent_notional_usd=15000.0,
            liquidation_bonus_pct=3.5,
            sol_priority_fee_usd=0.05,
            jito_tip_usd=2.50
        )
        self.assertTrue(res["is_profitable"])
        self.assertEqual(res["gross_seizure_bounty_usd"], 525.0)
        self.assertEqual(res["tx_cost_usd"], 2.55)
        self.assertEqual(res["net_profit_usd"], 522.45)
        self.assertGreater(res["roi_pct"], 20000.0)

    def test_vip_license_verification(self):
        sol_valid = verify_vip_license(
            tx_hash="5xabcdef1234567890abcdef1234567890abcdef1234567890abcdef12345678901234",
            chain="Solana",
            recipient="DW2MdHEq3qZ6nh9b5YFUoaPnBuuxC8Gz2785kwbbjSAM",
            amount=0.03
        )
        self.assertTrue(sol_valid["verified"])

        base_valid = verify_vip_license(
            tx_hash="0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef12345678901234",
            chain="Base",
            recipient="0xF0E0D361bBE899F3089f0a968506eF2B97693c01",
            amount=5.0
        )
        self.assertTrue(base_valid["verified"])

        invalid = verify_vip_license(
            tx_hash="short",
            chain="Solana",
            recipient="DW2MdHEq3qZ6nh9b5YFUoaPnBuuxC8Gz2785kwbbjSAM",
            amount=0.01
        )
        self.assertFalse(invalid["verified"])

if __name__ == "__main__":
    unittest.main()
