#!/usr/bin/env python3
import unittest
from pendle_yield_radar import (
    calculate_pt_fixed_apy,
    calculate_yt_leveraged_carry,
    calculate_pendle_amm_pull_to_par,
    evaluate_pendle_trade_signal,
)

class TestPendleYieldRadar(unittest.TestCase):

    def test_pt_fixed_apy(self):
        res = calculate_pt_fixed_apy(pt_price=0.940, days_to_maturity=90, deposit_amount_usd=10000.0)
        self.assertAlmostEqual(res["net_profit_usd"], 638.30, places=1)
        self.assertAlmostEqual(res["net_roi_pct"], 6.38, places=1)
        self.assertGreater(res["fixed_apy_pct"], 25.0)
        self.assertEqual(res["days_to_maturity"], 90)

    def test_yt_leveraged_carry(self):
        res = calculate_yt_leveraged_carry(
            underlying_price=1.0,
            yt_price=0.060,
            actual_variable_apr=0.30,
            implied_yield_apr=0.12,
            days_held=90,
            capital_usd=10000.0
        )
        self.assertAlmostEqual(res["leverage_ratio"], 16.67, places=1)
        self.assertGreater(res["net_profit_usd"], 2000.0)
        self.assertGreater(res["net_roi_pct"], 20.0)
        self.assertAlmostEqual(res["breakeven_variable_apr_pct"], 24.33, places=1)

    def test_pendle_amm_pull_to_par(self):
        start = calculate_pendle_amm_pull_to_par(initial_pt_price=0.940, days_elapsed=0, total_days=90)
        self.assertEqual(start["current_pt_price"], 0.940)
        self.assertEqual(start["discount_captured_pct"], 0.0)

        mid = calculate_pendle_amm_pull_to_par(initial_pt_price=0.940, days_elapsed=45, total_days=90)
        self.assertGreater(mid["current_pt_price"], 0.940)
        self.assertLess(mid["current_pt_price"], 1.0)

        end = calculate_pendle_amm_pull_to_par(initial_pt_price=0.940, days_elapsed=90, total_days=90)
        self.assertEqual(end["current_pt_price"], 1.0)
        self.assertEqual(end["discount_captured_pct"], 100.0)

    def test_evaluate_pendle_trade_signal(self):
        sig_buy_pt = evaluate_pendle_trade_signal(fixed_apy=28.0, current_variable_apr=0.15, pt_price=0.940)
        self.assertEqual(sig_buy_pt["recommendation"], "STRONG_BUY_PT")

        sig_buy_yt = evaluate_pendle_trade_signal(fixed_apy=10.0, current_variable_apr=0.25, pt_price=0.970)
        self.assertEqual(sig_buy_yt["recommendation"], "STRONG_BUY_YT")

        sig_neutral = evaluate_pendle_trade_signal(fixed_apy=15.0, current_variable_apr=0.145, pt_price=0.960)
        self.assertEqual(sig_neutral["recommendation"], "NEUTRAL_LP_DEPOSIT")

    def test_invalid_parameters_raise(self):
        with self.assertRaises(ValueError):
            calculate_pt_fixed_apy(pt_price=1.05)
        with self.assertRaises(ValueError):
            calculate_yt_leveraged_carry(yt_price=-0.05)
        with self.assertRaises(ValueError):
            calculate_pendle_amm_pull_to_par(days_elapsed=100, total_days=90)

if __name__ == "__main__":
    unittest.main()
