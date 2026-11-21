import unittest
from uxd_stablecoin_radar import (
    calculate_delta_neutral_funding_yield,
    calculate_negative_funding_insurance_runway,
    calculate_uxd_peg_arbitrage,
    verify_vip_license,
    BASE_USDC_RECEIVE_ADDRESS,
    SOLANA_RECEIVE_ADDRESS
)

class TestUXDStablecoinRadar(unittest.TestCase):
    def test_delta_neutral_funding_yield(self):
        # $10,000 deposit, 18.5% funding APR, 15% insurance cut ($277.50)
        # Net staker yield = $1,572.50 (15.725% net APR, $4.3082/day)
        res = calculate_delta_neutral_funding_yield(
            deposit_amount_usd=10000.0,
            funding_rate_apr_pct=18.5,
            protocol_insurance_cut_pct=15.0
        )
        self.assertEqual(res["deposit_amount_usd"], 10000.0)
        self.assertAlmostEqual(res["gross_funding_usd"], 1850.0, delta=0.1)
        self.assertAlmostEqual(res["insurance_cut_usd"], 277.50, delta=0.1)
        self.assertAlmostEqual(res["net_staker_yield_usd"], 1572.50, delta=0.1)
        self.assertAlmostEqual(res["net_staker_apr_pct"], 15.725, delta=0.01)
        self.assertAlmostEqual(res["daily_cashflow_usd"], 4.3082, delta=0.01)

    def test_negative_funding_insurance_runway_safe(self):
        # $5M supply, 5.0% negative funding ($250k/yr -> $684.93/day)
        # $250k insurance fund -> 365.0 days runway (safe)
        res = calculate_negative_funding_insurance_runway(
            total_uxd_supply_usd=5000000.0,
            negative_funding_apr_pct=5.0,
            insurance_fund_balance_usd=250000.0
        )
        self.assertFalse(res["is_solvency_risk"])
        self.assertAlmostEqual(res["daily_funding_cost_usd"], 684.93, delta=0.1)
        self.assertAlmostEqual(res["runway_days"], 365.0, delta=0.5)

    def test_negative_funding_insurance_runway_risk(self):
        # $5M supply, 15.0% severe negative funding, only $50k insurance fund
        # Daily cost = $2,054.79 -> 24.3 days runway (< 30 days -> risk!)
        res = calculate_negative_funding_insurance_runway(
            total_uxd_supply_usd=5000000.0,
            negative_funding_apr_pct=15.0,
            insurance_fund_balance_usd=50000.0
        )
        self.assertTrue(res["is_solvency_risk"])
        self.assertLess(res["runway_days"], 30.0)

    def test_uxd_peg_arbitrage(self):
        # Secondary price $0.985, $10,000 capital, 10 bps fee ($10.15), $0.001 gas
        # Tokens = 10,152.28 -> Net proceeds = $10,142.13 -> Net profit = $142.13 (1.42% ROI)
        res = calculate_uxd_peg_arbitrage(
            secondary_uxd_price_usd=0.985,
            trade_capital_usd=10000.0,
            redemption_fee_bps=10.0,
            solana_tx_fee_usd=0.001
        )
        self.assertEqual(res["trade_capital_usd"], 10000.0)
        self.assertAlmostEqual(res["net_profit_usd"], 142.13, delta=0.1)
        self.assertAlmostEqual(res["roi_pct"], 1.42, delta=0.05)

    def test_verify_vip_license(self):
        # Base valid
        b_res = verify_vip_license("0xuxdtx1234567890", "base", 5.0, BASE_USDC_RECEIVE_ADDRESS)
        self.assertTrue(b_res["valid"])
        self.assertEqual(b_res["granted_chain"], "base")

        # Solana valid
        s_res = verify_vip_license("soluxdtx123456789", "solana", 0.03, SOLANA_RECEIVE_ADDRESS)
        self.assertTrue(s_res["valid"])
        self.assertEqual(s_res["granted_chain"], "solana")

        # Insufficient SOL
        bad_sol = verify_vip_license("soluxdtx123456789", "solana", 0.02, SOLANA_RECEIVE_ADDRESS)
        self.assertFalse(bad_sol["valid"])

if __name__ == "__main__":
    unittest.main()
