#!/usr/bin/env python3
"""
Unit tests for Base Euler v2 Modular Vault Connector & Bad Debt Isolation Radar
"""

import unittest
from euler_v2_vault_radar import (
    calculate_vault_connector_yield,
    simulate_contagion_isolation,
    calculate_dutch_auction_liquidation,
    generate_commercial_license,
    BASE_PAYOUT_WALLET,
    SOLANA_PAYOUT_WALLET
)

class TestEulerV2VaultRadar(unittest.TestCase):

    def test_calculate_vault_connector_yield(self):
        # 25,000 deposit at 8.5% base + 4.2% boost = 12.70% net APY.
        # Annual = 25,000 * 0.1270 = $3,175. Daily = $8.6986.
        res = calculate_vault_connector_yield(
            deposit_usd=25000.0,
            base_lending_apr_pct=8.5,
            connector_reward_apr_pct=4.2,
            collateral_factor_pct=82.0
        )
        self.assertEqual(res.deposit_usd, 25000.0)
        self.assertEqual(res.effective_net_apy_pct, 12.70)
        self.assertEqual(res.annual_revenue_usd, 3175.0)
        self.assertEqual(res.daily_revenue_usd, 8.6986)
        self.assertEqual(res.collateral_factor_pct, 82.0)

    def test_simulate_contagion_isolation(self):
        # Vault has $500,000 bad debt in 5M TVL.
        # External vaults 45M TVL. Contagion spillover MUST be 0.0.
        res = simulate_contagion_isolation(
            target_vault_bad_debt_usd=500000.0,
            target_vault_tvl_usd=5000000.0,
            external_vaults_tvl_usd=45000000.0
        )
        self.assertEqual(res.contagion_spillover_usd, 0.0)
        self.assertEqual(res.isolation_score_pct, 100.0)
        self.assertEqual(res.status, "MINOR_VAULT_IMPAIRMENT_ZERO_SPILLOVER")

    def test_calculate_dutch_auction_liquidation(self):
        # Repay 15,000 debt. Elapsed 600s / 1800s = 33.33% of auction.
        # Max discount 12% -> current discount = 4.0%.
        # Seized = 15,000 * 1.04 = 15,600. Gross = $600. Net = 600 - 0.35 = $599.65.
        res = calculate_dutch_auction_liquidation(
            repay_debt_usd=15000.0,
            elapsed_seconds=600,
            total_auction_seconds=1800,
            max_discount_pct=12.0,
            gas_cost_usd=0.35
        )
        self.assertEqual(res.repay_debt_usd, 15000.0)
        self.assertEqual(res.current_discount_pct, 4.0)
        self.assertEqual(res.seized_collateral_usd, 15600.0)
        self.assertEqual(res.net_profit_usd, 599.65)
        self.assertTrue(res.is_profitable)
        self.assertEqual(res.status, "OPTIMAL_AUCTION_ENTRY_TRIGGER")

    def test_generate_commercial_license(self):
        lic_base = generate_commercial_license(
            tx_hash="0xabcdef1234567890abcdef1234567890abcdef12",
            payer_address="0x1111222233334444555566667777888899990000",
            chain="base"
        )
        self.assertEqual(lic_base["status"], "VIP_COMMERCIAL_LICENSE_ACTIVE")
        self.assertEqual(lic_base["recipient_wallet"], BASE_PAYOUT_WALLET)
        self.assertTrue(lic_base["license_id"].startswith("EULER-V2-VIP-"))
        
        lic_sol = generate_commercial_license(
            tx_hash="5xTestHashSolanaTx1234567890",
            payer_address="DW2MdHEq3qZ6nh9b5YFUoaPnBuuxC8Gz2785kwbbjSAM",
            chain="solana"
        )
        self.assertEqual(lic_sol["recipient_wallet"], SOLANA_PAYOUT_WALLET)

    def test_edge_cases(self):
        # Zero debt returns 0 profit
        res_zero = calculate_dutch_auction_liquidation(repay_debt_usd=0.0)
        self.assertFalse(res_zero.is_profitable)
        
        with self.assertRaises(ValueError):
            calculate_vault_connector_yield(deposit_usd=-100.0)
            
        with self.assertRaises(ValueError):
            generate_commercial_license(tx_hash="short", payer_address="valid_address_12345")

if __name__ == "__main__":
    unittest.main()
