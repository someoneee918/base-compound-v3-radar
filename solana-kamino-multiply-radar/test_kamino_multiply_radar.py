#!/usr/bin/env python3
"""
Unit tests for Solana Kamino Multiply Looping Leverage & Flash-Repay Sentinel Radar
"""

import unittest
from kamino_multiply_radar import (
    calculate_multiply_position,
    simulate_lst_depeg_liquidation,
    calculate_flash_repay_unwind,
    generate_commercial_license,
    SOLANA_PAYOUT_WALLET,
    BASE_PAYOUT_WALLET
)

class TestKaminoMultiplyRadar(unittest.TestCase):

    def test_calculate_multiply_position(self):
        # 100 SOL initial at 4.0x leverage -> 400 SOL collateral, 300 SOL debt
        # Staking 7.8% on 400 SOL = 31.2 SOL earn. Borrow 4.2% on 300 SOL = 12.6 SOL cost.
        # Net earn = 18.6 SOL on 100 SOL initial = 18.60% net APY.
        res = calculate_multiply_position(
            initial_deposit_sol=100.0,
            leverage_multiplier=4.0,
            lst_staking_yield_apr=7.8,
            sol_borrow_apr=4.2
        )
        self.assertEqual(res.initial_deposit_sol, 100.0)
        self.assertEqual(res.leverage_multiplier, 4.0)
        self.assertEqual(res.total_collateral_lst, 400.0)
        self.assertEqual(res.borrowed_sol, 300.0)
        self.assertEqual(res.current_ltv_pct, 75.0)
        self.assertEqual(res.net_staking_apr_pct, 18.60)
        self.assertAlmostEqual(res.gross_yield_boost_factor, 2.38, places=1)
        self.assertGreater(res.daily_cashflow_sol, 0.05)

    def test_simulate_lst_depeg_liquidation(self):
        # At 4x leverage, Debt/Collateral = 0.75. Liq LTV = 0.85.
        # P_liq = 0.75 / 0.85 = 0.8824 SOL.
        # Max tolerable depeg = (1.0 - 0.8824) / 1.0 = 11.76%
        res = simulate_lst_depeg_liquidation(leverage_multiplier=4.0, lst_price_in_sol=1.0, liquidation_ltv_pct=85.0)
        self.assertEqual(res.liquidation_price_sol, 0.8824)
        self.assertEqual(res.max_tolerable_depeg_pct, 11.76)
        self.assertEqual(res.status, "HEALTHY_DEPEG_BUFFER")
        self.assertTrue(res.is_safe)
        
        # High leverage (5.5x) where buffer is narrow
        res_tight = simulate_lst_depeg_liquidation(leverage_multiplier=5.5, lst_price_in_sol=1.0, liquidation_ltv_pct=85.0)
        self.assertLess(res_tight.max_tolerable_depeg_pct, 5.0)
        self.assertIn("DEPEG", res_tight.status)

    def test_calculate_flash_repay_unwind(self):
        # 400 SOL collateral, 300 SOL debt, price = 1.0 SOL
        res = calculate_flash_repay_unwind(
            total_collateral_lst=400.0,
            borrowed_sol=300.0,
            current_lst_price=1.0,
            slippage_pct=0.15,
            flashloan_fee_pct=0.05,
            liquidation_penalty_pct=5.0
        )
        self.assertEqual(res.flash_loan_amount_sol, 300.0)
        self.assertEqual(res.flash_loan_fee_sol, 0.15)
        self.assertGreater(res.net_equity_recovered_sol, 90.0)
        # 5% liquidation penalty on 300 SOL = 15 SOL. Minus small fees, avoided loss > 14 SOL.
        self.assertGreater(res.liquidation_loss_avoided_sol, 14.0)
        self.assertTrue(res.is_favorable)

    def test_generate_commercial_license(self):
        lic_sol = generate_commercial_license(
            tx_hash="5xTestHashSolanaTransaction1234567890",
            payer_address="DW2MdHEq3qZ6nh9b5YFUoaPnBuuxC8Gz2785kwbbjSAM",
            chain="solana"
        )
        self.assertEqual(lic_sol["status"], "VIP_COMMERCIAL_LICENSE_ACTIVE")
        self.assertEqual(lic_sol["recipient_wallet"], SOLANA_PAYOUT_WALLET)
        self.assertTrue(lic_sol["license_id"].startswith("KAMINO-MULTIPLY-VIP-"))
        
        lic_base = generate_commercial_license(
            tx_hash="0xabcd1234ef567890abcdef1234567890abcdef12",
            payer_address="0x1234567890123456789012345678901234567890",
            chain="base"
        )
        self.assertEqual(lic_base["recipient_wallet"], BASE_PAYOUT_WALLET)

    def test_edge_cases(self):
        # 1.0x leverage (no debt)
        res_1x = calculate_multiply_position(initial_deposit_sol=50.0, leverage_multiplier=1.0)
        self.assertEqual(res_1x.borrowed_sol, 0.0)
        self.assertEqual(res_1x.current_ltv_pct, 0.0)
        
        depeg_1x = simulate_lst_depeg_liquidation(leverage_multiplier=1.0)
        self.assertEqual(depeg_1x.status, "DELEVERAGED_ZERO_RISK")
        self.assertTrue(depeg_1x.is_safe)
        
        with self.assertRaises(ValueError):
            calculate_multiply_position(initial_deposit_sol=-10.0, leverage_multiplier=3.0)
            
        with self.assertRaises(ValueError):
            generate_commercial_license(tx_hash="short", payer_address="valid_payer_address_12345")

if __name__ == "__main__":
    unittest.main()
