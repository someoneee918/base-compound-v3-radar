#!/usr/bin/env python3
"""
Unit tests for Solana Orca Whirlpool Concentrated Liquidity Dynamic Fee & Volatility Tick Radar
"""

import unittest
from orca_whirlpool_radar import (
    calculate_whirlpool_concentrated_yield,
    simulate_volatility_tick_drift,
    calculate_fee_harvest_compound_net,
    generate_commercial_license,
    SOLANA_PAYOUT_WALLET,
    BASE_PAYOUT_WALLET
)

class TestOrcaWhirlpoolRadar(unittest.TestCase):

    def test_calculate_whirlpool_concentrated_yield(self):
        # 10,000 deposit, 4% tick range -> 50x concentration multiplier!
        # Pool TVL 10M, Daily Volume 5M at 30 bps fee tier = $15,000/day pool fees.
        # Effective deposit = 500k. LP share = 500k / 10M = 5.0%.
        # Daily revenue = $15,000 * 5% = $750/day. APY = (750 * 365 / 10000) * 100 = 2737.5%
        res = calculate_whirlpool_concentrated_yield(
            deposit_usd=10000.0,
            fee_tier_bps=30.0,
            tick_range_width_pct=4.0,
            daily_volume_usd=5000000.0,
            pool_tvl_usd=10000000.0
        )
        self.assertEqual(res.deposit_usd, 10000.0)
        self.assertEqual(res.concentration_multiplier, 50.0)
        self.assertEqual(res.daily_pool_fee_usd, 15000.0)
        self.assertEqual(res.lp_daily_revenue_usd, 750.0)
        self.assertEqual(res.annualized_fee_apy_pct, 2737.5)
        self.assertGreater(res.annualized_fee_apy_pct, res.unconcentrated_apy_pct)

    def test_simulate_volatility_tick_drift(self):
        # In range: current 180, range 170-190
        res_in = simulate_volatility_tick_drift(
            current_price=180.0,
            lower_tick_price=170.0,
            upper_tick_price=190.0,
            annualized_volatility_pct=65.0,
            days_horizon=7.0
        )
        self.assertGreater(res_in.in_range_probability_pct, 40.0)
        self.assertIn(res_in.status, ["STABLE_IN_RANGE", "MODERATE_DRIFT_WATCH"])
        self.assertLess(res_in.rebalance_urgency_score, 80)
        
        # Out of range lower
        res_out_lower = simulate_volatility_tick_drift(
            current_price=165.0,
            lower_tick_price=170.0,
            upper_tick_price=190.0
        )
        self.assertEqual(res_out_lower.in_range_probability_pct, 0.0)
        self.assertEqual(res_out_lower.out_of_range_risk_pct, 100.0)
        self.assertEqual(res_out_lower.status, "OUT_OF_RANGE_100_TOKEN_B")
        self.assertEqual(res_out_lower.rebalance_urgency_score, 100)

        # Out of range upper
        res_out_upper = simulate_volatility_tick_drift(
            current_price=195.0,
            lower_tick_price=170.0,
            upper_tick_price=190.0
        )
        self.assertEqual(res_out_upper.status, "OUT_OF_RANGE_100_TOKEN_A")

    def test_calculate_fee_harvest_compound_net(self):
        # Uncollected $15.00 fees, $0.002 gas, 0.1% slippage ($0.015).
        # Net = $14.98. Favorable = True.
        res = calculate_fee_harvest_compound_net(
            uncollected_fees_usd=15.0,
            sol_gas_fee_usd=0.002,
            reinvestment_slippage_pct=0.10
        )
        self.assertEqual(res.uncollected_fees_usd, 15.0)
        self.assertEqual(res.net_reinvested_usd, 14.98)
        self.assertTrue(res.is_favorable)
        self.assertEqual(res.optimal_harvest_frequency_hours, 24)

    def test_generate_commercial_license(self):
        lic_sol = generate_commercial_license(
            tx_hash="5xTestHashSolanaTx1234567890",
            payer_address="DW2MdHEq3qZ6nh9b5YFUoaPnBuuxC8Gz2785kwbbjSAM",
            chain="solana"
        )
        self.assertEqual(lic_sol["status"], "VIP_COMMERCIAL_LICENSE_ACTIVE")
        self.assertEqual(lic_sol["recipient_wallet"], SOLANA_PAYOUT_WALLET)
        self.assertTrue(lic_sol["license_id"].startswith("ORCA-WHIRLPOOL-VIP-"))
        
        lic_base = generate_commercial_license(
            tx_hash="0xabcd1234ef567890abcdef1234567890abcdef12",
            payer_address="0x1234567890123456789012345678901234567890",
            chain="base"
        )
        self.assertEqual(lic_base["recipient_wallet"], BASE_PAYOUT_WALLET)

    def test_edge_cases(self):
        # Zero fees
        res_zero = calculate_fee_harvest_compound_net(uncollected_fees_usd=0.0)
        self.assertFalse(res_zero.is_favorable)
        self.assertEqual(res_zero.net_reinvested_usd, 0.0)
        
        with self.assertRaises(ValueError):
            calculate_whirlpool_concentrated_yield(deposit_usd=-500.0)
            
        with self.assertRaises(ValueError):
            generate_commercial_license(tx_hash="short", payer_address="valid_payer_address_12345")

if __name__ == "__main__":
    unittest.main()
