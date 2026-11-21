# Solana Zeta Markets Perps & Options Cross-Margin Radar

A high-precision mathematical simulation engine and commercial edge application designed for Solana Zeta Markets (ZX).

## Features
- **Dynamic Initial & Maintenance Margin (IMR/MMR):** Models position scaling square-root margin expansions and real-time maintenance thresholds.
- **Account Liquidation Health & Distance:** Computes exact liquidation breach boundaries, 2.5% penalty seizures, and liquidator net rewards.
- **Passive Maker Rebate Engine:** Analyzes fee rebate yields (1.5 bps effective with ZX staking boost) producing passive daily cashflows.
- **VIP Sentinel License:** Commercial non-custodial checkout for 5 Base USDC or 0.03 SOL.

## Verification
```bash
python3 test_zeta_markets_radar.py
```
