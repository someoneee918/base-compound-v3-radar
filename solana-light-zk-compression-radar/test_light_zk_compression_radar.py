#!/usr/bin/env python3
import unittest
from light_zk_compression_radar import (
    calculate_zk_state_rent_savings,
    calculate_groth16_compute_budget,
    calculate_photon_indexer_efficiency,
    evaluate_zk_architecture_viability,
)

class TestLightZKCompressionRadar(unittest.TestCase):

    def test_zk_state_rent_savings(self):
        res = calculate_zk_state_rent_savings(
            total_token_accounts=1000000,
            traditional_rent_per_account_sol=0.00203928,
            zk_cost_per_leaf_sol=0.000005,
            sol_price_usd=200.0
        )
        self.assertAlmostEqual(res["traditional_total_sol"], 2039.28, places=2)
        self.assertAlmostEqual(res["traditional_total_usd"], 407856.0, places=1)
        self.assertEqual(res["zk_total_sol"], 5.0)
        self.assertEqual(res["zk_total_usd"], 1000.0)
        self.assertAlmostEqual(res["sol_saved"], 2034.28, places=2)
        self.assertAlmostEqual(res["usd_saved"], 406856.0, places=1)
        self.assertGreater(res["savings_pct"], 99.7)

    def test_groth16_compute_budget(self):
        res = calculate_groth16_compute_budget(
            num_proofs=4,
            units_per_groth16_proof=210000,
            base_tx_overhead_units=15000,
            max_tx_compute_limit=1400000
        )
        self.assertEqual(res["total_tx_cus"], 855000)
        self.assertTrue(res["is_within_limit"])
        self.assertEqual(res["max_possible_proofs_per_tx"], 6)
        self.assertEqual(res["headroom_cus"], 545000)
        self.assertAlmostEqual(res["cu_utilization_pct"], 61.07, places=2)

    def test_photon_indexer_efficiency(self):
        res = calculate_photon_indexer_efficiency(
            monthly_queries=2000000,
            cache_hit_ratio=0.85,
            cost_per_million_queries_usd=15.0
        )
        self.assertEqual(res["actual_rpc_queries"], 300000)
        self.assertEqual(res["uncached_cost_usd"], 30.0)
        self.assertEqual(res["actual_cost_usd"], 4.5)
        self.assertEqual(res["usd_saved"], 25.5)
        self.assertEqual(res["savings_pct"], 85.0)

    def test_evaluate_zk_architecture_viability(self):
        large = evaluate_zk_architecture_viability(total_accounts=500000, tx_throughput_per_sec=100.0)
        self.assertEqual(large["recommendation"], "MANDATORY_ZK_COMPRESSION")

        mid = evaluate_zk_architecture_viability(total_accounts=50000, tx_throughput_per_sec=10.0)
        self.assertEqual(mid["recommendation"], "HIGHLY_BENEFICIAL")

        small = evaluate_zk_architecture_viability(total_accounts=500, tx_throughput_per_sec=1.0)
        self.assertEqual(small["recommendation"], "OPTIONAL_EVALUATION")

    def test_invalid_parameters_raise(self):
        with self.assertRaises(ValueError):
            calculate_zk_state_rent_savings(total_token_accounts=-100)
        with self.assertRaises(ValueError):
            calculate_groth16_compute_budget(num_proofs=-1)
        with self.assertRaises(ValueError):
            calculate_photon_indexer_efficiency(cache_hit_ratio=1.2)

if __name__ == "__main__":
    unittest.main()
