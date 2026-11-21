import unittest
from armada_liquidity_radar import (
    calculate_lbp_weight_and_price_trajectory,
    calculate_auction_capital_raised_and_fdv,
    calculate_post_lbp_liquidity_migration,
    verify_vip_license,
    BASE_USDC_RECEIVE_ADDRESS,
    SOLANA_RECEIVE_ADDRESS
)

class TestArmadaLiquidityRadar(unittest.TestCase):
    def test_lbp_start_trajectory(self):
        # 10M base tokens, $100k USDC, 90% base / 10% quote start
        # Spot price = (100k / 0.10) / (10M / 0.90) = 1,000,000 / 11,111,111 = $0.0900
        res = calculate_lbp_weight_and_price_trajectory(
            initial_base_reserves=10000000.0,
            initial_quote_reserves_usd=100000.0,
            initial_base_weight_pct=90.0,
            terminal_base_weight_pct=10.0,
            total_duration_hours=72.0,
            elapsed_hours=0.0
        )
        self.assertEqual(res["progress_pct"], 0.0)
        self.assertEqual(res["current_base_weight_pct"], 90.0)
        self.assertEqual(res["current_quote_weight_pct"], 10.0)
        self.assertAlmostEqual(res["spot_price_usd"], 0.0900, delta=0.0001)
        self.assertEqual(res["price_decay_pct"], 0.0)

    def test_lbp_midpoint_trajectory(self):
        # Midpoint at 36 hrs (50% progress): weights = 50% base, 50% quote
        # Spot price = (100k / 0.50) / (10M / 0.50) = 200,000 / 20,000,000 = $0.0100
        res = calculate_lbp_weight_and_price_trajectory(
            initial_base_reserves=10000000.0,
            initial_quote_reserves_usd=100000.0,
            initial_base_weight_pct=90.0,
            terminal_base_weight_pct=10.0,
            total_duration_hours=72.0,
            elapsed_hours=36.0
        )
        self.assertEqual(res["progress_pct"], 50.0)
        self.assertEqual(res["current_base_weight_pct"], 50.0)
        self.assertEqual(res["current_quote_weight_pct"], 50.0)
        self.assertAlmostEqual(res["spot_price_usd"], 0.0100, delta=0.0001)
        # Price dropped from 0.0900 to 0.0100: decay = (0.09 - 0.01)/0.09 = 88.89%
        self.assertAlmostEqual(res["price_decay_pct"], 88.89, delta=0.05)

    def test_auction_capital_raised_and_fdv(self):
        # 5M tokens sold at avg $0.05, 100M total supply, 100 bps fee
        res = calculate_auction_capital_raised_and_fdv(
            tokens_sold=5000000.0,
            avg_execution_price_usd=0.05,
            total_token_supply=100000000.0,
            pool_fee_bps=100.0
        )
        self.assertEqual(res["gross_capital_raised_usd"], 250000.0)
        self.assertEqual(res["protocol_fee_usd"], 2500.0)
        self.assertEqual(res["net_capital_raised_usd"], 247500.0)
        self.assertEqual(res["implied_fdv_usd"], 5000000.0)
        self.assertEqual(res["capital_efficiency_pct"], 99.0)

    def test_post_lbp_liquidity_migration(self):
        # $247,500 net capital, 50% allocated to LP -> $123,750 quote, $247,500 AMM depth
        # 2.5x annual volume ($618,750), 0.25% fee tier -> $1,546.875 annual fees
        res = calculate_post_lbp_liquidity_migration(
            net_capital_raised_usd=247500.0,
            target_lp_quote_ratio_pct=50.0,
            volume_to_tvl_multiple=2.5,
            amm_fee_tier_pct=0.25
        )
        self.assertEqual(res["quote_allocated_usd"], 123750.0)
        self.assertEqual(res["treasury_retained_usd"], 123750.0)
        self.assertEqual(res["initial_amm_depth_usd"], 247500.0)
        self.assertAlmostEqual(res["annual_lp_fee_usd"], 1546.88, delta=0.1)
        self.assertAlmostEqual(res["lp_fee_apy_pct"], 0.625, delta=0.01)

    def test_verify_vip_license(self):
        # Base valid
        b_res = verify_vip_license("0xarmadatx12345678", "base", 5.0, BASE_USDC_RECEIVE_ADDRESS)
        self.assertTrue(b_res["valid"])
        self.assertEqual(b_res["granted_chain"], "base")

        # Solana valid
        s_res = verify_vip_license("solarmadatx12345678", "solana", 0.03, SOLANA_RECEIVE_ADDRESS)
        self.assertTrue(s_res["valid"])
        self.assertEqual(s_res["granted_chain"], "solana")

        # Insufficient fee
        bad_fee = verify_vip_license("solarmadatx12345678", "solana", 0.01, SOLANA_RECEIVE_ADDRESS)
        self.assertFalse(bad_fee["valid"])

if __name__ == "__main__":
    unittest.main()
