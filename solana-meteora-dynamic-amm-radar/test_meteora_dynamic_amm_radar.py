#!/usr/bin/env python3
"""
Unit tests for Meteora Dynamic AMM & DLMM Volatility Fee Multiplier Radar
"""

import unittest
from meteora_dynamic_amm_radar import (
    calculate_dynamic_fee,
    simulate_dlmm_bin_yield,
    check_rebalance_trigger,
    generate_commercial_license,
    SOLANA_PAYOUT_WALLET,
    BASE_PAYOUT_WALLET
)

class TestMeteoraDynamicAMMRadar(unittest.TestCase):

    def test_calculate_dynamic_fee_low_and_spike(self):
        # Low volatility
        fee_low = calculate_dynamic_fee(base_fee_bps=15.0, volatility_index=2.0)
        self.assertEqual(fee_low.base_fee_bps, 15.0)
        self.assertAlmostEqual(fee_low.variable_fee_bps, 2.0, places=1)
        self.assertEqual(fee_low.volatility_regime, "CALM_LOW_VOLATILITY")
        
        # High volatility surge capped at max_fee_bps (500 bps)
        fee_spike = calculate_dynamic_fee(base_fee_bps=25.0, volatility_index=40.0, max_fee_bps=500.0)
        self.assertEqual(fee_spike.total_fee_bps, 500.0)
        self.assertEqual(fee_spike.total_fee_pct, 5.0)
        self.assertEqual(fee_spike.volatility_regime, "EXTREME_VOLATILITY_SPIKE")

    def test_simulate_dlmm_bin_yield(self):
        # 10k deposit in 100k active bin (10% share), $1,000,000 volume, 150 bps dynamic fee
        res = simulate_dlmm_bin_yield(
            deposit_usd=10000.0,
            active_bin_liquidity_usd=100000.0,
            daily_volume_usd=1000000.0,
            total_dynamic_fee_bps=150.0
        )
        self.assertEqual(res.deposit_usd, 10000.0)
        # Total daily fee = 1,000,000 * 0.0150 = 15,000; 10% share = 1,500/day
        self.assertEqual(res.active_bin_fees_daily, 15000.0)
        self.assertEqual(res.lp_daily_revenue_usd, 1500.0)
        # Annualized APY = (1500 * 365 / 10000) * 100 = 5475%
        self.assertEqual(res.annualized_fee_apy_pct, 5475.0)
        self.assertGreater(res.dynamic_boost_factor, 1.0)

    def test_check_rebalance_trigger_states(self):
        # Case 1: Healthy in range (current 150, range 100 - 200)
        res_in = check_rebalance_trigger(current_price=150.0, min_bin_price=100.0, max_bin_price=200.0)
        self.assertEqual(res_in.status, "HEALTHY_IN_RANGE")
        self.assertFalse(res_in.action_required)
        
        # Case 2: Near upper edge (current 198, range 100 - 200)
        res_near = check_rebalance_trigger(current_price=198.0, min_bin_price=100.0, max_bin_price=200.0)
        self.assertEqual(res_near.status, "NEAR_EDGE_REBALANCE_WARNING")
        self.assertTrue(res_near.action_required)
        
        # Case 3: Out of range lower (current 95, range 100 - 200) -> 100% Token B
        res_out_b = check_rebalance_trigger(current_price=95.0, min_bin_price=100.0, max_bin_price=200.0)
        self.assertEqual(res_out_b.status, "OUT_OF_RANGE_100_TOKEN_B")
        self.assertTrue(res_out_b.action_required)
        self.assertEqual(res_out_b.rebalance_urgency_score, 100)

        # Case 4: Out of range upper (current 205, range 100 - 200) -> 100% Token A
        res_out_a = check_rebalance_trigger(current_price=205.0, min_bin_price=100.0, max_bin_price=200.0)
        self.assertEqual(res_out_a.status, "OUT_OF_RANGE_100_TOKEN_A")
        self.assertTrue(res_out_a.action_required)

    def test_generate_commercial_license(self):
        lic_sol = generate_commercial_license(
            tx_hash="5xTestHashSolanaTransaction1234567890",
            payer_address="So11111111111111111111111111111111111111112",
            chain="solana"
        )
        self.assertEqual(lic_sol["status"], "VIP_COMMERCIAL_LICENSE_ACTIVE")
        self.assertEqual(lic_sol["recipient_wallet"], SOLANA_PAYOUT_WALLET)
        self.assertTrue(lic_sol["license_id"].startswith("METEORA-VIP-"))
        
        lic_base = generate_commercial_license(
            tx_hash="0xabcd1234ef567890abcdef1234567890abcdef12",
            payer_address="0x1234567890123456789012345678901234567890",
            chain="base"
        )
        self.assertEqual(lic_base["recipient_wallet"], BASE_PAYOUT_WALLET)

    def test_edge_cases(self):
        # Zero volume
        res_zero = simulate_dlmm_bin_yield(
            deposit_usd=1000.0,
            active_bin_liquidity_usd=10000.0,
            daily_volume_usd=0.0,
            total_dynamic_fee_bps=100.0
        )
        self.assertEqual(res_zero.lp_daily_revenue_usd, 0.0)
        self.assertEqual(res_zero.annualized_fee_apy_pct, 0.0)
        
        # Invalid bounds raise ValueError
        with self.assertRaises(ValueError):
            check_rebalance_trigger(current_price=100.0, min_bin_price=150.0, max_bin_price=120.0)
            
        with self.assertRaises(ValueError):
            generate_commercial_license(tx_hash="short", payer_address="valid_payer_address_12345")

if __name__ == "__main__":
    unittest.main()
