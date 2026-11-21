#!/usr/bin/env python3
import unittest
from sharky_fi_radar import (
    calculate_sharky_loan_yield,
    calculate_default_foreclosure_profit,
    calculate_floor_drawdown_buffer,
    evaluate_sharky_collection_risk,
)

class TestSharkyFiRadar(unittest.TestCase):

    def test_sharky_loan_yield(self):
        res = calculate_sharky_loan_yield(
            principal_sol=100.0,
            stated_apr=0.40,
            duration_days=14,
            protocol_fee_pct=1.5
        )
        self.assertAlmostEqual(res["gross_interest_sol"], 1.5342, places=3)
        self.assertAlmostEqual(res["protocol_fee_sol"], 0.0230, places=3)
        self.assertAlmostEqual(res["net_interest_sol"], 1.5112, places=3)
        self.assertAlmostEqual(res["net_realized_apr_pct"], 39.40, places=1)

    def test_default_foreclosure_profit(self):
        res = calculate_default_foreclosure_profit(
            floor_price_sol=150.0,
            loan_principal_sol=97.5,
            marketplace_taker_fee_pct=2.0
        )
        self.assertEqual(res["ltv_pct"], 65.0)
        self.assertEqual(res["net_liquidation_value_sol"], 147.0)
        self.assertEqual(res["net_profit_sol"], 49.5)
        self.assertAlmostEqual(res["net_roi_pct"], 50.77, places=1)

    def test_floor_drawdown_buffer(self):
        res = calculate_floor_drawdown_buffer(floor_price_sol=150.0, loan_principal_sol=97.5)
        self.assertEqual(res["breakeven_floor_sol"], 97.5)
        self.assertEqual(res["drawdown_buffer_sol"], 52.5)
        self.assertEqual(res["drawdown_buffer_pct"], 35.0)

    def test_evaluate_sharky_collection_risk(self):
        prime = evaluate_sharky_collection_risk(ltv_pct=50.0, stated_apr_pct=40.0, drawdown_buffer_pct=50.0)
        self.assertEqual(prime["status"], "PRIME_UNDERWRITING")
        self.assertGreaterEqual(prime["safety_score"], 80.0)

        risky = evaluate_sharky_collection_risk(ltv_pct=90.0, stated_apr_pct=20.0, drawdown_buffer_pct=10.0)
        self.assertEqual(risky["status"], "HIGH_DEFAULT_EXPOSURE")
        self.assertLess(risky["safety_score"], 50.0)

    def test_invalid_parameters_raise(self):
        with self.assertRaises(ValueError):
            calculate_sharky_loan_yield(principal_sol=-5.0)
        with self.assertRaises(ValueError):
            calculate_default_foreclosure_profit(floor_price_sol=-10.0)
        with self.assertRaises(ValueError):
            calculate_floor_drawdown_buffer(floor_price_sol=0.0)

if __name__ == "__main__":
    unittest.main()
