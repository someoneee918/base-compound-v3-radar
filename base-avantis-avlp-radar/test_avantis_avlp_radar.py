#!/usr/bin/env python3
"""
Unit tests for Base Avantis Protocol Senior/Junior AVLP Tranche Yield & Skew Funding Velocity Radar
"""

import unittest
from avantis_avlp_radar import (
    calculate_tranche_yield_waterfall,
    simulate_skew_funding_velocity,
    calculate_trader_liquidation_margin,
    generate_commercial_license,
    BASE_PAYOUT_WALLET,
    SOLANA_PAYOUT_WALLET
)

class TestAvantisAVLPRadar(unittest.TestCase):

    def test_calculate_tranche_yield_waterfall(self):
        # Senior TVL 6M, Junior TVL 2M, Volume 8M at 6 bps = $4,800/day fees.
        # Senior receives 35% = $1,680/day -> APY = (1680 * 365 / 6M) * 100 = 10.22%
        # Junior receives 65% = $3,120/day + trader losses $15,000 = $18,120/day -> APY = (18120 * 365 / 2M) * 100 = 330.69%
        res_jr = calculate_tranche_yield_waterfall(
            deposit_usd=10000.0,
            tranche="junior",
            total_senior_tvl=6000000.0,
            total_junior_tvl=2000000.0,
            daily_trading_volume=8000000.0,
            trader_net_pnl_daily=-15000.0,
            base_trading_fee_bps=6.0
        )
        self.assertEqual(res_jr.tranche, "JUNIOR")
        self.assertEqual(res_jr.senior_apy_pct, 10.22)
        self.assertEqual(res_jr.junior_apy_pct, 330.69)
        self.assertEqual(res_jr.user_annual_apy_pct, 330.69)
        self.assertGreater(res_jr.user_daily_revenue_usd, 50.0)
        
        # Senior test
        res_sr = calculate_tranche_yield_waterfall(deposit_usd=50000.0, tranche="senior")
        self.assertEqual(res_sr.tranche, "SENIOR")
        self.assertEqual(res_sr.user_annual_apy_pct, res_sr.senior_apy_pct)
        self.assertEqual(res_sr.first_loss_absorbed_usd, 0.0)

    def test_simulate_skew_funding_velocity(self):
        # Long OI 7M, Short OI 3M -> Total 10M. Skew = (7-3)/10 = +0.40.
        # Annual funding = 0.40 * 25.0 + 6.0 = 16.0%.
        # Arbitrage ROI = 16.0 - 2.5 = 13.5%.
        res = simulate_skew_funding_velocity(
            long_oi_usd=7000000.0,
            short_oi_usd=3000000.0,
            base_borrow_apr=6.0,
            skew_multiplier=0.25
        )
        self.assertEqual(res.skew_ratio, 0.40)
        self.assertEqual(res.skew_direction, "LONG_HEAVY_PAYING_SHORTS")
        self.assertEqual(res.annualized_funding_rate_pct, 16.0)
        self.assertEqual(res.arbitrage_annual_roi_pct, 13.5)
        self.assertEqual(res.arbitrage_urgency, "HIGH_CONVICTION_ARBITRAGE")

    def test_calculate_trader_liquidation_margin(self):
        # 10,000 col, 100,000 position (10x leverage). Fee = 100. MM = 1.0% (1,000).
        # Effective col = 9,900. Remaining equity = 9,900 - 1,000 = 8,900.
        # Drop pct = 8,900 / 100,000 = 8.90%.
        res = calculate_trader_liquidation_margin(
            collateral_usd=10000.0,
            position_size_usd=100000.0,
            accumulated_fee_usd=100.0,
            maintenance_margin_pct=1.0
        )
        self.assertEqual(res.leverage, 10.0)
        self.assertEqual(res.remaining_equity_usd, 8900.0)
        self.assertEqual(res.liquidation_drop_pct, 8.90)
        self.assertEqual(res.status, "HEALTHY_MARGIN_BUFFER")
        self.assertFalse(res.is_liquidatable)
        
        # Liquidatable position
        res_liq = calculate_trader_liquidation_margin(
            collateral_usd=1000.0,
            position_size_usd=100000.0,
            accumulated_fee_usd=500.0
        )
        self.assertTrue(res_liq.is_liquidatable)
        self.assertEqual(res_liq.status, "LIQUIDATABLE_IMMEDIATE")

    def test_generate_commercial_license(self):
        lic_base = generate_commercial_license(
            tx_hash="0xabcdef1234567890abcdef1234567890abcdef12",
            payer_address="0x1234567890123456789012345678901234567890",
            chain="base"
        )
        self.assertEqual(lic_base["status"], "VIP_COMMERCIAL_LICENSE_ACTIVE")
        self.assertEqual(lic_base["recipient_wallet"], BASE_PAYOUT_WALLET)
        self.assertTrue(lic_base["license_id"].startswith("AVANTIS-VIP-"))
        
        lic_sol = generate_commercial_license(
            tx_hash="5xTestHashSolanaTx1234567890",
            payer_address="DW2MdHEq3qZ6nh9b5YFUoaPnBuuxC8Gz2785kwbbjSAM",
            chain="solana"
        )
        self.assertEqual(lic_sol["recipient_wallet"], SOLANA_PAYOUT_WALLET)

    def test_edge_cases(self):
        # Balanced market skew
        res_zero = simulate_skew_funding_velocity(long_oi_usd=5000000.0, short_oi_usd=5000000.0)
        self.assertEqual(res_zero.skew_ratio, 0.0)
        self.assertEqual(res_zero.arbitrage_urgency, "BALANCED_MARKET")
        
        with self.assertRaises(ValueError):
            calculate_tranche_yield_waterfall(deposit_usd=-100.0)
            
        with self.assertRaises(ValueError):
            generate_commercial_license(tx_hash="short", payer_address="valid_address_12345")

if __name__ == "__main__":
    unittest.main()
