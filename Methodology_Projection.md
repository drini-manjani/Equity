# Projection Methodology (Cashflows, NAV, Grades, IRR)

This document describes how the projection engine runs, how cashflows and NAV are simulated, and how grades are assigned and diagnosed.

---

## 1) Overall run flow

### Whole‑portfolio run (calibration + projection)
1. **Calibrate** timing, ratios, omega, copula on historical data.
2. **Simulate** the full portfolio with Monte Carlo.
3. **Post‑simulation grading** (mean path): compute per‑fund metrics by quarter from the mean Monte‑Carlo paths, then assign grades by strategy quartiles.
4. **Write outputs** (portfolio series, fund means, grade thresholds, grade updates, diagnostics).

### Test‑portfolio run
1. **Load calibration** from the whole‑portfolio run.
2. **Simulate** only the test portfolio.
3. **Post‑simulation grading** (mean path): apply strategy‑wise thresholds (from the whole portfolio) to the test portfolio.
4. **Write outputs** (test portfolio series, fund means, grade updates, diagnostics).

---

## 2) Data inputs

Required (minimum):
- FundID
- Quarter/Year (or quarter_end)
- Adj Strategy
- Grade (seed grade)
- Adj Drawdown EUR
- Adj Repayment EUR
- NAV Adjusted EUR
- Commitment EUR
- Fund_Age_Quarters
- Recallable, Recallable_Percentage_Decimal, Expiration_Quarters
- Planned End Date (or equivalent)
- MSCI index file (for omega projection)

---

## 3) Cashflow simulation (per fund, per quarter)

### 3.1 Drawdowns
**Model structure**
- Draw event probability: `p_draw` from timing fits by (Strategy, Grade, AgeBucket) with hierarchical fallback.
- Draw size: distribution fit of draw ratios by (Strategy, Grade, AgeBucket).
- Ratio model uses **cumulative draw ratio** (cumulative draw / commitment), so ratios can exceed 1 due to recallables.
- Draws are paced using a **draw pace** estimated from historical delta ratios to avoid unrealistic jump‑to‑target.

**Capacity**
- Capacity = remaining commitment + recallable available.
- A draw is capped by available capacity.

**Gating**
- Early years use draw probability gating (`U < p_draw`).
- After early buckets, gating is relaxed and draw amounts follow the catch‑up/pace logic.

### 3.2 Repayments
**Model structure**
- Repayment event probability: `p_rep` from timing fits by (Strategy, Grade, AgeBucket) with fallback.
- Repayment size: distribution fit of repayment ratio to NAV.
- Repayment amount = `rep_ratio * NAV_prev`.

### 3.3 Recallables
- Recallables are generated only when repayments occur.
- Recallable ratio is fit conditional on repayment.
- Recallable is capped by LPA rules (Recallable_Percentage_Decimal × Commitment) and available history.
- Recallable capacity is consumed **first** for subsequent drawdowns.

---

## 4) NAV projection

**Quarter update**
```
NAV_after_flow = max(NAV_prev + drawdown - repayment, 0)
NAV_t = NAV_after_flow * (1 + omega_t)
```

**Omega**
- Omega is calibrated from historical NAV/flows and MSCI via NAV Logic and applied by strategy/grade/age where available.
- Omega is clipped to avoid explosive values.

---

## 5) Monte‑Carlo simulation

- Each simulation uses its own RNG seed (`seed + sim_index`).
- Cashflow randomness and copula correlation are simulation‑specific.
- Mean paths across simulations are computed for reporting:
  - `sim_fund_draw_mean.csv`
  - `sim_fund_rep_mean.csv`
  - `sim_fund_nav_mean.csv`

---

## 6) Grading logic

### 6.1 Why grading is relative
Grades are **relative** within each strategy. Quartiles are computed per strategy and quarter:
- Bottom 25% → D
- 25–50% → C
- 50–75% → B
- Top 25% → A

### 6.2 Post‑simulation grading (preferred)
**After MC**, for each fund and quarter:
1. Compute **mean path** metrics:
   - Paid‑in (cumulative draws)
   - Distributed (cumulative reps)
   - NAV
   - DPI, TVPI, IRR
2. Compute **strategy‑wise quartile thresholds** for DPI/TVPI/IRR by quarter.
3. Apply grading rules:
   - If StrategyFundCount < 30 → use **worse** of DPI/TVPI.
   - Debt → use IRR.
   - In investment period → use TVPI (VC) or DPI (PE).
   - Harvest period → use IRR, but downgrade if DPI is worse.

### 6.3 Grade persistence
Grades are updated **yearly** (every 4 quarters). Between grading quarters, the prior grade is carried forward.

### 6.4 Output files
- `grade_thresholds_by_quarter.csv` (strategy quartiles)
- `grade_updates_by_quarter.csv` (fund grade over time)
- `sim_fund_metrics_mean.csv` (fund metrics + grade)

---

## 7) IRR calculation (robust)

### 7.1 IRR inputs
- Drawdowns are negative cashflows.
- Repayments are positive cashflows.
- NAV is included as terminal value at quarter end.

### 7.2 Solver
1. Newton‑Raphson attempt (`xirr_newton`).
2. **Bisection fallback** if Newton fails (`xirr_bisect`).

### 7.3 Failure conditions
- No cashflows to date → IRR = NaN.
- No sign change (all positive or all negative) → IRR = NaN.
- Solver failure → IRR = NaN.

All failures are logged to:
- `irr_failures_grade_update.csv`

This ensures grading doesn’t silently fail — you can inspect how many funds/quarters lacked valid IRR.

---

## 8) Diagnostics outputs

Saved under `projection/diagnostics/`:
- `sim_diagnostics_summary.csv` (historical vs projected checks)
- `sim_diagnostics_by_age.csv` (draw timing checks)
- `draw_zero_reasons_by_quarter.csv`
- `irr_failures_grade_update.csv`
- `grade_thresholds_by_quarter.csv`
- `grade_updates_by_quarter.csv`
- `sim_fund_metrics_mean.csv`

---

## 9) Separation of whole portfolio vs test portfolio

Whole portfolio:
- Generates thresholds and serves as the **reference population**.

Test portfolio:
- Uses **same thresholds** from the whole portfolio.
- Produces its own fund‑level grade evolution and metrics.

---

## 10) Reproducibility

- All randomness controlled via seed + sim index.
- Outputs are saved per run tag.
- Grade rules and IRR logic are deterministic given inputs.

---

## 11) Key output paths (defaults)

Whole portfolio:
- `model_fits/runs/2025Q3/projection/diagnostics/grade_thresholds_by_quarter.csv`
- `model_fits/runs/2025Q3/projection/diagnostics/grade_updates_by_quarter.csv`

Test portfolio:
- `model_fits/runs/test_portfolio_2025Q3/projection/diagnostics/grade_updates_by_quarter.csv`

---

## 12) Notes / constraints

- Grades are relative by strategy; the population definition matters.
- IRR is undefined if there is no sign change in cashflows.
- Grades are only updated yearly and carried forward between updates.

