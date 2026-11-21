import unittest
from whales_market_radar import (
    calculate_premarket_implied_fdv,
    calculate_seller_default_slashing_payout,
    calculate_otc_settlement_timeline,
    evaluate_whales_market_opportunity
)

class TestWhalesMarketRadar(unittest.TestCase):
    def test_premarket_implied_fdv_undervalued(self):
        # 1B supply, premarket price $0.35 -> Implied FDV = $350,000,000
        # Comparable benchmark FDV = $500,000,000
        # Basis = (350M - 500M) / 500M = -30.0%
        res = calculate_premarket_implied_fdv(
            premarket_price_usd=0.35,
            total_supply=1000000000.0,
            comparable_live_fdv_usd=500000000.0
        )
        self.assertEqual(res["implied_fdv_usd"], 350000000.0)
        self.assertEqual(res["fdv_basis_pct"], -30.0)
        self.assertEqual(res["recommendation"], "UNDERVALUED_BUY_DISCOUNT_ALLOCATION")

    def test_premarket_implied_fdv_overvalued(self):
        # Price $0.75 -> FDV = $750M vs $500M (+50.0% premium)
        res = calculate_premarket_implied_fdv(
            premarket_price_usd=0.75,
            total_supply=1000000000.0,
            comparable_live_fdv_usd=500000000.0
        )
        self.assertEqual(res["implied_fdv_usd"], 750000000.0)
        self.assertEqual(res["fdv_basis_pct"], 50.0)
        self.assertEqual(res["recommendation"], "OVERVALUED_HEDGE_SHORT_BASIS")

    def test_seller_default_slashing_payout(self):
        # Order size $5,000, 100% collateral ($5,000)
        # Protocol fee 2.5% = $125.00
        # Buyer receives: $5,000 principal + $4,875 seller collateral = $9,875.00
        # Net windfall profit = $4,875.00 (97.5% ROI)
        res = calculate_seller_default_slashing_payout(
            order_size_usd=5000.0,
            seller_collateral_ratio_pct=100.0,
            protocol_fee_pct=2.5
        )
        self.assertEqual(res["seller_collateral_usd"], 5000.0)
        self.assertEqual(res["protocol_cut_usd"], 125.0)
        self.assertEqual(res["buyer_slashed_collateral_received"], 4875.0)
        self.assertEqual(res["total_buyer_payout_usd"], 9875.0)
        self.assertEqual(res["net_windfall_profit_usd"], 4875.0)
        self.assertEqual(res["windfall_roi_pct"], 97.5)

    def test_otc_settlement_timeline_defaulted(self):
        # TGE at t=10000, current at t=10000 + (25 * 3600) -> 25 hours elapsed (> 24h)
        res = calculate_otc_settlement_timeline(
            tge_timestamp=10000.0,
            current_timestamp=10000.0 + (25.0 * 3600.0)
        )
        self.assertEqual(res["hours_elapsed"], 25.0)
        self.assertEqual(res["hours_remaining"], 0.0)
        self.assertTrue(res["is_defaulted"])
        self.assertEqual(res["status"], "DEFAULT_SLASH_CLAIMABLE")

    def test_evaluate_whales_market_opportunity(self):
        res = evaluate_whales_market_opportunity(
            premarket_price=0.35,
            order_size_usd=5000.0,
            tge_time=10000.0,
            current_time=10000.0 + (10.0 * 3600.0)
        )
        self.assertEqual(res["tier"], "PRIME_OTC_DISCOUNT_ACCUMULATION")

if __name__ == "__main__":
    unittest.main()
