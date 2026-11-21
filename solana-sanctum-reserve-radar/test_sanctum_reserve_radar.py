"""
Unit tests for Solana Sanctum Reserve Pool & Instant Unstake Liquidity Radar.
"""

import unittest
from sanctum_reserve_radar import (
    calculate_instant_unstake_fee,
    calculate_reserve_pool_lp_yield,
    calculate_delayed_vs_instant_unstake_arbitrage,
    verify_vip_license
)

class TestSanctumReserveRadar(unittest.TestCase):
    def test_instant_unstake_fee(self):
        # 100 SOL unstake, 500k total reserve, 350k borrowed (70% util)
        res = calculate_instant_unstake_fee(
            unstake_amount_sol=100.0,
            total_reserve_sol=500000.0,
            borrowed_reserve_sol=350000.0,
            min_fee_pct=0.08,
            max_fee_pct=3.0
        )
        self.assertEqual(res["utilization_pct"], 70.0)
        self.assertEqual(res["fee_pct"], 1.5108)
        self.assertEqual(res["fee_sol"], 1.5108)
        self.assertEqual(res["received_sol"], 98.4892)

    def test_reserve_pool_lp_yield(self):
        # 500k SOL reserve, 7.20% native staking APR, 25k daily volume @ 1.5% fee
        res = calculate_reserve_pool_lp_yield(
            total_reserve_sol=500000.0,
            native_staking_apr_pct=7.20,
            daily_unstake_volume_sol=25000.0,
            avg_fee_pct=1.50
        )
        self.assertEqual(res["daily_fee_revenue_sol"], 375.0)
        self.assertEqual(res["fee_apr_pct"], 27.38)
        self.assertEqual(res["total_lp_apy_pct"], 34.58)
        self.assertAlmostEqual(res["daily_yield_per_100_sol"], 0.0947, places=4)

    def test_delayed_vs_instant_arbitrage_wait(self):
        # 100 SOL, 1.51% fee vs 2 days wait @ 12% annual cost
        res = calculate_delayed_vs_instant_unstake_arbitrage(
            unstake_amount_sol=100.0,
            fee_pct=1.51,
            days_until_epoch_end=2.0,
            annual_cost_of_capital_pct=12.0
        )
        self.assertEqual(res["instant_fee_sol"], 1.51)
        self.assertEqual(res["delayed_capital_cost_sol"], 0.0658)
        self.assertEqual(res["savings_by_waiting_sol"], 1.4442)
        self.assertEqual(res["recommendation"], "Wait for Epoch Deactivation")

    def test_delayed_vs_instant_arbitrage_instant(self):
        # High cost of capital (800% APR e.g. urgent liquidation or MEV opportunity)
        res = calculate_delayed_vs_instant_unstake_arbitrage(
            unstake_amount_sol=100.0,
            fee_pct=0.50,
            days_until_epoch_end=2.5,
            annual_cost_of_capital_pct=800.0
        )
        self.assertEqual(res["recommendation"], "Instant Unstake via Reserve Pool")

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
