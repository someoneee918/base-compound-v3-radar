import unittest
from curvance_market_radar import (
    calculate_curvance_leveraged_carry,
    calculate_dutch_auction_liquidation,
    calculate_account_safety_buffer,
    evaluate_curvance_market
)

class TestCurvanceMarketRadar(unittest.TestCase):
    def test_curvance_leveraged_carry(self):
        # Deposit $10,000, 3.0x leverage -> supplied $30,000, borrowed $20,000
        # Collateral yield 8.5% -> gross = 30,000 * 0.085 = $2,550
        # Borrow rate 3.5% -> borrow cost = 20,000 * 0.035 = $700
        # Net annual profit = 2550 - 700 = $1,850.00
        # Net APY = 1850 / 10000 = 18.5%
        # Daily = 1850 / 365 = $5.07/day
        res = calculate_curvance_leveraged_carry(
            deposit_amount_usd=10000.0,
            target_leverage=3.0,
            collateral_yield_apy=8.5,
            borrow_rate_apy=3.5
        )
        self.assertEqual(res["total_supplied_usd"], 30000.0)
        self.assertEqual(res["debt_borrowed_usd"], 20000.0)
        self.assertEqual(res["net_annual_profit_usd"], 1850.0)
        self.assertEqual(res["net_leveraged_apy"], 18.5)
        self.assertAlmostEqual(res["daily_cashflow_usd"], 5.07, places=2)

    def test_dutch_auction_liquidation_start(self):
        # Elapsed 0s, start discount 10.0%, debt repaid $5,000
        # Seized = 5000 * 1.10 = $5,500 -> Gross profit = $500, Gas = $0.04 -> Net = $499.96
        res = calculate_dutch_auction_liquidation(
            repaid_debt_usd=5000.0,
            elapsed_seconds=0.0
        )
        self.assertEqual(res["current_discount_pct"], 10.0)
        self.assertEqual(res["gross_profit_usd"], 500.0)
        self.assertEqual(res["net_profit_usd"], 499.96)
        self.assertAlmostEqual(res["roi_pct"], 10.0, places=1)

    def test_dutch_auction_liquidation_halfway(self):
        # Elapsed 900s of 1800s (50% progress)
        # discount = 10.0 - (0.50 * 8.0) = 6.0%
        # Seized = 5000 * 1.06 = $5,300 -> Gross = $300, Net = $299.96
        res = calculate_dutch_auction_liquidation(
            repaid_debt_usd=5000.0,
            elapsed_seconds=900.0
        )
        self.assertEqual(res["current_discount_pct"], 6.0)
        self.assertEqual(res["gross_profit_usd"], 300.0)
        self.assertEqual(res["net_profit_usd"], 299.96)

    def test_account_safety_buffer(self):
        # Collateral $30,000, Debt $20,000, LT 85%
        # Effective collateral = 30000 * 0.85 = $25,500
        # HF = 25500 / 20000 = 1.275
        # Max drawdown = (1 - 20000/25500) * 100 = 21.57%
        res = calculate_account_safety_buffer(
            collateral_usd=30000.0,
            debt_usd=20000.0,
            liquidation_threshold_pct=85.0
        )
        self.assertEqual(res["health_factor"], 1.275)
        self.assertEqual(res["max_drawdown_pct"], 21.57)
        self.assertFalse(res["is_liquidatable"])
        self.assertEqual(res["status"], "HEALTHY")

    def test_evaluate_curvance_market(self):
        res = evaluate_curvance_market(
            deposit_usd=10000.0,
            leverage=3.0,
            collateral_yield=8.5,
            borrow_rate=3.5,
            elapsed_seconds=900.0
        )
        self.assertEqual(res["tier"], "PRIME_CURVANCE_CARRY_LOOP")

if __name__ == "__main__":
    unittest.main()
