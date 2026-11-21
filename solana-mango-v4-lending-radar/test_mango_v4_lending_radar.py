#!/usr/bin/env python3
"""
Unit tests for Solana Mango Markets v4 Multi-Token Lending Utilization & Liquidation Sentinel Radar
"""

import unittest
from mango_v4_lending_radar import (
    calculate_lending_pool_kink_rate,
    calculate_cross_margin_health_factor,
    calculate_liquidator_bounty,
    generate_commercial_license,
    SOLANA_PAYOUT_WALLET,
    BASE_PAYOUT_WALLET
)

class TestMangoV4LendingRadar(unittest.TestCase):

    def test_calculate_lending_pool_kink_rate(self):
        # Normal utilization below kink (60%):
        # Base 2% + (60/80)*6% = 2 + 4.5 = 6.50% borrow APR.
        # Deposit APR = 6.50% * 0.60 * 0.90 = 3.51%.
        res_normal = calculate_lending_pool_kink_rate(utilization_pct=60.0)
        self.assertEqual(res_normal.borrow_apr_pct, 6.50)
        self.assertEqual(res_normal.deposit_apr_pct, 3.51)
        self.assertFalse(res_normal.is_above_kink)
        self.assertEqual(res_normal.status, "NORMAL_UTILIZATION_OPTIMAL")
        
        # Surge above kink (92%):
        # Base 2% + 6% + ((92-80)/20)*40% = 8% + 24% = 32.00% borrow APR!
        # Deposit APR = 32.00% * 0.92 * 0.90 = 26.50%.
        res_surge = calculate_lending_pool_kink_rate(utilization_pct=92.0)
        self.assertEqual(res_surge.borrow_apr_pct, 32.00)
        self.assertEqual(res_surge.deposit_apr_pct, 26.50)
        self.assertTrue(res_surge.is_above_kink)
        self.assertEqual(res_surge.status, "UTILIZATION_SPIKE_HIGH_BORROW_SURGE")
        self.assertGreater(res_surge.daily_interest_earned_usd, 5.0)

    def test_calculate_cross_margin_health_factor(self):
        # $25,000 deposits * 0.90 weight = $22,500 maint collateral.
        # $18,000 borrows -> HF = 22,500 / 18,000 = 1.2500.
        # Cushion = +$4,500. Drop buffer = 1 - 1/1.25 = 20.0%.
        res_safe = calculate_cross_margin_health_factor(deposits_val_usd=25000.0, borrows_val_usd=18000.0)
        self.assertEqual(res_safe.maint_health_factor, 1.2500)
        self.assertEqual(res_safe.liquidation_cushion_usd, 4500.0)
        self.assertEqual(res_safe.max_tolerable_drop_pct, 20.0)
        self.assertEqual(res_safe.status, "MODERATE_RISK_WARNING")
        self.assertFalse(res_safe.is_liquidatable)
        
        # Underwater position: $18,000 deposits * 0.90 = $16,200 vs $18,000 borrows -> HF = 0.9000
        res_under = calculate_cross_margin_health_factor(deposits_val_usd=18000.0, borrows_val_usd=18000.0)
        self.assertEqual(res_under.maint_health_factor, 0.9000)
        self.assertTrue(res_under.is_liquidatable)
        self.assertEqual(res_under.status, "UNDERWATER_LIQUIDATABLE")

    def test_calculate_liquidator_bounty(self):
        # $10,000 debt repaid. 5% bonus = $500 gross bounty. Seized = $10,500.
        # Priority fee = 0.0001 SOL * $180 = $0.018. Net profit = $499.98.
        res = calculate_liquidator_bounty(
            repay_debt_usd=10000.0,
            liquidation_fee_pct=5.0,
            priority_fee_sol=0.0001,
            sol_price_usd=180.0
        )
        self.assertEqual(res.repay_debt_usd, 10000.0)
        self.assertEqual(res.seized_collateral_usd, 10500.0)
        self.assertEqual(res.gross_bounty_usd, 500.0)
        self.assertEqual(res.net_profit_usd, 499.98)
        self.assertTrue(res.is_profitable)

    def test_generate_commercial_license(self):
        lic_sol = generate_commercial_license(
            tx_hash="5xTestHashSolanaTx1234567890",
            payer_address="DW2MdHEq3qZ6nh9b5YFUoaPnBuuxC8Gz2785kwbbjSAM",
            chain="solana"
        )
        self.assertEqual(lic_sol["status"], "VIP_COMMERCIAL_LICENSE_ACTIVE")
        self.assertEqual(lic_sol["recipient_wallet"], SOLANA_PAYOUT_WALLET)
        self.assertTrue(lic_sol["license_id"].startswith("MANGO-V4-VIP-"))
        
        lic_base = generate_commercial_license(
            tx_hash="0xabcd1234ef567890abcdef1234567890abcdef12",
            payer_address="0x1234567890123456789012345678901234567890",
            chain="base"
        )
        self.assertEqual(lic_base["recipient_wallet"], BASE_PAYOUT_WALLET)

    def test_edge_cases(self):
        # Zero borrows
        res_zero = calculate_cross_margin_health_factor(deposits_val_usd=15000.0, borrows_val_usd=0.0)
        self.assertEqual(res_zero.maint_health_factor, 999.0)
        self.assertEqual(res_zero.status, "ZERO_DEBT_SAFE")
        
        with self.assertRaises(ValueError):
            calculate_lending_pool_kink_rate(utilization_pct=105.0)
            
        with self.assertRaises(ValueError):
            generate_commercial_license(tx_hash="short", payer_address="valid_payer_address_12345")

if __name__ == "__main__":
    unittest.main()
