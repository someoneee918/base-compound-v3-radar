# Base Curvance Modular Money Market Radar

A high-precision mathematical simulation engine and commercial edge application designed for Base Curvance modular money market vaults.

## Features
- **Yield-Bearing Collateral Looping:** Models net carry yields (18.50% net APY at 3.0x leverage) on yield-bearing LSTs, LRTs, and LP tokens.
- **Dutch Auction Liquidation Decay:** Simulates descending Dutch auctions (10% decaying to 2% over 1,800 seconds) with optimal liquidator entry modeling.
- **Account Safety Buffer & Contagion Containment:** Computes precise health factors and max drawdown tolerances under isolated risk boundaries.
- **VIP Sentinel License:** Commercial non-custodial checkout for 5 Base USDC or 0.03 SOL.

## Verification
```bash
python3 test_curvance_market_radar.py
```
