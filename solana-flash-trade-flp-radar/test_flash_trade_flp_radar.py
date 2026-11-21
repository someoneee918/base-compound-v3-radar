import unittest
from flash_trade_flp_radar import (
    calculate_flp_dynamic_fee,
    calculate_trader_borrow_fee,
    calculate_flp_staking_apr,
    evaluate_flash_trade_market
)

class TestFlashTradeFlpRadar(unittest.TestCase):
    def test_dynamic_fee_rebalance_discount(self):
        # Actual weight 37%, Target 40% -> delta = -3%
        # fee = 20.0 + (-3 * 5.0) = 5.0 bps (min cap)
        # Deposit $10,000 -> fee cost = $10,000 * 0.0005 = $5.00
        res = calculate_flp_dynamic_fee(
            deposit_amount_usd=10000.0,
            actual_weight_pct=37.0,
            target_weight_pct=40.0,
            base_fee_bps=20.0,
            penalty_slope=5.0
        )
        self.assertEqual(res["fee_bps"], 5.0)
        self.assertEqual(res["fee_cost_usd"], 5.00)
        self.assertEqual(res["action_type"], "REBALANCING_DEPOSIT_DISCOUNT")

    def test_dynamic_fee_overweight_penalty(self):
        # Actual weight 44%, Target 40% -> delta = +4%
        # fee = 20.0 + (4 * 5.0) = 40.0 bps
        # Deposit $10,000 -> fee cost = $10,000 * 0.0040 = $40.00
        res = calculate_flp_dynamic_fee(
            deposit_amount_usd=10000.0,
            actual_weight_pct=44.0,
            target_weight_pct=40.0,
            base_fee_bps=20.0,
            penalty_slope=5.0
        )
        self.assertEqual(res["fee_bps"], 40.0)
        self.assertEqual(res["fee_cost_usd"], 40.00)
        self.assertEqual(res["action_type"], "OVERWEIGHT_PENALTY_SURGE")

    def test_trader_borrow_fee(self):
        # Position $25,000, Utilization 75%, base rate 0.5 bps/hr
        # rate = 0.5 * (1 + 0.75 * 2) = 0.5 * 2.5 = 1.25 bps/hr
        # hourly fee = 25000 * 0.000125 = $3.125
        # daily fee = 3.125 * 24 = $75.00/day
        # annual fee = 75 * 365 = $27,375 -> APR = 109.5%
        res = calculate_trader_borrow_fee(
            position_size_usd=25000.0,
            pool_utilization_pct=75.0,
            base_hourly_rate_bps=0.5
        )
        self.assertEqual(res["hourly_rate_bps"], 1.25)
        self.assertEqual(res["hourly_fee_usd"], 3.12)
        self.assertEqual(res["daily_fee_usd"], 75.00)
        self.assertEqual(res["borrow_apr_pct"], 109.5)

    def test_flp_staking_apr(self):
        # User deposit $20,000 in $5,000,000 TVL pool (0.40% share)
        # Daily volume $10,000,000, 6.0 bps trading fee = $6,000/day
        # 70% share to FLP = $4,200/day
        # User daily income = 4200 * 0.0040 = $16.80/day
        # User annual income = 16.80 * 365 = $6,132.00
        # FLP APR = 6132 / 20000 = 30.66%
        res = calculate_flp_staking_apr(
            user_flp_deposit_usd=20000.0,
            pool_daily_volume_usd=10000000.0,
            trading_fee_bps=6.0,
            flp_fee_share_pct=70.0,
            pool_flp_tvl_usd=5000000.0
        )
        self.assertEqual(res["user_share_pct"], 0.40)
        self.assertEqual(res["user_daily_income_usd"], 16.80)
        self.assertEqual(res["user_annual_income_usd"], 6132.00)
        self.assertEqual(res["flp_staking_apr_pct"], 30.66)

    def test_evaluate_flash_trade_market(self):
        res = evaluate_flash_trade_market(
            deposit_amount_usd=20000.0,
            actual_weight=37.0,
            target_weight=40.0,
            pool_daily_volume_usd=10000000.0,
            pool_utilization_pct=75.0
        )
        self.assertEqual(res["tier"], "PRIME_FLP_REBALANCE_ACCUMULATION")

if __name__ == "__main__":
    unittest.main()
