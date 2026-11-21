import unittest
from zeta_markets_radar import (
    calculate_zeta_margin_requirements,
    calculate_account_liquidation_health,
    calculate_maker_rebate_yield,
    evaluate_zeta_profile
)

class TestZetaMarketsRadar(unittest.TestCase):
    def test_margin_requirements(self):
        # Position notional $40,000
        # sqrt(40000) = 200
        # dynamic scaling = 0.005 * 200 = 1.0%
        # imr = 10.0 + 1.0 = 11.0%
        # mmr = 11.0 / 2 = 5.5%
        res = calculate_zeta_margin_requirements(position_notional_usd=40000.0)
        self.assertEqual(res["imr_pct"], 11.0)
        self.assertEqual(res["mmr_pct"], 5.5)
        self.assertEqual(res["required_imr_usd"], 4400.0)
        self.assertEqual(res["required_mmr_usd"], 2200.0)

    def test_account_liquidation_health(self):
        # Collateral $5,000, Unrealized PnL -$1,000 -> Equity $4,000
        # Position $40,000 -> Margin ratio = 4000 / 40000 = 10.0%
        # MMR = 5.5% -> Distance = 10.0 - 5.5 = 4.5%
        res = calculate_account_liquidation_health(
            collateral_usd=5000.0,
            unrealized_pnl_usd=-1000.0,
            position_notional_usd=40000.0,
            mmr_pct=5.5
        )
        self.assertEqual(res["equity_usd"], 4000.0)
        self.assertEqual(res["margin_ratio_pct"], 10.0)
        self.assertEqual(res["distance_to_liq_pct"], 4.5)
        self.assertFalse(res["is_liquidatable"])
        self.assertEqual(res["liquidation_penalty_usd"], 1000.0) # 2.5% of 40,000
        self.assertEqual(res["liquidator_reward_usd"], 500.0)

    def test_liquidatable_state(self):
        # Collateral $2,500, PnL -$600 -> Equity $1,900
        # Position $40,000 -> Margin ratio = 1900 / 40000 = 4.75% <= 5.5%
        res = calculate_account_liquidation_health(
            collateral_usd=2500.0,
            unrealized_pnl_usd=-600.0,
            position_notional_usd=40000.0,
            mmr_pct=5.5
        )
        self.assertEqual(res["margin_ratio_pct"], 4.75)
        self.assertTrue(res["is_liquidatable"])
        self.assertEqual(res["distance_to_liq_pct"], 0.0)

    def test_maker_rebate_yield(self):
        # Daily volume $100,000, 1.0 bps base, 50% boost -> 1.5 bps effective
        # Daily rebate = 100000 * 0.00015 = $15.00/day
        # Annual rebate = 15.00 * 365 = $5,475
        # Capital = $10,000 -> Rebate APY = 54.75%
        res = calculate_maker_rebate_yield(
            daily_maker_volume_usd=100000.0,
            base_maker_rebate_bps=1.0,
            zx_stake_boost_pct=50.0,
            capital_allocated_usd=10000.0
        )
        self.assertEqual(res["effective_rebate_bps"], 1.5)
        self.assertEqual(res["daily_rebate_usd"], 15.0)
        self.assertEqual(res["annual_rebate_usd"], 5475.0)
        self.assertEqual(res["rebate_apy_pct"], 54.75)

    def test_evaluate_zeta_profile(self):
        res = evaluate_zeta_profile(
            collateral_usd=5000.0,
            unrealized_pnl_usd=0.0,
            position_notional_usd=40000.0,
            daily_maker_volume_usd=100000.0,
            capital_allocated_usd=10000.0
        )
        self.assertEqual(res["recommendation"], "HIGH_YIELD_MAKER_REBATE_FARMING")
        self.assertFalse(res["liquidation_health"]["is_liquidatable"])

if __name__ == "__main__":
    unittest.main()
