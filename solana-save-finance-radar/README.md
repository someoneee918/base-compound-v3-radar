# Solana Save Finance (ex-Solend) Isolated Pool & Liquidation Radar

A high-precision mathematical simulation engine and commercial edge application designed for Solana's foundational lending market: Save Finance.

## Features
- **Account Health Factor & Drawdown Buffer:** Computes precise collateral thresholds, drawdown boundaries, and liquidation states.
- **Piecewise Utilization Kink Interest Curves:** Models 80% kink utilization and exponential rate surges up to 60% APR during liquidity crunches.
- **Flash Liquidator Seizure Economics:** Calculates 20% close factor repayments, 8.0% collateral seizure bonuses, and net profit margins after priority fees.
- **VIP Sentinel License:** Commercial non-custodial checkout for 5 Base USDC or 0.03 SOL.

## Verification
```bash
python3 test_save_finance_radar.py
```
