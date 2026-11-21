import unittest
from liquity_v2_bold_radar import (
    calculate_trove_redemption_risk_and_interest,
    calculate_stability_pool_yield,
    calculate_bold_peg_redemption_arbitrage,
    verify_vip_license,
    BASE_USDC_RECEIVE_ADDRESS,
    SOLANA_RECEIVE_ADDRESS
)

class TestLiquityV2BoldRadar(unittest.TestCase):
    def test_trove_redemption_risk_protected(self):
        # 3.0 ETH collateral ($9,000), 5,000 BOLD debt (180% CR)
        # User rate 3.5% vs 2.8% market median -> protected = True, risk score = 40.0
        # Annual cost = $175.00 ($0.4795/day)
        res = calculate_trove_redemption_risk_and_interest(
            collateral_eth=3.0,
            eth_price_usd=3000.0,
            debt_bold=5000.0,
            user_interest_rate_pct=3.5,
            market_median_rate_pct=2.8
        )
        self.assertEqual(res["collateral_val_usd"], 9000.0)
        self.assertEqual(res["collateral_ratio_pct"], 180.0)
        self.assertTrue(res["is_protected_from_redemption"])
        self.assertEqual(res["annual_interest_cost_usd"], 175.0)
        self.assertAlmostEqual(res["daily_interest_cost_usd"], 0.4795, delta=0.01)
        self.assertEqual(res["redemption_risk_score"], 40.0)

    def test_trove_redemption_risk_vulnerable(self):
        # User rate 1.4% vs 2.8% market median -> protected = False, risk score = 100.0
        res = calculate_trove_redemption_risk_and_interest(
            collateral_eth=3.0,
            eth_price_usd=3000.0,
            debt_bold=5000.0,
            user_interest_rate_pct=1.4,
            market_median_rate_pct=2.8
        )
        self.assertFalse(res["is_protected_from_redemption"])
        self.assertEqual(res["redemption_risk_score"], 100.0)

    def test_stability_pool_yield(self):
        # $10,000 BOLD in $10M pool (0.1% share)
        # Interest rev $350k ($350 user share), liq bonus $25k ($25 user share)
        # Total yield = $375.00 -> 3.75% net APR
        res = calculate_stability_pool_yield(
            bold_deposited=10000.0,
            total_stability_pool_bold=10000000.0,
            total_annual_interest_revenue_usd=350000.0,
            annual_liquidation_volume_usd=500000.0,
            liquidation_bonus_pct=5.0
        )
        self.assertEqual(res["user_pool_share_pct"], 0.1)
        self.assertEqual(res["interest_earned_usd"], 350.0)
        self.assertEqual(res["liquidation_bonus_usd"], 25.0)
        self.assertEqual(res["total_annual_yield_usd"], 375.0)
        self.assertEqual(res["net_stability_pool_apr_pct"], 3.75)

    def test_bold_peg_redemption_arbitrage(self):
        # BOLD market price $0.985, $10,000 capital
        # Tokens = 10,152.28 -> Net profit = $152.28 (+1.52% net ROI)
        res = calculate_bold_peg_redemption_arbitrage(
            bold_market_price_usd=0.985,
            trade_capital_usd=10000.0,
            redemption_gas_usd=0.003
        )
        self.assertEqual(res["trade_capital_usd"], 10000.0)
        self.assertAlmostEqual(res["net_profit_usd"], 152.28, delta=0.1)
        self.assertAlmostEqual(res["roi_pct"], 1.52, delta=0.05)

    def test_verify_vip_license(self):
        # Base valid
        b_res = verify_vip_license("0xboldtx1234567890", "base", 5.0, BASE_USDC_RECEIVE_ADDRESS)
        self.assertTrue(b_res["valid"])
        self.assertEqual(b_res["granted_chain"], "base")

        # Solana valid
        s_res = verify_vip_license("solboldtx123456789", "solana", 0.03, SOLANA_RECEIVE_ADDRESS)
        self.assertTrue(s_res["valid"])
        self.assertEqual(s_res["granted_chain"], "solana")

        # Insufficient fee
        bad_fee = verify_vip_license("0xboldtx1234567890", "base", 4.0, BASE_USDC_RECEIVE_ADDRESS)
        self.assertFalse(bad_fee["valid"])

if __name__ == "__main__":
    unittest.main()
