import unittest
from biconomy_mee_radar import (
    calculate_biconomy_userop_bundling_profit,
    calculate_paymaster_treasury_runway_and_alerts,
    calculate_mee_cross_chain_intent_settlement,
    verify_vip_license
)

class TestBiconomyMeeRadar(unittest.TestCase):
    def test_userop_bundling_cost_and_profit(self):
        # 10,000 ops, 150,000 gas, 0.005 gwei, $0.0008 blob fee, $3000 ETH, 10% markup
        # L2 gas = 150000 * 5e-12 * 3000 = $0.00225
        # Total cost per op = $0.00225 + $0.0008 = $0.00305
        # 10% markup -> revenue = $0.003355, profit per op = $0.000305
        # 10,000 ops -> total profit = $3.05
        res = calculate_biconomy_userop_bundling_profit(
            userop_count=10000,
            avg_execution_gas=150000,
            base_l2_fee_gwei=0.005,
            l1_data_fee_usd=0.0008,
            eth_price_usd=3000.0,
            paymaster_markup_pct=10.0
        )
        self.assertEqual(res["userop_count"], 10000)
        self.assertEqual(res["actual_cost_per_op_usd"], 0.00305)
        self.assertAlmostEqual(res["profit_per_op_usd"], 0.000305, places=6)
        self.assertAlmostEqual(res["total_bundle_cost_usd"], 30.50, delta=0.01)
        self.assertAlmostEqual(res["total_bundle_profit_usd"], 3.05, delta=0.01)

    def test_paymaster_treasury_runway_safe(self):
        # $500 deposit, 10,000 daily ops, $0.00305 cost per op -> daily burn = $30.50
        # Runway = 500 / 30.5 = 16.4 days (safe)
        res = calculate_paymaster_treasury_runway_and_alerts(
            entrypoint_deposit_usd=500.0,
            daily_userop_volume=10000,
            actual_cost_per_op_usd=0.00305,
            low_runway_alert_days=3.0
        )
        self.assertEqual(res["daily_burn_usd"], 30.5)
        self.assertEqual(res["runway_days"], 16.4)
        self.assertFalse(res["is_runway_critical"])
        self.assertEqual(res["suggested_topup_usd"], 0.0)

    def test_paymaster_treasury_runway_critical(self):
        # $50 deposit, 10,000 daily ops ($30.50 burn) -> 1.6 days runway (critical <= 3 days)
        res = calculate_paymaster_treasury_runway_and_alerts(
            entrypoint_deposit_usd=50.0,
            daily_userop_volume=10000,
            actual_cost_per_op_usd=0.00305,
            low_runway_alert_days=3.0
        )
        self.assertEqual(res["runway_days"], 1.6)
        self.assertTrue(res["is_runway_critical"])
        self.assertGreater(res["suggested_topup_usd"], 150.0)

    def test_mee_cross_chain_intent_settlement(self):
        # $5,000 intent, 8 bps quote spread ($4.00 gross), $0.15 bridging gas
        # Net profit = $3.85 (7.70 bps margin)
        res = calculate_mee_cross_chain_intent_settlement(
            intent_volume_usd=5000.0,
            solver_quote_spread_bps=8.0,
            bridging_gas_cost_usd=0.15
        )
        self.assertEqual(res["gross_solver_spread_usd"], 4.0)
        self.assertEqual(res["net_solver_profit_usd"], 3.85)
        self.assertEqual(res["net_margin_bps"], 7.7)

    def test_verify_vip_license(self):
        valid_base = verify_vip_license(
            tx_hash="0x" + "1" * 64,
            chain="base",
            recipient="0xF0E0D361bBE899F3089f0a968506eF2B97693c01",
            amount=5.0
        )
        self.assertTrue(valid_base["verified"])
        self.assertEqual(valid_base["tier"], "Biconomy MEE VIP Sentinel")

        valid_sol = verify_vip_license(
            tx_hash="1" * 64,
            chain="solana",
            recipient="DW2MdHEq3qZ6nh9b5YFUoaPnBuuxC8Gz2785kwbbjSAM",
            amount=0.03
        )
        self.assertTrue(valid_sol["verified"])

if __name__ == "__main__":
    unittest.main()