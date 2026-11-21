"""
Unit tests for Solana Dialect Actions & Blinks Creator Fee & Compute Unit Radar.
"""

import unittest
from dialect_blinks_radar import (
    calculate_blink_creator_revenue,
    calculate_compute_unit_landing_rate,
    calculate_conversion_loss_due_to_drops,
    verify_vip_license
)

class TestDialectBlinksRadar(unittest.TestCase):
    def test_blink_creator_revenue(self):
        # 25k impressions, 1.2% conversion => 300 txs @ $45 avg volume, 1.0% creator fee
        res = calculate_blink_creator_revenue(
            daily_impressions=25000,
            conversion_rate_pct=1.2,
            avg_tx_volume_usd=45.0,
            creator_fee_pct=1.0
        )
        self.assertEqual(res["daily_executed_txs"], 300)
        self.assertEqual(res["total_daily_volume_usd"], 13500.0)
        self.assertEqual(res["daily_creator_revenue_usd"], 135.0)
        self.assertEqual(res["monthly_revenue_usd"], 4050.0)
        self.assertEqual(res["annual_revenue_usd"], 49275.0)

    def test_compute_unit_landing_rate_high(self):
        # 150k CU, 50k micro-lamports vs 30k p75 threshold
        res = calculate_compute_unit_landing_rate(
            cu_limit=150000,
            micro_lamports_per_cu=50000,
            current_p75_micro_lamports=30000
        )
        self.assertEqual(res["landing_rate_pct"], 98.5)
        self.assertEqual(res["priority_tier"], "High Priority (Immediate Next Block)")
        self.assertEqual(res["priority_fee_lamports"], 7500)
        self.assertEqual(res["total_tx_fee_lamports"], 12500)

    def test_compute_unit_landing_rate_low(self):
        res = calculate_compute_unit_landing_rate(
            cu_limit=150000,
            micro_lamports_per_cu=1000,
            current_p75_micro_lamports=30000
        )
        self.assertEqual(res["landing_rate_pct"], 65.0)
        self.assertEqual(res["priority_tier"], "Low / Dropped under Congestion")

    def test_conversion_loss_due_to_drops(self):
        # 25k impressions, 1.2% conversion => 300 potential, 65% landing rate => 105 failed txs @ $0.45 rev
        res = calculate_conversion_loss_due_to_drops(
            daily_impressions=25000,
            conversion_rate_pct=1.2,
            avg_revenue_per_tx_usd=0.45,
            landing_rate_pct=65.0
        )
        self.assertEqual(res["potential_daily_txs"], 300.0)
        self.assertEqual(res["failed_daily_txs"], 105.0)
        self.assertEqual(res["daily_lost_revenue_usd"], 47.25)
        self.assertEqual(res["annual_lost_revenue_usd"], 17246.25)

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
