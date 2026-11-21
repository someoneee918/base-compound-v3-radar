# Base Liquity v2 (BOLD) User-Set Interest Rate Trove & Redemption Queue Radar

Quantitative simulation and risk management engine for Liquity v2 (BOLD) decentralized borrow positions, user-set interest rate redemption queue priorities, Stability Pool fee accrual, and secondary DEX peg arbitrage on Base.

## Key Capabilities
- **User-Set Interest Rate & Redemption Protection:** Models redemption queue sorting where higher interest rates shield Troves from early redemption during BOLD peg discounts.
- **Stability Pool Real-Yield Accrual:** Calculates yield composed of direct borrower interest disbursements and liquidation bonuses (3.75% net APR on BOLD deposits).
- **Secondary DEX Peg Arbitrage:** Evaluates atomic redemption profits acquiring discounted BOLD on DEXs and redeeming 1:1 against lowest-rate Troves (+1.52% net ROI on 150 bps discount).
- **VIP Commercial License:** Integrated on-chain license verification for 5 Base USDC or 0.03 SOL.
