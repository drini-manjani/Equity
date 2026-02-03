<div style="text-align:right;">
  <img class="eif-logo" src="European_Investment_Fund_logo.svg" alt="EIF Logo" />
</div>

# Equity Cashflow Projections: Sentral


## Summary

- We project fund-level drawdowns, repayments, recallables, and NAV forward from a chosen cutoff quarter.
- The model is driven by historical fund behavior (by strategy, grade, and age) and a market factor (MSCI).
- Outputs are averaged across Monte Carlo simulations to provide a stable expected path and risk bands.

## How the Projections Work

1) **Start from history**
   - We load all historical fund cashflows (draws, repayments, NAV) and fund attributes.
   - We define a cutoff quarter (e.g., 2025-09-30). History ends there; projections start immediately after.

2) **Simulate fund cashflows quarter by quarter**
   - **Drawdowns** follow historical draw patterns by strategy/grade/age.
   - **Repayments** occur with a historical probability and size relative to NAV.
   - **Recallables** occur only after repayments and are capped by legal and economic limits.

3) **NAV updates**
   - NAV evolves each quarter based on net cashflows and a market-sensitive growth rate (omega).
   - Omega is calibrated from history and linked to MSCI returns.

4) **Repeat many times (Monte Carlo)**
   - Each simulation draws random events and sizes consistent with history.
   - We average across simulations to get the expected portfolio path.

## Model Assumptions

### MSCI Projection (Market Path)
- We use a projected MSCI return path to represent the market environment.
- The model supports different scenarios (normal / bullish / bearish).
- MSCI returns do **not** directly create cashflows, but they influence **NAV growth** through the calibrated omega process.
- This gives NAV a market‑sensitive drift while still respecting fund‑specific cashflow dynamics.

### NAV Dynamics
- NAV starts from the latest observed value and updates each quarter based on:
  - **Net cashflow** (draws increase NAV, repayments reduce NAV).
  - **Market-sensitive growth** (omega, calibrated by strategy/grade/age and MSCI).
- NAV is bounded to avoid unrealistic jumps, keeping projections stable.
- For late‑life funds, optional NAV anchoring can smooth NAV relative to paid‑in ratios.

### Calibration of Cashflow Timing and Size
- **Timing**: Probability of drawdowns/repayments by strategy, grade, and age bucket.
  - Draw timing is blended with historical draw frequency to match observed pacing.
- **Size**: Draw/repayment sizes are sampled from historical distributions.
  - Size distributions are stratified by strategy, grade, and age bucket.
- Recallables are modelled only after repayments and capped by contractual limits.
 - **Dependency structure**: Event timing and size draws use a one‑factor copula.
   - `rho_event` links **timing** across funds; `rho_size` links **sizes** across funds.
   - This creates realistic cross‑fund co‑movement without forcing all funds to move together.
 - **Hierarchical fitting**: If a bucket is sparse, the model falls back in order:
   - strategy+grade+age → strategy+age → strategy → global
   - This keeps the model stable while preserving the most specific information available.

### Current Grade Logic
- Grades are derived from performance metrics (DPI, TVPI, IRR).
- Logic varies by fund type:
  - **Debt**: IRR is the primary metric.
  - **Venture Capital**: during investment period, TVPI is emphasized.
  - **Other strategies**: DPI is emphasized during investment, IRR post‑investment.
- For the first five years (from first close), grades are anchored to the seed grade to avoid premature downgrades.
- After that, grades can update every four quarters based on projected performance.

### Automation and Consistency
- The entire process is automated once inputs are provided (portfolio file + calibration files).
- Scenario runs use the same calibrated mechanics, ensuring apples‑to‑apples comparisons.
- Diagnostics are produced alongside projections to highlight pacing, repayment rates, and grade shifts.

## Key Drivers

- **Strategy mix and grade**: Higher grades and favorable strategies increase repayment rates and NAV growth.
- **Fund age**: Drawdown timing and repayment patterns change as funds mature.
- **Market environment (MSCI)**: MSCI paths feed into NAV growth through omega.

## Latest Run (Charts)

> These charts are generated from run tag **test_portfolio_2025Q3_Sentral**.


### 1) Cumulative Drawdowns (Portfolio)

![Cumulative Drawdowns](model_fits/figures/sentral_cumulative_drawdowns.png)

### 2) Cumulative Repayments (Portfolio)

![Cumulative Repayments](model_fits/figures/sentral_cumulative_repayments.png)


### 3) Quarterly Drawdowns vs Repayments

![Drawdowns vs Repayments](model_fits/figures/sentral_draw_vs_rep_quarterly.png)

### 4) Active Funds Over Time

![Active Funds Over Time](model_fits/figures/sentral_active_funds_over_time.png)

### 5) Repayment Probability by Age Bucket

![Repayment Probability by Age Bucket](model_fits/figures/sentral_repayment_rate_by_age_bucket.png)


## Notes on Grading

- Funds are assigned a grade based on performance metrics (DPI, TVPI, IRR).
- Grades influence expected drawdown and repayment behavior.
- For the test portfolio, we can either:
  - Use the input grades as-is (static), or
  - Enable dynamic updates (every 4 quarters) to reflect projected performance.


## Sentral – Projection Table (Drawdowns & Repayments)

| Year | Drawdowns (Bn EUR) | Repayments (Bn EUR) | Cumulative Drawdowns (Bn EUR) | Cumulative Repayments (Bn EUR) |
|---:|---:|---:|---:|---:|
| 2025 | 0.00 | 0.00 | 0.00 | 0.00 |
| 2026 | 0.02 | 0.00 | 0.02 | 0.00 |
| 2027 | 0.12 | 0.00 | 0.14 | 0.00 |
| 2028 | 0.19 | 0.01 | 0.33 | 0.02 |
| 2029 | 0.25 | 0.03 | 0.58 | 0.05 |
| 2030 | 0.27 | 0.05 | 0.85 | 0.10 |
| 2031 | 0.21 | 0.08 | 1.07 | 0.17 |
| 2032 | 0.15 | 0.11 | 1.22 | 0.29 |
| 2033 | 0.09 | 0.14 | 1.31 | 0.43 |
| 2034 | 0.05 | 0.15 | 1.35 | 0.58 |
| 2035 | 0.02 | 0.14 | 1.37 | 0.71 |
| 2036 | 0.01 | 0.12 | 1.38 | 0.83 |
| 2037 | 0.00 | 0.10 | 1.38 | 0.94 |
| 2038 | 0.00 | 0.09 | 1.38 | 1.03 |
| 2039 | 0.00 | 0.07 | 1.38 | 1.10 |
| 2040 | 0.00 | 0.05 | 1.38 | 1.14 |
| 2041 | 0.00 | 0.02 | 1.38 | 1.16 |
| 2042 | 0.00 | 0.00 | 1.38 | 1.17 |
