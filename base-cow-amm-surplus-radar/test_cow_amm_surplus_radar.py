"""
Unit tests for Base CoW AMM MEV-Capturing Liquidity & LVR Protection Radar.
"""

import unittest
from cow_amm_surplus_radar import (
    calculate_lvr_loss_and_cow_surplus,
    calculate_solver_batch_auction_bid,
    calculate_annual_lp_surplus_dollar_gain,
    verify_vip_license
)

class TestCowAmmSurplusRadar(unittest.TestCase):
    def test_lvr_loss_and_cow_surplus(self):
        # $5M TVL, 60% vol, 15% fee APR, 85% surplus capture rate
        res = calculate_lvr_loss_and_cow_surplus(
            pool_tvl_usd=5000000.0,
            annual_volatility_pct=60.0,
            base_fee_apr_pct=15.0,
            solver_surplus_capture_rate_pct=85.0
        )
        self.assertEqual(res["lvr_loss_pct"], 4.5)
        self.assertEqual(res["annual_lvr_loss_usd"], 225000.0)
        self.assertEqual(res["standard_lp_net_apr_pct"], 10.5)
        self.assertAlmostEqual(res["surplus_captured_pct"], 3.825, delta=0.01)
        self.assertAlmostEqual(res["cow_lp_net_apr_pct"], 18.825, delta=0.01)
        self.assertAlmostEqual(res["outperformance_delta_pct"], 8.325, delta=0.01)
        self.assertAlmostEqual(res["daily_cashflow_per_10k_usd"], 5.16, delta=0.02)

    def test_solver_batch_auction_bid(self):
        # $250 arb opportunity, $0.35 gas, 15% solver margin ($37.50)
        res = calculate_solver_batch_auction_bid(
            arb_opportunity_usd=250.0,
            l2_gas_cost_usd=0.35,
            target_solver_margin_pct=15.0
        )
        self.assertTrue(res["is_profitable_for_solver"])
        self.assertEqual(res["solver_margin_usd"], 37.50)
        self.assertEqual(res["surplus_bid_to_pool_usd"], 212.15)
        self.assertEqual(res["surplus_share_pct"], 84.86)

    def test_annual_lp_surplus_dollar_gain(self):
        # $10k deposit, 8.33% delta
        res = calculate_annual_lp_surplus_dollar_gain(
            deposit_usd=10000.0,
            outperformance_delta_pct=8.33
        )
        self.assertEqual(res["annual_dollar_gain"], 833.0)
        self.assertAlmostEqual(res["daily_dollar_gain"], 2.28, delta=0.02)

    def test_solver_batch_auction_bid_zero_opportunity(self):
        # Edge case: zero opportunity raises ValueError
        with self.assertRaises(ValueError):
            calculate_solver_batch_auction_bid(arb_opportunity_usd=0.0)

    def test_vip_license_verification(self):
        base_valid = verify_vip_license(
            tx_hash="0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef12345678901234",
            chain="Base",
            recipient="0xF0E0D361bBE899F3089f0a968506eF2B97693c01",
            amount=5.0
        )
        self.assertTrue(base_valid["verified"])

        sol_valid = verify_vip_license(
            tx_hash="5xabcdef1234567890abcdef1234567890abcdef1234567890abcdef12345678901234",
            chain="Solana",
            recipient="DW2MdHEq3qZ6nh9b5YFUoaPnBuuxC8Gz2785kwbbjSAM",
            amount=0.03
        )
        self.assertTrue(sol_valid["verified"])

        invalid = verify_vip_license(
            tx_hash="short",
            chain="Base",
            recipient="0x0000000000000000000000000000000000000000",
            amount=1.0
        )
        self.assertFalse(invalid["verified"])

if __name__ == "__main__":
    unittest.main()
