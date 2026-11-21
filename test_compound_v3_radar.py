#!/usr/bin/env python3
"""
Unit Tests for Base Compound v3 Comet Single-Borrow Market Radar
"""

import unittest
from compound_v3_radar import (
    calculate_comet_account_health,
    calculate_comet_absorption_auction_profit,
    calculate_comet_utilization_curve,
    calculate_reserves_solvency_buffer,
    generate_vip_sentinel_script,
    BASE_RECEIVE_ADDRESS,
    SOL_RECEIVE_ADDRESS
)

class TestCompoundV3Radar(unittest.TestCase):

    def test_comet_account_health(self):
        # 1.0 ETH @ $3,200. Borrow CF: 80% ($2560), Liq CF: 88% ($2816).
        # Debt: 2,500 USDC.
        # Borrow HF = 2560 / 2500 = 1.024
        # Liq HF = 2816 / 2500 = 1.1264 (Safe)
        collateral = [{"symbol": "ETH", "amount": 1.0, "price": 3200.0, "borrow_cf": 0.80, "liq_cf": 0.88}]
        healthy = calculate_comet_account_health(collateral, borrowed_base_usdc=2500.0)
        self.assertEqual(healthy["total_nominal_collateral_usd"], 3200.0)
        self.assertEqual(healthy["total_borrow_capacity_usd"], 2560.0)
        self.assertEqual(healthy["total_liquidation_capacity_usd"], 2816.0)
        self.assertEqual(healthy["borrow_health_factor"], 1.024)
        self.assertEqual(healthy["liquidation_health_factor"], 1.1264)
        self.assertFalse(healthy["is_absorbable"])
        self.assertEqual(healthy["status"], "HEALTHY")
        
        # Absorbable case: Debt = $3,000 -> Liq HF = 2816 / 3000 = 0.9387 (Absorbable)
        absorbable = calculate_comet_account_health(collateral, borrowed_base_usdc=3000.0)
        self.assertTrue(absorbable["is_absorbable"])
        self.assertEqual(absorbable["status"], "ABSORBABLE")

    def test_comet_absorption_auction_profit(self):
        # Collateral: $10,000. Auction discount: 5% ($500). Purchase: $9,500.
        # Market sale slippage: 0.4% ($40) -> Sale proceeds: $9,960.
        # Gross profit: $9,960 - $9,500 = $460.00. Base gas: $0.02 -> Net: $459.98.
        auction = calculate_comet_absorption_auction_profit(
            absorbed_collateral_usd=10000.0,
            auction_discount_pct=0.05,
            base_gas_usd=0.02,
            dex_slippage_pct=0.004
        )
        self.assertEqual(auction["purchase_price_usd"], 9500.0)
        self.assertEqual(auction["market_sale_usd"], 9960.0)
        self.assertEqual(auction["gross_profit_usd"], 460.0)
        self.assertEqual(auction["net_profit_usd"], 459.98)
        self.assertTrue(auction["is_profitable"])

    def test_comet_utilization_curve(self):
        # Normal (68% utilization <= 85% kink)
        # Base 1.5% + (68 / 85) * 4.0% = 1.5% + 3.2% = 4.70%
        normal = calculate_comet_utilization_curve(total_usdc_borrows=680000.0, total_usdc_supply=1000000.0)
        self.assertEqual(normal["utilization_pct"], 68.0)
        self.assertFalse(normal["is_kinked"])
        self.assertEqual(normal["borrow_rate_pct"], 4.7)
        
        # Surged (95% utilization > 85% kink)
        # Normal rate = 1.5 + 4.0 = 5.5%
        # Excess = (95 - 85) / 15 = 10 / 15 = 0.6667. Jump = 0.6667 * 80% = 53.33%
        # Rate = 5.5% + 53.33% = 58.83%
        surged = calculate_comet_utilization_curve(total_usdc_borrows=950000.0, total_usdc_supply=1000000.0)
        self.assertEqual(surged["utilization_pct"], 95.0)
        self.assertTrue(surged["is_kinked"])
        self.assertAlmostEqual(surged["borrow_rate_pct"], 58.83, places=1)

    def test_reserves_solvency_buffer(self):
        # Current reserves $600k, Borrows $10M -> Target (5%) = $500k. Surplus $100k (120% ratio)
        reserves = calculate_reserves_solvency_buffer(600000.0, 10000000.0)
        self.assertTrue(reserves["is_fully_buffered"])
        self.assertEqual(reserves["target_reserves_usd"], 500000.0)
        self.assertEqual(reserves["reserve_surplus_usd"], 100000.0)
        self.assertEqual(reserves["solvency_ratio_pct"], 120.0)

    def test_generate_vip_script(self):
        script = generate_vip_sentinel_script(BASE_RECEIVE_ADDRESS, SOL_RECEIVE_ADDRESS)
        self.assertIn("Comet Sentinel", script)
        self.assertIn(BASE_RECEIVE_ADDRESS, script)
        self.assertIn(SOL_RECEIVE_ADDRESS, script)
        self.assertIn("COMET_USDC_ADDRESS", script)

if __name__ == "__main__":
    unittest.main()
