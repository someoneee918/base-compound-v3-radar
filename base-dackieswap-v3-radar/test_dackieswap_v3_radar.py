import unittest
from dackieswap_v3_radar import (
    calculate_v3_tick_efficiency,
    calculate_lp_fee_revenue,
    calculate_atomic_cross_dex_arbitrage,
    evaluate_dackieswap_market
)

class TestDackieSwapV3Radar(unittest.TestCase):
    def test_v3_tick_efficiency(self):
        # Range 0.98 to 1.02 -> ratio = 0.96078 -> sqrt = 0.98019
        # multiplier = 1 / (1 - 0.98019) = 50.48x
        res = calculate_v3_tick_efficiency(
            lower_tick_price=0.98,
            upper_tick_price=1.02,
            current_price=1.00
        )
        self.assertAlmostEqual(res["capital_multiplier"], 50.48, places=1)
        self.assertTrue(res["is_in_range"])
        self.assertEqual(res["status"], "ACTIVE_FEE_HARVEST")

    def test_out_of_range(self):
        res = calculate_v3_tick_efficiency(
            lower_tick_price=0.98,
            upper_tick_price=1.02,
            current_price=1.06
        )
        self.assertFalse(res["is_in_range"])
        self.assertEqual(res["status"], "OUT_OF_RANGE_DORMANT")

    def test_lp_fee_revenue(self):
        # Liquidity $10,000, 50.48x mult -> virtual = $504,800
        # Pool TVL $1,000,000 + $504,800 = $1,504,800 -> share = 33.55%
        # Volume $1,000,000, Fee 0.25% = $2,500/day
        # User daily fees = 2500 * 0.33546 = $838.65/day
        # Annual fees = 838.65 * 365 = $306,107.25 -> APY = 3061.07%
        res = calculate_lp_fee_revenue(
            liquidity_usd=10000.0,
            pool_daily_volume_usd=1000000.0,
            fee_tier_pct=0.25,
            effective_multiplier=50.48,
            pool_tvl_usd=1000000.0
        )
        self.assertAlmostEqual(res["fee_share_pct"], 33.55, places=1)
        self.assertGreater(res["user_daily_fees_usd"], 800.0)
        self.assertGreater(res["fee_apy_pct"], 2500.0)

    def test_atomic_cross_dex_arbitrage(self):
        # Dackie price 1.0030, External DEX 1.0000 (0.30% spread)
        # Trade $10,000 -> gross = $30.00, gas = $0.04 -> net = $29.96
        res = calculate_atomic_cross_dex_arbitrage(
            dackie_price=1.0030,
            external_dex_price=1.0000,
            trade_size_usd=10000.0,
            base_l2_gas_usd=0.04
        )
        self.assertEqual(res["spread_pct"], 0.30)
        self.assertEqual(res["gross_profit_usd"], 30.00)
        self.assertEqual(res["net_profit_usd"], 29.96)
        self.assertTrue(res["is_profitable"])

    def test_evaluate_dackieswap_market(self):
        res = evaluate_dackieswap_market(
            lower_tick=0.98,
            upper_tick=1.02,
            current_price=1.00,
            liquidity_usd=10000.0,
            volume=1000000.0,
            fee_tier=0.25,
            dackie_price=1.0030,
            external_price=1.0000
        )
        self.assertEqual(res["tier"], "HIGH_CONVICTION_CROSS_DEX_ARBITRAGE")

if __name__ == "__main__":
    unittest.main()
