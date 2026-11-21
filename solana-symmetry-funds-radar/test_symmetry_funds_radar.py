import unittest
from symmetry_funds_radar import (
    calculate_fund_target_drift_and_rebalance_volume,
    calculate_rebalancing_arbitrage_profit,
    calculate_fund_management_fee_cashflow,
    verify_vip_license
)

class TestSymmetryFundsRadar(unittest.TestCase):
    def test_fund_target_drift_and_turnover(self):
        # 4 tokens, Total AUM = $100,000
        # SOL: $50,000 (Target 40% -> $40k -> +$10k overweight SELL)
        # JTO: $25,000 (Target 30% -> $30k -> -$5k underweight BUY)
        # PYTH: $15,000 (Target 20% -> $20k -> -$5k underweight BUY)
        # JUP: $10,000 (Target 10% -> $10k -> 0 drift)
        tokens = [
            {"symbol": "SOL", "balance_usd": 50000.0, "target_weight_pct": 40.0},
            {"symbol": "JTO", "balance_usd": 25000.0, "target_weight_pct": 30.0},
            {"symbol": "PYTH", "balance_usd": 15000.0, "target_weight_pct": 20.0},
            {"symbol": "JUP", "balance_usd": 10000.0, "target_weight_pct": 10.0}
        ]
        res = calculate_fund_target_drift_and_rebalance_volume(tokens)
        self.assertEqual(res["total_aum_usd"], 100000.0)
        self.assertEqual(res["max_drift_pct"], 10.0)
        self.assertTrue(res["needs_rebalance"])
        self.assertEqual(res["turnover_volume_usd"], 10000.0) # (|10k| + |-5k| + |-5k| + |0|) / 2 = 10k

    def test_rebalancing_arbitrage_profit(self):
        # $10,000 rebalance volume, 30 bps spread incentive, 5 bps DEX fee -> 25 bps net spread
        # Net profit = $10,000 * 0.0025 = $25.00
        res = calculate_rebalancing_arbitrage_profit(
            rebalance_trade_volume_usd=10000.0,
            arbitrage_spread_bps=30.0,
            dex_swap_fee_pct=0.05
        )
        self.assertEqual(res["net_spread_bps"], 25.0)
        self.assertEqual(res["gross_profit_usd"], 30.0)
        self.assertEqual(res["dex_fee_usd"], 5.0)
        self.assertEqual(res["net_profit_usd"], 25.0)
        self.assertEqual(res["net_roi_pct"], 0.25)

    def test_fund_management_fee_cashflow(self):
        # $1,000,000 AUM, 1% management fee ($10k/yr), 10% performance fee on 25% return ($25k/yr)
        # Total annual = $35,000 ($95.89/day, $2,916.67/mo)
        res = calculate_fund_management_fee_cashflow(
            fund_aum_usd=1000000.0,
            management_fee_annual_pct=1.0,
            performance_fee_pct=10.0,
            annual_fund_return_pct=25.0
        )
        self.assertEqual(res["annual_management_fee_usd"], 10000.0)
        self.assertEqual(res["annual_performance_fee_usd"], 25000.0)
        self.assertEqual(res["total_annual_fee_usd"], 35000.0)
        self.assertAlmostEqual(res["daily_fee_cashflow_usd"], 95.89, delta=0.01)

    def test_fund_zero_performance_fee_on_negative_return(self):
        res = calculate_fund_management_fee_cashflow(
            fund_aum_usd=1000000.0,
            management_fee_annual_pct=1.0,
            performance_fee_pct=10.0,
            annual_fund_return_pct=-15.0 # Loss year
        )
        self.assertEqual(res["annual_performance_fee_usd"], 0.0)
        self.assertEqual(res["total_annual_fee_usd"], 10000.0)

    def test_verify_vip_license(self):
        valid_sol = verify_vip_license(
            tx_hash="f" * 64,
            chain="solana",
            recipient="DW2MdHEq3qZ6nh9b5YFUoaPnBuuxC8Gz2785kwbbjSAM",
            amount=0.03
        )
        self.assertTrue(valid_sol["verified"])
        self.assertEqual(valid_sol["tier"], "Symmetry Funds VIP Sentinel")

        valid_base = verify_vip_license(
            tx_hash="0x" + "f" * 64,
            chain="base",
            recipient="0xF0E0D361bBE899F3089f0a968506eF2B97693c01",
            amount=5.0
        )
        self.assertTrue(valid_base["verified"])

if __name__ == "__main__":
    unittest.main()