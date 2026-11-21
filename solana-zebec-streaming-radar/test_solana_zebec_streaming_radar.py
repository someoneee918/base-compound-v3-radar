import unittest
from solana_zebec_streaming_radar import (
    calculate_stream_flow_metrics,
    calculate_streaming_treasury_gas_savings,
    calculate_escrow_yield_harvesting,
    verify_vip_license,
    BASE_USDC_RECEIVE_ADDRESS,
    SOLANA_RECEIVE_ADDRESS
)

class TestSolanaZebecStreamingRadar(unittest.TestCase):
    def test_stream_flow_metrics_active_post_cliff(self):
        # $120,000 stream over 365 days, 90 days cliff, 120 days elapsed
        res = calculate_stream_flow_metrics(
            total_amount_usd=120000.0,
            duration_days=365.0,
            cliff_days=90.0,
            elapsed_days=120.0
        )
        self.assertEqual(res["total_amount_usd"], 120000.0)
        self.assertFalse(res["is_cliff_active"])
        self.assertAlmostEqual(res["rate_per_day_usd"], 328.7671, delta=0.01)
        self.assertAlmostEqual(res["rate_per_second_usd"], 0.003805, delta=0.0001)
        self.assertAlmostEqual(res["unlocked_amount_usd"], 39452.05, delta=0.1)
        self.assertAlmostEqual(res["remaining_amount_usd"], 80547.95, delta=0.1)
        self.assertAlmostEqual(res["completion_pct"], 32.88, delta=0.05)

    def test_stream_flow_metrics_during_cliff(self):
        # 60 days elapsed with a 90 days cliff -> 0 unlocked
        res = calculate_stream_flow_metrics(
            total_amount_usd=120000.0,
            duration_days=365.0,
            cliff_days=90.0,
            elapsed_days=60.0
        )
        self.assertTrue(res["is_cliff_active"])
        self.assertEqual(res["unlocked_amount_usd"], 0.0)
        self.assertEqual(res["remaining_amount_usd"], 120000.0)
        self.assertEqual(res["completion_pct"], 0.0)

    def test_streaming_treasury_gas_savings(self):
        # 100 employees, weekly (52/yr), 1 yr, $0.0005/tx, $0.0020 setup
        res = calculate_streaming_treasury_gas_savings(
            num_employees=100,
            payroll_frequency_per_year=52,
            years=1.0,
            solana_tx_fee_usd=0.0005,
            stream_creation_fee_usd=0.0020
        )
        self.assertEqual(res["discrete_txs"], 5200)
        self.assertAlmostEqual(res["discrete_gas_cost_usd"], 2.60, delta=0.01)
        self.assertAlmostEqual(res["streaming_gas_cost_usd"], 0.20, delta=0.01)
        self.assertAlmostEqual(res["gas_saved_usd"], 2.40, delta=0.01)
        self.assertAlmostEqual(res["savings_pct"], 92.31, delta=0.05)

    def test_escrow_yield_harvesting(self):
        # $1,000,000 stream pool, 6.5% lending APY, 365 days
        res = calculate_escrow_yield_harvesting(
            stream_pool_balance_usd=1000000.0,
            lending_apy_pct=6.5,
            stream_duration_days=365.0
        )
        self.assertEqual(res["average_escrow_balance_usd"], 500000.0)
        self.assertAlmostEqual(res["harvested_yield_usd"], 32500.0, delta=0.1)
        self.assertAlmostEqual(res["daily_yield_usd"], 89.0411, delta=0.05)

    def test_verify_vip_license(self):
        # Base valid
        b_res = verify_vip_license("0xstreamtx12345678", "base", 5.0, BASE_USDC_RECEIVE_ADDRESS)
        self.assertTrue(b_res["valid"])
        self.assertEqual(b_res["granted_chain"], "base")

        # Solana valid
        s_res = verify_vip_license("soltxstream12345678", "solana", 0.03, SOLANA_RECEIVE_ADDRESS)
        self.assertTrue(s_res["valid"])
        self.assertEqual(s_res["granted_chain"], "solana")

        # Insufficient SOL
        bad_sol = verify_vip_license("soltxstream12345678", "solana", 0.029, SOLANA_RECEIVE_ADDRESS)
        self.assertFalse(bad_sol["valid"])

if __name__ == "__main__":
    unittest.main()
