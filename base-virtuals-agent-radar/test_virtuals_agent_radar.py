"""
Unit tests for Base Virtuals Protocol AI Agent Token Staking & Liquidity Subsidies Radar.
"""

import unittest
from virtuals_agent_radar import (
    calculate_agent_lp_staking_yield,
    calculate_agent_inference_buyback_burn,
    calculate_bonding_curve_graduation_progress,
    verify_vip_license
)

class TestVirtualsAgentRadar(unittest.TestCase):
    def test_lp_staking_yield(self):
        # $10k deposit, $1M pool TVL (1% share), $1.2M emissions (120% APR), $200k/day volume @ 1% fee (73% APR)
        res = calculate_agent_lp_staking_yield(
            deposit_usd=10000.0,
            total_lp_staked_usd=1000000.0,
            annual_virtual_reward_usd=1200000.0,
            agent_swap_volume_24h_usd=200000.0,
            pool_swap_fee_pct=1.0
        )
        self.assertEqual(res["staker_share_pct"], 1.0)
        self.assertEqual(res["emission_apr_pct"], 120.0)
        self.assertEqual(res["swap_fee_apr_pct"], 73.0)
        self.assertEqual(res["combined_net_apy_pct"], 193.0)
        self.assertEqual(res["daily_cashflow_usd"], 52.88)

    def test_inference_buyback_burn(self):
        # 50k calls/day @ 0.01 VIRTUAL ($1.50) => $750/day @ $0.05 token price = 15k tokens/day, 100M supply
        res = calculate_agent_inference_buyback_burn(
            daily_inference_calls=50000,
            avg_call_price_virtual=0.01,
            virtual_price_usd=1.50,
            agent_token_price_usd=0.05,
            agent_circulating_supply=100000000.0
        )
        self.assertEqual(res["daily_virtual_revenue"], 500.0)
        self.assertEqual(res["daily_revenue_usd"], 750.0)
        self.assertEqual(res["daily_agent_tokens_burned"], 15000.0)
        self.assertEqual(res["annual_tokens_burned"], 5475000.0)
        self.assertAlmostEqual(res["annual_deflation_pct"], 5.475, delta=0.01)

    def test_bonding_curve_graduation_progress(self):
        # 31,800 VIRTUAL out of 42,400 => 75%
        res = calculate_bonding_curve_graduation_progress(
            virtual_accumulated=31800.0,
            graduation_target_virtual=42400.0,
            virtual_price_usd=1.50
        )
        self.assertEqual(res["progress_pct"], 75.0)
        self.assertEqual(res["remaining_virtual"], 10600.0)
        self.assertEqual(res["remaining_usd"], 15900.0)
        self.assertFalse(res["graduated"])

    def test_bonding_curve_graduated(self):
        res = calculate_bonding_curve_graduation_progress(
            virtual_accumulated=45000.0,
            graduation_target_virtual=42400.0,
            virtual_price_usd=1.50
        )
        self.assertEqual(res["progress_pct"], 100.0)
        self.assertEqual(res["remaining_virtual"], 0.0)
        self.assertTrue(res["graduated"])

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
