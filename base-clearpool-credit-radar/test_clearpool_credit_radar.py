import unittest
from clearpool_credit_radar import (
    calculate_clearpool_utilization_and_borrow_rate,
    calculate_lender_net_yield_and_credit_spread,
    calculate_insurance_pool_coverage,
    verify_vip_license,
    BASE_USDC_RECEIVE_ADDRESS,
    SOLANA_RECEIVE_ADDRESS
)

class TestClearpoolCreditRadar(unittest.TestCase):
    def test_utilization_below_kink(self):
        # $1M pool, $600k borrowed -> 60% util, below 80% kink
        # borrow APR = 2.0 + (60/80)*10 = 2.0 + 7.5 = 9.5%
        # supply APR = 9.5 * 0.60 * 0.95 = 5.415%
        res = calculate_clearpool_utilization_and_borrow_rate(
            pool_total_liquidity_usd=1000000.0,
            total_borrowed_usd=600000.0,
            base_rate_pct=2.0,
            kink_utilization_pct=80.0,
            slope1_pct=10.0,
            slope2_pct=60.0,
            insurance_cut_pct=5.0
        )
        self.assertEqual(res["utilization_pct"], 60.0)
        self.assertFalse(res["is_above_kink"])
        self.assertAlmostEqual(res["borrow_apr_pct"], 9.5, delta=0.01)
        self.assertAlmostEqual(res["supply_apr_pct"], 5.415, delta=0.01)
        self.assertEqual(res["available_liquidity_usd"], 400000.0)

    def test_utilization_above_kink_rate_surge(self):
        # $1M pool, $850k borrowed -> 85% util, above 80% kink
        # excess util = (85 - 80)/(100 - 80) = 5/20 = 0.25
        # borrow APR = 2.0 + 10.0 + (0.25 * 60) = 27.0%
        # supply APR = 27.0 * 0.85 * 0.95 = 21.8025%
        res = calculate_clearpool_utilization_and_borrow_rate(
            pool_total_liquidity_usd=1000000.0,
            total_borrowed_usd=850000.0,
            base_rate_pct=2.0,
            kink_utilization_pct=80.0,
            slope1_pct=10.0,
            slope2_pct=60.0,
            insurance_cut_pct=5.0
        )
        self.assertEqual(res["utilization_pct"], 85.0)
        self.assertTrue(res["is_above_kink"])
        self.assertAlmostEqual(res["borrow_apr_pct"], 27.0, delta=0.01)
        self.assertAlmostEqual(res["supply_apr_pct"], 21.8025, delta=0.01)

    def test_lender_net_yield_and_credit_spread(self):
        # $10,000 deposit, supply APR = 21.8025%, default prob = 1.0%, recovery = 40.0%
        # expected loss rate = 1.0 * (1 - 0.40) = 0.60%
        # net interest APR = 21.8025 - 0.60 = 21.2025%
        # total net APR with 3.5% CPOOL rewards = 24.7025%
        # credit spread over 4.5% SOFR = +20.2025% = +2020.25 bps
        res = calculate_lender_net_yield_and_credit_spread(
            deposit_amount_usd=10000.0,
            supply_apr_pct=21.8025,
            default_probability_pct=1.0,
            recovery_rate_pct=40.0,
            cpool_rewards_apr_pct=3.5,
            risk_free_rate_pct=4.5
        )
        self.assertEqual(res["deposit_amount_usd"], 10000.0)
        self.assertAlmostEqual(res["expected_loss_rate_pct"], 0.60, delta=0.01)
        self.assertAlmostEqual(res["net_total_apr_pct"], 24.7025, delta=0.01)
        self.assertAlmostEqual(res["credit_spread_bps"], 2020.25, delta=1.0)
        self.assertAlmostEqual(res["annual_net_cashflow_usd"], 2470.25, delta=0.1)
        self.assertAlmostEqual(res["daily_net_cashflow_usd"], 6.7678, delta=0.01)

    def test_insurance_pool_coverage_adequacy(self):
        # $850k debt, 5% buffer required = $42,500
        # Scenario A: $50k reserve -> 117.65% coverage (adequate)
        res_a = calculate_insurance_pool_coverage(
            borrower_debt_usd=850000.0,
            insurance_pool_cpool_usd=50000.0,
            required_buffer_pct=5.0
        )
        self.assertTrue(res_a["is_adequately_covered"])
        self.assertAlmostEqual(res_a["coverage_ratio_pct"], 117.65, delta=0.05)
        self.assertEqual(res_a["shortfall_usd"], 0.0)

        # Scenario B: $30k reserve -> 70.59% coverage (shortfall $12,500)
        res_b = calculate_insurance_pool_coverage(
            borrower_debt_usd=850000.0,
            insurance_pool_cpool_usd=30000.0,
            required_buffer_pct=5.0
        )
        self.assertFalse(res_b["is_adequately_covered"])
        self.assertAlmostEqual(res_b["shortfall_usd"], 12500.0, delta=0.1)

    def test_verify_vip_license(self):
        # Base valid
        b_res = verify_vip_license("0xcredittx12345678", "base", 5.0, BASE_USDC_RECEIVE_ADDRESS)
        self.assertTrue(b_res["valid"])
        self.assertEqual(b_res["granted_chain"], "base")

        # Solana valid
        s_res = verify_vip_license("solcreditstream123", "solana", 0.03, SOLANA_RECEIVE_ADDRESS)
        self.assertTrue(s_res["valid"])
        self.assertEqual(s_res["granted_chain"], "solana")

        # Underfunded Base
        bad_base = verify_vip_license("0xcredittx12345678", "base", 4.9, BASE_USDC_RECEIVE_ADDRESS)
        self.assertFalse(bad_base["valid"])

if __name__ == "__main__":
    unittest.main()
