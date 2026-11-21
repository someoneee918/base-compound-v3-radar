#!/usr/bin/env python3
"""
Unit tests for Base Moonwell Flagship Multi-Asset Lending & Safety Module Staking Radar
"""

import unittest
from moonwell_flagship_radar import (
    calculate_account_health,
    simulate_safety_module_slashing,
    calculate_liquidator_profit,
    generate_commercial_license,
    BASE_PAYOUT_WALLET,
    SOLANA_PAYOUT_WALLET
)

class TestMoonwellFlagshipRadar(unittest.TestCase):

    def test_calculate_account_health_safe_and_underwater(self):
        # Case 1: Overcollateralized safe
        collaterals_safe = [
            {"asset": "WETH", "value_usd": 20000.0, "collateral_factor": 0.80},
            {"asset": "cbBTC", "value_usd": 30000.0, "collateral_factor": 0.75}
        ]
        # Capacity = 16000 + 22500 = 38500. Borrows = 15000. HF = 38500 / 15000 = 2.5667
        borrows_safe = [{"asset": "USDC", "value_usd": 15000.0}]
        res_safe = calculate_account_health(collaterals_safe, borrows_safe)
        self.assertEqual(res_safe.total_collateral_usd, 50000.0)
        self.assertEqual(res_safe.weighted_borrow_capacity_usd, 38500.0)
        self.assertEqual(res_safe.health_factor, 2.5667)
        self.assertEqual(res_safe.status, "HEALTHY_OVERCOLLATERALIZED")
        self.assertFalse(res_safe.urgency_score > 50)
        
        # Case 2: Underwater liquidatable
        borrows_underwater = [{"asset": "USDC", "value_usd": 40000.0}]
        res_under = calculate_account_health(collaterals_safe, borrows_underwater)
        self.assertLess(res_under.health_factor, 1.0)
        self.assertEqual(res_under.status, "UNDERWATER_LIQUIDATABLE")
        self.assertEqual(res_under.urgency_score, 100)

    def test_simulate_safety_module_slashing(self):
        # User has 100,000 stkWELL at $0.05 ($5,000 staked). Total module = $1,000,000.
        # Bad debt = $50,000. User share = 0.5% -> $250 exposure.
        res = simulate_safety_module_slashing(
            stkwell_staked=100000.0,
            well_price_usd=0.05,
            protocol_bad_debt_usd=50000.0,
            total_safety_module_staked_usd=1000000.0,
            max_slashing_cap_pct=30.0,
            base_staking_apr_pct=18.5
        )
        self.assertEqual(res.staked_value_usd, 5000.0)
        self.assertEqual(res.potential_slashing_loss_usd, 250.0)
        # Loss pct = (250 / 5000) * 100 = 5.0%. Net APR = 18.5 - 5.0 = 13.5%
        self.assertEqual(res.net_expected_yield_apr_pct, 13.5)
        self.assertEqual(res.safety_cushion_ratio, 20.0)

    def test_calculate_liquidator_profit(self):
        # Total debt $20,000. Close factor 50% = repay $10,000. Seize 8% bonus = $10,800.
        # Gross = $800. Gas = $0.45. Net = $799.55.
        res = calculate_liquidator_profit(
            total_borrow_usd=20000.0,
            close_factor_pct=50.0,
            liquidation_incentive_pct=8.0,
            gas_cost_usd=0.45
        )
        self.assertEqual(res.repay_debt_usd, 10000.0)
        self.assertEqual(res.seized_collateral_usd, 10800.0)
        self.assertEqual(res.gross_bonus_usd, 800.0)
        self.assertEqual(res.net_profit_usd, 799.55)
        self.assertTrue(res.is_profitable)
        self.assertAlmostEqual(res.profit_margin_pct, 8.0, places=1)

    def test_generate_commercial_license(self):
        lic_base = generate_commercial_license(
            tx_hash="0xabcdef1234567890abcdef1234567890abcdef12",
            payer_address="0x9876543210987654321098765432109876543210",
            chain="base"
        )
        self.assertEqual(lic_base["status"], "VIP_COMMERCIAL_LICENSE_ACTIVE")
        self.assertEqual(lic_base["recipient_wallet"], BASE_PAYOUT_WALLET)
        self.assertTrue(lic_base["license_id"].startswith("MOONWELL-VIP-"))
        
        lic_sol = generate_commercial_license(
            tx_hash="5xTestHashSolanaTx1234567890",
            payer_address="DW2MdHEq3qZ6nh9b5YFUoaPnBuuxC8Gz2785kwbbjSAM",
            chain="solana"
        )
        self.assertEqual(lic_sol["recipient_wallet"], SOLANA_PAYOUT_WALLET)

    def test_edge_cases(self):
        # Zero debt returns safe
        res_zero = calculate_account_health(
            collaterals=[{"asset": "WETH", "value_usd": 10000.0, "collateral_factor": 0.80}],
            borrows=[]
        )
        self.assertEqual(res_zero.health_factor, 999.0)
        self.assertEqual(res_zero.status, "ZERO_DEBT_SAFE")
        
        # Zero borrow in liquidation returns zero profit
        liq_zero = calculate_liquidator_profit(total_borrow_usd=0.0)
        self.assertFalse(liq_zero.is_profitable)
        
        with self.assertRaises(ValueError):
            generate_commercial_license(tx_hash="short", payer_address="valid_address_12345")

if __name__ == "__main__":
    unittest.main()
