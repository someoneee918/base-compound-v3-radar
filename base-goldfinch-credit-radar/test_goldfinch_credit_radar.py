import unittest
from goldfinch_credit_radar import (
    calculate_tranche_waterfall_yields,
    calculate_default_impairment_waterfall,
    calculate_secondary_loan_token_discount,
    verify_vip_license,
    BASE_USDC_RECEIVE_ADDRESS,
    SOLANA_RECEIVE_ADDRESS
)

class TestGoldfinchCreditRadar(unittest.TestCase):
    def test_tranche_waterfall_yields(self):
        # $1,000,000 loan, 12% borrower rate, 20% junior ($200k), 80% senior ($800k)
        # 20% reallocation bonus from senior to junior, 10% protocol fee
        # senior net income = (800k*0.12 - 96k*0.20)*0.90 = 76,800 * 0.90 = $69,120 -> 8.64% APY
        # junior net income = (200k*0.12 + 96k*0.20)*0.90 = 43,200 * 0.90 = $38,880 -> 19.44% APY
        res = calculate_tranche_waterfall_yields(
            borrower_principal_usd=1000000.0,
            borrower_interest_rate_pct=12.0,
            junior_tranche_ratio_pct=20.0,
            junior_reallocation_pct=20.0,
            protocol_reserve_fee_pct=10.0
        )
        self.assertEqual(res["senior_capital_usd"], 800000.0)
        self.assertEqual(res["junior_capital_usd"], 200000.0)
        self.assertAlmostEqual(res["senior_net_annual_income_usd"], 69120.0, delta=0.1)
        self.assertAlmostEqual(res["junior_net_annual_income_usd"], 38880.0, delta=0.1)
        self.assertAlmostEqual(res["senior_net_apy_pct"], 8.64, delta=0.01)
        self.assertAlmostEqual(res["junior_net_apy_pct"], 19.44, delta=0.01)
        self.assertAlmostEqual(res["junior_yield_boost_pct"], 10.80, delta=0.01)

    def test_default_impairment_within_junior_buffer(self):
        # $150,000 default loss on $200k junior buffer -> junior takes 75% hit, senior protected
        res = calculate_default_impairment_waterfall(
            borrower_principal_usd=1000000.0,
            default_loss_amount_usd=150000.0,
            junior_tranche_ratio_pct=20.0
        )
        self.assertEqual(res["junior_loss_absorbed_usd"], 150000.0)
        self.assertEqual(res["senior_loss_absorbed_usd"], 0.0)
        self.assertAlmostEqual(res["junior_impairment_pct"], 75.0, delta=0.01)
        self.assertEqual(res["senior_impairment_pct"], 0.0)
        self.assertTrue(res["senior_principal_protected"])

    def test_default_impairment_breaching_senior_buffer(self):
        # $300,000 default loss on $200k junior buffer -> junior 100% wiped out, senior takes $100k (12.5%)
        res = calculate_default_impairment_waterfall(
            borrower_principal_usd=1000000.0,
            default_loss_amount_usd=300000.0,
            junior_tranche_ratio_pct=20.0
        )
        self.assertEqual(res["junior_loss_absorbed_usd"], 200000.0)
        self.assertEqual(res["senior_loss_absorbed_usd"], 100000.0)
        self.assertEqual(res["junior_impairment_pct"], 100.0)
        self.assertAlmostEqual(res["senior_impairment_pct"], 12.5, delta=0.01)
        self.assertFalse(res["senior_principal_protected"])

    def test_secondary_loan_token_discount(self):
        # $10,000 face value, 150 bps discount, 6 months holding, 10% coupon
        # buy price = $9,850, discount gain = $150, coupon = $500, total = $650
        # annualized yield = (650 / 9850) * 2 * 100 = 13.198%
        res = calculate_secondary_loan_token_discount(
            face_value_usd=10000.0,
            secondary_discount_bps=150.0,
            holding_months=6.0,
            annual_coupon_pct=10.0
        )
        self.assertEqual(res["buy_price_usd"], 9850.0)
        self.assertEqual(res["discount_gain_usd"], 150.0)
        self.assertEqual(res["coupon_income_usd"], 500.0)
        self.assertEqual(res["total_return_usd"], 650.0)
        self.assertAlmostEqual(res["annualized_yield_pct"], 13.20, delta=0.05)

    def test_verify_vip_license(self):
        # Base valid
        b_res = verify_vip_license("0xgoldfinchtx123456", "base", 5.0, BASE_USDC_RECEIVE_ADDRESS)
        self.assertTrue(b_res["valid"])
        self.assertEqual(b_res["granted_chain"], "base")

        # Solana valid
        s_res = verify_vip_license("solgoldfinchtx1234", "solana", 0.03, SOLANA_RECEIVE_ADDRESS)
        self.assertTrue(s_res["valid"])
        self.assertEqual(s_res["granted_chain"], "solana")

        # Wrong recipient
        bad_rec = verify_vip_license("0xgoldfinchtx123456", "base", 5.0, "0x0000000000000000000000000000000000000000")
        self.assertFalse(bad_rec["valid"])

if __name__ == "__main__":
    unittest.main()
