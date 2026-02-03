from __future__ import annotations

from pathlib import Path
from typing import List, Dict
import math
import pandas as pd
import numpy as np


def xnpv(rate: float, cfs: np.ndarray, dts: np.ndarray) -> float:
    dts = np.asarray(dts, dtype="datetime64[ns]")
    cfs = np.asarray(cfs, dtype=float)
    t0 = dts[0]
    day_counts = (dts - t0) / np.timedelta64(1, "D")
    years = day_counts / 365.0
    return float(np.sum(cfs / ((1.0 + rate) ** years)))


def xirr_newton(cfs: np.ndarray, dts: np.ndarray, guess: float = 0.1, max_iter: int = 80, tol: float = 1e-7) -> float:
    dts = np.asarray(dts, dtype="datetime64[ns]")
    cfs = np.asarray(cfs, dtype=float)
    rate = float(guess)
    for _ in range(max_iter):
        f = xnpv(rate, cfs, dts)
        if not np.isfinite(f):
            return math.nan
        if abs(f) < tol:
            return rate
        eps = 1e-6
        f1 = xnpv(rate + eps, cfs, dts)
        df = (f1 - f) / eps
        if df == 0 or not np.isfinite(df):
            return math.nan
        rate_new = rate - f / df
        if rate_new <= -0.999999 or not np.isfinite(rate_new):
            return math.nan
        rate = rate_new
    return math.nan


def xirr_bisect(cfs: np.ndarray, dts: np.ndarray, low: float = -0.9999, high: float = 10.0, max_iter: int = 200, tol: float = 1e-7) -> float:
    dts = np.asarray(dts, dtype="datetime64[ns]")
    cfs = np.asarray(cfs, dtype=float)
    f_low = xnpv(low, cfs, dts)
    f_high = xnpv(high, cfs, dts)
    if not np.isfinite(f_low) or not np.isfinite(f_high):
        return math.nan
    it_expand = 0
    while f_low * f_high > 0 and it_expand < 50:
        high *= 2.0
        f_high = xnpv(high, cfs, dts)
        it_expand += 1
        if not np.isfinite(f_high):
            break
    if f_low * f_high > 0:
        return math.nan
    for _ in range(max_iter):
        mid = (low + high) / 2.0
        f_mid = xnpv(mid, cfs, dts)
        if not np.isfinite(f_mid):
            return math.nan
        if abs(f_mid) < tol:
            return mid
        if f_low * f_mid <= 0:
            high = mid
            f_high = f_mid
        else:
            low = mid
            f_low = f_mid
    return (low + high) / 2.0


def compute_end_irr(series: pd.DataFrame) -> float:
    # Net cashflow per quarter
    cfs = (series["sim_rep_mean"].values - series["sim_draw_mean"].values).astype(float)
    dts = series["quarter_end"].values.astype("datetime64[ns]")
    nav_end = float(series["sim_nav_mean"].iloc[-1]) if len(series) else 0.0
    cfs_full = np.append(cfs, nav_end)
    dts_full = np.append(dts, series["quarter_end"].iloc[-1])
    if not (np.any(cfs_full < 0) and np.any(cfs_full > 0)):
        return math.nan
    guess = 0.10
    irr = xirr_newton(cfs_full, dts_full, guess=guess)
    if not np.isfinite(irr):
        irr = xirr_bisect(cfs_full, dts_full)
    return irr


def load_series(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["quarter_end"] = pd.to_datetime(df["quarter_end"], errors="coerce")
    df = df.sort_values("quarter_end")
    df["cum_draw"] = df["sim_draw_mean"].cumsum()
    df["cum_rep"] = df["sim_rep_mean"].cumsum()
    df["tvpi"] = np.where(df["cum_draw"] > 0, (df["cum_rep"] + df["sim_nav_mean"]) / df["cum_draw"], np.nan)
    df["dpi"] = np.where(df["cum_draw"] > 0, df["cum_rep"] / df["cum_draw"], np.nan)
    return df


def _resolve_root() -> Path:
    # Handle running from repo root or from within model_fits/
    cwd = Path.cwd().resolve()
    if (cwd / "runs").exists():  # cwd is model_fits/
        return cwd.parent
    if (cwd / "model_fits" / "runs").exists():
        return cwd
    if (cwd.parent / "model_fits" / "runs").exists():
        return cwd.parent
    if (cwd.parent.parent / "model_fits" / "runs").exists():
        return cwd.parent.parent
    return cwd


def main() -> None:
    root = _resolve_root()
    runs = {
        "normal": "test_portfolio_2025Q3",
        "bullish": "test_portfolio_2025Q3_bullish",
        "bearish": "test_portfolio_2025Q3_bearish",
    }

    all_rows: List[pd.DataFrame] = []
    summary_rows: List[Dict[str, float]] = []

    for label, tag in runs.items():
        series_path = root / "model_fits" / "runs" / tag / "projection" / "sim_outputs" / "sim_portfolio_series.csv"
        if not series_path.exists():
            print(f"Missing series for {label}: {series_path}")
            continue
        df = load_series(series_path)
        df.insert(0, "scenario", label)
        all_rows.append(df)

        irr_end = compute_end_irr(df)
        draw_total = float(df["sim_draw_mean"].sum())
        rep_total = float(df["sim_rep_mean"].sum())
        nav_end = float(df["sim_nav_mean"].iloc[-1]) if len(df) else 0.0
        tvpi_end = float(df["tvpi"].iloc[-1]) if len(df) else math.nan
        dpi_end = float(df["dpi"].iloc[-1]) if len(df) else math.nan

        summary_rows.append({
            "scenario": label,
            "run_tag": tag,
            "draw_total": draw_total,
            "rep_total": rep_total,
            "nav_end": nav_end,
            "tvpi_end": tvpi_end,
            "dpi_end": dpi_end,
            "irr_end": irr_end,
        })

    if not all_rows:
        print("No series loaded. Check run tags.")
        return

    out_ts = root / "model_fits" / "scenario_compare_tvpi_dpi_timeseries.csv"
    out_sum = root / "model_fits" / "scenario_compare_irr_summary.csv"

    pd.concat(all_rows, ignore_index=True).to_csv(out_ts, index=False)
    pd.DataFrame(summary_rows).to_csv(out_sum, index=False)

    print(f"Wrote: {out_ts}")
    print(f"Wrote: {out_sum}")


if __name__ == "__main__":
    main()
