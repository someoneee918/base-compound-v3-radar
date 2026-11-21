"""
Unit tests for Base BasePaint ($BRUSH) Canvas Mint Royalty & Liquidity Radar.
"""

import unittest
from basepaint_canvas_radar import (
    calculate_artist_canvas_royalty,
    calculate_brush_deflation_velocity,
    calculate_secondary_edition_arbitrage,
    verify_vip_license
)

class TestBasePaintCanvasRadar(unittest.TestCase):
    def test_artist_royalty_calculation(self):
        # 500 pixels painted out of 25,000 (2% share), 1200 mints @ 0.0026 ETH ($7.80 @ $3000 ETH), $0.05 brush cost
        res = calculate_artist_canvas_royalty(
            pixels_painted=500,
            total_canvas_pixels=25000,
            total_mints=1200,
            mint_price_eth=0.0026,
            eth_price_usd=3000.0,
            brush_cost_usd_per_pixel=0.05
        )
        self.assertTrue(res["is_profitable"])
        self.assertEqual(res["artist_pixel_share_pct"], 2.0)
        self.assertEqual(res["gross_mint_eth"], 3.12)
        self.assertEqual(res["artist_pool_eth"], 2.808)
        self.assertEqual(res["artist_payout_eth"], 0.05616)
        self.assertEqual(res["artist_payout_usd"], 168.48)
        self.assertEqual(res["artist_input_cost_usd"], 25.0)
        self.assertEqual(res["net_artist_profit_usd"], 143.48)
        self.assertEqual(res["roi_pct"], 573.92)

    def test_brush_deflation_velocity(self):
        # 50k canvas pixels/day + 5k secondary burn, 100M supply
        res = calculate_brush_deflation_velocity(
            daily_canvas_pixels=50000,
            brush_circulating_supply=100000000.0,
            daily_secondary_burn=5000.0
        )
        self.assertEqual(res["total_daily_burned"], 55000)
        self.assertEqual(res["annual_burn_runrate"], 20075000.0)
        self.assertEqual(res["burn_rate_annual_pct"], 20.08)

    def test_secondary_arbitrage(self):
        # Mint @ 0.0026 ETH, secondary floor @ 0.0040 ETH, 0.5% marketplace + 5.0% royalty
        res = calculate_secondary_edition_arbitrage(
            mint_price_eth=0.0026,
            secondary_floor_eth=0.0040,
            marketplace_fee_pct=0.5,
            creator_royalty_pct=5.0,
            eth_price_usd=3000.0
        )
        self.assertTrue(res["is_profitable_arbitrage"])
        self.assertEqual(res["net_seller_proceeds_eth"], 0.0038)
        self.assertEqual(res["net_profit_eth"], 0.0012)
        self.assertEqual(res["net_profit_usd"], 3.54)
        self.assertAlmostEqual(res["arbitrage_roi_pct"], 45.38, delta=0.5)

    def test_artist_royalty_zero_cost(self):
        # Edge case: zero brush cost (free brushes or airdrop)
        res = calculate_artist_canvas_royalty(
            pixels_painted=100,
            total_canvas_pixels=10000,
            total_mints=500,
            mint_price_eth=0.002,
            eth_price_usd=3000.0,
            brush_cost_usd_per_pixel=0.0
        )
        self.assertTrue(res["is_profitable"])
        self.assertEqual(res["artist_input_cost_usd"], 0.0)
        self.assertEqual(res["net_artist_profit_usd"], 27.0)

    def test_vip_license_verification(self):
        base_valid = verify_vip_license(
            tx_hash="0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef12345678901234",
            chain="Base",
            recipient="0xF0E0D361bBE899F3089f0a968506eF2B97693c01",
            amount=5.0
        )
        self.assertTrue(base_valid["verified"])

        sol_valid = verify_vip_license(
            tx_hash="5xabcdef1234567890abcdef1234567890abcdef1234567890abcdef12345678901234",
            chain="Solana",
            recipient="DW2MdHEq3qZ6nh9b5YFUoaPnBuuxC8Gz2785kwbbjSAM",
            amount=0.03
        )
        self.assertTrue(sol_valid["verified"])

        invalid = verify_vip_license(
            tx_hash="short",
            chain="Base",
            recipient="0x0000000000000000000000000000000000000000",
            amount=2.0
        )
        self.assertFalse(invalid["verified"])

if __name__ == "__main__":
    unittest.main()
