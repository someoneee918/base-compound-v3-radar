#!/usr/bin/env python3
"""
Unit tests for Solana Marinade Finance mSOL Fair NAV Redemption & Instant Unstake Radar
"""

import unittest
from marinade_msol_radar import (
    calculate_msol_fair_nav_arbitrage,
    simulate_instant_unstake_liquidity_fee,
    generate_commercial_license,
    SOLANA_PAYOUT_WALLET,
    BASE_PAYOUT_WALLET
)

class TestMarinadeMSOLRadar(unittest.TestCase):

    def test_calculate_msol_fair_nav_arbitrage(self):
        # 100 mSOL at Fair NAV 1.2450 SOL vs Market 1.2280 SOL (Discount = 1.37%)
        # Purchase cost = 122.80 SOL. Gross redemption = 124.50 SOL.
        # Gross profit = 1.70 SOL.
        # Opportunity cost over 2.5 days @ 6% = 122.80 * 0.06 * (2.5 / 365) = 0.0505 SOL.
        # Net profit = 1.70 - 0.0505 = 1.6495 SOL.
        # Annualized ROI = (1.6495 / 122.80) * (365 / 2.5) * 100 = 19.61%
        res = calculate_msol_fair_nav_arbitrage(
            msol_amount=100.0,
            msol_fair_nav_sol=1.2450,
            msol_market_price_sol=1.2280,
            sol_price_usd=180.0,
            delayed_unstake_days=2.5,
            annual_opportunity_cost_apr=6.0
        )
        self.assertEqual(res.msol_amount, 100.0)
        self.assertEqual(res.discount_pct, 1.37)
        self.assertEqual(res.purchase_cost_sol, 122.80)
        self.assertEqual(res.gross_redemption_sol, 124.50)
        self.assertEqual(res.gross_profit_sol, 1.70)
        self.assertAlmostEqual(res.net_profit_sol, 1.6495, places=3)
        self.assertEqual(res.status, "HIGH_CONVICTION_NAV_DISCOUNT_ARBITRAGE")
        self.assertGreater(res.annualized_arbitrage_roi_pct, 18.0)

    def test_simulate_instant_unstake_liquidity_fee(self):
        # Available 45,000 SOL in 100,000 target. Unstake 500 SOL.
        # Remaining = 44,500. Ratio = 0.445.
        # Fee = 9.0 - (9.0 - 0.1) * 0.445 = 9.0 - 3.9605 = 5.04%
        res = simulate_instant_unstake_liquidity_fee(
            unstake_sol_amount=500.0,
            pool_available_sol=45000.0,
            pool_target_sol=100000.0,
            min_fee_pct=0.10,
            max_fee_pct=9.0
        )
        self.assertEqual(res.unstake_sol_amount, 500.0)
        self.assertEqual(res.dynamic_fee_pct, 5.04)
        self.assertEqual(res.fee_cost_sol, 25.2)
        self.assertEqual(res.net_sol_received, 474.8)
        self.assertIn("Route via Delayed Unstake", res.recommended_route)
        
        # Abundant liquidity test (available 98,000 in 100,000 target) -> min fee
        res_liquid = simulate_instant_unstake_liquidity_fee(
            unstake_sol_amount=100.0,
            pool_available_sol=98000.0,
            pool_target_sol=100000.0
        )
        self.assertLess(res_liquid.dynamic_fee_pct, 0.50)
        self.assertIn("Liquid", res_liquid.recommended_route)

    def test_generate_commercial_license(self):
        lic_sol = generate_commercial_license(
            tx_hash="5xTestHashSolanaTx1234567890",
            payer_address="DW2MdHEq3qZ6nh9b5YFUoaPnBuuxC8Gz2785kwbbjSAM",
            chain="solana"
        )
        self.assertEqual(lic_sol["status"], "VIP_COMMERCIAL_LICENSE_ACTIVE")
        self.assertEqual(lic_sol["recipient_wallet"], SOLANA_PAYOUT_WALLET)
        self.assertTrue(lic_sol["license_id"].startswith("MARINADE-VIP-"))
        
        lic_base = generate_commercial_license(
            tx_hash="0xabcd1234ef567890abcdef1234567890abcdef12",
            payer_address="0x1234567890123456789012345678901234567890",
            chain="base"
        )
        self.assertEqual(lic_base["recipient_wallet"], BASE_PAYOUT_WALLET)

    def test_edge_cases(self):
        # Zero discount
        res_zero = calculate_msol_fair_nav_arbitrage(
            msol_amount=50.0,
            msol_fair_nav_sol=1.2000,
            msol_market_price_sol=1.2000
        )
        self.assertEqual(res_zero.discount_pct, 0.0)
        self.assertEqual(res_zero.net_profit_sol, 0.0)
        self.assertEqual(res_zero.status, "TIGHT_PARITY_HOLD")
        
        with self.assertRaises(ValueError):
            calculate_msol_fair_nav_arbitrage(msol_amount=-10.0)
            
        with self.assertRaises(ValueError):
            generate_commercial_license(tx_hash="short", payer_address="valid_payer_address_12345")

if __name__ == "__main__":
    unittest.main()
