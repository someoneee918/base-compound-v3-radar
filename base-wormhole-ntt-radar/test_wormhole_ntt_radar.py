import unittest
from wormhole_ntt_radar import (
    calculate_wormhole_ntt_relayer_delivery_profit,
    calculate_ntt_rate_limit_capacity_and_backlog,
    calculate_ntt_cross_chain_basis_arbitrage,
    verify_vip_license
)

class TestWormholeNttRadar(unittest.TestCase):
    def test_wormhole_ntt_relayer_delivery_profit(self):
        # $1,000 transfer, $1.50 fee, 120,000 gas, 0.005 gwei, $3000 ETH, 50 transfers/day
        # Gas cost = 120000 * 5e-12 * 3000 = $0.0018
        # Net profit per tx = 1.50 - 0.0018 = $1.4982 (99.88% margin)
        # Daily profit = 1.4982 * 50 = $74.91
        res = calculate_wormhole_ntt_relayer_delivery_profit(
            transfer_amount_usd=1000.0,
            relayer_fee_usd=1.50,
            base_execution_gas=120000,
            base_gas_fee_gwei=0.005,
            eth_price_usd=3000.0,
            transfers_per_day=50
        )
        self.assertEqual(res["base_gas_cost_usd"], 0.0018)
        self.assertEqual(res["net_profit_per_tx_usd"], 1.4982)
        self.assertEqual(res["daily_profit_usd"], 74.91)
        self.assertGreater(res["relayer_margin_pct"], 99.8)

    def test_ntt_rate_limit_within_capacity(self):
        # 100,000 capacity, 40,000 used (60,000 available), pending 10,000 transfer
        res = calculate_ntt_rate_limit_capacity_and_backlog(
            total_24h_capacity_tokens=100000.0,
            current_used_tokens=40000.0,
            rolling_refill_rate_per_sec=1.1574, # 100k / 86400s
            pending_transfer_tokens=10000.0
        )
        self.assertEqual(res["available_capacity_tokens"], 60000.0)
        self.assertFalse(res["exceeds_rate_limit"])
        self.assertEqual(res["delay_seconds"], 0.0)

    def test_ntt_rate_limit_exceeded_backlog(self):
        # 100,000 capacity, 90,000 used (10,000 available), pending 20,000 transfer
        # Deficit = 10,000 tokens. Refill rate = 2 tokens/sec -> delay = 5,000 seconds
        res = calculate_ntt_rate_limit_capacity_and_backlog(
            total_24h_capacity_tokens=100000.0,
            current_used_tokens=90000.0,
            rolling_refill_rate_per_sec=2.0,
            pending_transfer_tokens=20000.0
        )
        self.assertTrue(res["exceeds_rate_limit"])
        self.assertEqual(res["deficit_tokens"], 10000.0)
        self.assertEqual(res["delay_seconds"], 5000.0)

    def test_ntt_cross_chain_basis_arbitrage(self):
        # Source price = $1.00, Base price = $1.02 (+2% spread)
        # 5,000 tokens -> Gross = $100. Bridge fees = $2.50 -> Net = $97.50 (+1.95% ROI)
        res = calculate_ntt_cross_chain_basis_arbitrage(
            token_price_source_usd=1.00,
            token_price_base_usd=1.02,
            transfer_size_tokens=5000.0,
            total_bridge_fees_usd=2.50
        )
        self.assertTrue(res["is_arbitrage_viable"])
        self.assertEqual(res["price_spread_pct"], 2.0)
        self.assertEqual(res["gross_arbitrage_profit_usd"], 100.0)
        self.assertEqual(res["net_arbitrage_profit_usd"], 97.50)
        self.assertEqual(res["net_roi_pct"], 1.95)

    def test_verify_vip_license(self):
        valid_base = verify_vip_license(
            tx_hash="0x" + "5" * 64,
            chain="base",
            recipient="0xF0E0D361bBE899F3089f0a968506eF2B97693c01",
            amount=5.0
        )
        self.assertTrue(valid_base["verified"])
        self.assertEqual(valid_base["tier"], "Wormhole NTT VIP Sentinel")

        valid_sol = verify_vip_license(
            tx_hash="5" * 64,
            chain="solana",
            recipient="DW2MdHEq3qZ6nh9b5YFUoaPnBuuxC8Gz2785kwbbjSAM",
            amount=0.03
        )
        self.assertTrue(valid_sol["verified"])

if __name__ == "__main__":
    unittest.main()