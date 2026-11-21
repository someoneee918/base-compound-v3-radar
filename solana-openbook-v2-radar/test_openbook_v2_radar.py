#!/usr/bin/env python3
"""
Unit tests for Solana OpenBook v2 On-Chain CLOB Maker Rebate & Crank Bounty Radar
"""

import unittest
from openbook_v2_radar import (
    calculate_maker_rebate_yield,
    simulate_crank_bounty_profitability,
    calculate_rent_reclaim_capital,
    generate_commercial_license,
    SOLANA_PAYOUT_WALLET,
    BASE_PAYOUT_WALLET
)

class TestOpenBookV2Radar(unittest.TestCase):

    def test_calculate_maker_rebate_yield(self):
        # 50 fills/day of $1,000 = $50,000 daily vol.
        # At 2 bps rebate = $50,000 * 0.0002 = $10.00/day.
        # On $5,000 capital = $3,650/year = 73.0% net APY!
        res = calculate_maker_rebate_yield(
            order_size_usd=1000.0,
            maker_rebate_bps=2.0,
            fills_per_day=50,
            capital_deployed_usd=5000.0
        )
        self.assertEqual(res.order_size_usd, 1000.0)
        self.assertEqual(res.daily_volume_usd, 50000.0)
        self.assertEqual(res.daily_rebate_usd, 10.0)
        self.assertEqual(res.annualized_rebate_usd, 3650.0)
        self.assertEqual(res.annualized_maker_apy_pct, 73.0)
        self.assertEqual(res.efficiency_score, 10.0)

    def test_simulate_crank_bounty_profitability(self):
        # 40 events * 5,000 lamports = 200,000 lamports = 0.000200 SOL.
        # Priority fee = 0.000050 SOL. Net = 0.000150 SOL.
        # At $180 SOL = $0.0270 net profit.
        res = simulate_crank_bounty_profitability(
            unmatched_events_count=40,
            reward_per_event_lamports=5000,
            priority_fee_sol=0.00005,
            sol_price_usd=180.0
        )
        self.assertEqual(res.unmatched_events_count, 40)
        self.assertEqual(res.gross_reward_sol, 0.0002)
        self.assertEqual(res.net_profit_sol, 0.00015)
        self.assertEqual(res.net_profit_usd, 0.027)
        self.assertTrue(res.is_profitable)
        self.assertEqual(res.status, "PROFITABLE_CRANK_EXECUTE")
        
        # Sub-threshold crank (e.g. 5 events -> 25,000 lamports = 0.000025 SOL vs 0.000050 fee)
        res_sub = simulate_crank_bounty_profitability(
            unmatched_events_count=5,
            reward_per_event_lamports=5000,
            priority_fee_sol=0.00005
        )
        self.assertFalse(res_sub.is_profitable)
        self.assertEqual(res_sub.status, "UNPROFITABLE_SUB_THRESHOLD")

    def test_calculate_rent_reclaim_capital(self):
        # 100 inactive accounts at 0.024 SOL = 2.40 SOL. At $180 = $432.00.
        res = calculate_rent_reclaim_capital(
            open_orders_accounts_count=100,
            rent_per_account_sol=0.024,
            sol_price_usd=180.0
        )
        self.assertEqual(res.open_orders_accounts_count, 100)
        self.assertEqual(res.total_reclaimable_sol, 2.4)
        self.assertEqual(res.total_reclaimable_usd, 432.0)
        self.assertIn("High Capital Locked", res.recommendation)

    def test_generate_commercial_license(self):
        lic_sol = generate_commercial_license(
            tx_hash="5xTestHashSolanaTransaction1234567890",
            payer_address="DW2MdHEq3qZ6nh9b5YFUoaPnBuuxC8Gz2785kwbbjSAM",
            chain="solana"
        )
        self.assertEqual(lic_sol["status"], "VIP_COMMERCIAL_LICENSE_ACTIVE")
        self.assertEqual(lic_sol["recipient_wallet"], SOLANA_PAYOUT_WALLET)
        self.assertTrue(lic_sol["license_id"].startswith("OPENBOOK-VIP-"))
        
        lic_base = generate_commercial_license(
            tx_hash="0xabcd1234ef567890abcdef1234567890abcdef12",
            payer_address="0x1234567890123456789012345678901234567890",
            chain="base"
        )
        self.assertEqual(lic_base["recipient_wallet"], BASE_PAYOUT_WALLET)

    def test_edge_cases(self):
        # Zero events in crank returns 0 profit
        res_zero = simulate_crank_bounty_profitability(unmatched_events_count=0)
        self.assertFalse(res_zero.is_profitable)
        
        # Zero accounts in rent reclaim
        res_zero_acc = calculate_rent_reclaim_capital(open_orders_accounts_count=0)
        self.assertEqual(res_zero_acc.total_reclaimable_sol, 0.0)
        self.assertIn("Clean Ledger", res_zero_acc.recommendation)
        
        with self.assertRaises(ValueError):
            calculate_maker_rebate_yield(order_size_usd=-500.0)
            
        with self.assertRaises(ValueError):
            generate_commercial_license(tx_hash="short", payer_address="valid_payer_address_12345")

if __name__ == "__main__":
    unittest.main()
