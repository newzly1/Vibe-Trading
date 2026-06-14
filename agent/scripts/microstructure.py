#!/usr/bin/env python3
"""Market microstructure metrics — Amihud illiquidity, Roll implied spread, Kyle's lambda, VPIN.

Standalone script — reads OHLCV CSV and computes microstructure metrics.
Use via Claude Code Bash tool::

    python scripts/microstructure.py --input ohlcv.csv --method amihud
    python scripts/microstructure.py --input ohlcv.csv --method roll
    python scripts/microstructure.py --input ohlcv.csv --method kyle
    python scripts/microstructure.py --input ohlcv.csv --method vpin --volume_bucket 100
    python scripts/microstructure.py --input ohlcv.csv --method all

Input CSV must have columns: trade_date, open, high, low, close, volume.
For VPIN, minute-level data with volume is recommended (falls back to daily).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats


def _load(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["trade_date"]).sort_values("trade_date")
    for col in ["open", "high", "low", "close", "volume"]:
        if col not in df.columns:
            raise ValueError(f"Missing column: {col}")
    return df


# ---- Amihud Illiquidity -----------------------------------------------------

def amihud_illiquidity(df: pd.DataFrame, window: int = 20) -> pd.DataFrame:
    """Amihud illiquidity: |return| / dollar_volume, averaged over window.

    Higher values = more illiquid. Typical screening: Amihud < 1e-6 for liquid stocks.
    """
    df = df.copy()
    df["return"] = df["close"].pct_change().abs()
    df["dollar_vol"] = df["close"] * df["volume"]
    # Avoid zero volume
    df["dollar_vol"] = df["dollar_vol"].replace(0, np.nan)

    illiq = (df["return"] / df["dollar_vol"]).replace([np.inf, -np.inf], np.nan)
    result = pd.DataFrame({
        "trade_date": df["trade_date"],
        "amihud": illiq,
        "amihud_ma": illiq.rolling(window).mean(),
    })
    # Summary
    avg = illiq.dropna().mean()
    result.attrs["summary"] = {
        "metric": "Amihud Illiquidity",
        "mean": round(float(avg), 12) if not np.isnan(avg) else None,
        "window": window,
        "interpretation": "Higher = more illiquid. < 1e-6 typically indicates liquid stock."
    }
    return result


# ---- Roll Implied Spread -----------------------------------------------------

def roll_implied_spread(df: pd.DataFrame, window: int = 20) -> pd.DataFrame:
    """Roll (1984) implied spread: 2 * sqrt(-cov(R_t, R_{t-1})).

    Uses rolling window. Returns NaN when autocov is positive (model assumption violated).
    """
    df = df.copy()
    ret = df["close"].pct_change()
    ret_lag = ret.shift(1)

    roll_series = pd.Series(np.nan, index=df.index)
    for i in range(window, len(ret)):
        r = ret.iloc[i - window + 1: i + 1]
        r_lag = ret_lag.iloc[i - window + 1: i + 1]
        valid = pd.concat([r, r_lag], axis=1).dropna()
        if len(valid) < 10:
            continue
        cov = float(np.cov(valid.iloc[:, 0], valid.iloc[:, 1])[0, 1])
        if cov < 0:
            roll_series.iloc[i] = 2.0 * np.sqrt(-cov)
        else:
            roll_series.iloc[i] = 0.0  # Model violation — treat as zero

    result = pd.DataFrame({
        "trade_date": df["trade_date"],
        "roll_spread": roll_series,
    })
    recent = roll_series.dropna()
    result.attrs["summary"] = {
        "metric": "Roll Implied Spread",
        "mean": round(float(recent.mean()), 8) if len(recent) > 0 else None,
        "window": window,
        "interpretation": "Effective bid-ask spread estimate. Zero when autocov >= 0 (model violation)."
    }
    return result


# ---- Kyle's Lambda -----------------------------------------------------------

def kyle_lambda(df: pd.DataFrame, window: int = 20) -> pd.DataFrame:
    """Kyle's lambda: price impact per unit of net order flow.

    Regression: dP = a + lambda * Q + e, where Q = signed volume proxy.
    Uses rolling window OLS to estimate lambda_t.
    """
    df = df.copy()
    dp = df["close"].diff()
    # Signed volume proxy: positive return = buyer-initiated, negative = seller-initiated
    ret_sign = np.sign(df["close"].pct_change().fillna(0))
    q = df["volume"] * ret_sign

    lambdas = pd.Series(np.nan, index=df.index)
    for i in range(window, len(df)):
        dpi = dp.iloc[i - window + 1: i + 1].values
        qi = q.iloc[i - window + 1: i + 1].values
        mask = ~(np.isnan(dpi) | np.isnan(qi))
        if mask.sum() < 10:
            continue
        slope, _, _, _, _ = stats.linregress(qi[mask], dpi[mask])
        lambdas.iloc[i] = slope

    result = pd.DataFrame({
        "trade_date": df["trade_date"],
        "kyle_lambda": lambdas,
    })
    recent = lambdas.dropna()
    result.attrs["summary"] = {
        "metric": "Kyle's Lambda",
        "mean": round(float(recent.mean()), 10) if len(recent) > 0 else None,
        "window": window,
        "interpretation": "Price impact per unit of net order flow. Higher = lower liquidity."
    }
    return result


# ---- VPIN (Volume-synchronized Probability of Informed Trading) ---------------

def vpin(df: pd.DataFrame, volume_bucket: int = 50, n_buckets: int = 50) -> pd.DataFrame:
    """Volume-synchronized PIN (Easley et al.).

    Args:
        volume_bucket: Number of trades/volume bars per bucket.
        n_buckets: Number of buckets in rolling VPIN window.

    Uses daily data with volume as a proxy for trade intensity.
    For accurate VPIN, minute-level trade data is preferred.
    """
    df = df.copy()
    df["price_change"] = df["close"].diff()
    df["buy_vol"] = df["volume"].where(df["price_change"] >= 0, 0)
    df["sell_vol"] = df["volume"].where(df["price_change"] < 0, 0)

    # Accumulate volume into buckets
    cum_vol = 0
    cum_buy, cum_sell = 0.0, 0.0
    bucket_buy_sell = []
    for _, row in df.iterrows():
        cum_buy += row["buy_vol"]
        cum_sell += row["sell_vol"]
        cum_vol += row["volume"]
        if cum_vol >= volume_bucket:
            total = cum_buy + cum_sell
            bucket_buy_sell.append(abs(cum_buy - cum_sell) / total if total > 0 else 0)
            cum_vol, cum_buy, cum_sell = 0, 0.0, 0.0

    if len(bucket_buy_sell) < n_buckets:
        n_buckets = max(1, len(bucket_buy_sell))

    vpin_series = pd.Series(np.nan, index=df.index)
    if bucket_buy_sell:
        for i in range(n_buckets - 1, len(bucket_buy_sell)):
            window_vals = bucket_buy_sell[i - n_buckets + 1: i + 1]
            vpin_val = sum(window_vals) / len(window_vals)
            # Map bucket index to approximate original index
            orig_idx = min(i * volume_bucket // int(df["volume"].mean()) if df["volume"].mean() > 0 else i,
                          len(df) - 1)
            vpin_series.iloc[orig_idx] = vpin_val

    # Forward fill to cover all dates
    vpin_series = vpin_series.ffill()

    result = pd.DataFrame({
        "trade_date": df["trade_date"],
        "vpin": vpin_series,
    })
    recent = vpin_series.dropna()
    result.attrs["summary"] = {
        "metric": "VPIN (Volume-synchronized PIN)",
        "mean": round(float(recent.mean()), 6) if len(recent) > 0 else None,
        "latest": round(float(recent.iloc[-1]), 6) if len(recent) > 0 else None,
        "volume_bucket": volume_bucket,
        "n_buckets": n_buckets,
        "interpretation": "> 0.8 suggests high informed trading (potential adverse selection). < 0.3 suggests low."
    }
    return result


# ---- Main --------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Market microstructure metrics")
    parser.add_argument("--input", required=True, help="Path to OHLCV CSV")
    parser.add_argument("--method", required=True,
                        choices=["amihud", "roll", "kyle", "vpin", "all"])
    parser.add_argument("--window", type=int, default=20, help="Rolling window (default: 20)")
    parser.add_argument("--volume_bucket", type=int, default=100, help="Volume per VPIN bucket (default: 100)")
    parser.add_argument("--output", help="Optional output CSV path")
    args = parser.parse_args()

    df = _load(args.input)
    results = {}

    if args.method in ("amihud", "all"):
        results["amihud"] = amihud_illiquidity(df, args.window)
    if args.method in ("roll", "all"):
        results["roll"] = roll_implied_spread(df, args.window)
    if args.method in ("kyle", "all"):
        results["kyle"] = kyle_lambda(df, args.window)
    if args.method in ("vpin", "all"):
        results["vpin"] = vpin(df, args.volume_bucket)

    # Print summaries
    for key, rdf in results.items():
        summary = getattr(rdf, "attrs", {}).get("summary", {})
        if summary:
            print(f"\n[{key}] {summary.get('metric')}", file=sys.stderr)
            print(f"  mean: {summary.get('mean')}", file=sys.stderr)
            print(f"  {summary.get('interpretation', '')}", file=sys.stderr)

    if args.output:
        merged = pd.DataFrame({"trade_date": df["trade_date"]})
        for key, rdf in results.items():
            for col in rdf.columns:
                if col != "trade_date":
                    merged[f"{key}_{col}"] = rdf[col].values
        merged.to_csv(args.output, index=False)
        print(f"\nResults written to {args.output}")
    else:
        summaries = {k: getattr(rdf, "attrs", {}).get("summary", {}) for k, rdf in results.items()}
        print(json.dumps(summaries, ensure_ascii=False, default=str, indent=2))


if __name__ == "__main__":
    main()
