#!/usr/bin/env python3
"""Machine learning walk-forward strategy training.

Builds features from OHLCV data, trains sklearn models in walk-forward fashion,
and outputs predicted signals.

Use via Claude Code Bash tool::

    python scripts/ml_walkforward.py --input ohlcv.csv --model random_forest --window 252 --retrain 63
    python scripts/ml_walkforward.py --input ohlcv.csv --model gradient_boosting --window 252 --retrain 63

Input CSV must have columns: trade_date, open, high, low, close, volume.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


def _load(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["trade_date"]).sort_values("trade_date")
    for col in ["open", "high", "low", "close", "volume"]:
        if col not in df.columns:
            raise ValueError(f"Missing column: {col}")
    return df.reset_index(drop=True)


def validate_data(df: pd.DataFrame) -> dict:
    """Check data quality before training."""
    issues = []
    if len(df) < 252:
        issues.append(f"Only {len(df)} rows — minimum 252 recommended")
    for col in ["open", "high", "low", "close", "volume"]:
        nan_pct = df[col].isna().mean()
        if nan_pct > 0.1:
            issues.append(f"{col} has {nan_pct:.1%} NaN")
    if (df["close"] <= 0).any():
        issues.append("close contains non-positive values")
    return {"n_rows": len(df), "issues": issues, "ok": len(issues) == 0}


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """Build 10 predictive features from OHLCV data."""
    close = df["close"]
    vol = df["volume"]
    high = df["high"]
    low = df["low"]

    features = pd.DataFrame(index=df.index)
    features["ret_5d"] = close.pct_change(5)
    features["ret_20d"] = close.pct_change(20)
    features["vol_20d"] = close.pct_change().rolling(20).std()
    features["ma_ratio"] = close / close.rolling(20).mean()
    features["volume_ratio"] = vol / vol.rolling(20).mean()
    # RSI(14)
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss.replace(0, np.nan)
    features["rsi_14"] = 100 - (100 / (1 + rs))
    # Bollinger position
    bb_mean = close.rolling(20).mean()
    bb_std = close.rolling(20).std()
    features["bb_position"] = (close - bb_mean) / bb_std.replace(0, np.nan)
    features["high_low_ratio"] = high / low
    features["close_open_ratio"] = df["close"] / df["open"]
    features["skew_20d"] = close.pct_change().rolling(20).skew()

    return features


def walk_forward_predict(df: pd.DataFrame, model_type: str = "random_forest",
                         train_window: int = 252, retrain_every: int = 63) -> pd.DataFrame:
    """Walk-forward ML training and prediction.

    Args:
        df: OHLCV DataFrame.
        model_type: 'random_forest', 'gradient_boosting', or 'logistic'.
        train_window: Initial training window in rows.
        retrain_every: Retrain every N rows.

    Returns:
        DataFrame with date, prediction, and probability columns.
    """
    try:
        from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
        from sklearn.linear_model import LogisticRegression
        from sklearn.preprocessing import StandardScaler
    except ImportError:
        raise ImportError("scikit-learn not installed. Run: pip install scikit-learn")

    features = build_features(df)
    # Target: next-day return direction (1 = up, 0 = down)
    target = (df["close"].pct_change().shift(-1) > 0).astype(int)
    data = pd.concat([features, target.rename("target")], axis=1).dropna()

    if len(data) < train_window:
        raise ValueError(f"Only {len(data)} clean rows after feature engineering — need {train_window}")

    models = {
        "random_forest": RandomForestClassifier,
        "gradient_boosting": GradientBoostingClassifier,
        "logistic": LogisticRegression,
    }
    if model_type not in models:
        raise ValueError(f"Unknown model: {model_type}. Choose: {list(models.keys())}")

    model_cls = models[model_type]
    feature_cols = [c for c in features.columns]
    predictions = []
    correct = 0
    total = 0

    for t in range(train_window, len(data)):
        if (t - train_window) % retrain_every == 0:
            train = data.iloc[t - train_window:t]
            X_train = train[feature_cols].values
            y_train = train["target"].values
            scaler = StandardScaler()
            X_train = scaler.fit_transform(X_train)
            if model_type == "logistic":
                model = LogisticRegression(max_iter=1000)
            elif model_type == "random_forest":
                model = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
            else:
                model = GradientBoostingClassifier(n_estimators=100, max_depth=3, random_state=42)
            model.fit(X_train, y_train)

        X_test = scaler.transform(data[feature_cols].iloc[t:t + 1].values)
        proba = model.predict_proba(X_test)[0]
        pred = int(proba[1] > 0.5)
        actual = int(data["target"].iloc[t])
        correct += 1 if pred == actual else 0
        total += 1
        predictions.append({
            "trade_date": str(df["trade_date"].iloc[data.index[t]]),
            "prediction": pred,
            "prob_up": round(float(proba[1]), 4),
            "actual": actual,
        })

    accuracy = correct / total if total > 0 else 0
    pred_df = pd.DataFrame(predictions)

    return pred_df, {
        "model": model_type,
        "train_window": train_window,
        "retrain_every": retrain_every,
        "n_predictions": len(predictions),
        "accuracy": round(accuracy, 4),
        "feature_count": len(feature_cols),
    }


def main():
    parser = argparse.ArgumentParser(description="ML walk-forward strategy training")
    parser.add_argument("--input", required=True, help="Path to OHLCV CSV")
    parser.add_argument("--model", default="random_forest",
                        choices=["random_forest", "gradient_boosting", "logistic"])
    parser.add_argument("--window", type=int, default=252, help="Training window rows (default: 252)")
    parser.add_argument("--retrain", type=int, default=63, help="Retrain every N rows (default: 63)")
    parser.add_argument("--output", help="Optional output CSV for predictions")
    args = parser.parse_args()

    df = _load(args.input)

    validation = validate_data(df)
    if not validation["ok"]:
        print("Data issues:", file=sys.stderr)
        for issue in validation["issues"]:
            print(f"  - {issue}", file=sys.stderr)

    try:
        pred_df, summary = walk_forward_predict(df, args.model, args.window, args.retrain)

        print(json.dumps(summary, ensure_ascii=False, indent=2), file=sys.stderr)

        # Signal summary
        pred_counts = pred_df["prediction"].value_counts().to_dict()
        long_pct = pred_counts.get(1, 0) / len(pred_df) * 100
        print(f"Long signal: {long_pct:.1f}%", file=sys.stderr)

        if args.output:
            pred_df.to_csv(args.output, index=False)
            print(f"Predictions written to {args.output}")
        else:
            print(pred_df.tail(20).to_json(orient="records", date_format="iso"))

    except ImportError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
