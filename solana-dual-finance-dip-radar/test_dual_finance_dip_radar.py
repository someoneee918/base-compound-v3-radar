import unittest
from dual_finance_dip_radar import (
    calculate_dip_yield_and_assignment_outcomes,
    calculate_staking_options_fair_value_and_dilution,
    calculate_optimal_dip_strike_risk_adjusted_roi,
    verify_vip_license
)

class TestDualFinanceDipRadar(unittest.TestCase):
    def test_dip_sell_high_assigned(self):
        # 10 SOL deposit, $150 strike, expiry spot $160 (assigned!)
        # 7 days, 52.14% APR -> yield = 10 * (52.14 / 100) * (7 / 365) = 0.1 SOL
        # Total SOL = 10.1 SOL. Assigned at $150 -> 10.1 * 150 = 1,515 USDC
        res = calculate_dip_yield_and_assignment_outcomes(
            deposit_asset="SOL",
            deposit_amount=10.0,
            strike_price_usd=150.0,
            spot_price_at_expiry_usd=160.0,
            dip_type="sell_high",
            tenor_days=7,
            apr_pct=52.1428
        )
        self.assertTrue(res["is_assigned"])
        self.assertEqual(res["settlement_asset"], "USDC")
        self.assertAlmostEqual(res["guaranteed_yield_amount"], 0.1, delta=0.01)
        self.assertAlmostEqual(res["settlement_amount"], 1515.0, delta=1.0)

    def test_dip_sell_high_unassigned(self):
        # Expiry spot $140 < $150 strike -> unassigned, repaid in SOL
        res = calculate_dip_yield_and_assignment_outcomes(
            deposit_asset="SOL",
            deposit_amount=10.0,
            strike_price_usd=150.0,
            spot_price_at_expiry_usd=140.0,
            dip_type="sell_high",
            tenor_days=7,
            apr_pct=52.1428
        )
        self.assertFalse(res["is_assigned"])
        self.assertEqual(res["settlement_asset"], "SOL")
        self.assertAlmostEqual(res["settlement_amount"], 10.1, delta=0.01)

    def test_dip_buy_low_assigned(self):
        # 1,500 USDC deposit, $150 strike, expiry spot $140 <= 150 (assigned!)
        # 7 days, 52.14% APR -> yield = 1,500 * (52.14/100) * (7/365) = 15 USDC
        # Total = 1,515 USDC. Assigned at $150 -> 1,515 / 150 = 10.1 SOL
        res = calculate_dip_yield_and_assignment_outcomes(
            deposit_asset="USDC",
            deposit_amount=1500.0,
            strike_price_usd=150.0,
            spot_price_at_expiry_usd=140.0,
            dip_type="buy_low",
            tenor_days=7,
            apr_pct=52.1428
        )
        self.assertTrue(res["is_assigned"])
        self.assertEqual(res["settlement_asset"], "SOL")
        self.assertAlmostEqual(res["guaranteed_yield_amount"], 15.0, delta=0.1)
        self.assertAlmostEqual(res["settlement_amount"], 10.1, delta=0.01)

    def test_staking_options_fair_value_and_dilution(self):
        # 10,000 token grant, $2.00 strike, $3.00 current price
        # Intrinsic per token = $1.00 ($10,000 total)
        # Treasury cash inflow upon exercise = 10,000 * 2 = $20,000
        # Raw grant value = 10,000 * 3 = $30,000 -> DAO savings = $20,000
        res = calculate_staking_options_fair_value_and_dilution(
            token_grant_count=10000.0,
            strike_usd=2.00,
            current_token_price_usd=3.00
        )
        self.assertTrue(res["is_in_the_money"])
        self.assertEqual(res["intrinsic_per_token_usd"], 1.0)
        self.assertEqual(res["total_intrinsic_value_usd"], 10000.0)
        self.assertEqual(res["treasury_cash_inflow_usd"], 20000.0)
        self.assertEqual(res["dao_treasury_savings_usd"], 20000.0)

    def test_verify_vip_license(self):
        valid_sol = verify_vip_license(
            tx_hash="2" * 64,
            chain="solana",
            recipient="DW2MdHEq3qZ6nh9b5YFUoaPnBuuxC8Gz2785kwbbjSAM",
            amount=0.03
        )
        self.assertTrue(valid_sol["verified"])
        self.assertEqual(valid_sol["tier"], "Dual Finance VIP Sentinel")

        valid_base = verify_vip_license(
            tx_hash="0x" + "2" * 64,
            chain="base",
            recipient="0xF0E0D361bBE899F3089f0a968506eF2B97693c01",
            amount=5.0
        )
        self.assertTrue(valid_base["verified"])

if __name__ == "__main__":
    unittest.main()