import unittest
from intentx_solver_radar import (
    calculate_symmio_cva_and_party_margin,
    calculate_solver_hedging_spread_and_funding_profit,
    calculate_liquidation_unwind_payout,
    verify_vip_license
)

class TestIntentXSolverRadar(unittest.TestCase):
    def test_symmio_cva_and_party_margin(self):
        # $10,000 notional, 10x leverage, CVA 0.5%, LF 0.3%, PartyB MM 2%
        res = calculate_symmio_cva_and_party_margin(
            notional_usd=10000.0,
            leverage=10.0,
            cva_pct=0.5,
            lf_pct=0.3,
            party_b_mm_pct=2.0
        )
        self.assertEqual(res["party_a_im_usd"], 1000.0)
        self.assertEqual(res["party_a_cva_usd"], 50.0)
        self.assertEqual(res["party_a_lf_usd"], 30.0)
        self.assertEqual(res["party_a_total_lock_usd"], 1080.0)
        self.assertEqual(res["party_b_mm_usd"], 200.0)
        self.assertEqual(res["party_b_total_lock_usd"], 250.0)
        self.assertEqual(res["total_locked_capital_usd"], 1330.0)
        self.assertEqual(res["liquidation_price_move_pct"], 8.0) # 800 / 10000 * 100 = 8%

    def test_solver_hedging_spread_and_funding_profit(self):
        # $10k notional, 6 bps spread, 2 bps CEX hedge cost -> 4 bps net spread ($4/trade)
        # 15 trades/day = $60/day spread
        # 18.25% funding APR on $10k notional = $5.00/day
        # Total daily = $65.00/day ($23,725/yr on $50k capital -> 47.45% ROI)
        res = calculate_solver_hedging_spread_and_funding_profit(
            notional_usd=10000.0,
            solver_spread_bps=6.0,
            daily_funding_rate_apr_pct=18.25,
            hedger_cex_cost_bps=2.0,
            trades_per_day=15,
            solver_allocated_capital_usd=50000.0
        )
        self.assertEqual(res["net_spread_bps"], 4.0)
        self.assertEqual(res["spread_profit_per_trade_usd"], 4.0)
        self.assertEqual(res["daily_spread_profit_usd"], 60.0)
        self.assertEqual(res["daily_funding_profit_usd"], 5.0)
        self.assertEqual(res["total_daily_solver_profit_usd"], 65.0)
        self.assertEqual(res["total_annual_solver_profit_usd"], 23725.0)
        self.assertEqual(res["solver_annual_roi_pct"], 47.45)

    def test_liquidation_unwind_payout_long(self):
        res = calculate_liquidation_unwind_payout(
            notional_usd=10000.0,
            entry_price=3000.0,
            mark_price=2760.0, # -8% drop
            position_side="long",
            party_a_cva_usd=50.0,
            party_a_lf_usd=30.0
        )
        self.assertEqual(res["price_pnl_pct"], -8.0)
        self.assertEqual(res["pnl_usd"], -800.0)
        self.assertEqual(res["solver_liquidation_bonus_usd"], 80.0)

    def test_liquidation_unwind_payout_short(self):
        res = calculate_liquidation_unwind_payout(
            notional_usd=10000.0,
            entry_price=3000.0,
            mark_price=3240.0, # +8% rise against short
            position_side="short",
            party_a_cva_usd=50.0,
            party_a_lf_usd=30.0
        )
        self.assertEqual(res["price_pnl_pct"], -8.0)
        self.assertEqual(res["pnl_usd"], -800.0)
        self.assertEqual(res["solver_liquidation_bonus_usd"], 80.0)

    def test_verify_vip_license(self):
        valid_base = verify_vip_license(
            tx_hash="0x" + "c" * 64,
            chain="base",
            recipient="0xF0E0D361bBE899F3089f0a968506eF2B97693c01",
            amount=5.0
        )
        self.assertTrue(valid_base["verified"])
        self.assertEqual(valid_base["tier"], "IntentX Solver VIP Sentinel")

        valid_sol = verify_vip_license(
            tx_hash="c" * 64,
            chain="solana",
            recipient="DW2MdHEq3qZ6nh9b5YFUoaPnBuuxC8Gz2785kwbbjSAM",
            amount=0.03
        )
        self.assertTrue(valid_sol["verified"])

if __name__ == "__main__":
    unittest.main()