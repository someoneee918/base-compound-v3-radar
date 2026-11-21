"""
Unit tests for Solana Hawksight Automated Liquidity Management (ALM) & CLMM Volatility Rebalance Radar.
"""

import unittest
from hawksight_clmm_radar import (
    calculate_clmm_capital_efficiency,
    calculate_hawksight_strategy_yield,
    calculate_volatility_regime_recommendation,
    verify_vip_license
)

class TestHawksightClmmRadar(unittest.TestCase):
    def test_capital_efficiency(self):
        # 5% range width => p_min = 0.95, p_max = 1.05
        res = calculate_clmm_capital_efficiency(5.0)
        self.assertEqual(res["range_width_pct"], 5.0)
        self.assertEqual(res["capital_multiplier"], 20.49)

    def test_strategy_yield(self):
        # $10k deposit, $5M 24h volume, $10M TVL, 0.05% fee, 5% width, 85% in range, 5% annual rebalance cost, 12x/day autocompound
        res = calculate_hawksight_strategy_yield(
            deposit_usd=10000.0,
            pool_volume_24h=5000000.0,
            pool_tvl=10000000.0,
            fee_tier_pct=0.05,
            range_width_pct=5.0,
            in_range_pct=85.0,
            rebalance_cost_annual_pct=5.0,
            autocompound_freq_per_day=12
        )
        self.assertEqual(res["base_fee_apr_pct"], 9.12)
        self.assertEqual(res["capital_multiplier"], 20.49)
        self.assertAlmostEqual(res["effective_fee_apr_pct"], 158.89, delta=0.5)
        self.assertGreater(res["compounded_apy_pct"], 350.0)
        self.assertGreater(res["net_apy_pct"], 340.0)
        self.assertGreater(res["daily_cashflow_usd"], 90.0)

    def test_volatility_regime_low(self):
        res = calculate_volatility_regime_recommendation(25.0)
        self.assertEqual(res["regime"], "Low Volatility (Tight Range)")
        self.assertEqual(res["recommended_range_width_pct"], 2.5)
        self.assertEqual(res["expected_in_range_pct"], 92.0)
        self.assertGreater(res["capital_multiplier"], 35.0)

    def test_volatility_regime_high(self):
        res = calculate_volatility_regime_recommendation(85.0)
        self.assertEqual(res["regime"], "High Volatility (Defensive Wide Range)")
        self.assertEqual(res["recommended_range_width_pct"], 15.0)
        self.assertEqual(res["expected_in_range_pct"], 76.0)

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
