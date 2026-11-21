# Base Synthetix v3 Perps Liquidity & Spot Synth Arbitrage Radar

Automated atomic spot synth price parity arbitrage, dynamic skew fee spread calculation, and Core LP Vault USDC collateral staking returns for Synthetix v3 on Base.

## Features
- **Spot Synth Atomic Arbitrage Engine:** Computes net atomic arbitrage between Synthetix v3 Spot synths (sUSDC, sETH, sBTC) and external DEXes (Aerodrome/Uniswap v3) factoring dynamic skew fees ($f_{skew} = \text{skew}/\text{scale}$) and Base L2 gas ($0.35).
- **Core LP Vault Staking Yields:** Models USDC collateral delegation to the Synthetix Core pool capturing 30.66% APY from perpetual trading volume fees and liquidation bounties.
- **Vault C-Ratio Health Sentinel:** Monitors real-time collateralization ratio against the 125% liquidation threshold and computes recapitalization cushions.
- **Commercial VIP Sentinel:** Non-custodial 5 Base USDC or 0.03 SOL checkout for real-time WebSocket alerts and automated TypeScript keeper scripts.

## Receive Wallets
- **Base EVM (ETH / USDC):** `0xF0E0D361bBE899F3089f0a968506eF2B97693c01`
- **Solana (SOL / USDC):** `DW2MdHEq3qZ6nh9b5YFUoaPnBuuxC8Gz2785kwbbjSAM`
