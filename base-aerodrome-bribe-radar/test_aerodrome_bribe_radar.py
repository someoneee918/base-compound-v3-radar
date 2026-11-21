import unittest
from aerodrome_bribe_radar import (
    calculate_voter_bribe_apr,
    calculate_protocol_emission_multiplier,
    evaluate_gauge_opportunity
)

class TestAerodromeBribeRadar(unittest.TestCase):
    def test_voter_bribe_apr(self):
        # 10,000 veAERO votes in gauge with 200,000 total votes (5% share)
        # Gauge bribes = $5,000 USD
        # Weekly payout = 5000 * 0.05 = $250.00
        # Annual payout = 250 * 52 = $13,000.00
        # AERO price = $1.20 -> veAERO value = 10,000 * 1.20 = $12,000.00
        # Voter APR = (13,000 / 12,000) * 100 = 108.33%
        res = calculate_voter_bribe_apr(
            ve_aero_votes=10000.0,
            gauge_total_votes=200000.0,
            total_bribes_usd=5000.0,
            aero_price_usd=1.20
        )
        self.assertEqual(res["vote_share_pct"], 5.0)
        self.assertEqual(res["user_weekly_bribe_usd"], 250.0)
        self.assertEqual(res["user_annual_bribe_usd"], 13000.0)
        self.assertEqual(res["voter_apr_pct"], 108.33)
        self.assertEqual(res["bribe_per_1k_votes_usd"], 25.0)

    def test_protocol_emission_multiplier(self):
        # Protocol deposits $5,000 bribe, attracting 2,000,000 votes
        # Epoch total votes = 100,000,000 (2.0% share)
        # Weekly emissions = 10,000,000 AERO -> directed = 200,000 AERO
        # Emission value at $1.20 = $240,000.00
        # Multiplier = 240,000 / 5,000 = 48.0x
        res = calculate_protocol_emission_multiplier(
            bribe_amount_usd=5000.0,
            votes_attracted=2000000.0,
            epoch_total_votes=100000000.0,
            weekly_aero_emissions=10000000.0,
            aero_price_usd=1.20
        )
        self.assertEqual(res["gauge_vote_share_pct"], 2.0)
        self.assertEqual(res["aero_emissions_directed"], 200000.0)
        self.assertEqual(res["emission_value_usd"], 240000.0)
        self.assertEqual(res["multiplier"], 48.0)
        self.assertEqual(res["net_subsidy_profit_usd"], 235000.0)

    def test_realistic_multiplier(self):
        # Realistic protocol: $50,000 bribe attracts 1,000,000 votes (1% of emissions = 100,000 AERO = $120,000)
        # Multiplier = 120,000 / 50,000 = 2.4x
        res = calculate_protocol_emission_multiplier(
            bribe_amount_usd=50000.0,
            votes_attracted=1000000.0,
            epoch_total_votes=100000000.0,
            weekly_aero_emissions=10000000.0,
            aero_price_usd=1.20
        )
        self.assertEqual(res["multiplier"], 2.4)
        self.assertEqual(res["net_subsidy_profit_usd"], 70000.0)

    def test_evaluate_gauge_opportunity(self):
        res = evaluate_gauge_opportunity(voter_apr_pct=108.33, emission_multiplier=2.4)
        self.assertEqual(res["tier"], "HYPER_EFFICIENT_BRIBE_OPPORTUNITY")

    def test_zero_votes_handling(self):
        res = calculate_voter_bribe_apr(
            ve_aero_votes=0.0,
            gauge_total_votes=200000.0,
            total_bribes_usd=5000.0,
            aero_price_usd=1.20
        )
        self.assertEqual(res["voter_apr_pct"], 0.0)
        self.assertEqual(res["user_weekly_bribe_usd"], 0.0)

if __name__ == "__main__":
    unittest.main()
