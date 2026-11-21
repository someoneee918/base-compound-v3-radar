import unittest
from adrena_alp_radar import (
    calculate_alp_rebalancing_fee,
    calculate_skew_funding_rate,
    calculate_alp_real_yield_apr,
    evaluate_adrena_market
)

class TestAdrenaAlpRadar(unittest.TestCase):
    def test_rebalancing_fee_zero_cost(self):
        # Actual weight 30%, Target 35% -> delta = -5%
        # fee = 15.0 + (-5 * 4.0) = 15 - 20 = -5 -> max(0, -5) = 0.0 bps
        # Deposit $15,000 -> fee = $0.00
        res = calculate_alp_rebalancing_fee(
            deposit_amount_usd=15000.0,
            actual_weight_pct=30.0,
            target_weight_pct=35.0,
            base_fee_bps=15.0,
            slope=4.0
        )
        self.assertEqual(res["fee_bps"], 0.0)
        self.assertEqual(res["fee_cost_usd"], 0.0)
        self.assertEqual(res["status"], "ZERO_FEE_REBALANCE_BONUS")

    def test_overweight_fee_penalty(self):
        # Actual weight 40%, Target 35% -> delta = +5%
        # fee = 15.0 + (5 * 4.0) = 35.0 bps
        # Deposit $15,000 -> fee = 15000 * 0.0035 = $52.50
        res = calculate_alp_rebalancing_fee(
            deposit_amount_usd=15000.0,
            actual_weight_pct=40.0,
            target_weight_pct=35.0,
            base_fee_bps=15.0,
            slope=4.0
        )
        self.assertEqual(res["fee_bps"], 35.0)
        self.assertEqual(res["fee_cost_usd"], 52.50)
        self.assertEqual(res["status"], "OVERWEIGHT_SURCHARGE")

    def test_skew_funding_rate(self):
        # Long OI $6M, Short OI $3M, Pool TVL $10M -> Skew = +$3M (30% ratio)
        # Hourly funding = 0.30 * 0.05 * 100 = 1.5 bps/hr
        # Daily = 1.5 * 24 = 36.0 bps/day
        # Annual APR = 36 * 365 / 100 = 131.4% APR
        res = calculate_skew_funding_rate(
            long_oi_usd=6000000.0,
            short_oi_usd=3000000.0,
            pool_liquidity_usd=10000000.0,
            velocity_factor=0.05
        )
        self.assertEqual(res["skew_usd"], 3000000.0)
        self.assertEqual(res["skew_ratio_pct"], 30.0)
        self.assertEqual(res["hourly_funding_bps"], 1.5)
        self.assertEqual(res["annual_funding_apr_pct"], 131.4)

    def test_alp_real_yield_apr(self):
        # Deposit $20,000 in $8,000,000 pool (0.25% share)
        # Daily volume $15,000,000, 8.0 bps fee = $12,000/day
        # 70% share to ALP = $8,400/day
        # User income = 8400 * 0.0025 = $21.00/day
        # Annual income = 21.00 * 365 = $7,665.00
        # ALP APR = 7665 / 20000 = 38.325 -> 38.33%
        res = calculate_alp_real_yield_apr(
            user_deposit_usd=20000.0,
            pool_daily_volume_usd=15000000.0,
            trading_fee_bps=8.0,
            protocol_revenue_share_pct=70.0,
            pool_alp_tvl_usd=8000000.0
        )
        self.assertEqual(res["user_share_pct"], 0.25)
        self.assertEqual(res["user_daily_income_usd"], 21.00)
        self.assertEqual(res["user_annual_income_usd"], 7665.00)
        self.assertEqual(res["alp_staking_apr_pct"], 38.32)

    def test_evaluate_adrena_market(self):
        res = evaluate_adrena_market(
            deposit_usd=20000.0,
            actual_weight=30.0,
            target_weight=35.0,
            long_oi=6000000.0,
            short_oi=3000000.0,
            volume=15000000.0
        )
        self.assertEqual(res["tier"], "PRIME_ZERO_FEE_ALP_ACCUMULATION")

if __name__ == "__main__":
    unittest.main()
