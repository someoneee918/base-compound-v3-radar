import unittest
from blazestake_bsol_radar import (
    calculate_bsol_nav_accretion,
    calculate_secondary_dex_discount_arbitrage,
    calculate_validator_gauge_yield,
    evaluate_blazestake_market
)

class TestBlazeStakeBsolRadar(unittest.TestCase):
    def test_bsol_nav_accretion(self):
        # 1,080,000 SOL staked, 1,000,000 bSOL supply -> NAV = 1.080000 SOL
        res = calculate_bsol_nav_accretion(
            staked_sol_reserves=1080000.0,
            bsol_supply=1000000.0,
            network_staking_apy_pct=7.20
        )
        self.assertEqual(res["fair_nav_sol"], 1.080000)
        self.assertAlmostEqual(res["projected_nav_1y"], 1.080000 * 1.072, places=4)
        self.assertGreater(res["projected_nav_30d"], 1.080000)

    def test_secondary_dex_discount_arbitrage(self):
        # Fair NAV = 1.080000 SOL, Secondary price = 1.072000 SOL (0.7407% discount)
        # Trade size = 50 SOL -> buy 50 / 1.072 = 46.6418 bSOL
        # Redeem at 1.080 = 46.6418 * 1.08 = 50.3731 SOL
        # Gross profit = 0.3731 SOL at $180 = $67.16 net profit (0.75% ROI)
        res = calculate_secondary_dex_discount_arbitrage(
            fair_nav_sol=1.080000,
            secondary_dex_price_sol=1.072000,
            trade_size_sol=50.0,
            sol_price_usd=180.0
        )
        self.assertAlmostEqual(res["discount_pct"], 0.7407, places=3)
        self.assertAlmostEqual(res["gross_profit_sol"], 0.3731, places=3)
        self.assertAlmostEqual(res["net_profit_usd"], 67.16, places=1)
        self.assertEqual(res["roi_pct"], 0.75)
        self.assertTrue(res["is_profitable"])

    def test_at_or_above_nav_no_arbitrage(self):
        res = calculate_secondary_dex_discount_arbitrage(
            fair_nav_sol=1.080000,
            secondary_dex_price_sol=1.080500
        )
        self.assertFalse(res["is_profitable"])
        self.assertEqual(res["gross_profit_sol"], 0.0)

    def test_validator_gauge_yield(self):
        # 100,000 BLZE votes in 10,000,000 pool (1% share)
        # 50,000 epoch SOL directed -> 500 SOL directed
        res = calculate_validator_gauge_yield(
            blze_votes=100000.0,
            total_gauge_votes=10000000.0,
            epoch_sol_directed=50000.0
        )
        self.assertEqual(res["vote_share_pct"], 1.0)
        self.assertEqual(res["sol_directed"], 500.0)

    def test_evaluate_blazestake_market(self):
        res = evaluate_blazestake_market(
            reserves=1080000.0,
            supply=1000000.0,
            secondary_price=1.072000,
            trade_size_sol=50.0
        )
        self.assertEqual(res["tier"], "HIGH_CONVICTION_BSOL_ARBITRAGE")
        self.assertTrue(res["arbitrage"]["is_profitable"])

if __name__ == "__main__":
    unittest.main()
