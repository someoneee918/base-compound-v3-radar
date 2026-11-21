# Base Derive (ex-Lyra v2) Sub-Account Portfolio Margin & Variance Risk Premium (VRP) Options Radar

Automated quantitative analytics and volatility harvesting engine for Derive options on Base L2, sub-account portfolio cross-margin offset requirements, Variance Risk Premium (VRP) delta-hedged yields, and expiry settlement payoffs.

## Key Capabilities
- **Options Payoff & Settlement Engine:** Evaluates intrinsic value, net settlement PnL, and ROI across Long/Short Calls and Puts on Base L2.
- **Variance Risk Premium (VRP) Harvesting:** Models theta decay capture from selling elevated Implied Volatility (IV) against lower Realized Volatility (RV) with dynamic delta-hedging transaction costs ($29.48\%\text{ annualized APR}$ at 14 days to expiry).
- **Sub-Account Portfolio Cross-Margin:** Calculates gross notional vs hedged pair margin offsets (40% discount for covered perps/calls), capital utilization buffers, and liquidation prevention.
- **VIP Real-Yield License:** Verifies 5 Base USDC or 0.03 SOL on-chain payment for automated webhook alerts.
