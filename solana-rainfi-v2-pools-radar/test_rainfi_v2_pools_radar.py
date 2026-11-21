import unittest
from rainfi_v2_pools_radar import (
    calculate_pool_utilization_and_compounding_yield,
    calculate_refinancing_arbitrage_and_ltv_buffer,
    calculate_default_liquidation_auction_recovery,
    verify_vip_license
)

class TestRainFiV2PoolsRadar(unittest.TestCase):
    def test_pool_utilization_and_compounding_yield(self):
        # 1000 SOL pool, 800 SOL borrowed (80% util), 25% borrow APR, 10% take rate
        res = calculate_pool_utilization_and_compounding_yield(
            pool_deposit_sol=1000.0,
            active_borrowed_sol=800.0,
            base_borrow_apr_pct=25.0,
            protocol_take_rate_pct=10.0,
            compounding_frequency=52
        )
        self.assertEqual(res["utilization_rate_pct"], 80.0)
        self.assertEqual(res["net_annual_interest_sol"], 180.0) # 800 * 0.25 * 0.9
        self.assertEqual(res["net_lender_apr_pct"], 18.0)      # 180 / 1000
        self.assertGreater(res["net_lender_apy_pct"], 18.0)    # Compounding boost (~19.7%)
        self.assertGreater(res["daily_interest_sol"], 0.49)

    def test_refinancing_profitable_savings(self):
        # 20 SOL loan, 40 SOL floor (50% LTV), 30% old APR vs 18% new APR, 60 days left
        res = calculate_refinancing_arbitrage_and_ltv_buffer(
            current_loan_principal_sol=20.0,
            collateral_floor_price_sol=40.0,
            current_loan_apr_pct=30.0,
            new_offer_apr_pct=18.0,
            remaining_duration_days=60
        )
        self.assertEqual(res["current_ltv_pct"], 50.0)
        self.assertEqual(res["ltv_safety_buffer_pct"], 50.0)
        self.assertTrue(res["is_refinance_profitable"])
        self.assertGreater(res["interest_savings_sol"], 0.39)
        self.assertEqual(res["savings_pct"], 40.0)

    def test_refinancing_unprofitable(self):
        res = calculate_refinancing_arbitrage_and_ltv_buffer(
            current_loan_principal_sol=20.0,
            collateral_floor_price_sol=40.0,
            current_loan_apr_pct=20.0,
            new_offer_apr_pct=25.0, # Higher rate
            remaining_duration_days=30
        )
        self.assertFalse(res["is_refinance_profitable"])
        self.assertEqual(res["interest_savings_sol"], 0.0)

    def test_default_auction_full_recovery(self):
        # 10 SOL principal, 1 SOL interest = 11 SOL debt, auction settles at 15 SOL, 5% liquidator bonus
        res = calculate_default_liquidation_auction_recovery(
            loan_principal_sol=10.0,
            accumulated_interest_sol=1.0,
            auction_settlement_price_sol=15.0,
            liquidator_bonus_pct=5.0
        )
        self.assertEqual(res["total_debt_owed_sol"], 11.0)
        self.assertEqual(res["liquidator_fee_sol"], 0.75) # 15 * 0.05
        self.assertEqual(res["net_proceeds_sol"], 14.25)
        self.assertEqual(res["lender_recovered_sol"], 11.0)
        self.assertEqual(res["borrower_surplus_sol"], 3.25)
        self.assertEqual(res["bad_debt_shortfall_sol"], 0.0)
        self.assertEqual(res["lender_recovery_rate_pct"], 100.0)

    def test_verify_vip_license(self):
        valid_sol = verify_vip_license(
            tx_hash="5" * 64,
            chain="solana",
            recipient="DW2MdHEq3qZ6nh9b5YFUoaPnBuuxC8Gz2785kwbbjSAM",
            amount=0.03
        )
        self.assertTrue(valid_sol["verified"])
        self.assertEqual(valid_sol["tier"], "RainFi v2 VIP Sentinel")

        valid_base = verify_vip_license(
            tx_hash="0x" + "b" * 64,
            chain="base",
            recipient="0xF0E0D361bBE899F3089f0a968506eF2B97693c01",
            amount=5.0
        )
        self.assertTrue(valid_base["verified"])

if __name__ == "__main__":
    unittest.main()