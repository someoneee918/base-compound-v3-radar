# Base Aave v3 E-Mode Correlated Leverage & Ultra-Tight Liquidation Radar

High-precision modeling of Aave v3 Category 1 (ETH Correlated) 93% LTV looping leverage net APY, cbETH/wstETH depeg liquidation thresholds, and 1.0% ultra-tight liquidator economics on Base.

## Features
- **E-Mode Correlated Looping Engine:** Simulates up to 14x leverage looping yields on ETH-correlated assets (e.g. cbETH 3.6% yield vs 2.1% borrow rate generating 17.10% net APY).
- **LST Depeg Liquidation Sentinel:** Models exact depeg ratios ($\text{Price}_{liq} = \frac{\text{Lev}-1}{\text{Lev} \cdot 0.95}$) and safety buffers.
- **Ultra-Tight Liquidator Profitability:** Calculates net execution profit on Aave v3's 1.0% E-Mode liquidation incentive factoring Base L2 gas costs ($0.35) and DEX slippage.
- **Commercial VIP Sentinel:** Non-custodial 5 Base USDC or 0.03 SOL checkout for real-time WebSocket alerts and automated TypeScript keeper scripts.

## Receive Wallets
- **Base EVM (ETH / USDC):** `0xF0E0D361bBE899F3089f0a968506eF2B97693c01`
- **Solana (SOL / USDC):** `DW2MdHEq3qZ6nh9b5YFUoaPnBuuxC8Gz2785kwbbjSAM`
