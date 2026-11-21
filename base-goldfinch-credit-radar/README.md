# Base Goldfinch / Finterest RWA Private Credit Junior & Senior Tranche Waterfall Radar

Quantitative simulation and risk management engine for Goldfinch Protocol RWA borrower pools, first-loss Junior tranche risk-reallocation premiums, Senior tranche capital protection, and secondary loan token discounts on Base.

## Key Capabilities
- **Tranche Waterfall Yields:** Calculates cashflow distributions and risk-reallocated yields between Senior tranches (8.64% net APY) and first-loss Junior Backer tranches (19.44% net APY with +10.80% risk premium boost).
- **Default Loss Waterfall & Buffer Stress-Testing:** Simulates loss absorption scenarios where Junior capital absorbs 100% of defaults up to its $200k buffer, insulating Senior lenders.
- **Secondary Loan Token Discount Arbitrage:** Models early-exit liquidity discounts (150 bps) for boosted annualized yields (13.20% on 6-month hold).
- **VIP Commercial License:** Integrated on-chain license verification for 5 Base USDC or 0.03 SOL.
