#!/usr/bin/env python3
"""Pair trading, correlation, and cointegration analysis.

Standalone script — reads OHLCV CSV(s) and outputs structured results.
Use via Claude Code Bash tool::

    python scripts/pair_analysis.py --input ohlcv.csv --method correlation
    python scripts/pair_analysis.py --input multi.csv --method cointegration --asset1 AAPL --asset2 MSFT
    python scripts/pair_analysis.py --input multi.csv --method pair_signal --asset1 AAPL --asset2 MSFT
    python scripts/pair_analysis.py --input multi.csv --method all

Input CSV must have columns: trade_date, open, high, low, close, volume.
For multi-asset input, include a ``symbol`` column to distinguish assets.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import kendalltau, pearsonr, spearmanr

# ---- Helpers -----------------------------------------------------------------

def _load_data(path: str) -> pd.DataFrame:
    """Load OHLCV CSV. Auto-detects single-asset vs multi-asset format."""
    df = pd.read_csv(path, parse_dates=["trade_date"])
    required = {"trade_date", "close"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    return df.sort_values("trade_date")


def _daily_returns(df: pd.DataFrame, price_col: str = "close") -> pd.Series:
    return df.set_index("trade_date")[price_col].pct_change().dropna()


def _to_json(result: dict | pd.DataFrame | pd.Series) -> str:
    if isinstance(result, (pd.DataFrame, pd.Series)):
        return result.to_json(orient="records" if isinstance(result, pd.DataFrame) else "index", date_format="iso")
    return json.dumps(result, ensure_ascii=False, default=str, indent=2)


# ---- Correlation -------------------------------------------------------------

def correlation_matrix(df: pd.DataFrame, window: int = 60, method: str = "pearson") -> dict:
    """Compute rolling correlation matrix for multi-asset data.

    Args:
        df: DataFrame with columns: trade_date, symbol, close.
        window: Rolling window in trading days.
        method: 'pearson' or 'spearman'.

    Returns:
        Dict with keys: labels, matrix, window, method.
    """
    if "symbol" not in df.columns:
        raise ValueError("Multi-asset correlation requires a 'symbol' column")

    pivoted = df.pivot(index="trade_date", columns="symbol", values="close").sort_index()
    returns = pivoted.pct_change().dropna().iloc[-window:]

    if len(returns) < 2:
        raise ValueError(f"Not enough overlapping data: {len(returns)} rows after window={window}")

    codes = list(returns.columns)
    n = len(codes)
    matrix = [[1.0] * n for _ in range(n)]

    for i in range(n):
        for j in range(i + 1, n):
            xi, xj = returns.iloc[:, i].values, returns.iloc[:, j].values
            if method == "spearman":
                corr, _ = spearmanr(xi, xj)
            else:
                corr = float(np.corrcoef(xi, xj)[0, 1])
            corr = 0.0 if np.isnan(corr) else round(corr, 4)
            matrix[i][j] = matrix[j][i] = corr

    return {"labels": codes, "matrix": matrix, "window": window, "method": method}


def target_correlation(df: pd.DataFrame, target: str, window: int = 60) -> dict:
    """Correlate one asset against all others.

    Returns correlation ranking for the target asset.
    """
    if "symbol" not in df.columns:
        raise ValueError("Requires 'symbol' column")
    pivoted = df.pivot(index="trade_date", columns="symbol", values="close").sort_index()
    returns = pivoted.pct_change().dropna().iloc[-window:]
    if target not in returns.columns:
        raise ValueError(f"Target '{target}' not found. Available: {list(returns.columns)}")

    target_rets = returns[target]
    results = []
    for col in returns.columns:
        if col == target:
            continue
        valid = pd.concat([target_rets, returns[col]], axis=1).dropna()
        if len(valid) < 10:
            continue
        r, p = pearsonr(valid.iloc[:, 0], valid.iloc[:, 1])
        results.append({"symbol": col, "correlation": round(r, 4), "p_value": round(p, 6)})

    results.sort(key=lambda x: abs(x["correlation"]), reverse=True)
    return {"target": target, "window": window, "results": results[:30]}


# ---- Cointegration -----------------------------------------------------------

def engle_granger_coint(df: pd.DataFrame, asset1: str, asset2: str) -> dict:
    """Engle-Granger cointegration test between two assets.

    Returns test statistic, p-value, critical values, and hedge ratio.
    """
    if "symbol" not in df.columns:
        raise ValueError("Requires 'symbol' column")
    pivoted = df.pivot(index="trade_date", columns="symbol", values="close").sort_index()
    if asset1 not in pivoted.columns or asset2 not in pivoted.columns:
        raise ValueError(f"Assets not found. Available: {list(pivoted.columns)}")

    pair = pivoted[[asset1, asset2]].dropna()
    y, x = pair[asset1].values, pair[asset2].values

    # OLS: y = α + β·x
    X = np.column_stack([np.ones(len(x)), x])
    beta_hat = np.linalg.lstsq(X, y, rcond=None)[0]
    alpha, beta = beta_hat[0], beta_hat[1]
    residuals = y - (alpha + beta * x)

    # ADF test on residuals
    try:
        from statsmodels.tsa.stattools import adfuller
        adf_stat, adf_pvalue, adf_lags, adf_nobs, adf_crit, *_ = adfuller(residuals, maxlag=int(len(residuals) ** 0.25))
    except ImportError:
        return {"error": "statsmodels not installed. Run: pip install statsmodels"}

    # Half-life of mean reversion
    spread = pd.Series(y - beta * x)
    spread_lag = spread.shift(1)
    valid = pd.concat([spread, spread_lag], axis=1).dropna()
    if len(valid) > 1:
        delta = valid.iloc[:, 0] - valid.iloc[:, 1]
        ols_half = np.linalg.lstsq(
            np.column_stack([np.ones(len(valid)), valid.iloc[:, 1].values]), delta.values, rcond=None
        )[0]
        half_life = -np.log(2) / ols_half[1] if ols_half[1] < 0 else float("inf")
    else:
        half_life = float("inf")

    return {
        "asset1": asset1,
        "asset2": asset2,
        "hedge_ratio": round(beta, 6),
        "intercept": round(alpha, 6),
        "adf_statistic": round(adf_stat, 4),
        "adf_pvalue": round(adf_pvalue, 6),
        "adf_critical_values": {k: round(v, 4) for k, v in adf_crit.items()},
        "is_cointegrated_5pct": adf_stat < adf_crit["5%"],
        "half_life_days": round(half_life, 1) if half_life != float("inf") else None,
        "n_obs": len(residuals),
    }


# ---- Pair Trading Signals ----------------------------------------------------

def pair_trading_signals(df: pd.DataFrame, asset1: str, asset2: str,
                         lookback: int = 60, entry_z: float = 2.0, exit_z: float = 0.5) -> dict:
    """Generate pair trading signals based on spread Z-score.

    Returns signal series and summary statistics.
    """
    if "symbol" not in df.columns:
        raise ValueError("Requires 'symbol' column")
    pivoted = df.pivot(index="trade_date", columns="symbol", values="close").sort_index()
    if asset1 not in pivoted.columns or asset2 not in pivoted.columns:
        raise ValueError(f"Assets not found. Available: {list(pivoted.columns)}")

    pair = pivoted[[asset1, asset2]].dropna()
    y, x = pair[asset1].values, pair[asset2].values

    X = np.column_stack([np.ones(len(x)), x])
    beta = np.linalg.lstsq(X, y, rcond=None)[0][1]
    spread = pd.Series(y - beta * x, index=pair.index)

    spread_mean = spread.rolling(lookback).mean()
    spread_std = spread.rolling(lookback).std()
    z_score = ((spread - spread_mean) / spread_std).dropna()

    # Signal: +1 = long spread (buy asset1, sell asset2), -1 = short spread
    signal = pd.Series(0, index=z_score.index)
    position = 0
    for i in range(1, len(z_score)):
        if position == 0:
            if z_score.iloc[i] > entry_z:
                signal.iloc[i] = -1
                position = -1
            elif z_score.iloc[i] < -entry_z:
                signal.iloc[i] = 1
                position = 1
        elif position == 1 and z_score.iloc[i] > -exit_z:
            signal.iloc[i] = 0
            position = 0
        elif position == -1 and z_score.iloc[i] < exit_z:
            signal.iloc[i] = 0
            position = 0

    recent = signal.tail(10)
    return {
        "asset1": asset1,
        "asset2": asset2,
        "hedge_ratio": round(beta, 6),
        "lookback": lookback,
        "entry_z": entry_z,
        "exit_z": exit_z,
        "latest_z_score": round(z_score.iloc[-1], 4) if len(z_score) > 0 else None,
        "latest_signal": int(signal.iloc[-1]) if len(signal) > 0 else 0,
        "n_signals": int((signal != 0).sum()),
        "signal_last_10": signal.tail(10).tolist(),
        "zscore_last_10": z_score.tail(10).round(4).tolist(),
    }


# ---- Main CLI ----------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Pair trading, correlation, and cointegration analysis")
    parser.add_argument("--input", required=True, help="Path to OHLCV CSV")
    parser.add_argument("--method", required=True,
                        choices=["correlation", "cointegration", "pair_signal", "all"])
    parser.add_argument("--window", type=int, default=60, help="Rolling window in days (default: 60)")
    parser.add_argument("--asset1", help="First asset symbol (for cointegration / pair_signal)")
    parser.add_argument("--asset2", help="Second asset symbol (for cointegration / pair_signal)")
    parser.add_argument("--target", help="Target asset for correlation ranking (optional)")
    parser.add_argument("--entry_z", type=float, default=2.0, help="Entry Z-score threshold (default: 2.0)")
    parser.add_argument("--exit_z", type=float, default=0.5, help="Exit Z-score threshold (default: 0.5)")
    parser.add_argument("--output", help="Optional output path for JSON results")
    args = parser.parse_args()

    df = _load_data(args.input)
    results = {}

    if args.method in ("correlation", "all"):
        if args.target:
            results["correlation"] = target_correlation(df, args.target, args.window)
        else:
            results["correlation"] = correlation_matrix(df, args.window)

    if args.method in ("cointegration", "all"):
        if args.asset1 and args.asset2:
            results["cointegration"] = engle_granger_coint(df, args.asset1, args.asset2)
        elif args.method == "cointegration":
            print("Error: --asset1 and --asset2 required for cointegration", file=sys.stderr)
            sys.exit(1)

    if args.method in ("pair_signal", "all"):
        if args.asset1 and args.asset2:
            results["pair_signal"] = pair_trading_signals(
                df, args.asset1, args.asset2, args.window, args.entry_z, args.exit_z
            )
        elif args.method == "pair_signal":
            print("Error: --asset1 and --asset2 required for pair_signal", file=sys.stderr)
            sys.exit(1)

    output = _to_json(results)
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"Results written to {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
