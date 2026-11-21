import unittest
from citrus_lending_radar import (
    calculate_p2p_loan_yield,
    calculate_default_foreclosure_arbitrage,
    calculate_collection_drawdown_safety,
    verify_vip_license,
    BASE_USDC_RECEIVE_ADDRESS,
    SOLANA_RECEIVE_ADDRESS
)

class TestCitrusLendingRadar(unittest.TestCase):
    def test_p2p_loan_yield(self):
        # 50 SOL principal, 32.0% APR, 14 days duration, 1.5% protocol fee
        # gross = 50 * 0.32 * (14/365) = 0.613699 SOL
        # protocol fee = 0.613699 * 0.015 = 0.009205 SOL
        # net = 0.604493 SOL -> net APR = 31.52%
        res = calculate_p2p_loan_yield(
            principal_sol=50.0,
            apr_pct=32.0,
            duration_days=14,
            protocol_fee_cut_pct=1.5
        )
        self.assertEqual(res["principal_sol"], 50.0)
        self.assertAlmostEqual(res["gross_interest_sol"], 0.613699, delta=0.0001)
        self.assertAlmostEqual(res["protocol_fee_sol"], 0.009205, delta=0.0001)
        self.assertAlmostEqual(res["net_interest_sol"], 0.604493, delta=0.0001)
        self.assertAlmostEqual(res["net_realized_apr_pct"], 31.52, delta=0.05)

    def test_default_foreclosure_arbitrage(self):
        # 60 SOL loan principal, 100 SOL floor price, 2% marketplace fee
        # net proceeds = 98.0 SOL -> profit = 38.0 SOL (+63.33% ROI)
        res = calculate_default_foreclosure_arbitrage(
            loan_principal_sol=60.0,
            collection_floor_sol=100.0,
            marketplace_fee_pct=2.0
        )
        self.assertEqual(res["loan_principal_sol"], 60.0)
        self.assertEqual(res["collection_floor_sol"], 100.0)
        self.assertEqual(res["net_liquidation_proceeds_sol"], 98.0)
        self.assertEqual(res["foreclosure_profit_sol"], 38.0)
        self.assertAlmostEqual(res["foreclosure_roi_pct"], 63.33, delta=0.05)

    def test_collection_drawdown_safety_healthy(self):
        # 100 SOL floor, 60 SOL loan principal -> 40 SOL buffer (40% buffer)
        res = calculate_collection_drawdown_safety(
            current_floor_sol=100.0,
            loan_principal_sol=60.0
        )
        self.assertFalse(res["is_underwater"])
        self.assertEqual(res["buffer_sol"], 40.0)
        self.assertEqual(res["buffer_pct"], 40.0)

    def test_collection_drawdown_safety_underwater(self):
        # Floor crashed to 55 SOL, below 60 SOL loan principal
        res = calculate_collection_drawdown_safety(
            current_floor_sol=55.0,
            loan_principal_sol=60.0
        )
        self.assertTrue(res["is_underwater"])
        self.assertEqual(res["buffer_sol"], 0.0)

    def test_verify_vip_license(self):
        # Base valid
        b_res = verify_vip_license("0xcitrustx12345678", "base", 5.0, BASE_USDC_RECEIVE_ADDRESS)
        self.assertTrue(b_res["valid"])
        self.assertEqual(b_res["granted_chain"], "base")

        # Solana valid
        s_res = verify_vip_license("solcitrustx1234567", "solana", 0.03, SOLANA_RECEIVE_ADDRESS)
        self.assertTrue(s_res["valid"])
        self.assertEqual(s_res["granted_chain"], "solana")

        # Underfunded SOL
        bad_sol = verify_vip_license("solcitrustx1234567", "solana", 0.015, SOLANA_RECEIVE_ADDRESS)
        self.assertFalse(bad_sol["valid"])

if __name__ == "__main__":
    unittest.main()
