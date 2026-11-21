import unittest
from solayer_susd_radar import (
    calculate_susd_composite_yield_and_cashflow,
    calculate_susd_secondary_dex_peg_arbitrage,
    calculate_avs_slashing_risk_and_net_return,
    verify_vip_license
)

class TestSolayerSusdRadar(unittest.TestCase):
    def test_susd_composite_yield_and_cashflow(self):
        # $10k deposit, 4.8% RWA T-Bill APR, 5.2% InfiniSVM AVS APR, 5% protocol fee
        # Gross = 10.0%, Net = 9.50% APR
        # Annual cashflow = $950.00, Daily = $2.60
        res = calculate_susd_composite_yield_and_cashflow(
            deposit_usd=10000.0,
            rwa_treasury_apr_pct=4.80,
            avs_restaking_apr_pct=5.20,
            protocol_fee_cut_pct=5.0
        )
        self.assertEqual(res["gross_composite_apr_pct"], 10.0)
        self.assertEqual(res["net_composite_apr_pct"], 9.50)
        self.assertEqual(res["annual_cashflow_usd"], 950.0)
        self.assertEqual(res["daily_cashflow_usd"], 2.60)
        self.assertAlmostEqual(res["monthly_cashflow_usd"], 79.17, delta=0.01)

    def test_susd_secondary_dex_peg_arbitrage(self):
        # sUSD trading at $0.9920 on Orca DEX (0.80% discount), $10k trade, 0.05% fee
        res = calculate_susd_secondary_dex_peg_arbitrage(
            secondary_susd_price_usd=0.9920,
            trade_amount_usd=10000.0,
            dex_swap_fee_pct=0.05,
            par_redemption_price_usd=1.00
        )
        self.assertEqual(res["discount_spread_pct"], 0.80)
        self.assertEqual(res["dex_fee_usd"], 5.0)
        self.assertGreater(res["tokens_acquired"], 10080.0)
        self.assertGreater(res["net_profit_usd"], 75.0) # ~$75.65 net profit
        self.assertGreater(res["net_roi_pct"], 0.70)

    def test_susd_no_arbitrage_at_par(self):
        res = calculate_susd_secondary_dex_peg_arbitrage(
            secondary_susd_price_usd=1.00,
            trade_amount_usd=10000.0,
            dex_swap_fee_pct=0.05,
            par_redemption_price_usd=1.00
        )
        self.assertEqual(res["discount_spread_pct"], 0.0)
        self.assertEqual(res["net_profit_usd"], 0.0)

    def test_avs_slashing_risk_and_net_return(self):
        # 9.50% net APR, 0.2% slashing probability, 5% max slash -> expected loss = 0.01%
        res = calculate_avs_slashing_risk_and_net_return(
            deposit_usd=10000.0,
            net_composite_apr_pct=9.50,
            slashing_incident_probability_pct=0.2,
            slashing_penalty_pct=5.0
        )
        self.assertEqual(res["expected_loss_pct"], 0.01)
        self.assertEqual(res["risk_adjusted_apr_pct"], 9.49)
        self.assertEqual(res["annual_risk_adjusted_return_usd"], 949.0)

    def test_verify_vip_license(self):
        valid_sol = verify_vip_license(
            tx_hash="d" * 64,
            chain="solana",
            recipient="DW2MdHEq3qZ6nh9b5YFUoaPnBuuxC8Gz2785kwbbjSAM",
            amount=0.03
        )
        self.assertTrue(valid_sol["verified"])
        self.assertEqual(valid_sol["tier"], "Solayer sUSD VIP Sentinel")

        valid_base = verify_vip_license(
            tx_hash="0x" + "d" * 64,
            chain="base",
            recipient="0xF0E0D361bBE899F3089f0a968506eF2B97693c01",
            amount=5.0
        )
        self.assertTrue(valid_base["verified"])

if __name__ == "__main__":
    unittest.main()