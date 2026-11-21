import unittest
from lifinity_amm_radar import (
    calculate_dynamic_spread,
    calculate_lvr_reduction_savings,
    calculate_lifinity_lp_yield,
    evaluate_lifinity_market
)

class TestLifinityAmmRadar(unittest.TestCase):
    def test_dynamic_spread(self):
        # Base 10 bps, Volatility 2.5%, Rebalancing 1.0
        # Vol markup = 2.5 * 2.0 = 5.0 bps
        # Inv markup = 1.0 * 1.5 = 1.5 bps
        # Total = 10 + 5 + 1.5 = 16.5 bps
        res = calculate_dynamic_spread(
            base_spread_bps=10.0,
            volatility_index_pct=2.5,
            rebalancing_factor=1.0
        )
        self.assertEqual(res["dynamic_spread_bps"], 16.5)
        self.assertEqual(res["effective_spread_pct"], 0.165)

    def test_lvr_reduction_savings(self):
        # Pool daily volume $1,000,000, Standard LVR 25 bps = $2,500/day
        # Lifinity 75% LVR reduction = $1,875/day saved by pool
        # User share 1.0% -> user saves $18.75/day ($6,843.75/year)
        res = calculate_lvr_reduction_savings(
            pool_daily_volume_usd=1000000.0,
            standard_amm_lvr_bps=25.0,
            lifinity_lvr_reduction_pct=75.0,
            user_lp_share_pct=1.0
        )
        self.assertEqual(res["standard_pool_daily_lvr_usd"], 2500.0)
        self.assertEqual(res["saved_pool_daily_lvr_usd"], 1875.0)
        self.assertEqual(res["user_daily_saved_lvr_usd"], 18.75)
        self.assertEqual(res["user_annual_saved_lvr_usd"], 6843.75)

    def test_lifinity_lp_yield(self):
        # User liquidity $10,000 in $1,000,000 pool (1.0% share)
        # Volume $1,000,000, Spread 16.5 bps = $1,650/day pool fees
        # User daily fees = $16.50/day ($6,022.50/year) -> Fee APY = 60.23%
        # LVR savings $6,843.75/year -> LVR Alpha APY = 68.44%
        # True Net APY = 60.23 + 68.44 = 128.67%
        res = calculate_lifinity_lp_yield(
            user_liquidity_usd=10000.0,
            pool_daily_volume_usd=1000000.0,
            dynamic_spread_bps=16.5,
            pool_total_liquidity_usd=1000000.0,
            user_annual_saved_lvr_usd=6843.75
        )
        self.assertEqual(res["user_share_pct"], 1.0)
        self.assertEqual(res["user_daily_fee_usd"], 16.5)
        self.assertEqual(res["fee_apy_pct"], 60.22)
        self.assertEqual(res["lvr_alpha_apy_pct"], 68.44)
        self.assertEqual(res["true_net_apy_pct"], 128.66)

    def test_zero_volume_bounds(self):
        res = calculate_lvr_reduction_savings(
            pool_daily_volume_usd=0.0,
            user_lp_share_pct=1.0
        )
        self.assertEqual(res["user_annual_saved_lvr_usd"], 0.0)

    def test_evaluate_lifinity_market(self):
        res = evaluate_lifinity_market(
            user_liquidity_usd=10000.0,
            pool_daily_volume_usd=1000000.0,
            base_spread_bps=10.0,
            volatility_index_pct=2.5,
            rebalancing_factor=1.0,
            pool_total_liquidity_usd=1000000.0
        )
        self.assertEqual(res["recommendation"], "PRIME_PMM_LP_ACCUMULATION")
        self.assertGreater(res["yield_data"]["true_net_apy_pct"], 100.0)

if __name__ == "__main__":
    unittest.main()
