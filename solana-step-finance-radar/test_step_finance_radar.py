"""
Unit tests for Solana Step Finance xSTEP Protocol Revenue & Staking Yield Radar.
"""

import unittest
from step_finance_radar import (
    calculate_xstep_accretion_and_yield,
    calculate_xstep_secondary_arbitrage,
    calculate_annual_compounded_staking_return,
    verify_vip_license
)

class TestStepFinanceRadar(unittest.TestCase):
    def test_xstep_accretion_and_yield(self):
        # 100M STEP, 80M xSTEP (1.25 ratio), $0.05 STEP price, $3500 daily fee
        res = calculate_xstep_accretion_and_yield(
            total_staked_step=100000000.0,
            total_xstep_supply=80000000.0,
            step_price_usd=0.05,
            daily_protocol_fee_usd=3500.0
        )
        self.assertEqual(res["current_ratio"], 1.25)
        self.assertEqual(res["xstep_fair_value_usd"], 0.0625)
        self.assertEqual(res["total_staked_value_usd"], 5000000.0)
        self.assertEqual(res["annual_fee_revenue_usd"], 1277500.0)
        self.assertEqual(res["staking_apy_pct"], 25.55)
        self.assertEqual(res["daily_cashflow_per_10k_usd"], 7.00)
        self.assertEqual(res["projected_annual_ratio"], 1.5694)

    def test_secondary_arbitrage_profitable(self):
        # Fair value $0.0625 vs secondary market $0.0610 (2.4% discount)
        res = calculate_xstep_secondary_arbitrage(
            secondary_xstep_price_usd=0.0610,
            fair_xstep_value_usd=0.0625,
            redemption_fee_pct=0.0
        )
        self.assertTrue(res["is_profitable_arbitrage"])
        self.assertEqual(res["discount_pct"], 2.40)
        self.assertEqual(res["net_arb_profit_per_xstep_usd"], 0.0015)
        self.assertAlmostEqual(res["roi_pct"], 2.46, delta=0.02)

    def test_secondary_arbitrage_no_discount(self):
        # Trading at premium
        res = calculate_xstep_secondary_arbitrage(
            secondary_xstep_price_usd=0.0630,
            fair_xstep_value_usd=0.0625,
            redemption_fee_pct=0.0
        )
        self.assertFalse(res["is_profitable_arbitrage"])
        self.assertEqual(res["discount_pct"], 0.0)

    def test_annual_compounded_return(self):
        res = calculate_annual_compounded_staking_return(
            principal_usd=10000.0,
            staking_apy_pct=25.55,
            years=1
        )
        self.assertEqual(res["final_usd"], 12555.0)
        self.assertEqual(res["net_profit_usd"], 2555.0)

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
