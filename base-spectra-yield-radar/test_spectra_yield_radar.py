import unittest
from spectra_yield_radar import (
    calculate_pt_fixed_yield_discount,
    calculate_yt_leverage_yield_pnl,
    calculate_amm_time_decay_convergence,
    verify_vip_license,
    BASE_USDC_RECEIVE_ADDRESS,
    SOLANA_RECEIVE_ADDRESS
)

class TestSpectraYieldRadar(unittest.TestCase):
    def test_pt_fixed_yield_discount(self):
        # $10,000 underlying, 180 days maturity, 8.5% implied fixed APR
        # time_fraction = 180 / 365 = 0.49315
        # pt_ratio = 1 / (1 + 0.085 * 0.49315) = 1 / 1.041918 = 0.959768
        # pt_buy_price = $9,597.68, fixed_gain = $402.32 -> realized APR = 8.50%
        res = calculate_pt_fixed_yield_discount(
            underlying_deposit_usd=10000.0,
            maturity_days=180,
            fixed_implied_apr_pct=8.5
        )
        self.assertEqual(res["underlying_deposit_usd"], 10000.0)
        self.assertEqual(res["maturity_days"], 180)
        self.assertAlmostEqual(res["pt_price_ratio"], 0.959768, delta=0.0001)
        self.assertAlmostEqual(res["pt_buy_price_usd"], 9597.68, delta=0.1)
        self.assertAlmostEqual(res["fixed_interest_gain_usd"], 402.32, delta=0.1)
        self.assertAlmostEqual(res["realized_fixed_apr_pct"], 8.50, delta=0.05)

    def test_yt_leverage_yield_profitable(self):
        # Invest $402.32 in YT representing $10,000 principal
        # Variable yield surged to 14.0% over 180 days -> $690.41 harvested
        # Net profit = $690.41 - $402.32 = $288.09 (+71.61% ROI)
        res = calculate_yt_leverage_yield_pnl(
            yt_capital_invested_usd=402.32,
            underlying_principal_represented_usd=10000.0,
            variable_actual_apy_pct=14.0,
            maturity_days=180
        )
        self.assertTrue(res["is_profitable"])
        self.assertAlmostEqual(res["variable_interest_harvested_usd"], 690.41, delta=0.1)
        self.assertAlmostEqual(res["net_yt_profit_usd"], 288.09, delta=0.1)
        self.assertAlmostEqual(res["yt_roi_pct"], 71.61, delta=0.1)

    def test_yt_leverage_yield_loss_on_rate_drop(self):
        # Invest $402.32 in YT, but variable yield collapsed to 4.0%
        # Harvested = 10,000 * 0.04 * (180 / 365) = $197.26
        # Net profit = 197.26 - 402.32 = -$205.06 (loss)
        res = calculate_yt_leverage_yield_pnl(
            yt_capital_invested_usd=402.32,
            underlying_principal_represented_usd=10000.0,
            variable_actual_apy_pct=4.0,
            maturity_days=180
        )
        self.assertFalse(res["is_profitable"])
        self.assertLess(res["net_yt_profit_usd"], 0)
        self.assertAlmostEqual(res["variable_interest_harvested_usd"], 197.26, delta=0.1)

    def test_amm_time_decay_convergence(self):
        # PT price ratio = 0.959768 with 180 days left
        # Pull to par gain = (1.0 - 0.959768)/0.959768 = 4.19% (8.50% annualized)
        res = calculate_amm_time_decay_convergence(
            current_pt_price_ratio=0.959768,
            days_to_maturity=180,
            initial_maturity_days=180
        )
        self.assertAlmostEqual(res["pull_to_par_gain_pct"], 4.19, delta=0.05)
        self.assertAlmostEqual(res["annualized_convergence_apr_pct"], 8.50, delta=0.05)

    def test_verify_vip_license(self):
        # Base valid
        b_res = verify_vip_license("0xspectratx12345678", "base", 5.0, BASE_USDC_RECEIVE_ADDRESS)
        self.assertTrue(b_res["valid"])
        self.assertEqual(b_res["granted_chain"], "base")

        # Solana valid
        s_res = verify_vip_license("solspectratx1234567", "solana", 0.03, SOLANA_RECEIVE_ADDRESS)
        self.assertTrue(s_res["valid"])
        self.assertEqual(s_res["granted_chain"], "solana")

        # Insufficient fee
        bad_fee = verify_vip_license("0xspectratx12345678", "base", 4.0, BASE_USDC_RECEIVE_ADDRESS)
        self.assertFalse(bad_fee["valid"])

if __name__ == "__main__":
    unittest.main()
