import unittest
from switchboard_ondemand_radar import (
    calculate_switchboard_ondemand_gas_savings,
    calculate_vrf_randomness_fulfillment_profit,
    calculate_oracle_attestation_confidence_buffer,
    verify_vip_license
)

class TestSwitchboardOnDemandRadar(unittest.TestCase):
    def test_switchboard_ondemand_gas_savings(self):
        # 5 feeds, 10k queries/day per feed ($0.0003/query -> $15/day)
        # Push feeds: 5 * 86,400 * $0.0005 = $216/day
        # Daily savings = $216 - $15 = $201/day ($73,365/year savings -> 93.06% savings)
        res = calculate_switchboard_ondemand_gas_savings(
            active_feeds_count=5,
            daily_queries_per_feed=10000,
            cost_per_ondemand_pull_usd=0.0003,
            traditional_push_frequency_sec=1,
            cost_per_push_tx_usd=0.0005
        )
        self.assertEqual(res["total_daily_push_cost_usd"], 216.0)
        self.assertEqual(res["total_daily_ondemand_cost_usd"], 15.0)
        self.assertEqual(res["daily_savings_usd"], 201.0)
        self.assertEqual(res["annual_savings_usd"], 73365.0)
        self.assertAlmostEqual(res["savings_pct"], 93.06, delta=0.1)

    def test_vrf_randomness_fulfillment_profit(self):
        # 200 requests/day, 0.002 SOL fee ($0.30), 0.000015 SOL gas ($0.00225)
        # Net per tx = 0.001985 SOL ($0.29775) -> 99.25% margin
        # Daily profit = 200 * 0.001985 = 0.397 SOL ($59.55/day -> $21,735.75/year)
        res = calculate_vrf_randomness_fulfillment_profit(
            daily_vrf_requests=200,
            protocol_request_fee_sol=0.002,
            execution_gas_sol=0.000015,
            sol_price_usd=150.0
        )
        self.assertEqual(res["net_profit_per_tx_sol"], 0.001985)
        self.assertAlmostEqual(res["net_profit_per_tx_usd"], 0.2978, delta=0.001)
        self.assertEqual(res["daily_profit_sol"], 0.397)
        self.assertEqual(res["daily_profit_usd"], 59.55)
        self.assertEqual(res["profit_margin_pct"], 99.25)

    def test_oracle_attestation_confidence_healthy(self):
        # SOL price $150.00, TEE std dev $0.15 (0.10% deviation <= 0.25% max)
        res = calculate_oracle_attestation_confidence_buffer(
            price_usd=150.0,
            tee_std_deviation_usd=0.15,
            max_safe_deviation_pct=0.25
        )
        self.assertEqual(res["deviation_ratio_pct"], 0.1)
        self.assertTrue(res["is_consensus_healthy"])
        self.assertEqual(res["price_lower_bound"], 149.7)
        self.assertEqual(res["price_upper_bound"], 150.3)

    def test_oracle_attestation_confidence_unhealthy(self):
        # TEE std dev $0.60 (0.40% deviation > 0.25% max)
        res = calculate_oracle_attestation_confidence_buffer(
            price_usd=150.0,
            tee_std_deviation_usd=0.60,
            max_safe_deviation_pct=0.25
        )
        self.assertEqual(res["deviation_ratio_pct"], 0.4)
        self.assertFalse(res["is_consensus_healthy"])

    def test_verify_vip_license(self):
        valid_sol = verify_vip_license(
            tx_hash="6" * 64,
            chain="solana",
            recipient="DW2MdHEq3qZ6nh9b5YFUoaPnBuuxC8Gz2785kwbbjSAM",
            amount=0.03
        )
        self.assertTrue(valid_sol["verified"])
        self.assertEqual(valid_sol["tier"], "Switchboard On-Demand VIP Sentinel")

        valid_base = verify_vip_license(
            tx_hash="0x" + "6" * 64,
            chain="base",
            recipient="0xF0E0D361bBE899F3089f0a968506eF2B97693c01",
            amount=5.0
        )
        self.assertTrue(valid_base["verified"])

if __name__ == "__main__":
    unittest.main()