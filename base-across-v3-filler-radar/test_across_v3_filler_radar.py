"""
Unit tests for Base Across Protocol v3 Intent Settlement & Filler Gas Profitability Radar.
"""

import unittest
from across_v3_filler_radar import (
    calculate_filler_profit,
    calculate_across_lp_dynamic_apy,
    calculate_priority_gas_bidding,
    verify_vip_license
)

class TestAcrossV3FillerRadar(unittest.TestCase):
    def test_filler_profit_profitable(self):
        # $10,000 fill, 10 bps fee ($10), 0.0001 ETH gas at $3000 ($0.30), 2h delay at 12% annual cost
        res = calculate_filler_profit(
            fill_amount_usdc=10000.0,
            user_relayer_fee_bps=10.0,
            l2_gas_eth=0.0001,
            eth_price_usd=3000.0,
            reimbursement_delay_hours=2.0,
            annual_cost_of_capital_pct=12.0
        )
        self.assertTrue(res["is_profitable"])
        self.assertEqual(res["gross_fee_usdc"], 10.0)
        self.assertEqual(res["gas_cost_usd"], 0.30)
        self.assertEqual(res["net_profit_usdc"], 9.43)
        self.assertEqual(res["net_margin_bps"], 9.43)
        self.assertEqual(res["annualized_roi_pct"], 412.86)

    def test_filler_profit_unprofitable_gas_spike(self):
        # Small $50 fill with high gas ($1.50) and low fee (5 bps = $0.025)
        res = calculate_filler_profit(
            fill_amount_usdc=50.0,
            user_relayer_fee_bps=5.0,
            l2_gas_eth=0.0005,
            eth_price_usd=3000.0,
            reimbursement_delay_hours=2.0,
            annual_cost_of_capital_pct=10.0
        )
        self.assertFalse(res["is_profitable"])
        self.assertLess(res["net_profit_usdc"], 0.0)

    def test_across_lp_dynamic_apy(self):
        # $50M total, $35M borrowed (70% util), kink at 80%
        res = calculate_across_lp_dynamic_apy(
            total_pool_liquidity_usdc=50000000.0,
            borrowed_liquidity_usdc=35000000.0,
            base_fee_pct=1.0,
            kink_utilization_pct=80.0,
            slope1_pct=4.0,
            slope2_pct=25.0
        )
        self.assertEqual(res["utilization_pct"], 70.0)
        self.assertEqual(res["borrow_rate_pct"], 4.5)
        self.assertEqual(res["lp_yield_apy_pct"], 3.15)
        self.assertEqual(res["daily_lp_yield_per_10k_usd"], 0.86)

    def test_priority_gas_bidding(self):
        res = calculate_priority_gas_bidding(
            standard_priority_gwei=0.001,
            fast_priority_gwei=0.05,
            gas_units=150000,
            eth_price_usd=3000.0
        )
        self.assertGreater(res["estimated_fill_win_rate_pct"], 90.0)
        self.assertGreater(res["priority_premium_usd"], 0.0)

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
            tx_hash="0x123",
            chain="Base",
            recipient="0x0000000000000000000000000000000000000000",
            amount=1.0
        )
        self.assertFalse(invalid["verified"])

if __name__ == "__main__":
    unittest.main()
