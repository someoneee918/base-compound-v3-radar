# Base Overnight.fi USD+ Daily Rebase & Peg Arbitrage Radar

A high-precision mathematical simulation engine and commercial edge application designed for Base Overnight.fi USD+ and ETS strategies.

## Features
- **Daily Rebase Yield Compounding:** Models net rebasing cashflow ($2.69/day on $10k deposit at 10.35% net APY).
- **Secondary DEX Peg Redemption Arbitrage:** Analyzes on-chain 1:1 redemption arbitrage when USD+ trades at a discount ($46.19 net profit per $10k flash trade at $0.9950).
- **Delta-Neutral ETS Carry:** Models short hedge funding rate cashflow combined with DEX LP yields (25.0% net APR).
- **VIP Sentinel License:** Commercial non-custodial checkout for 5 Base USDC or 0.03 SOL.

## Verification
```bash
python3 test_overnight_usd_plus_radar.py
```
