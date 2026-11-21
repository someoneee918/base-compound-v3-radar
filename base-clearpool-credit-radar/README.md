# Base Clearpool Institutional Uncollateralized Credit & Prime Borrowing Radar

Automated quantitative analytics and risk management engine for Clearpool single-borrower uncollateralized lending pools, piecewise utilization kink curves, cpToken yield accrual, and CPOOL insurance coverage on Base.

## Key Capabilities
- **Dynamic Piecewise Kink Rate Curve:** Models institutional borrow APR and lender supply APR across pre-kink (10% slope) and post-kink surge (60% slope at >80% utilization) regimes.
- **Risk-Adjusted Return & SOFR Credit Spread:** Evaluates net yield deducting uncollateralized default loss probabilities while adding CPOOL reward subsidies (+2,020 bps spread over 4.5% SOFR).
- **CPOOL Insurance Pool Buffer Adequacy:** Monitors 5% required reserve coverage to protect lender principal against borrower default events.
- **VIP Commercial License:** Integrated on-chain license verification for 5 Base USDC or 0.03 SOL.
