import unittest
from save_finance_radar import (
    calculate_account_health_factor,
    calculate_save_kink_borrow_rate,
    calculate_liquidator_seizure_profit,
    evaluate_save_position
)

class TestSaveFinanceRadar(unittest.TestCase):
    def test_account_health_factor(self):
        # Collateral $20,000, Debt $14,000, LT 80%
        # Threshold USD = 20,000 * 0.80 = $16,000
        # HF = 16,000 / 14,000 = 1.1429
        # Max drawdown = (1 - 14000/16000) * 100 = 12.5%
        res = calculate_account_health_factor(
            collateral_usd=20000.0,
            borrowed_usd=14000.0,
            liquidation_threshold_pct=80.0
        )
        self.assertEqual(res["liquidation_threshold_usd"], 16000.0)
        self.assertEqual(res["health_factor"], 1.1429)
        self.assertEqual(res["max_drawdown_pct"], 12.5)
        self.assertFalse(res["is_liquidatable"])
        self.assertEqual(res["status"], "HEALTHY")

    def test_liquidatable_state(self):
        # Collateral $20,000, Debt $17,000, LT 80%
        # Threshold USD = $16,000 -> HF = 16,000 / 17,000 = 0.9412 < 1.0
        res = calculate_account_health_factor(
            collateral_usd=20000.0,
            borrowed_usd=17000.0,
            liquidation_threshold_pct=80.0
        )
        self.assertEqual(res["health_factor"], 0.9412)
        self.assertTrue(res["is_liquidatable"])
        self.assertEqual(res["status"], "LIQUIDATABLE")

    def test_piecewise_borrow_rates(self):
        # Below kink (60% util, kink 80%):
        # rate = 2.0 + (60/80)*6.0 = 2.0 + 4.5 = 6.5%
        # supply = (6.5 * 0.60) * 0.90 = 3.51%
        res_below = calculate_save_kink_borrow_rate(utilization_pct=60.0)
        self.assertEqual(res_below["borrow_rate_pct"], 6.5)
        self.assertEqual(res_below["lender_supply_apy_pct"], 3.51)
        self.assertFalse(res_below["is_above_kink"])

        # Above kink (90% util, kink 80%):
        # excess = (90 - 80) / 20 = 0.50
        # rate = 2.0 + 6.0 + (0.50 * 50.0) = 8.0 + 25.0 = 33.0%
        # supply = (33.0 * 0.90) * 0.90 = 26.73%
        res_above = calculate_save_kink_borrow_rate(utilization_pct=90.0)
        self.assertEqual(res_above["borrow_rate_pct"], 33.0)
        self.assertEqual(res_above["lender_supply_apy_pct"], 26.73)
        self.assertTrue(res_above["is_above_kink"])

    def test_liquidator_seizure_profit(self):
        # Debt $17,000, 20% close factor = $3,400 repaid
        # 8% bonus -> seized = 3,400 * 1.08 = $3,672
        # Gross profit = $272.00
        # Priority fee: 0.005 SOL at $180 = $0.90 -> Net = $271.10
        res = calculate_liquidator_seizure_profit(
            borrowed_usd=17000.0,
            close_factor_pct=20.0,
            liquidation_bonus_pct=8.0,
            priority_fee_sol=0.005,
            sol_price_usd=180.0
        )
        self.assertEqual(res["repaid_usd"], 3400.0)
        self.assertEqual(res["seized_usd"], 3672.0)
        self.assertEqual(res["gross_profit_usd"], 272.0)
        self.assertEqual(res["net_profit_usd"], 271.1)
        self.assertAlmostEqual(res["roi_pct"], 7.97, places=2)

    def test_evaluate_save_position(self):
        res = evaluate_save_position(
            collateral_usd=20000.0,
            borrowed_usd=17000.0,
            utilization_pct=85.0
        )
        self.assertEqual(res["tier"], "LIQUIDATION_ACTIVE_REPAY_CHUNK")
        self.assertIsNotNone(res["liquidator"])
        self.assertEqual(res["liquidator"]["net_profit_usd"], 271.1)

if __name__ == "__main__":
    unittest.main()
