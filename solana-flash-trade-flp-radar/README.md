# Solana Flash Trade Multi-Asset FLP Liquidity Radar

A high-precision mathematical simulation engine and commercial edge application designed for Solana's premier peer-to-pool perps DEX: Flash Trade.

## Features
- **Dynamic Entry/Exit Fees:** Models target asset weight deviations with rebalancing fee discounts (down to 5.0 bps) and overweight penalties.
- **FLP Real Staking APR:** Calculates 70% trading fee protocol revenue distribution to FLP token holders.
- **Hourly Trader Borrow Interest:** Computes utilization-based continuous funding and borrow fees.
- **VIP Sentinel License:** Commercial non-custodial checkout for 5 Base USDC or 0.03 SOL.

## Verification
```bash
python3 test_flash_trade_flp_radar.py
```
