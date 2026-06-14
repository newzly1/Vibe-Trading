#!/usr/bin/env python3
"""Execution models — VWAP, TWAP, slippage estimation, market impact.

Standalone script — reads OHLCV CSV and computes execution benchmarks.
Use via Claude Code Bash tool::

    python scripts/execution.py --input ohlcv.csv --method vwap
    python scripts/execution.py --input ohlcv.csv --method twap
    python scripts/execution.py --input ohlcv.csv --method slippage --model sqrt --participation 0.1
    python scripts/execution.py --input ohlcv.csv --method all

Input CSV must have columns: trade_date, open, high, low, close, volume.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd


def _load(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["trade_date"]).sort_values("trade_date")
    for col in ["open", "high", "low", "close", "volume"]:
        if col not in df.columns:
            raise ValueError(f"Missing column: {col}")
    return df.reset_index(drop=True)


# ---- VWAP / TWAP -------------------------------------------------------------

def compute_vwap(df: pd.DataFrame) -> pd.DataFrame:
    """Cumulative VWAP using (H+L+C)/3 * volume."""
    typical = (df["high"] + df["low"] + df["close"]) / 3
    cum_pv = (typical * df["volume"]).cumsum()
    cum_vol = df["volume"].cumsum()
    result = pd.DataFrame({
        "trade_date": df["trade_date"],
        "vwap": cum_pv / cum_vol.replace(0, np.nan),
        "typical_price": typical,
    })
    result.attrs["summary"] = {
        "metric": "VWAP",
        "latest": round(float(result["vwap"].iloc[-1]), 4) if len(result) > 0 else None,
    }
    return result


def compute_twap(df: pd.DataFrame) -> pd.DataFrame:
    """Cumulative TWAP using expanding mean of close."""
    result = pd.DataFrame({
        "trade_date": df["trade_date"],
        "twap": df["close"].expanding().mean(),
        "close": df["close"],
    })
    result.attrs["summary"] = {
        "metric": "TWAP",
        "latest": round(float(result["twap"].iloc[-1]), 4) if len(result) > 0 else None,
    }
    return result


# ---- Slippage Models ---------------------------------------------------------

def fixed_slippage(price: float, bps: float = 5.0) -> float:
    """Fixed bps slippage: price * (1 - bps/10000) for buy."""
    return price * (1 - bps / 10000)


def linear_impact(df: pd.DataFrame, participation: float = 0.05, bps_per_pct: float = 2.0) -> pd.Series:
    """Linear market impact: proportional to participation rate.

    Args:
        df: OHLCV DataFrame.
        participation: Order size as fraction of daily volume.
        bps_per_pct: Basis points of impact per 1% participation.
    """
    impact_bps = participation * 100 * bps_per_pct
    return df["close"] * (1 - impact_bps / 10000)


def sqrt_impact(df: pd.DataFrame, participation: float = 0.05, eta: float = 0.1) -> pd.Series:
    """Almgren-Chriss square-root impact model.

    impact = eta * sigma * (Q/V)^0.5

    Args:
        df: OHLCV DataFrame.
        participation: Order size Q as fraction of daily volume V.
        eta: Market impact coefficient (~0.1 for equities).
    """
    sigma = df["close"].pct_change().rolling(20).std().fillna(0.02)
    impact = eta * sigma * np.sqrt(participation)
    return df["close"] * (1 - impact)


def estimate_slippage(df: pd.DataFrame, model: str = "sqrt",
                      participation: float = 0.05, bps: float = 5.0) -> dict:
    """Estimate slippage for the latest bar."""
    latest = df.iloc[-1]
    price = float(latest["close"])
    daily_vol = float(latest["volume"])
    sigma = float(df["close"].pct_change().rolling(20).std().iloc[-1] or 0.02)
    order_size = daily_vol * participation
    n = max(1, len(df))

    if model == "fixed":
        adj_price = fixed_slippage(price, bps)
        impact_bps = bps
    elif model == "linear":
        adj_price = float(linear_impact(df, participation).iloc[-1])
        impact_bps = participation * 100 * 2.0
    elif model == "sqrt":
        adj_price = float(sqrt_impact(df, participation).iloc[-1])
        impact_bps = 0.1 * sigma * np.sqrt(participation) * 10000
    else:
        raise ValueError(f"Unknown model: {model}. Choose: fixed, linear, sqrt")

    return {
        "model": model,
        "price": round(price, 4),
        "adjusted_price": round(adj_price, 4),
        "slippage_pct": round((price - adj_price) / price * 100, 6),
        "impact_bps": round(impact_bps, 2),
        "participation": participation,
        "order_size_est": int(order_size),
        "daily_vol_avg": int(df["volume"].tail(20).mean()),
        "sigma_annual": round(sigma * np.sqrt(n), 4),
    }


# ---- Main --------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Execution models: VWAP, TWAP, slippage")
    parser.add_argument("--input", required=True, help="Path to OHLCV CSV")
    parser.add_argument("--method", required=True,
                        choices=["vwap", "twap", "slippage", "all"])
    parser.add_argument("--model", default="sqrt", choices=["fixed", "linear", "sqrt"],
                        help="Slippage model (default: sqrt)")
    parser.add_argument("--participation", type=float, default=0.05,
                        help="Order size as fraction of daily volume (default: 0.05)")
    parser.add_argument("--bps", type=float, default=5.0,
                        help="Fixed slippage in bps (default: 5.0)")
    parser.add_argument("--output", help="Optional output CSV path")
    args = parser.parse_args()

    df = _load(args.input)
    results = {}

    if args.method in ("vwap", "all"):
        results["vwap"] = compute_vwap(df)
    if args.method in ("twap", "all"):
        results["twap"] = compute_twap(df)
    if args.method in ("slippage", "all"):
        results["slippage"] = estimate_slippage(df, args.model, args.participation, args.bps)

    # Print summary
    if "vwap" in results:
        print(f"VWAP: {results['vwap'].attrs['summary']['latest']}", file=sys.stderr)
    if "twap" in results:
        print(f"TWAP: {results['twap'].attrs['summary']['latest']}", file=sys.stderr)
    if "slippage" in results:
        s = results["slippage"]
        print(f"Slippage ({s['model']}): {s['slippage_pct']:.4f}% ({s['impact_bps']:.1f} bps)", file=sys.stderr)

    if args.output and "vwap" in results:
        merged = pd.DataFrame({"trade_date": df["trade_date"]})
        for key, rdf in results.items():
            if isinstance(rdf, pd.DataFrame):
                for col in rdf.columns:
                    if col != "trade_date":
                        merged[f"{key}_{col}"] = rdf[col].values
        merged.to_csv(args.output, index=False)
        print(f"Results written to {args.output}")
    else:
        json_results = {}
        for k, v in results.items():
            if isinstance(v, pd.DataFrame):
                json_results[k] = {
                    "latest": {col: round(float(v[col].iloc[-1]), 6) for col in v.columns if col != "trade_date"}
                }
            else:
                json_results[k] = v
        print(json.dumps(json_results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
