import unittest
from seamless_lending_radar import (
    calculate_ilm_looping_yield,
    calculate_deleveraging_boundaries,
    calculate_keeper_rebalance_bounty,
    evaluate_seamless_opportunity
)

class TestSeamlessLendingRadar(unittest.TestCase):
    def test_ilm_looping_yield(self):
        # Deposit $10,000, 3.5x leverage
        # Supply: $35,000 at 4.5% = $1,575
        # Debt: $25,000 at 2.8% = $700
        # ILM Rewards: $35,000 at 3.0% = $1,050
        # Net Profit: 1575 - 700 + 1050 = $1,925
        # Net APY: 1925 / 10000 = 19.25%
        res = calculate_ilm_looping_yield(
            deposit_amount_usd=10000.0,
            target_leverage=3.5,
            base_supply_apy=4.5,
            borrow_apy=2.8,
            ilm_reward_apr=3.0
        )
        self.assertEqual(res["total_supplied_usd"], 35000.0)
        self.assertEqual(res["borrowed_debt_usd"], 25000.0)
        self.assertEqual(res["net_annual_profit_usd"], 1925.0)
        self.assertEqual(res["net_leveraged_apy"], 19.25)
        self.assertAlmostEqual(res["daily_cashflow_usd"], 1925.0 / 365.0, places=2)

    def test_deleveraging_boundaries(self):
        # Collateral $35,000, Debt $25,000, LT 85%
        # Effective Collateral = 35000 * 0.85 = $29,750
        # HF = 29750 / 25000 = 1.19
        # Max Drawdown = (1 - 25000/29750) * 100 = 15.97%
        res = calculate_deleveraging_boundaries(
            collateral_usd=35000.0,
            debt_usd=25000.0,
            liquidation_threshold_pct=85.0
        )
        self.assertEqual(res["health_factor"], 1.19)
        self.assertEqual(res["max_drawdown_pct"], 15.97)
        # Standard penalty: 35000 * 0.05 = $1,750
        self.assertEqual(res["standard_liquidation_penalty_usd"], 1750.0)
        # Flash cost: 35000 * 0.0015 = $52.50
        self.assertEqual(res["flash_rebalance_cost_usd"], 52.5)
        # Savings: 1750 - 52.5 = $1,697.50
        self.assertEqual(res["penalty_savings_usd"], 1697.5)
        self.assertFalse(res["is_emergency_triggered"])

    def test_zero_debt_risk_free(self):
        res = calculate_deleveraging_boundaries(collateral_usd=10000.0, debt_usd=0.0)
        self.assertEqual(res["health_factor"], 999.0)
        self.assertEqual(res["status"], "ZERO_DEBT_RISK_FREE")

    def test_keeper_rebalance_bounty(self):
        # Unwind volume $25,000, 1.25% bounty = $312.50, gas $0.04
        res = calculate_keeper_rebalance_bounty(
            unwind_volume_usd=25000.0,
            keeper_bounty_pct=1.25,
            base_l2_gas_usd=0.04
        )
        self.assertEqual(res["gross_bounty_usd"], 312.5)
        self.assertEqual(res["net_keeper_profit_usd"], 312.46)
        self.assertGreater(res["profit_margin_pct"], 99.0)

    def test_evaluate_seamless_opportunity(self):
        # High carry scenario
        res = evaluate_seamless_opportunity(
            deposit_amount_usd=10000.0,
            target_leverage=3.5,
            base_supply_apy=4.5,
            borrow_apy=2.8,
            ilm_reward_apr=3.0,
            liquidation_threshold_pct=85.0
        )
        self.assertEqual(res["tier"], "EXCEPTIONAL_CARRY_OPPORTUNITY")
        self.assertEqual(res["carry_metrics"]["net_leveraged_apy"], 19.25)

if __name__ == "__main__":
    unittest.main()
