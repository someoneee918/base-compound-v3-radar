import unittest
from derive_options_radar import (
    calculate_options_payoff_and_settlement_pnl,
    calculate_variance_risk_premium_and_harvest_roi,
    calculate_subaccount_portfolio_margin_requirement,
    verify_vip_license
)

class TestDeriveOptionsRadar(unittest.TestCase):
    def test_options_call_payoff_itm(self):
        # 3000 Strike, 3200 Spot at expiry, $100 premium, 2 contracts Long Call
        # Gross payout = (3200 - 3000) * 2 = $400
        # Premium paid = 100 * 2 = $200
        # Net PnL = $200 (+100% ROI)
        res = calculate_options_payoff_and_settlement_pnl(
            strike_price=3000.0,
            underlying_spot_at_expiry=3200.0,
            option_type="call",
            is_long=True,
            option_premium_usd=100.0,
            contracts_count=2.0
        )
        self.assertTrue(res["is_in_the_money"])
        self.assertEqual(res["intrinsic_value"], 200.0)
        self.assertEqual(res["gross_total_payout_usd"], 400.0)
        self.assertEqual(res["net_pnl_usd"], 200.0)
        self.assertEqual(res["roi_pct"], 100.0)

    def test_options_put_payoff_otm(self):
        # 2800 Strike, 3000 Spot at expiry, Put is OTM
        res = calculate_options_payoff_and_settlement_pnl(
            strike_price=2800.0,
            underlying_spot_at_expiry=3000.0,
            option_type="put",
            is_long=True,
            option_premium_usd=50.0,
            contracts_count=1.0
        )
        self.assertFalse(res["is_in_the_money"])
        self.assertEqual(res["intrinsic_value"], 0.0)
        self.assertEqual(res["gross_total_payout_usd"], 0.0)
        self.assertEqual(res["net_pnl_usd"], -50.0)
        self.assertEqual(res["roi_pct"], -100.0)

    def test_vrp_harvest_roi(self):
        # 65% IV vs 45% RV -> VRP = +20%
        # Premium collected $400, $10k delta-hedged capital, 14 days to expiry, $10 hedging cost
        # VRP ratio = 20 / 65 = ~0.3077 -> Gross VRP = 400 * 0.3077 = $123.08
        # Net VRP = $113.08 on $10k capital = 1.13% in 14 days (~29.48% APR)
        res = calculate_variance_risk_premium_and_harvest_roi(
            implied_vol_pct=65.0,
            realized_vol_pct=45.0,
            option_premium_collected_usd=400.0,
            delta_hedged_capital_usd=10000.0,
            days_to_expiry=14,
            hedging_cost_usd=10.0
        )
        self.assertTrue(res["is_vrp_positive"])
        self.assertEqual(res["vrp_spread_pct"], 20.0)
        self.assertAlmostEqual(res["net_vrp_profit_usd"], 113.08, delta=0.5)
        self.assertGreater(res["annualized_vrp_apr_pct"], 25.0)

    def test_subaccount_portfolio_margin_discount(self):
        # $10k collateral, $20k long perps, $20k short calls (covered call pair)
        # Base margin rate 10% -> Base = $40k * 0.1 = $4,000
        # Hedged pair = $20k -> Discount = $20k * 0.1 * 0.4 = $800 discount
        # Net required margin = $3,200 (32% util -> safe)
        res = calculate_subaccount_portfolio_margin_requirement(
            subaccount_collateral_usd=10000.0,
            long_perps_notional_usd=20000.0,
            short_calls_notional_usd=20000.0,
            short_puts_notional_usd=0.0,
            base_margin_rate_pct=10.0,
            offset_discount_pct=40.0
        )
        self.assertEqual(res["base_required_margin_usd"], 4000.0)
        self.assertEqual(res["margin_discount_usd"], 800.0)
        self.assertEqual(res["net_required_margin_usd"], 3200.0)
        self.assertEqual(res["margin_utilization_pct"], 32.0)
        self.assertTrue(res["is_margin_safe"])

    def test_verify_vip_license(self):
        valid_base = verify_vip_license(
            tx_hash="0x" + "e" * 64,
            chain="base",
            recipient="0xF0E0D361bBE899F3089f0a968506eF2B97693c01",
            amount=5.0
        )
        self.assertTrue(valid_base["verified"])
        self.assertEqual(valid_base["tier"], "Derive Options VIP Sentinel")

        valid_sol = verify_vip_license(
            tx_hash="e" * 64,
            chain="solana",
            recipient="DW2MdHEq3qZ6nh9b5YFUoaPnBuuxC8Gz2785kwbbjSAM",
            amount=0.03
        )
        self.assertTrue(valid_sol["verified"])

if __name__ == "__main__":
    unittest.main()