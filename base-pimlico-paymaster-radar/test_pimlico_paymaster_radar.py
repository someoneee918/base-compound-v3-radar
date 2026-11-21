"""
Unit tests for Base Pimlico / ERC-4337 Account Abstraction Paymaster & Bundler Gas Sponsorship Radar.
"""

import unittest
from pimlico_paymaster_radar import (
    calculate_userop_gas_cost,
    calculate_paymaster_treasury_runway,
    calculate_daily_paymaster_earnings,
    verify_vip_license
)

class TestPimlicoPaymasterRadar(unittest.TestCase):
    def test_userop_gas_cost_calculation(self):
        # 100k call + 50k verification + 30k preVerification = 180k gas @ 0.05 Gwei + 15e12 wei L1 fee, $3000 ETH, 15% markup
        res = calculate_userop_gas_cost(
            call_gas_limit=100000,
            verification_gas_limit=50000,
            pre_verification_gas=30000,
            max_fee_per_gas_gwei=0.05,
            l1_data_fee_wei=15000000000000,
            eth_price_usd=3000.0,
            paymaster_markup_pct=15.0
        )
        self.assertEqual(res["total_l2_gas_units"], 180000)
        self.assertEqual(res["total_userop_gas_eth"], 0.000024)
        self.assertEqual(res["actual_cost_usd"], 0.0720)
        self.assertEqual(res["sponsored_price_charged_usd"], 0.0828)
        self.assertEqual(res["paymaster_net_profit_usd"], 0.0108)
        self.assertAlmostEqual(res["margin_pct"], 13.04, delta=0.5)

    def test_paymaster_treasury_runway_healthy(self):
        # 2.0 ETH deposit, 10,000 userops/day @ 0.000024 ETH/op, $3000 ETH
        res = calculate_paymaster_treasury_runway(
            entrypoint_deposit_eth=2.0,
            daily_userops=10000,
            avg_userop_gas_eth=0.000024,
            eth_price_usd=3000.0
        )
        self.assertTrue(res["is_healthy"])
        self.assertEqual(res["entrypoint_deposit_usd"], 6000.0)
        self.assertEqual(res["daily_gas_consumption_eth"], 0.24)
        self.assertEqual(res["daily_cost_usd"], 720.0)
        self.assertEqual(res["runway_days"], 8.33)

    def test_paymaster_treasury_runway_critical(self):
        # Low deposit: 0.1 ETH with 10k ops/day => runway < 1 day
        res = calculate_paymaster_treasury_runway(
            entrypoint_deposit_eth=0.1,
            daily_userops=10000,
            avg_userop_gas_eth=0.000024,
            eth_price_usd=3000.0
        )
        self.assertFalse(res["is_healthy"])
        self.assertLess(res["runway_days"], 1.0)

    def test_daily_paymaster_earnings(self):
        res = calculate_daily_paymaster_earnings(
            daily_userops=10000,
            avg_profit_per_userop_usd=0.0108
        )
        self.assertEqual(res["daily_profit_usd"], 108.0)
        self.assertEqual(res["monthly_runrate_usd"], 3240.0)
        self.assertEqual(res["annual_runrate_usd"], 39420.0)

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
