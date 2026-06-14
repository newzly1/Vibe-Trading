#!/usr/bin/env python3
"""Unified pattern detection — candlestick, chart, Elliott Wave, Harmonic, Ichimoku, SMC, Chanlun.

Standalone script — reads OHLCV CSV and outputs detected patterns.
Use via Claude Code Bash tool::

    python scripts/patterns.py --input ohlcv.csv --method candlestick
    python scripts/patterns.py --input ohlcv.csv --method chart
    python scripts/patterns.py --input ohlcv.csv --method elliott
    python scripts/patterns.py --input ohlcv.csv --method harmonic
    python scripts/patterns.py --input ohlcv.csv --method ichimoku
    python scripts/patterns.py --input ohlcv.csv --method all --output signals.csv

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


# =============================================================================
# Helpers
# =============================================================================

def _load_ohlcv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["trade_date"])
    for col in ["open", "high", "low", "close", "volume"]:
        if col not in df.columns:
            raise ValueError(f"Missing column: {col}")
    return df.sort_values("trade_date").reset_index(drop=True)


def _to_json(result: Any) -> str:
    if isinstance(result, (pd.DataFrame, pd.Series)):
        return result.to_json(orient="records", date_format="iso")
    return json.dumps(result, ensure_ascii=False, default=str, indent=2)


# =============================================================================
# 15 Candlestick Patterns (from vt-candlestick skill — pure pandas)
# =============================================================================

def _body(open_: pd.Series, close: pd.Series) -> pd.Series:
    return (close - open_).abs()


def _range(high: pd.Series, low: pd.Series) -> pd.Series:
    return high - low


def _upper_shadow(open_: pd.Series, close: pd.Series, high: pd.Series) -> pd.Series:
    return high - pd.concat([open_, close], axis=1).max(axis=1)


def _lower_shadow(open_: pd.Series, close: pd.Series, low: pd.Series) -> pd.Series:
    return pd.concat([open_, close], axis=1).min(axis=1) - low


def detect_candlestick_15(df: pd.DataFrame) -> pd.DataFrame:
    """Detect 15 classic candlestick patterns. Returns DF with pattern columns (0/1 flags)."""
    o, h, l, c = df["open"], df["high"], df["low"], df["close"]
    body = _body(o, c)
    rng = _range(h, l).replace(0, np.nan)
    upper = _upper_shadow(o, c, h)
    lower = _lower_shadow(o, c, l)
    result = pd.DataFrame(index=df.index)

    # -- Single-candle patterns --
    result["doji"] = (body / rng < 0.10).astype(int)
    result["hammer"] = ((lower > 2 * body) & (upper < body) & (body / rng > 0.1)).astype(int)
    result["inverted_hammer"] = ((upper > 2 * body) & (lower < body) & (body / rng > 0.1)).astype(int)
    result["shooting_star"] = ((upper > 2 * body) & (lower < body * 0.5) & ((c < o) | (c > o.shift(1)))).astype(int)
    result["spinning_top"] = ((body / rng < 0.3) & (upper > body) & (lower > body)).astype(int)

    # -- Double-candle patterns --
    bullish_engulf = (c.shift(1) < o.shift(1)) & (c > o) & (o <= c.shift(1)) & (c >= o.shift(1)) & (body > body.shift(1))
    bearish_engulf = (c.shift(1) > o.shift(1)) & (c < o) & (o >= c.shift(1)) & (c <= o.shift(1)) & (body > body.shift(1))
    result["bullish_engulfing"] = bullish_engulf.astype(int)
    result["bearish_engulfing"] = bearish_engulf.astype(int)

    harami_small = body < body.shift(1) * 0.5
    result["bullish_harami"] = ((c.shift(1) < o.shift(1)) & (c > o) & harami_small &
                                 (o > c.shift(1)) & (c < o.shift(1))).astype(int)
    result["bearish_harami"] = ((c.shift(1) > o.shift(1)) & (c < o) & harami_small &
                                 (o < c.shift(1)) & (c > o.shift(1))).astype(int)

    prev_down = c.shift(1) < o.shift(1)
    prev_up = c.shift(1) > o.shift(1)
    mid_prev = (o.shift(1) + c.shift(1)) / 2
    result["piercing_line"] = (prev_down & (c > o) & (o < c.shift(1)) & (c > mid_prev) & (c < o.shift(1))).astype(int)
    result["dark_cloud"] = (prev_up & (c < o) & (o > c.shift(1)) & (c < mid_prev) & (c > o.shift(1))).astype(int)

    # -- Triple-candle patterns --
    up3 = (c > o) & (c > c.shift(1))
    down3 = (c < o) & (c < c.shift(1))
    result["three_white_soldiers"] = (up3 & up3.shift(1) & up3.shift(2)).astype(int)
    result["three_black_crows"] = (down3 & down3.shift(1) & down3.shift(2)).astype(int)

    is_small = body < body.rolling(20).mean() * 0.5
    result["morning_star"] = (down3.shift(2) & is_small.shift(1) & up3).astype(int)
    result["evening_star"] = (up3.shift(2) & is_small.shift(1) & down3).astype(int)

    return result


# =============================================================================
# Chart Patterns (from pattern_tool.py — pure pandas)
# =============================================================================

def find_peaks_valleys(close: pd.Series, window: int = 5) -> dict:
    n = len(close)
    if n < 2 * window + 1:
        return {"peaks": [], "valleys": []}
    values = close.values.astype(float)
    peaks, valleys = [], []
    for i in range(window, n - window):
        seg = values[i - window: i + window + 1]
        if np.isnan(values[i]):
            continue
        seg = seg[~np.isnan(seg)]
        if len(seg) == 0:
            continue
        if values[i] == np.max(seg):
            peaks.append(i)
        if values[i] == np.min(seg):
            valleys.append(i)
    return {"peaks": peaks, "valleys": valleys}


def detect_head_and_shoulders(close: pd.Series, window: int = 10) -> pd.Series:
    result = pd.Series(0, index=close.index, dtype=int)
    pv = find_peaks_valleys(close, window=window)
    peaks, vals = pv["peaks"], close.values.astype(float)
    if len(peaks) < 3:
        return result
    for i in range(len(peaks) - 2):
        lv, hv, rv = vals[peaks[i]], vals[peaks[i + 1]], vals[peaks[i + 2]]
        if any(np.isnan(x) for x in (lv, hv, rv)):
            continue
        if hv <= lv or hv <= rv:
            continue
        avg = (lv + rv) / 2
        if avg == 0 or abs(lv - rv) / avg > 0.05:
            continue
        result.iloc[peaks[i + 1]] = 1
    return result


def detect_double_top_bottom(close: pd.Series, window: int = 10) -> pd.Series:
    result = pd.Series(0, index=close.index, dtype=int)
    pv = find_peaks_valleys(close, window=window)
    vals = close.values.astype(float)
    for lst, output in [(pv["peaks"], 1), (pv["valleys"], -1)]:
        if len(lst) < 2:
            continue
        for i in range(len(lst) - 1):
            v1, v2 = vals[lst[i]], vals[lst[i + 1]]
            if any(np.isnan(x) for x in (v1, v2)):
                continue
            if v1 == 0 or abs(v1 - v2) / abs(v1) > 0.03:
                continue
            dist = lst[i + 1] - lst[i]
            if dist < window or dist > window * 6:
                continue
            result.iloc[lst[i + 1]] = output
    return result


def detect_triangle(close: pd.Series, window: int = 20) -> pd.Series:
    result = pd.Series(0, index=close.index, dtype=int)
    slopes = pd.Series(np.nan, index=close.index)
    vals = close.values.astype(float)
    x = np.arange(window, dtype=float)
    for i in range(window - 1, len(close)):
        seg = vals[i - window + 1: i + 1]
        if np.any(np.isnan(seg)):
            continue
        slopes.iloc[i] = np.polyfit(x, seg, 1)[0]
    pv = find_peaks_valleys(close, window=window // 2)
    for lst, out in [(pv["peaks"], 1), (pv["valleys"], -1)]:
        if len(lst) < 3:
            continue
        for i in range(len(lst) - 2):
            s1 = slopes.iloc[lst[i]] if not pd.isna(slopes.iloc[lst[i]]) else 0
            s2 = slopes.iloc[lst[i + 1]] if not pd.isna(slopes.iloc[lst[i + 1]]) else 0
            s3 = slopes.iloc[lst[i + 2]] if not pd.isna(slopes.iloc[lst[i + 2]]) else 0
            if out == 1 and s1 > s2 > s3:
                result.iloc[lst[i + 2]] = 1
            elif out == -1 and s1 < s2 < s3:
                result.iloc[lst[i + 2]] = -1
    return result


def detect_broadening(close: pd.Series, window: int = 20) -> pd.Series:
    result = pd.Series(0, index=close.index, dtype=int)
    pv = find_peaks_valleys(close, window=window // 2)
    if len(pv["peaks"]) < 2 or len(pv["valleys"]) < 2:
        return result
    peaks = [close.values.astype(float)[i] for i in pv["peaks"]]
    valleys = [close.values.astype(float)[i] for i in pv["valleys"]]
    if len(peaks) >= 3 and len(valleys) >= 3:
        peak_expanding = peaks[-1] > peaks[-2] > peaks[-3]
        valley_expanding = valleys[-1] < valleys[-2] < valleys[-3]
        if peak_expanding and valley_expanding:
            result.iloc[-1] = 1
    return result


# =============================================================================
# Ichimoku (from vt-ichimoku skill — pure pandas)
# =============================================================================

def detect_ichimoku(df: pd.DataFrame, tenkan: int = 9, kijun: int = 26, senkou_b: int = 52) -> pd.DataFrame:
    """Compute Ichimoku five-line system and generate signals."""
    high, low, close = df["high"], df["low"], df["close"]

    def donchian_mid(h: pd.Series, l: pd.Series, period: int) -> pd.Series:
        return (h.rolling(period).max() + l.rolling(period).min()) / 2

    result = pd.DataFrame(index=df.index)
    result["tenkan_sen"] = donchian_mid(high, low, tenkan)
    result["kijun_sen"] = donchian_mid(high, low, kijun)
    result["senkou_span_a"] = ((result["tenkan_sen"] + result["kijun_sen"]) / 2).shift(kijun)
    result["senkou_span_b"] = donchian_mid(high, low, senkou_b).shift(kijun)
    result["chikou_span"] = close.shift(-kijun)

    # Signal: TK cross + cloud position + cloud color
    tk_cross_up = (result["tenkan_sen"] > result["kijun_sen"]) & (result["tenkan_sen"].shift(1) <= result["kijun_sen"].shift(1))
    tk_cross_down = (result["tenkan_sen"] < result["kijun_sen"]) & (result["tenkan_sen"].shift(1) >= result["kijun_sen"].shift(1))
    above_cloud = close > result[["senkou_span_a", "senkou_span_b"]].max(axis=1)
    below_cloud = close < result[["senkou_span_a", "senkou_span_b"]].min(axis=1)
    cloud_green = result["senkou_span_a"] > result["senkou_span_b"]

    result["signal"] = 0
    result.loc[tk_cross_up & above_cloud & cloud_green, "signal"] = 1
    result.loc[tk_cross_up & above_cloud, "signal"] = result["signal"].where(lambda x: x != -1, 1)
    result.loc[tk_cross_down & below_cloud & ~cloud_green, "signal"] = -1

    result["trade_date"] = df["trade_date"]
    return result


# =============================================================================
# Elliott Wave (from vt-elliott-wave skill — pure pandas)
# =============================================================================

def detect_elliott(df: pd.DataFrame) -> pd.DataFrame:
    """Detect Elliott Wave 5-wave impulse + ABC corrective patterns via Zigzag."""
    high, low, close = df["high"].values.astype(float), df["low"].values.astype(float), df["close"].values.astype(float)
    n = len(close)

    # Simple Zigzag — local extrema with minimum swing threshold
    swings: list[dict] = []
    last_extreme = 0
    last_type = ""
    atr = pd.Series(df["high"] - df["low"]).rolling(14).mean().fillna(0).values
    min_swing = np.nanmean(atr) * 0.5 if not np.isnan(np.nanmean(atr)) else 0.01 * close[-1]

    for i in range(2, n - 2):
        if high[i] >= high[i - 1] and high[i] >= high[i - 2] and high[i] > high[i + 1] and high[i] > high[i + 2]:
            if last_type != "high" and abs(high[i] - last_extreme) > min_swing:
                swings.append({"idx": i, "price": float(high[i]), "type": "high"})
                last_extreme, last_type = float(high[i]), "high"
        if low[i] <= low[i - 1] and low[i] <= low[i - 2] and low[i] < low[i + 1] and low[i] < low[i + 2]:
            if last_type != "low" and abs(low[i] - last_extreme) > min_swing:
                swings.append({"idx": i, "price": float(low[i]), "type": "low"})
                last_extreme, last_type = float(low[i]), "low"

    signals = pd.Series(0, index=df.index, dtype=int)
    surge_points = []
    # Scan for 5-swing impulse (3 rules: higher highs, higher lows, proper fib)
    if len(swings) >= 5:
        for i in range(len(swings) - 4):
            s0, s1, s2, s3, s4 = swings[i], swings[i + 1], swings[i + 2], swings[i + 3], swings[i + 4]
            # Wave 1 up
            if not (s0["type"] == "low" and s1["type"] == "high"):
                continue
            wave1 = s1["price"] - s0["price"]
            if wave1 <= 0:
                continue
            wave2_retrace = (s1["price"] - s2["price"]) / wave1
            if not (0.382 < wave2_retrace < 0.786):
                continue
            if s2["price"] <= s0["price"]:
                continue
            wave3 = s3["price"] - s2["price"]
            if wave3 <= 0:
                continue
            if wave3 < wave1 * 1.0 or wave3 > wave1 * 4.236:
                continue
            wave4_retrace = (s3["price"] - s4["price"]) / wave3
            if not (0.236 < wave4_retrace < 0.5):
                continue
            if s4["price"] <= s1["price"]:
                continue
            signals.iloc[s4["idx"]] = 1  # impulse complete
            surge_points.append({"date": str(df["trade_date"].iloc[s4["idx"]]), "type": "impulse_5_wave"})

    result = pd.DataFrame({"trade_date": df["trade_date"], "elliott_signal": signals.values})
    result["elliott_summary"] = json.dumps({"n_swings": len(swings), "surge_points": surge_points[-5:]})
    return result


# =============================================================================
# Harmonic Patterns (from vt-harmonic skill — pure pandas fallback)
# =============================================================================

HARMONIC_PATTERNS = {
    "gartley":    {"XA_AB": (0.618, 0.618), "BC_AB": (0.382, 0.886), "CD_BC": (1.272, 1.618), "XA_AD": (0.786, 0.786)},
    "bat":        {"XA_AB": (0.382, 0.500), "BC_AB": (0.382, 0.886), "CD_BC": (1.618, 2.618), "XA_AD": (0.886, 0.886)},
    "butterfly":  {"XA_AB": (0.786, 0.786), "BC_AB": (0.382, 0.886), "CD_BC": (1.618, 2.618), "XA_AD": (1.272, 1.618)},
    "crab":       {"XA_AB": (0.382, 0.618), "BC_AB": (0.382, 0.886), "CD_BC": (2.240, 3.618), "XA_AD": (1.618, 1.618)},
}


def detect_harmonic(df: pd.DataFrame) -> pd.DataFrame:
    """Detect harmonic patterns (Gartley, Bat, Butterfly, Crab) using pure pandas."""
    high, low = df["high"].values.astype(float), df["low"].values.astype(float)
    n = len(high)

    # Find swing points
    swings: list[dict] = []
    for i in range(3, n - 3):
        if high[i] >= max(high[i - 3:i]) and high[i] >= max(high[i + 1:i + 4]):
            swings.append({"idx": i, "price": float(high[i]), "type": "high"})
        if low[i] <= min(low[i - 3:i]) and low[i] <= min(low[i + 1:i + 4]):
            swings.append({"idx": i, "price": float(low[i]), "type": "low"})

    # Merge consecutive same-type swings
    merged = [swings[0]] if swings else []
    for s in swings[1:]:
        prev = merged[-1]
        if s["type"] == prev["type"]:
            if (s["type"] == "high" and s["price"] > prev["price"]) or (s["type"] == "low" and s["price"] < prev["price"]):
                merged[-1] = s
        else:
            merged.append(s)

    # Scan XABCD patterns
    result = pd.Series(0, index=df.index, dtype=int)
    found = []
    if len(merged) >= 5:
        for i in range(len(merged) - 4):
            X, A, B, C, D = merged[i], merged[i + 1], merged[i + 2], merged[i + 3], merged[i + 4]
            if not (X["type"] == A["type"]):  # Need alternating
                continue
            XA = abs(A["price"] - X["price"])
            AB = abs(B["price"] - A["price"])
            BC = abs(C["price"] - B["price"])
            CD = abs(D["price"] - C["price"])
            AD = abs(D["price"] - A["price"])
            if any(v == 0 for v in [XA, AB, BC]):
                continue

            for name, ratios in HARMONIC_PATTERNS.items():
                if not (ratios["XA_AB"][0] <= AB / XA <= ratios["XA_AB"][1]):
                    continue
                if not (ratios["BC_AB"][0] <= BC / AB <= ratios["BC_AB"][1]):
                    continue
                if not (ratios["CD_BC"][0] <= CD / BC <= ratios["CD_BC"][1]):
                    continue
                if not (ratios["XA_AD"][0] <= AD / XA <= ratios["XA_AD"][1]):
                    continue
                result.iloc[D["idx"]] = 1
                found.append({"date": str(df["trade_date"].iloc[D["idx"]]), "pattern": name, "type": A["type"], "price": D["price"]})

    return pd.DataFrame({"trade_date": df["trade_date"], "harmonic_signal": result.values,
                         "harmonic_summary": json.dumps({"found": found[-5:]})})


# =============================================================================
# SMC / ICT (Smart Money Concepts) — requires smartmoneyconcepts library
# =============================================================================

def detect_smc(df: pd.DataFrame, swing_length: int = 10, close_break: bool = True) -> pd.DataFrame:
    """Detect Smart Money Concepts patterns: BOS, ChoCH, FVG.

    Requires: pip install smartmoneyconcepts
    """
    try:
        from smartmoneyconcepts import smc as smc_lib
    except ImportError:
        raise ImportError("smartmoneyconcepts not installed. Run: pip install smartmoneyconcepts")

    ohlc = df[["open", "high", "low", "close", "volume"]].copy()
    ohlc.columns = ["open", "high", "low", "close", "volume"]

    if len(ohlc) < swing_length * 2:
        return pd.DataFrame({"trade_date": df["trade_date"], "smc_signal": 0})

    swing_hl = smc_lib.swing_highs_lows(ohlc, swing_length=swing_length)
    bos_choch = smc_lib.bos_choch(ohlc, swing_highs_lows=swing_hl, close_break=close_break)
    fvg = smc_lib.fvg(ohlc)

    bos_val = bos_choch["BOS"].fillna(0).astype(int)
    choch_val = bos_choch["CHOCH"].fillna(0).astype(int)
    fvg_val = fvg["FVG"].fillna(0).astype(int)

    structure = choch_val.where(choch_val != 0, bos_val)
    buy = (structure == 1) & (fvg_val >= 0)
    sell = (structure == -1) & (fvg_val <= 0)
    signal = buy.astype(int) - sell.astype(int)

    bos_count = int((bos_val != 0).sum())
    choch_count = int((choch_val != 0).sum())
    fvg_count = int((fvg_val != 0).sum())

    return pd.DataFrame({
        "trade_date": df["trade_date"],
        "smc_signal": signal.values,
        "smc_summary": json.dumps({
            "bos_count": bos_count, "choch_count": choch_count, "fvg_count": fvg_count,
            "swing_length": swing_length, "latest_signal": int(signal.iloc[-1]),
        }),
    })


# =============================================================================
# Chanlun (缠论) — requires czsc library
# =============================================================================

def detect_chanlun(df: pd.DataFrame, freq: str = "D") -> pd.DataFrame:
    """Detect Chanlun (缠论) patterns: 分型, 笔, 中枢, 一买/一卖 signals.

    Requires: pip install czsc
    """
    try:
        from czsc import CZSC, RawBar, Freq, ZS
        from czsc.signals.cxt import (
            cxt_first_buy_V221126, cxt_first_sell_V221126,
            cxt_bi_base_V230228, cxt_three_bi_V230618, cxt_five_bi_V230619,
        )
    except ImportError:
        raise ImportError("czsc not installed. Run: pip install czsc")

    freq_map = {"D": Freq.D, "W": Freq.W, "M": Freq.M, "60m": Freq.F60, "30m": Freq.F30}
    czsc_freq = freq_map.get(freq, Freq.D)

    # Convert DF to czsc RawBar list
    bars = []
    for i, (_, row) in enumerate(df.iterrows()):
        from datetime import datetime
        dt = row["trade_date"]
        if not isinstance(dt, datetime):
            dt = pd.Timestamp(dt).to_pydatetime()
        bars.append(RawBar(
            symbol="X", id=i, dt=dt, freq=czsc_freq,
            open=float(row["open"]), close=float(row["close"]),
            high=float(row["high"]), low=float(row["low"]),
            vol=float(row.get("volume", 0)), amount=0.0,
        ))

    signal = pd.Series(0, index=df.index)
    if len(bars) < 30:
        return pd.DataFrame({"trade_date": df["trade_date"], "chanlun_signal": signal.values,
                             "chanlun_summary": json.dumps({"error": "Insufficient bars (need >= 30)"})})

    def _compute_signals(c: CZSC) -> dict:
        """Manually compute all Chanlun signals for current bar."""
        s = {}
        try:
            s.update(cxt_first_buy_V221126(c))
            s.update(cxt_first_sell_V221126(c))
            s.update(cxt_bi_base_V230228(c))
            s.update(cxt_three_bi_V230618(c))
            s.update(cxt_five_bi_V230619(c))
        except Exception:
            pass
        return s

    def _check_zhongshu(bi_list: list):
        """Find the most recent valid 中枢."""
        if len(bi_list) < 3:
            return None
        for i in range(len(bi_list) - 3, max(len(bi_list) - 10, -1), -1):
            try:
                zs = ZS(bis=bi_list[i:i + 3])
                if zs.is_valid():
                    return zs
            except Exception:
                continue
        return None

    c = CZSC(bars[:30], max_bi_num=50)
    signal_count = {"buy": 0, "sell": 0}
    for bar in bars[30:]:
        c.update(bar)
        sig = 0

        # Compute signals for current state
        raw_signals = _compute_signals(c)
        s = {str(k): str(v) for k, v in raw_signals.items()}
        if not s:
            continue

        # Parse signals — check for buy/sell keywords
        buy1 = any("BUY1" in k and "一买" in v for k, v in s.items())
        sell1 = any("SELL1" in k and "一卖" in v for k, v in s.items())

        three_bi = {k: v for k, v in s.items() if "三笔" in k}
        five_bi = {k: v for k, v in s.items() if "五笔" in k}
        bi_key = {k: v for k, v in s.items() if "V230228" in k}

        if buy1:
            sig = 1
        elif sell1:
            sig = -1
        elif three_bi:
            val = list(three_bi.values())[0]
            if "向上盘背" in val or "向上" in val:
                sig = 1
            elif "向下盘背" in val or "向下" in val:
                sig = -1
        elif five_bi:
            val = list(five_bi.values())[0]
            if "类一买" in val:
                sig = 1
            elif "类一卖" in val:
                sig = -1
        elif bi_key and len(c.bi_list) >= 3:
            val = list(bi_key.values())[0]
            zs = _check_zhongshu(c.bi_list)
            if zs is not None:
                last_close = c.bars_raw[-1].close
                if "向下_转折" in val and last_close <= zs.zd:
                    sig = 1
                elif "向上_转折" in val and last_close >= zs.zg:
                    sig = -1

        if sig == 1:
            signal_count["buy"] += 1
        elif sig == -1:
            signal_count["sell"] += 1
        signal.iloc[bar.id] = sig

    return pd.DataFrame({
        "trade_date": df["trade_date"],
        "chanlun_signal": signal.values,
        "chanlun_summary": json.dumps({
            "n_bars": len(bars), "n_bi": len(c.bi_list),
            "buy_signals": signal_count["buy"], "sell_signals": signal_count["sell"],
            "latest_signal": int(signal.iloc[-1]),
        }),
    })


# =============================================================================
# Main CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(description="Unified pattern detection for OHLCV data")
    parser.add_argument("--input", required=True, help="Path to OHLCV CSV")
    parser.add_argument("--method", required=True,
                        choices=["candlestick", "chart", "elliott", "harmonic", "ichimoku", "smc", "chanlun", "all"])
    parser.add_argument("--output", help="Optional output CSV path")
    parser.add_argument("--window", type=int, default=10, help="Detection window for chart patterns (default: 10)")
    args = parser.parse_args()

    df = _load_ohlcv(args.input)
    results = {}

    if args.method in ("candlestick", "all"):
        cand = detect_candlestick_15(df)
        results["candlestick"] = cand
        # Print summary
        for col in cand.columns:
            total = cand[col].sum()
            if total > 0:
                print(f"  {col}: {int(total)} occurrences", file=sys.stderr)

    if args.method in ("chart", "all"):
        close = df["close"]
        chart = pd.DataFrame({"trade_date": df["trade_date"]})
        chart["head_shoulders"] = detect_head_and_shoulders(close, args.window)
        chart["double_top_bottom"] = detect_double_top_bottom(close, args.window)
        chart["triangle"] = detect_triangle(close, args.window)
        chart["broadening"] = detect_broadening(close, args.window)
        pv = find_peaks_valleys(close, args.window)
        chart["peaks"] = 0
        chart["valleys"] = 0
        for idx in pv["peaks"]:
            if idx < len(chart):
                chart.iloc[idx, chart.columns.get_loc("peaks")] = 1
        for idx in pv["valleys"]:
            if idx < len(chart):
                chart.iloc[idx, chart.columns.get_loc("valleys")] = 1
        results["chart"] = chart
        for col in ["head_shoulders", "double_top_bottom", "triangle", "broadening"]:
            total = (chart[col] != 0).sum()
            if total > 0:
                print(f"  {col}: {int(total)} occurrences", file=sys.stderr)

    if args.method in ("elliott", "all"):
        results["elliott"] = detect_elliott(df)
        print(f"  elliott: see elliott_summary column", file=sys.stderr)

    if args.method in ("harmonic", "all"):
        results["harmonic"] = detect_harmonic(df)
        print(f"  harmonic: see harmonic_summary column", file=sys.stderr)

    if args.method in ("ichimoku", "all"):
        results["ichimoku"] = detect_ichimoku(df)
        sig_last = results["ichimoku"]["signal"].tail(1).values[0]
        print(f"  ichimoku: latest signal = {sig_last}", file=sys.stderr)

    if args.method in ("smc", "all"):
        try:
            results["smc"] = detect_smc(df)
            msg = results["smc"]["smc_summary"].iloc[-1] if len(results["smc"]) > 0 else "{}"
            print(f"  smc: {msg}", file=sys.stderr)
        except ImportError as e:
            print(f"  smc: SKIPPED — {e}", file=sys.stderr)

    if args.method in ("chanlun", "all"):
        try:
            results["chanlun"] = detect_chanlun(df)
            msg = results["chanlun"]["chanlun_summary"].iloc[-1] if len(results["chanlun"]) > 0 else "{}"
            print(f"  chanlun: {msg}", file=sys.stderr)
        except ImportError as e:
            print(f"  chanlun: SKIPPED — {e}", file=sys.stderr)

    if args.output:
        # Merge all non-summary columns into one CSV
        merged = pd.DataFrame({"trade_date": df["trade_date"]})
        for key, rdf in results.items():
            if isinstance(rdf, pd.DataFrame):
                for col in rdf.columns:
                    if col != "trade_date":
                        merged[f"{key}_{col}"] = rdf[col].values if col in rdf else rdf[col]
        merged.to_csv(args.output, index=False)
        print(f"Results written to {args.output}")
    else:
        # JSON summary
        summary = {}
        for key, rdf in results.items():
            if isinstance(rdf, pd.DataFrame):
                # Only include signal columns where non-zero exists
                for col in rdf.columns:
                    if col != "trade_date" and rdf[col].dtype in (int, float) and (rdf[col] != 0).any():
                        summary[f"{key}_pattern_count"] = int((rdf[col] != 0).sum())
        print(_to_json(summary))


if __name__ == "__main__":
    main()
