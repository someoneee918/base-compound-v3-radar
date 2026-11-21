import unittest
from overnight_usd_plus_radar import (
    calculate_usd_plus_rebase_yield,
    calculate_peg_discount_arbitrage,
    calculate_ets_delta_neutral_carry,
    evaluate_overnight_market
)

class TestOvernightUsdPlusRadar(unittest.TestCase):
    def test_rebase_yield(self):
        # Deposit $10,000, 11.5% gross, 10% fee -> net = 10.35% APY
        # annual profit = $1,035.00
        # daily cashflow = ~2.69/day
        res = calculate_usd_plus_rebase_yield(
            deposit_usd=10000.0,
            gross_protocol_apy=11.5,
            protocol_fee_pct=10.0
        )
        self.assertEqual(res["net_apy_pct"], 10.35)
        self.assertEqual(res["annual_profit_usd"], 1035.00)
        self.assertAlmostEqual(res["daily_cashflow_usd"], 2.69, places=1)

    def test_peg_discount_arbitrage(self):
        # Secondary price $0.9950 (0.50% discount)
        # Trade $10,000 -> buy 10,000 / 0.995 = 10,050.25 USD+
        # Redeem 1:1 = $10,050.25 USDC
        # Redeem fee 0.04% = $4.02 -> net = 10,050.25 - 4.02 - 0.04 = $10,046.19
        # Net profit = $46.19 (0.46% ROI)
        res = calculate_peg_discount_arbitrage(
            secondary_dex_price=0.9950,
            trade_size_usd=10000.0,
            redeem_fee_pct=0.04,
            base_l2_gas_usd=0.04
        )
        self.assertEqual(res["discount_pct"], 0.50)
        self.assertEqual(res["tokens_bought"], 10050.25)
        self.assertEqual(res["net_profit_usd"], 46.19)
        self.assertEqual(res["roi_pct"], 0.46)
        self.assertTrue(res["is_profitable"])

    def test_at_or_above_peg_no_arbitrage(self):
        res = calculate_peg_discount_arbitrage(secondary_dex_price=1.0005)
        self.assertFalse(res["is_profitable"])
        self.assertEqual(res["net_profit_usd"], 0.0)

    def test_ets_delta_neutral_carry(self):
        # Capital $25,000, LP yield 18.5%, Funding 8.0%, Fee 1.5%
        # Net APR = 18.5 + 8.0 - 1.5 = 25.0%
        # Annual = 25,000 * 0.25 = $6,250.00
        # Daily = 6250 / 365 = $17.12/day
        res = calculate_ets_delta_neutral_carry(
            lp_yield_apr=18.5,
            hedge_funding_apr=8.0,
            capital_allocated_usd=25000.0,
            management_fee_pct=1.5
        )
        self.assertEqual(res["net_ets_apr_pct"], 25.0)
        self.assertEqual(res["annual_cashflow_usd"], 6250.0)
        self.assertAlmostEqual(res["daily_cashflow_usd"], 17.12, places=1)

    def test_evaluate_overnight_market(self):
        res = evaluate_overnight_market(
            deposit_usd=10000.0,
            secondary_price=0.9950,
            gross_apy=11.5,
            lp_yield_apr=18.5
        )
        self.assertEqual(res["tier"], "HIGH_CONVICTION_PEG_ARBITRAGE")
        self.assertTrue(res["peg_arbitrage"]["is_profitable"])

if __name__ == "__main__":
    unittest.main()
