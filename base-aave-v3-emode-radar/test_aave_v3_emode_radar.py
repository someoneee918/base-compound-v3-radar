#!/usr/bin/env python3
"""
Unit tests for Base Aave v3 E-Mode Correlated Leverage & Ultra-Tight Liquidation Radar
"""

import unittest
from aave_v3_emode_radar import (
    calculate_emode_position,
    simulate_correlated_depeg_liquidation,
    calculate_tight_liquidator_profit,
    generate_commercial_license,
    BASE_PAYOUT_WALLET,
    SOLANA_PAYOUT_WALLET
)

class TestAaveV3EModeRadar(unittest.TestCase):

    def test_calculate_emode_position(self):
        # 10 ETH initial at 10.0x leverage -> 100 ETH collateral, 90 ETH debt
        # Staking 3.6% on 100 ETH = 3.6 ETH earn. Borrow 2.1% on 90 ETH = 1.89 ETH cost.
        # Net earn = 1.71 ETH on 10 ETH deposit = 17.10% net APY!
        # Health factor = (100 * 0.95) / 90 = 95 / 90 = 1.0556
        res = calculate_emode_position(
            deposit_asset="cbETH",
            deposit_amount_eth=10.0,
            leverage_multiplier=10.0,
            staking_yield_apr=3.6,
            eth_borrow_apr=2.1
        )
        self.assertEqual(res.deposit_amount_eth, 10.0)
        self.assertEqual(res.leverage_multiplier, 10.0)
        self.assertEqual(res.total_collateral_eth, 100.0)
        self.assertEqual(res.borrowed_debt_eth, 90.0)
        self.assertEqual(res.current_ltv_pct, 90.0)
        self.assertEqual(res.health_factor, 1.0556)
        self.assertEqual(res.net_staking_apr_pct, 17.10)
        self.assertEqual(res.gross_yield_boost_factor, 4.75)
        self.assertGreater(res.daily_cashflow_usd, 14.0)

    def test_simulate_correlated_depeg_liquidation(self):
        # At 10x leverage, Debt/Collateral = 0.90. LT = 0.95.
        # Liq Ratio = 0.90 / 0.95 = 0.9474.
        # Tolerable depeg = (1.0 - 0.9474) / 1.0 = 5.26%.
        res = simulate_correlated_depeg_liquidation(leverage_multiplier=10.0)
        self.assertEqual(res.liquidation_price_ratio, 0.9474)
        self.assertEqual(res.max_tolerable_depeg_pct, 5.26)
        self.assertEqual(res.status, "HEALTHY_EMODE_BUFFER")
        self.assertTrue(res.is_safe)
        
        # At 14x leverage, Debt/Col = 13/14 = 0.92857. Liq Ratio = 0.92857 / 0.95 = 0.9774.
        # Buffer = 2.26%.
        res_high = simulate_correlated_depeg_liquidation(leverage_multiplier=14.0)
        self.assertEqual(res_high.liquidation_price_ratio, 0.9774)
        self.assertEqual(res_high.max_tolerable_depeg_pct, 2.26)
        self.assertEqual(res_high.status, "TIGHT_DEPEG_WARNING")
        self.assertTrue(res_high.is_safe)

    def test_calculate_tight_liquidator_profit(self):
        # Repaying 20 ETH debt at $3,200 ($64,000 value).
        # 1.0% bonus = $640. Slippage 0.15% on $64,640 = $96.96. Gas = $0.35.
        # Net profit = $640 - $96.96 - $0.35 = $542.69.
        res = calculate_tight_liquidator_profit(
            debt_to_repay_eth=20.0,
            eth_price_usd=3200.0,
            liquidation_bonus_pct=1.0,
            gas_cost_usd=0.35,
            dex_slippage_pct=0.15
        )
        self.assertEqual(res.debt_to_repay_eth, 20.0)
        self.assertEqual(res.debt_value_usd, 64000.0)
        self.assertEqual(res.seized_collateral_eth, 20.2)
        self.assertEqual(res.gross_bonus_usd, 640.0)
        self.assertEqual(res.net_profit_usd, 542.69)
        self.assertTrue(res.is_profitable)
        self.assertAlmostEqual(res.profit_margin_pct, 0.85, places=2)

    def test_generate_commercial_license(self):
        lic_base = generate_commercial_license(
            tx_hash="0xabcdef1234567890abcdef1234567890abcdef12",
            payer_address="0x1111222233334444555566667777888899990000",
            chain="base"
        )
        self.assertEqual(lic_base["status"], "VIP_COMMERCIAL_LICENSE_ACTIVE")
        self.assertEqual(lic_base["recipient_wallet"], BASE_PAYOUT_WALLET)
        self.assertTrue(lic_base["license_id"].startswith("AAVE-EMODE-VIP-"))
        
        lic_sol = generate_commercial_license(
            tx_hash="5xTestSolanaTx1234567890",
            payer_address="DW2MdHEq3qZ6nh9b5YFUoaPnBuuxC8Gz2785kwbbjSAM",
            chain="solana"
        )
        self.assertEqual(lic_sol["recipient_wallet"], SOLANA_PAYOUT_WALLET)

    def test_edge_cases(self):
        # 1.0x leverage (no debt)
        res_1x = calculate_emode_position(deposit_asset="cbETH", deposit_amount_eth=5.0, leverage_multiplier=1.0)
        self.assertEqual(res_1x.borrowed_debt_eth, 0.0)
        self.assertEqual(res_1x.health_factor, 999.0)
        
        depeg_1x = simulate_correlated_depeg_liquidation(leverage_multiplier=1.0)
        self.assertEqual(depeg_1x.status, "UNLEVERAGED_SAFE")
        self.assertTrue(depeg_1x.is_safe)
        
        with self.assertRaises(ValueError):
            calculate_emode_position(deposit_asset="cbETH", deposit_amount_eth=-2.0, leverage_multiplier=5.0)
            
        with self.assertRaises(ValueError):
            generate_commercial_license(tx_hash="short", payer_address="valid_address_12345")

if __name__ == "__main__":
    unittest.main()
