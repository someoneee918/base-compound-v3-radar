#!/usr/bin/env python3
import unittest
from helius_das_compression_radar import (
    calculate_das_rpc_batch_savings,
    calculate_canopy_proof_overhead,
    calculate_concurrent_merkle_tree_rent_savings,
    evaluate_das_indexing_health,
)

class TestHeliusDASCompressionRadar(unittest.TestCase):

    def test_das_rpc_batch_savings(self):
        res = calculate_das_rpc_batch_savings(
            total_assets_queried=500000,
            single_query_credits=10,
            batch_size=100,
            batch_query_credits=50,
            cost_per_million_credits_usd=10.0
        )
        self.assertEqual(res["unbatched_credits"], 5000000)
        self.assertEqual(res["num_batches"], 5000)
        self.assertEqual(res["batched_credits"], 250000)
        self.assertAlmostEqual(res["credit_savings_pct"], 95.0, places=1)
        self.assertEqual(res["unbatched_cost_usd"], 50.0)
        self.assertEqual(res["batched_cost_usd"], 2.5)
        self.assertEqual(res["usd_saved"], 47.5)

    def test_canopy_proof_overhead(self):
        res = calculate_canopy_proof_overhead(max_depth=20, canopy_depth=10, hash_size_bytes=32)
        self.assertEqual(res["full_proof_hashes"], 20)
        self.assertEqual(res["transmitted_proof_hashes"], 10)
        self.assertEqual(res["full_proof_bytes"], 640)
        self.assertEqual(res["transmitted_proof_bytes"], 320)
        self.assertEqual(res["bytes_saved_per_tx"], 320)
        self.assertEqual(res["overhead_reduction_pct"], 50.0)

    def test_concurrent_merkle_tree_rent_savings(self):
        res = calculate_concurrent_merkle_tree_rent_savings(
            total_mint_capacity=1000000,
            max_depth=20,
            max_buffer_size=64,
            canopy_depth=14,
            sol_price_usd=200.0
        )
        self.assertAlmostEqual(res["traditional_total_rent_sol"], 2039.28, places=2)
        self.assertAlmostEqual(res["traditional_total_cost_usd"], 407856.0, places=1)
        self.assertLessEqual(res["tree_rent_sol"], 15.0)
        self.assertGreater(res["savings_pct"], 99.0)
        self.assertGreater(res["usd_saved"], 400000.0)

    def test_evaluate_das_indexing_health(self):
        healthy = evaluate_das_indexing_health(monthly_queries=1000000, batch_ratio=0.95, canopy_depth=14, max_depth=20)
        self.assertEqual(healthy["status"], "HIGHLY_OPTIMIZED")
        self.assertGreaterEqual(healthy["health_score"], 80.0)

        unoptimized = evaluate_das_indexing_health(monthly_queries=1000000, batch_ratio=0.10, canopy_depth=2, max_depth=20)
        self.assertEqual(unoptimized["status"], "UNOPTIMIZED_CREDIT_LEAK")
        self.assertLess(unoptimized["health_score"], 50.0)

    def test_invalid_parameters_raise(self):
        with self.assertRaises(ValueError):
            calculate_das_rpc_batch_savings(total_assets_queried=-10)
        with self.assertRaises(ValueError):
            calculate_canopy_proof_overhead(max_depth=20, canopy_depth=25)
        with self.assertRaises(ValueError):
            calculate_concurrent_merkle_tree_rent_savings(total_mint_capacity=0)
        with self.assertRaises(ValueError):
            evaluate_das_indexing_health(batch_ratio=1.5)

if __name__ == "__main__":
    unittest.main()
