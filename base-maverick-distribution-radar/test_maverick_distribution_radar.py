import unittest
from maverick_distribution_radar import (
    calculate_bin_capital_efficiency,
    calculate_lp_fee_cashflow,
    calculate_bin_dex_arbitrage,
    evaluate_maverick_market
)

class TestMaverickDistributionRadar(unittest.TestCase):
    def test_bin_capital_efficiency(self):
        # 50 bps width = 0.5% -> base_multiplier = 100 / 0.5 = 200.0
        # Mode_Right bonus = 1.35x -> effective = 200.0 * 1.35 = 270.0x
        res = calculate_bin_capital_efficiency(bin_width_bps=50.0, mode="Mode_Right")
        self.assertEqual(res["base_multiplier"], 200.0)
        self.assertEqual(res["mode_bonus_multiplier"], 1.35)
        self.assertEqual(res["effective_multiplier"], 270.0)

    def test_bin_capital_efficiency_both(self):
        # Mode_Both bonus = 1.60x
        res = calculate_bin_capital_efficiency(bin_width_bps=50.0, mode="Mode_Both")
        self.assertEqual(res["effective_multiplier"], 320.0)

    def test_lp_fee_cashflow(self):
        # Liquidity $10,000, 270x effective -> virtual = $2,700,000
        # Pool total $1,000,000 + $2,700,000 = $3,700,000
        # Share = 2.7M / 3.7M = 72.97%
        # Daily volume $500,000, 0.05% fee -> pool fees = $250.00/day
        # LP fees = 250 * 0.72973 = $182.43/day
        # Annual = 182.43 * 365 = $66,587.84 -> APY = 665.88%
        res = calculate_lp_fee_cashflow(
            liquidity_usd=10000.0,
            pool_daily_volume_usd=500000.0,
            fee_tier_pct=0.05,
            effective_multiplier=270.0,
            pool_total_liquidity_usd=1000000.0
        )
        self.assertAlmostEqual(res["fee_share_pct"], 72.97, places=1)
        self.assertGreater(res["lp_daily_fees_usd"], 180.0)
        self.assertGreater(res["lp_fee_apy_pct"], 600.0)

    def test_bin_dex_arbitrage(self):
        # Maverick bin = $1.0040, External DEX = $1.0000 (0.40% spread)
        # $10,000 trade size -> gross = $40.00, gas = $0.04 -> net = $39.96
        res = calculate_bin_dex_arbitrage(
            maverick_bin_price=1.0040,
            external_dex_price=1.0000,
            trade_size_usd=10000.0,
            base_l2_gas_usd=0.04
        )
        self.assertEqual(res["price_diff_pct"], 0.40)
        self.assertEqual(res["gross_arbitrage_profit_usd"], 40.0)
        self.assertEqual(res["net_arbitrage_profit_usd"], 39.96)
        self.assertTrue(res["is_profitable"])

    def test_evaluate_maverick_market(self):
        res = evaluate_maverick_market(
            liquidity_usd=10000.0,
            pool_daily_volume_usd=500000.0,
            bin_width_bps=50.0,
            mode="Mode_Right",
            maverick_price=1.0040,
            external_price=1.0000
        )
        self.assertEqual(res["status"], "HIGH_CONVICTION_ATOMIC_ARBITRAGE")
        self.assertTrue(res["arbitrage"]["is_profitable"])

if __name__ == "__main__":
    unittest.main()
