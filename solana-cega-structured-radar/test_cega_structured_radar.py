import unittest
from cega_structured_radar import (
    calculate_autocall_structured_note_irr,
    calculate_knock_in_barrier_buffer,
    calculate_cega_vault_revenue_and_fees,
    verify_vip_license,
    BASE_USDC_RECEIVE_ADDRESS,
    SOLANA_RECEIVE_ADDRESS
)

class TestCegaStructuredRadar(unittest.TestCase):
    def test_autocall_structured_note_triggered(self):
        # $10,000 note, 22% coupon, 12 wks tenure, autocall week 4 at 105% barrier, current 108%
        res = calculate_autocall_structured_note_irr(
            deposit_amount_usd=10000.0,
            annual_coupon_pct=22.0,
            tenure_weeks=12,
            autocall_week=4,
            autocall_barrier_pct=105.0,
            current_price_pct=108.0
        )
        self.assertTrue(res["is_autocalled"])
        self.assertEqual(res["effective_tenure_weeks"], 4)
        self.assertAlmostEqual(res["coupon_earned_usd"], 169.23, delta=0.1)
        self.assertAlmostEqual(res["total_payout_usd"], 10169.23, delta=0.1)
        self.assertAlmostEqual(res["annualized_irr_pct"], 22.0, delta=0.01)

    def test_autocall_structured_note_not_triggered(self):
        # Current price 98% (below 105% barrier) -> full 12 weeks tenure
        res = calculate_autocall_structured_note_irr(
            deposit_amount_usd=10000.0,
            annual_coupon_pct=22.0,
            tenure_weeks=12,
            autocall_week=4,
            autocall_barrier_pct=105.0,
            current_price_pct=98.0
        )
        self.assertFalse(res["is_autocalled"])
        self.assertEqual(res["effective_tenure_weeks"], 12)
        self.assertAlmostEqual(res["coupon_earned_usd"], 507.69, delta=0.1)
        self.assertAlmostEqual(res["total_payout_usd"], 10507.69, delta=0.1)

    def test_knock_in_barrier_buffer_safe(self):
        # Initial spot $200, 50% barrier ($100), current market $180
        # Buffer = $80 (44.44% margin)
        res = calculate_knock_in_barrier_buffer(
            underlying_spot_usd=200.0,
            knock_in_barrier_pct=50.0,
            current_market_price_usd=180.0
        )
        self.assertEqual(res["barrier_price_usd"], 100.0)
        self.assertEqual(res["safety_buffer_usd"], 80.0)
        self.assertAlmostEqual(res["safety_buffer_pct"], 44.44, delta=0.05)
        self.assertFalse(res["is_barrier_breached"])

    def test_cega_vault_revenue_and_fees(self):
        # $5M TVL, 1.0% mgmt ($50k), 15% perf, 22% gross ($1.1M) -> perf fee $165k
        # Net lender yield = $1.1M - $215k = $885k -> 17.70% net APR
        res = calculate_cega_vault_revenue_and_fees(
            vault_tvl_usd=5000000.0,
            management_fee_pct=1.0,
            performance_fee_pct=15.0,
            gross_yield_apr_pct=22.0
        )
        self.assertEqual(res["gross_yield_usd"], 1100000.0)
        self.assertEqual(res["management_fee_usd"], 50000.0)
        self.assertEqual(res["performance_fee_usd"], 165000.0)
        self.assertEqual(res["total_protocol_fee_usd"], 215000.0)
        self.assertEqual(res["net_lender_yield_usd"], 885000.0)
        self.assertAlmostEqual(res["net_lender_apr_pct"], 17.70, delta=0.01)

    def test_verify_vip_license(self):
        # Base valid
        b_res = verify_vip_license("0xcegatx1234567890", "base", 5.0, BASE_USDC_RECEIVE_ADDRESS)
        self.assertTrue(b_res["valid"])
        self.assertEqual(b_res["granted_chain"], "base")

        # Solana valid
        s_res = verify_vip_license("solcegatx123456789", "solana", 0.03, SOLANA_RECEIVE_ADDRESS)
        self.assertTrue(s_res["valid"])
        self.assertEqual(s_res["granted_chain"], "solana")

        # Unsupported chain
        inv_res = verify_vip_license("0xcegatx1234567890", "arbitrum", 5.0, BASE_USDC_RECEIVE_ADDRESS)
        self.assertFalse(inv_res["valid"])

if __name__ == "__main__":
    unittest.main()
