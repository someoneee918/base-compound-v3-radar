import unittest
from superform_vault_radar import (
    calculate_cross_chain_vault_net_yield,
    calculate_multicall_batching_efficiency,
    calculate_superposition_secondary_basis_arbitrage,
    verify_vip_license,
    BASE_USDC_RECEIVE_ADDRESS,
    SOLANA_RECEIVE_ADDRESS
)

class TestSuperformVaultRadar(unittest.TestCase):
    def test_cross_chain_vault_net_yield_positive(self):
        # $10,000 deposit, 12% APY, $1.20 relayer, $0.003 gas, 90 days, 10 bps fee ($10)
        res = calculate_cross_chain_vault_net_yield(
            deposit_amount_usd=10000.0,
            gross_apy_pct=12.0,
            relayer_fee_usd=1.20,
            base_gas_usd=0.003,
            holding_period_days=90.0,
            superform_fee_bps=10.0
        )
        self.assertEqual(res["deposit_amount_usd"], 10000.0)
        self.assertEqual(res["gross_apy_pct"], 12.0)
        self.assertAlmostEqual(res["gross_yield_usd"], 295.8904, delta=0.01)
        self.assertAlmostEqual(res["total_fees_usd"], 11.203, delta=0.01)
        self.assertAlmostEqual(res["net_yield_usd"], 284.6874, delta=0.01)
        self.assertAlmostEqual(res["net_apy_pct"], 11.5456, delta=0.05)
        self.assertAlmostEqual(res["breakeven_days"], 3.41, delta=0.05)

    def test_cross_chain_vault_net_yield_short_horizon_drag(self):
        # Very short holding period (1 day) with high relayer fee ($5.00) causes negative net yield
        res = calculate_cross_chain_vault_net_yield(
            deposit_amount_usd=1000.0,
            gross_apy_pct=8.0,
            relayer_fee_usd=5.00,
            base_gas_usd=0.005,
            holding_period_days=1.0,
            superform_fee_bps=10.0
        )
        # Daily gross = 1000 * 0.08 / 365 = $0.219
        # Total fee = 5.00 + 0.005 + 1.00 = $6.005
        # Net yield < 0
        self.assertLess(res["net_yield_usd"], 0)
        self.assertLess(res["net_apy_pct"], 0)
        self.assertGreater(res["breakeven_days"], 25.0)

    def test_multicall_batching_efficiency(self):
        # 5 vaults: unbatched = 5 * 0.0045 = $0.0225, batched = 0.0020 + 5*0.0015 = $0.0095
        res = calculate_multicall_batching_efficiency(
            num_vault_deposits=5,
            single_tx_gas_usd=0.0045,
            batch_base_gas_usd=0.0020,
            per_vault_batch_gas_usd=0.0015
        )
        self.assertEqual(res["num_vault_deposits"], 5)
        self.assertAlmostEqual(res["unbatched_total_gas_usd"], 0.0225, delta=0.0001)
        self.assertAlmostEqual(res["batched_total_gas_usd"], 0.0095, delta=0.0001)
        self.assertAlmostEqual(res["gas_saved_usd"], 0.0130, delta=0.0001)
        self.assertAlmostEqual(res["savings_percentage"], 57.78, delta=0.05)

    def test_superposition_secondary_basis_arbitrage(self):
        # $10,000 face value, 25 bps discount, $0.0035 gas, 1 hr redemption
        res = calculate_superposition_secondary_basis_arbitrage(
            face_value_usd=10000.0,
            secondary_discount_bps=25.0,
            redemption_gas_usd=0.0035,
            settlement_hours=1.0
        )
        self.assertEqual(res["buy_price_usd"], 9975.0)
        self.assertEqual(res["gross_discount_profit_usd"], 25.0)
        self.assertAlmostEqual(res["net_arbitrage_profit_usd"], 24.9965, delta=0.0001)
        self.assertGreater(res["annualized_irr_pct"], 2000.0)

    def test_verify_vip_license(self):
        # Base valid
        base_valid = verify_vip_license("0xabc1234567890def", "base", 5.0, BASE_USDC_RECEIVE_ADDRESS)
        self.assertTrue(base_valid["valid"])
        self.assertEqual(base_valid["granted_chain"], "base")

        # Base insufficient amount
        base_invalid = verify_vip_license("0xabc1234567890def", "base", 4.9, BASE_USDC_RECEIVE_ADDRESS)
        self.assertFalse(base_invalid["valid"])

        # Solana valid
        sol_valid = verify_vip_license("5wG1234567890solana", "solana", 0.03, SOLANA_RECEIVE_ADDRESS)
        self.assertTrue(sol_valid["valid"])

        # Invalid chain
        inv_chain = verify_vip_license("0xabc1234567890def", "polygon", 10.0, BASE_USDC_RECEIVE_ADDRESS)
        self.assertFalse(inv_chain["valid"])

if __name__ == "__main__":
    unittest.main()
