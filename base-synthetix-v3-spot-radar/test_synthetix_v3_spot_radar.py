#!/usr/bin/env python3
"""
Unit tests for Base Synthetix v3 Perps Liquidity & Spot Synth Arbitrage Radar
"""

import unittest
from synthetix_v3_spot_radar import (
    calculate_spot_synth_arbitrage,
    simulate_synthetix_vault_lp_yield,
    calculate_c_ratio_buffer,
    generate_commercial_license,
    BASE_PAYOUT_WALLET,
    SOLANA_PAYOUT_WALLET
)

class TestSynthetixV3SpotRadar(unittest.TestCase):

    def test_calculate_spot_synth_arbitrage(self):
        # Oracle = $3,200, External DEX = $3,215 (Spread = $15 = 46.88 bps)
        # Trade size $20,000. Gross profit = 20,000 * (15 / 3200) = $93.75
        # Snx fee 5 bps = $10. DEX fee 5 bps = $10. Gas = $0.35. Total fee = $20.35
        # Net profit = 93.75 - 20.35 = $73.40 (ROI ~ 0.367%)
        res = calculate_spot_synth_arbitrage(
            spot_oracle_price_usd=3200.0,
            external_dex_price_usd=3215.0,
            trade_size_usd=20000.0,
            spot_market_skew_usd=0.0,
            base_atomic_fee_bps=5.0,
            dex_swap_fee_bps=5.0,
            gas_cost_usd=0.35
        )
        self.assertEqual(res.trade_size_usd, 20000.0)
        self.assertEqual(res.synthetix_fee_usd, 10.0)
        self.assertEqual(res.dex_fee_usd, 10.0)
        self.assertEqual(res.net_arbitrage_profit_usd, 73.40)
        self.assertTrue(res.is_profitable)
        self.assertEqual(res.status, "HIGH_CONVICTION_ATOMIC_ARBITRAGE")

    def test_simulate_synthetix_vault_lp_yield(self):
        # $50,000 deposit in 25M TVL (0.20% share).
        # Daily volume 40M at 4 bps = $16,000 + $5,000 liquidation penalties = $21,000 daily pool fees.
        # User daily = $21,000 * 0.20% = $42.00/day.
        # Annualized APY = (42 * 365 / 50000) * 100 = 30.66%
        res = simulate_synthetix_vault_lp_yield(
            collateral_deposited_usd=50000.0,
            pool_delegated_tvl_usd=25000000.0,
            perps_daily_volume_usd=40000000.0,
            base_trading_fee_bps=4.0,
            liquidation_penalties_daily_usd=5000.0
        )
        self.assertEqual(res.collateral_deposited_usd, 50000.0)
        self.assertEqual(res.daily_pool_fee_revenue_usd, 21000.0)
        self.assertEqual(res.lp_daily_cashflow_usd, 42.0)
        self.assertEqual(res.annualized_lp_apy_pct, 30.66)
        self.assertEqual(res.liquidation_bonus_share_daily_usd, 10.0)

    def test_calculate_c_ratio_buffer(self):
        # $100,000 collateral, $50,000 debt -> 200% C-Ratio (Safe)
        # Min collateral at 125% = $62,500. Cushion = $37,500.
        res_safe = calculate_c_ratio_buffer(
            collateral_usd=100000.0,
            debt_usd=50000.0,
            liquidation_c_ratio_pct=125.0
        )
        self.assertEqual(res_safe.current_c_ratio_pct, 200.0)
        self.assertEqual(res_safe.cushion_until_liquidation_usd, 37500.0)
        self.assertEqual(res_safe.status, "SAFE_TARGET_C_RATIO")
        
        # Underwater: $60,000 collateral, $50,000 debt -> 120% C-Ratio (Liquidatable)
        res_under = calculate_c_ratio_buffer(
            collateral_usd=60000.0,
            debt_usd=50000.0,
            liquidation_c_ratio_pct=125.0
        )
        self.assertEqual(res_under.current_c_ratio_pct, 120.0)
        self.assertLess(res_under.cushion_until_liquidation_usd, 0)
        self.assertEqual(res_under.status, "UNDERWATER_LIQUIDATABLE")

    def test_generate_commercial_license(self):
        lic_base = generate_commercial_license(
            tx_hash="0xabcdef1234567890abcdef1234567890abcdef12",
            payer_address="0x1111222233334444555566667777888899990000",
            chain="base"
        )
        self.assertEqual(lic_base["status"], "VIP_COMMERCIAL_LICENSE_ACTIVE")
        self.assertEqual(lic_base["recipient_wallet"], BASE_PAYOUT_WALLET)
        self.assertTrue(lic_base["license_id"].startswith("SNX-V3-VIP-"))
        
        lic_sol = generate_commercial_license(
            tx_hash="5xTestHashSolanaTx1234567890",
            payer_address="DW2MdHEq3qZ6nh9b5YFUoaPnBuuxC8Gz2785kwbbjSAM",
            chain="solana"
        )
        self.assertEqual(lic_sol["recipient_wallet"], SOLANA_PAYOUT_WALLET)

    def test_edge_cases(self):
        # Zero debt returns 999.0 safe
        res_zero = calculate_c_ratio_buffer(collateral_usd=50000.0, debt_usd=0.0)
        self.assertEqual(res_zero.current_c_ratio_pct, 999.0)
        self.assertEqual(res_zero.status, "ZERO_DEBT_SAFE")
        
        with self.assertRaises(ValueError):
            calculate_spot_synth_arbitrage(spot_oracle_price_usd=-100.0, external_dex_price_usd=100.0, trade_size_usd=1000.0)
            
        with self.assertRaises(ValueError):
            generate_commercial_license(tx_hash="short", payer_address="valid_address_12345")

if __name__ == "__main__":
    unittest.main()
