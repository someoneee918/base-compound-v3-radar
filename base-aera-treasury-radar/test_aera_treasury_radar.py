import unittest
from aera_treasury_radar import (
    calculate_portfolio_risk_and_sharpe,
    calculate_dutch_auction_rebalance_savings,
    calculate_guardian_circuit_breaker,
    verify_vip_license,
    BASE_USDC_RECEIVE_ADDRESS,
    SOLANA_RECEIVE_ADDRESS
)

class TestAeraTreasuryRadar(unittest.TestCase):
    def test_portfolio_risk_and_sharpe(self):
        weights = {"ETH": 0.40, "USDC": 0.40, "cbBTC": 0.10, "AERO": 0.10}
        returns = {"ETH": 15.0, "USDC": 5.0, "cbBTC": 20.0, "AERO": 35.0}
        volatilities = {"ETH": 55.0, "USDC": 0.5, "cbBTC": 50.0, "AERO": 80.0}
        res = calculate_portfolio_risk_and_sharpe(weights, returns, volatilities, risk_free_rate_pct=4.5)
        self.assertAlmostEqual(res["expected_return_pct"], 13.50, delta=0.01)
        self.assertAlmostEqual(res["portfolio_volatility_pct"], 23.94, delta=0.05)
        self.assertAlmostEqual(res["excess_return_pct"], 9.00, delta=0.01)
        self.assertAlmostEqual(res["sharpe_ratio"], 0.3759, delta=0.01)

    def test_dutch_auction_rebalance_savings(self):
        # $100k turnover, direct = 50 bps ($500), Dutch = 5 bps ($50)
        res = calculate_dutch_auction_rebalance_savings(
            turnover_usd=100000.0,
            direct_amm_slippage_bps=50.0,
            aera_dutch_slippage_bps=5.0
        )
        self.assertEqual(res["direct_amm_cost_usd"], 500.0)
        self.assertEqual(res["aera_dutch_cost_usd"], 50.0)
        self.assertEqual(res["mev_slippage_saved_usd"], 450.0)
        self.assertAlmostEqual(res["savings_percentage"], 90.0, delta=0.01)

    def test_guardian_circuit_breaker_safe(self):
        # 3.5% drawdown against 5.0% threshold
        res = calculate_guardian_circuit_breaker(
            current_drawdown_pct=3.5,
            max_allowed_drawdown_pct=5.0,
            portfolio_value_usd=1000000.0
        )
        self.assertFalse(res["is_circuit_breaker_triggered"])
        self.assertEqual(res["capital_at_risk_usd"], 35000.0)
        self.assertAlmostEqual(res["buffer_remaining_pct"], 1.5, delta=0.01)

    def test_guardian_circuit_breaker_triggered(self):
        # 5.5% drawdown against 5.0% threshold
        res = calculate_guardian_circuit_breaker(
            current_drawdown_pct=5.5,
            max_allowed_drawdown_pct=5.0,
            portfolio_value_usd=1000000.0
        )
        self.assertTrue(res["is_circuit_breaker_triggered"])
        self.assertEqual(res["capital_at_risk_usd"], 55000.0)
        self.assertEqual(res["buffer_remaining_pct"], 0.0)

    def test_verify_vip_license(self):
        # Base valid
        b_res = verify_vip_license("0xaeratx1234567890", "base", 5.0, BASE_USDC_RECEIVE_ADDRESS)
        self.assertTrue(b_res["valid"])
        self.assertEqual(b_res["granted_chain"], "base")

        # Solana valid
        s_res = verify_vip_license("solaeratx123456789", "solana", 0.03, SOLANA_RECEIVE_ADDRESS)
        self.assertTrue(s_res["valid"])
        self.assertEqual(s_res["granted_chain"], "solana")

        # Underfunded Base
        bad_b = verify_vip_license("0xaeratx1234567890", "base", 4.5, BASE_USDC_RECEIVE_ADDRESS)
        self.assertFalse(bad_b["valid"])

if __name__ == "__main__":
    unittest.main()
