import unittest
from baseswap_nitro_radar import (
    calculate_clmm_capital_efficiency_and_fee_apr,
    calculate_nitro_pool_boost_and_dual_rewards,
    calculate_impermanent_loss_and_breakeven_days,
    verify_vip_license
)

class TestBaseSwapNitroRadar(unittest.TestCase):
    def test_clmm_capital_efficiency_in_range(self):
        # Current price 3000, lower 2700, upper 3300 (+-10%)
        res = calculate_clmm_capital_efficiency_and_fee_apr(
            price_lower=2700.0,
            price_upper=3300.0,
            current_price=3000.0,
            pool_fee_tier_pct=0.05,
            daily_volume_usd=5000000.0, # $5M daily vol
            pool_tvl_usd=10000000.0,   # $10M pool TVL
            user_deposit_usd=10000.0
        )
        self.assertTrue(res["is_in_range"])
        self.assertGreater(res["capital_efficiency_multiplier"], 5.0)
        self.assertGreater(res["daily_fee_earned_usd"], 0)
        self.assertGreater(res["fee_apr_pct"], 0)

    def test_clmm_out_of_range(self):
        res = calculate_clmm_capital_efficiency_and_fee_apr(
            price_lower=2700.0,
            price_upper=3300.0,
            current_price=3500.0, # Out of range
            pool_fee_tier_pct=0.05,
            daily_volume_usd=5000000.0,
            pool_tvl_usd=10000000.0,
            user_deposit_usd=10000.0
        )
        self.assertFalse(res["is_in_range"])
        self.assertEqual(res["fee_apr_pct"], 0.0)

    def test_nitro_pool_boost_and_dual_rewards(self):
        # 180 days lock -> 3.0x multiplier
        res = calculate_nitro_pool_boost_and_dual_rewards(
            user_staked_lp_usd=10000.0,
            lock_days=180,
            total_nitro_staked_usd=5000000.0,
            daily_bsx_emissions_usd=2500.0,
            daily_partner_emissions_usd=1500.0
        )
        self.assertEqual(res["multiplier"], 3.0)
        self.assertEqual(res["boosted_user_power"], 30000.0)
        self.assertGreater(res["total_nitro_apr_pct"], 0)
        self.assertGreater(res["bsx_apr_pct"], 0)
        self.assertGreater(res["partner_apr_pct"], 0)

    def test_impermanent_loss_and_breakeven(self):
        # 20% price change, 40% fee APR
        res = calculate_impermanent_loss_and_breakeven_days(
            price_change_pct=20.0,
            fee_apr_pct=40.0
        )
        self.assertAlmostEqual(res["il_pct"], 0.4074, delta=0.05)
        self.assertLess(res["breakeven_days"], 10.0)

    def test_verify_vip_license(self):
        valid_base = verify_vip_license(
            tx_hash="0x" + "a" * 64,
            chain="base",
            recipient="0xF0E0D361bBE899F3089f0a968506eF2B97693c01",
            amount=5.0
        )
        self.assertTrue(valid_base["verified"])
        self.assertEqual(valid_base["tier"], "BaseSwap Nitro VIP Sentinel")

        invalid_sol = verify_vip_license(
            tx_hash="0x" + "a" * 64,
            chain="solana",
            recipient="DW2MdHEq3qZ6nh9b5YFUoaPnBuuxC8Gz2785kwbbjSAM",
            amount=0.01 # Under 0.03
        )
        self.assertFalse(invalid_sol["verified"])

if __name__ == "__main__":
    unittest.main()