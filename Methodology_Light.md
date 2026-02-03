<div style="text-align:right;">
  <img class="eif-logo" src="European_Investment_Fund_logo.svg" alt="EIF Logo" />
</div>

# Equity Cashflow Projections: ETCI 2.0 


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

> These charts are generated from run tag **test_portfolio_2025Q3**.

### 1) MSCI Paths (Expected + 10–90% Band)

![MSCI Mean and Band](model_fits/figures/msci_mean_band.png)

### 2) Cumulative Drawdowns (Portfolio)

![Cumulative Drawdowns](model_fits/figures/cumulative_drawdowns.png)

### 3) Cumulative Repayments (Portfolio)

![Cumulative Repayments](model_fits/figures/cumulative_repayments.png)


### 4) Quarterly Drawdowns vs Repayments

![Drawdowns vs Repayments](model_fits/figures/draw_vs_rep_quarterly.png)

### 5) Active Funds Over Time

![Active Funds Over Time](model_fits/figures/active_funds_over_time.png)

### 6) Repayment Probability by Age Bucket

![Repayment Probability by Age Bucket](model_fits/figures/repayment_rate_by_age_bucket.png)

## Scenario Comparison (Normal / Bullish / Bearish)

These results are computed from the scenario runs:

Summary (end of projection horizon):

| Scenario | Repayments (Bn EUR) | DPI (end) | IRR (end, %) |
|---|---:|---:|---:|
| normal | 7.441 | 1.330 | 5.56 |
| bullish | 8.007 | 1.431 | 6.90 |
| bearish | 7.101 | 1.269 | 4.69 |

## Notes on Grading

- Funds are assigned a grade based on performance metrics (DPI, TVPI, IRR).
- Grades influence expected drawdown and repayment behavior.
- For the test portfolio, we can either:
  - Use the input grades as-is (static), or
  - Enable dynamic updates (every 4 quarters) to reflect projected performance.


## ETCI 2.0 Phase 2 – Projection Table (Drawdowns & Repayments)

| Year | Drawdowns (Bn EUR) | Repayments (Bn EUR) | Cumulative Drawdowns (Bn EUR) | Cumulative Repayments (Bn EUR) |
|---:|---:|---:|---:|---:|
| 2025 | 0.00 | 0.00 | 0.00 | 0.00 |
| 2026 | 0.00 | 0.00 | 0.00 | 0.00 |
| 2027 | 0.38 | 0.00 | 0.38 | 0.00 |
| 2028 | 0.86 | 0.04 | 1.24 | 0.04 |
| 2029 | 1.32 | 0.13 | 2.56 | 0.17 |
| 2030 | 1.26 | 0.22 | 3.81 | 0.39 |
| 2031 | 0.86 | 0.30 | 4.68 | 0.69 |
| 2032 | 0.48 | 0.54 | 5.16 | 1.24 |
| 2033 | 0.24 | 0.77 | 5.40 | 2.00 |
| 2034 | 0.12 | 0.87 | 5.52 | 2.87 |
| 2035 | 0.04 | 0.87 | 5.56 | 3.74 |
| 2036 | 0.02 | 0.88 | 5.57 | 4.62 |
| 2037 | 0.01 | 0.82 | 5.58 | 5.44 |
| 2038 | 0.01 | 0.82 | 5.59 | 6.26 |
| 2039 | 0.00 | 0.70 | 5.59 | 6.97 |
| 2040 | 0.00 | 0.36 | 5.59 | 7.33 |
| 2041 | 0.00 | 0.11 | 5.60 | 7.44 |
