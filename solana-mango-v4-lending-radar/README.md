# Solana Mango Markets v4 Multi-Token Lending Utilization & Liquidation Sentinel Radar

Automated piecewise kinked borrow rate modeling, high-yield lender deposit APY, cross-margin maintenance health buffers, and 5% liquidation bonus capture for Mango Markets v4 on Solana.

## Features
- **Piecewise Kinked Interest Rate Engine:** Simulates 80% optimal utilization threshold where borrow rates surge from 8% up to 48% APR, unlocking 26.50% deposit APY for lenders.
- **Cross-Margin Maintenance Health Factor Sentinel:** Models 0.90 asset weight collateral maintenance buffers and exact tolerable price drops before liquidation.
- **Liquidator 5% Bonus Profitability:** Evaluates net atomic liquidation execution bounties factoring Solana compute unit priority fees.
- **Commercial VIP Sentinel:** Non-custodial 5 Base USDC or 0.03 SOL checkout for real-time WebSocket alerts and automated TypeScript keeper scripts.

## Receive Wallets
- **Solana (SOL / USDC):** `DW2MdHEq3qZ6nh9b5YFUoaPnBuuxC8Gz2785kwbbjSAM`
- **Base EVM (ETH / USDC):** `0xF0E0D361bBE899F3089f0a968506eF2B97693c01`
