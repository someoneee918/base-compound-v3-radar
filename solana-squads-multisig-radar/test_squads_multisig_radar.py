import unittest
from squads_multisig_radar import (
    calculate_multisig_proposal_execution_and_relayer_profit,
    calculate_stale_proposal_rent_reclamation,
    calculate_timelock_and_threshold_quorum_security,
    verify_vip_license
)

class TestSquadsMultisigRadar(unittest.TestCase):
    def test_multisig_proposal_execution_and_relayer_profit(self):
        # 100 proposals executed, 0.005 SOL bounty ($0.75), 150k CU, 50k micro-lamports priority
        # Base fee = 0.000005, priority = 150k * 50k / 1e12 = 0.0000075 -> Total cost = 0.0000125 SOL
        # Net profit per tx = 0.005 - 0.0000125 = 0.0049875 SOL (~$0.748)
        # Total profit for 100 txs = 0.4988 SOL (~$74.81)
        res = calculate_multisig_proposal_execution_and_relayer_profit(
            proposal_count=100,
            executor_bounty_sol=0.005,
            execution_cu=150000,
            priority_fee_micro_lamports=50000,
            sol_price_usd=150.0
        )
        self.assertEqual(res["proposal_count"], 100)
        self.assertAlmostEqual(res["net_profit_per_tx_sol"], 0.004987, delta=0.00001)
        self.assertAlmostEqual(res["total_profit_sol"], 0.4987, delta=0.001)
        self.assertGreater(res["profit_margin_pct"], 99.0)

    def test_stale_proposal_rent_reclamation(self):
        # 400 stale proposal accounts in DAO treasury, 0.0025 SOL rent per account
        # Total rent = 400 * 0.0025 = 1.0 SOL ($150.00)
        res = calculate_stale_proposal_rent_reclamation(
            stale_proposal_count=400,
            avg_proposal_rent_sol=0.0025,
            sol_price_usd=150.0
        )
        self.assertEqual(res["total_reclaimed_sol"], 1.0)
        self.assertEqual(res["total_reclaimed_usd"], 150.0)
        self.assertAlmostEqual(res["net_recovered_sol"], 0.9992, delta=0.001)

    def test_timelock_and_threshold_quorum_safe(self):
        # 3-of-5 multisig (60% quorum), 24h timelock, $10,000 spending limit, $5,000 transfer
        res = calculate_timelock_and_threshold_quorum_security(
            members_count=5,
            threshold=3,
            timelock_hours=24.0,
            daily_spending_limit_usd=10000.0,
            attempted_transfer_usd=5000.0
        )
        self.assertEqual(res["quorum_pct"], 60.0)
        self.assertFalse(res["exceeds_spending_limit"])
        self.assertFalse(res["requires_full_multisig"])
        self.assertTrue(res["has_timelock_protection"])

    def test_spending_limit_exceeded(self):
        # $50,000 transfer exceeds $10,000 spending limit
        res = calculate_timelock_and_threshold_quorum_security(
            members_count=5,
            threshold=3,
            timelock_hours=24.0,
            daily_spending_limit_usd=10000.0,
            attempted_transfer_usd=50000.0
        )
        self.assertTrue(res["exceeds_spending_limit"])
        self.assertTrue(res["requires_full_multisig"])

    def test_verify_vip_license(self):
        valid_sol = verify_vip_license(
            tx_hash="4" * 64,
            chain="solana",
            recipient="DW2MdHEq3qZ6nh9b5YFUoaPnBuuxC8Gz2785kwbbjSAM",
            amount=0.03
        )
        self.assertTrue(valid_sol["verified"])
        self.assertEqual(valid_sol["tier"], "Squads Multisig VIP Sentinel")

        valid_base = verify_vip_license(
            tx_hash="0x" + "4" * 64,
            chain="base",
            recipient="0xF0E0D361bBE899F3089f0a968506eF2B97693c01",
            amount=5.0
        )
        self.assertTrue(valid_base["verified"])

if __name__ == "__main__":
    unittest.main()