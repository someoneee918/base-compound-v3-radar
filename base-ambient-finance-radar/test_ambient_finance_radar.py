#!/usr/bin/env python3
import unittest
from ambient_finance_radar import (
    calculate_concentrated_vs_ambient_efficiency,
    calculate_knockout_limit_order_savings,
    calculate_single_contract_vault_gas_savings,
    evaluate_ambient_lp_strategy,
)

class TestAmbientFinanceRadar(unittest.TestCase):

    def test_concentrated_vs_ambient_efficiency(self):
        res = calculate_concentrated_vs_ambient_efficiency(
            current_price=3000.0,
            lower_tick_price=2700.0,
            upper_tick_price=3300.0,
            deposit_usd=10000.0,
            annual_volume_usd=100000000.0,
            fee_tier_pct=0.05
        )
        self.assertGreater(res["capital_efficiency_multiplier"], 5.0)
        self.assertGreater(res["concentrated_fee_yield_usd"], res["ambient_fee_yield_usd"])
        self.assertGreater(res["fee_boost_factor"], 5.0)

    def test_knockout_limit_order_savings(self):
        res = calculate_knockout_limit_order_savings(
            order_size_usd=25000.0,
            standard_taker_fee_pct=0.30,
            slippage_cost_pct=0.15,
            knockout_maker_fee_pct=0.0
        )
        self.assertEqual(res["total_market_cost_usd"], 112.50)
        self.assertEqual(res["knockout_fee_usd"], 0.0)
        self.assertEqual(res["net_savings_usd"], 112.50)
        self.assertEqual(res["savings_pct"], 100.0)

    def test_single_contract_vault_gas_savings(self):
        res = calculate_single_contract_vault_gas_savings(
            num_hops=3,
            standard_multicall_gas_units=185000,
            ambient_vault_gas_units=78000,
            base_l2_gas_price_gwei=0.05,
            eth_price_usd=3000.0
        )
        self.assertEqual(res["gas_units_saved"], 107000)
        self.assertAlmostEqual(res["gas_reduction_pct"], 57.84, places=1)
        self.assertGreater(res["usd_saved_per_swap"], 0.0)

    def test_evaluate_ambient_lp_strategy(self):
        volatile = evaluate_ambient_lp_strategy(price_volatility_pct=75.0, current_fee_apr=12.0, range_width_pct=60.0)
        self.assertEqual(volatile["recommendation"], "AMBIENT_FULL_RANGE")

        stable = evaluate_ambient_lp_strategy(price_volatility_pct=25.0, current_fee_apr=18.0, range_width_pct=15.0)
        self.assertEqual(stable["recommendation"], "CONCENTRATED_TIGHT_BAND")

    def test_invalid_parameters_raise(self):
        with self.assertRaises(ValueError):
            calculate_concentrated_vs_ambient_efficiency(lower_tick_price=3500.0, upper_tick_price=3000.0)
        with self.assertRaises(ValueError):
            calculate_knockout_limit_order_savings(order_size_usd=-500.0)
        with self.assertRaises(ValueError):
            calculate_single_contract_vault_gas_savings(standard_multicall_gas_units=50000, ambient_vault_gas_units=60000)

if __name__ == "__main__":
    unittest.main()
