"""
Unit tests for Solana Lifinity LFNTY Staking & Protocol Revenue Distribution Radar.
"""

import unittest
from lifinity_lfnty_radar import (
    calculate_velfnty_power_and_share,
    calculate_velfnty_staking_yield,
    calculate_protocol_revenue_projection,
    verify_vip_license
)

class TestLifinityLfntyRadar(unittest.TestCase):
    def test_velfnty_power_max_lock(self):
        # 10k LFNTY locked 48 months => 4.0x multiplier = 40k veLFNTY (2.0% share of 2M)
        res = calculate_velfnty_power_and_share(
            lfnty_staked=10000.0,
            lock_months=48,
            total_velfnty_supply=2000000.0
        )
        self.assertEqual(res["lock_months"], 48)
        self.assertEqual(res["multiplier"], 4.0)
        self.assertEqual(res["velfnty_power"], 40000.0)
        self.assertEqual(res["pool_share_pct"], 2.0)

    def test_velfnty_power_partial_lock(self):
        # 10k LFNTY locked 12 months => 1.0x multiplier = 10k veLFNTY
        res = calculate_velfnty_power_and_share(
            lfnty_staked=10000.0,
            lock_months=12,
            total_velfnty_supply=2000000.0
        )
        self.assertEqual(res["lock_months"], 12)
        self.assertEqual(res["multiplier"], 1.0)
        self.assertEqual(res["velfnty_power"], 10000.0)
        self.assertEqual(res["pool_share_pct"], 0.5)

    def test_velfnty_staking_yield(self):
        # $10k deposit, 48 mo lock, $1.00 LFNTY, 20M total veLFNTY, $7500 daily revenue
        res = calculate_velfnty_staking_yield(
            deposit_usd=10000.0,
            lock_months=48,
            total_velfnty_supply=20000000.0,
            daily_protocol_revenue_usd=7500.0,
            lfnty_price_usd=1.00
        )
        self.assertEqual(res["multiplier"], 4.0)
        self.assertEqual(res["velfnty_power"], 40000.0)
        self.assertEqual(res["pool_share_pct"], 0.2)
        self.assertEqual(res["daily_revenue_payout_usd"], 15.0)
        self.assertEqual(res["annual_revenue_payout_usd"], 5475.0)
        self.assertEqual(res["real_yield_apr_pct"], 54.75)

    def test_protocol_revenue_projection(self):
        # $15M daily volume @ 0.05% fee
        res = calculate_protocol_revenue_projection(
            daily_trading_volume_usd=15000000.0,
            avg_protocol_fee_pct=0.05
        )
        self.assertEqual(res["daily_revenue_usd"], 7500.0)
        self.assertEqual(res["monthly_revenue_usd"], 225000.0)
        self.assertEqual(res["annual_revenue_usd"], 2737500.0)

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
