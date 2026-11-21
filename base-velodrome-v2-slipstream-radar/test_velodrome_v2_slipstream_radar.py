import unittest
from velodrome_v2_slipstream_radar import (
    calculate_slipstream_concentrated_fee_apr,
    calculate_vevelo_gauge_bribe_roi_and_votes,
    calculate_protocol_bribe_emission_multiplier,
    verify_vip_license
)

class TestVelodromeV2SlipstreamRadar(unittest.TestCase):
    def test_slipstream_concentrated_fee_apr(self):
        # 3000 price, 2700 lower, 3300 upper (+-10%)
        # $10k user deposit, $5M daily volume, $10M pool TVL, 0.05% fee tier
        res = calculate_slipstream_concentrated_fee_apr(
            price_lower=2700.0,
            price_upper=3300.0,
            current_price=3000.0,
            pool_fee_tier_pct=0.05,
            daily_volume_usd=5000000.0,
            pool_tvl_usd=10000000.0,
            user_deposit_usd=10000.0
        )
        self.assertTrue(res["is_in_range"])
        self.assertGreater(res["capital_efficiency_multiplier"], 5.0)
        self.assertGreater(res["daily_fee_earned_usd"], 2.0)
        self.assertGreater(res["fee_apr_pct"], 8.0)

    def test_slipstream_out_of_range(self):
        res = calculate_slipstream_concentrated_fee_apr(
            price_lower=2700.0,
            price_upper=3300.0,
            current_price=3500.0,
            pool_fee_tier_pct=0.05,
            daily_volume_usd=5000000.0,
            pool_tvl_usd=10000000.0,
            user_deposit_usd=10000.0
        )
        self.assertFalse(res["is_in_range"])
        self.assertEqual(res["fee_apr_pct"], 0.0)

    def test_vevelo_gauge_bribe_roi(self):
        # 100,000 veVELO votes (basis = 100k * 0.15 = $15,000)
        # Total pool votes = 1,000,000 (10% share)
        # Epoch bribes = $20,000, epoch fees = $10,000 -> total epoch = $30,000
        # Voter gets 10% = $3,000/week -> $156,000/year -> 1,040% APR
        res = calculate_vevelo_gauge_bribe_roi_and_votes(
            vevelo_votes_cast=100000.0,
            total_pool_votes=1000000.0,
            epoch_bribes_usd=20000.0,
            epoch_fees_usd=10000.0,
            vevelo_token_price_usd=0.15
        )
        self.assertEqual(res["voter_pool_share_pct"], 10.0)
        self.assertEqual(res["voter_epoch_payout_usd"], 3000.0)
        self.assertEqual(res["voter_annual_payout_usd"], 156000.0)
        self.assertEqual(res["voter_capital_basis_usd"], 15000.0)
        self.assertEqual(res["voter_annual_apr_pct"], 1040.0)

    def test_protocol_bribe_emission_multiplier(self):
        # Deposit $5,000 bribe, attracts $12,500 in VELO emissions -> 2.5x multiplier
        res = calculate_protocol_bribe_emission_multiplier(
            bribe_deposited_usd=5000.0,
            expected_emissions_directed_usd=12500.0
        )
        self.assertEqual(res["capital_multiplier"], 2.5)
        self.assertEqual(res["net_subsidy_gain_usd"], 7500.0)
        self.assertEqual(res["roi_pct"], 150.0)

    def test_verify_vip_license(self):
        valid_base = verify_vip_license(
            tx_hash="0x" + "3" * 64,
            chain="base",
            recipient="0xF0E0D361bBE899F3089f0a968506eF2B97693c01",
            amount=5.0
        )
        self.assertTrue(valid_base["verified"])
        self.assertEqual(valid_base["tier"], "Velodrome Slipstream VIP Sentinel")

        valid_sol = verify_vip_license(
            tx_hash="3" * 64,
            chain="solana",
            recipient="DW2MdHEq3qZ6nh9b5YFUoaPnBuuxC8Gz2785kwbbjSAM",
            amount=0.03
        )
        self.assertTrue(valid_sol["verified"])

if __name__ == "__main__":
    unittest.main()