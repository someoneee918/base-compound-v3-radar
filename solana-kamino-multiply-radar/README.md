# Solana Kamino Multiply Looping Leverage & Flash-Repay Sentinel Radar

Automated looping leverage calculation, LST-to-SOL depeg liquidation boundaries, and atomic flash-repay deleveraging economics for Kamino Multiply on Solana.

## Features
- **Looping Leverage APY Engine:** Computes net carry returns on looped LST collateral (e.g. JitoSOL 7.8% yield vs 4.2% SOL borrow cost at up to 5.5x leverage).
- **LST Depeg Liquidation Sentinel:** Calculates exact depeg drop boundaries ($P_{liq} = \frac{\text{Leverage}-1}{\text{Leverage} \cdot LTV_{liq}}$) and safety buffers.
- **Atomic Flash-Repay Simulator:** Models single-instruction deleveraging via Jupiter flash-swap to recover user equity and avoid 5% liquidation penalties.
- **Commercial VIP Sentinel:** Non-custodial 5 Base USDC or 0.03 SOL checkout for real-time WebSocket alerts and automated TypeScript keeper scripts.

## Receive Wallets
- **Solana (SOL / USDC):** `DW2MdHEq3qZ6nh9b5YFUoaPnBuuxC8Gz2785kwbbjSAM`
- **Base EVM (ETH / USDC):** `0xF0E0D361bBE899F3089f0a968506eF2B97693c01`
