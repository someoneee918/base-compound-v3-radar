"""
Unit tests for Base Chainlink Data Streams & Automation Low-Latency Oracle Radar.
"""

import unittest
from chainlink_streams_radar import (
    calculate_data_streams_gas_savings,
    calculate_keeper_automation_profit,
    calculate_adverse_selection_protection,
    verify_vip_license
)

class TestChainlinkStreamsRadar(unittest.TestCase):
    def test_gas_savings_calculation(self):
        # 864k push updates vs 50k stream verifies
        res = calculate_data_streams_gas_savings(
            monthly_push_updates=864000,
            monthly_user_trades=50000,
            push_gas_units=80000,
            stream_verify_gas_units=120000,
            gas_price_gwei=0.05,
            eth_price_usd=3000.0
        )
        self.assertEqual(res["total_push_cost_usd"], 10368.0)
        self.assertEqual(res["total_stream_cost_usd"], 900.0)
        self.assertEqual(res["monthly_gas_savings_usd"], 9468.0)
        self.assertEqual(res["annual_gas_savings_usd"], 113616.0)
        self.assertEqual(res["gas_reduction_pct"], 91.32)

    def test_keeper_automation_profit(self):
        # 2,500 upkeeps/day @ 150k gas, 0.05 Gwei, $3000 ETH, 20% premium
        res = calculate_keeper_automation_profit(
            daily_upkeeps=2500,
            avg_execution_gas_units=150000,
            gas_price_gwei=0.05,
            eth_price_usd=3000.0,
            keeper_reward_premium_pct=20.0
        )
        self.assertEqual(res["gas_cost_usd"], 0.0225)
        self.assertEqual(res["payout_received_usd"], 0.0270)
        self.assertEqual(res["profit_per_upkeep_usd"], 0.0045)
        self.assertEqual(res["daily_profit_usd"], 11.25)
        self.assertEqual(res["annual_profit_usd"], 4106.25)

    def test_adverse_selection_protection(self):
        # $50k notional, 60s staleness
        res = calculate_adverse_selection_protection(
            trade_notional_usd=50000.0,
            oracle_staleness_seconds=60.0,
            volatility_per_second_bps=0.05
        )
        self.assertEqual(res["expected_price_lag_bps"], 3.0)
        self.assertEqual(res["front_running_risk_usd"], 15.0)
        self.assertAlmostEqual(res["protected_value_usd"], 14.875, delta=0.01)

    def test_negative_savings_handled(self):
        # Edge case: very high trades relative to push updates
        res = calculate_data_streams_gas_savings(
            monthly_push_updates=100,
            monthly_user_trades=100000,
            push_gas_units=80000,
            stream_verify_gas_units=120000,
            gas_price_gwei=0.05,
            eth_price_usd=3000.0
        )
        self.assertEqual(res["monthly_gas_savings_usd"], 0.0)

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
