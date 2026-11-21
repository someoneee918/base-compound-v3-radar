# Solana Lifinity Protocol Concentrated AMM Radar

A high-precision mathematical simulation engine and commercial edge application designed for Solana Lifinity Proactive Market Maker (PMM) pools.

## Features
- **Pyth Oracle-Guided Liquidity Curves:** Models proactive bid-ask curve re-centering that eliminates toxic arbitrageur frontrunning.
- **Dynamic Spread Anti-LVR Defense:** Calculates spread expansion (volatility markup + inventory skew) protecting liquidity providers from adverse selection.
- **True Net LP Yield Accounting:** Quantifies trading fee revenue combined with annualized Loss-Versus-Rebalancing (LVR) savings alpha.
- **VIP Sentinel License:** Commercial non-custodial checkout for 5 Base USDC or 0.03 SOL.

## Verification
```bash
python3 test_lifinity_amm_radar.py
```
