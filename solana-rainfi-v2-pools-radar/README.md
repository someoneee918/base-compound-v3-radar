# Solana RainFi v2 Collection Liquidity Pools & Automated Loan Refinancing Radar

Automated quantitative analytics and yield management engine for RainFi v2 collection lending pools, peer-to-peer loan refinancing, and default auction liquidations on Solana.

## Key Capabilities
- **Automated Collection Pools:** Calculates real utilization rates ($U = \text{borrowed} / \text{deposited}$), net lender APR after 10% protocol fee cut, and weekly compounding APY ($19.7\%\text{ APY}$ at $80\%\text{ util}$).
- **Refinancing Arbitrage:** Evaluates interest rate savings from refinancing older high-APR loans into fresh competitive collection pool offers while tracking LTV buffers against liquidation thresholds.
- **Foreclosure Auction Recovery:** Simulates default settlement auctions with 5% liquidator bonuses, lender debt recovery, and borrower equity preservation.
- **VIP Real-Yield License:** Verifies 5 Base USDC or 0.03 SOL on-chain payment for automated webhook alerts.
