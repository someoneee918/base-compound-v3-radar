import unittest
from alien_base_clmm_radar import (
    calculate_area51_concentrated_efficiency,
    calculate_stableswap_slippage,
    calculate_atomic_dex_arbitrage,
    evaluate_alien_base_market
)

class TestAlienBaseClmmRadar(unittest.TestCase):
    def test_area51_concentrated_efficiency(self):
        # Tick range 0.98 to 1.02 -> ratio = 0.98 / 1.02 = 0.96078
        # sqrt(ratio) = 0.98019
        # multiplier = 1 / (1 - 0.98019) = 50.48x
        res = calculate_area51_concentrated_efficiency(
            lower_tick_price=0.98,
            upper_tick_price=1.02,
            current_price=1.00
        )
        self.assertAlmostEqual(res["capital_multiplier"], 50.48, places=1)
        self.assertTrue(res["is_in_range"])
        self.assertEqual(res["status"], "ACTIVE_FEE_HARVEST")

    def test_out_of_range_tick(self):
        res = calculate_area51_concentrated_efficiency(
            lower_tick_price=0.98,
            upper_tick_price=1.02,
            current_price=1.05
        )
        self.assertFalse(res["is_in_range"])
        self.assertEqual(res["status"], "OUT_OF_RANGE_DORMANT")

    def test_stableswap_slippage(self):
        # Trade $50,000 in $1,000,000 pool (5% ratio), A = 100
        # slippage_pct = 0.05 * (100 / 100) * 0.10 = 0.005%
        # slippage_cost = 50000 * 0.00005 = $2.50
        # v2 slippage = 5% = $2,500.00
        # savings = $2,497.50
        res = calculate_stableswap_slippage(
            trade_amount_usd=50000.0,
            pool_liquidity_usd=1000000.0,
            amplification_coefficient=100.0
        )
        self.assertEqual(res["slippage_pct"], 0.005)
        self.assertEqual(res["slippage_cost_usd"], 2.50)
        self.assertEqual(res["v2_slippage_cost_usd"], 2500.0)
        self.assertEqual(res["slippage_savings_usd"], 2497.50)

    def test_atomic_dex_arbitrage(self):
        # Alien price 1.0035, Aerodrome price 1.0000 (0.35% spread)
        # Trade $10,000 -> gross = $35.00, gas = $0.04 -> net = $34.96
        res = calculate_atomic_dex_arbitrage(
            alien_price=1.0035,
            aerodrome_price=1.0000,
            trade_size_usd=10000.0,
            base_l2_gas_usd=0.04
        )
        self.assertEqual(res["spread_pct"], 0.35)
        self.assertEqual(res["gross_profit_usd"], 35.0)
        self.assertEqual(res["net_profit_usd"], 34.96)
        self.assertTrue(res["is_profitable"])

    def test_evaluate_alien_base_market(self):
        res = evaluate_alien_base_market(
            lower_tick=0.98,
            upper_tick=1.02,
            current_price=1.00,
            trade_amount_usd=10000.0,
            alien_price=1.0035,
            aerodrome_price=1.0000
        )
        self.assertEqual(res["tier"], "HIGH_CONVICTION_CROSS_DEX_ARBITRAGE")

if __name__ == "__main__":
    unittest.main()
