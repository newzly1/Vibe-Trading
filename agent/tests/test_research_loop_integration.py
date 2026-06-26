"""End-to-end proof of the data->backtest research loop after the
capability-surface trim.

The MCP ``write_file``/``read_file`` tools were removed; backtest inputs are
now authored with Claude Code's native ``Write`` into an allowed run root
(``agent/runs/``). This test reproduces that path in Python: it writes
``config.json`` + ``code/signal_engine.py`` by hand, runs the backtest
through the same entry point the ``backtest`` MCP tool uses, and asserts a
metrics artifact with a numeric Sharpe is produced.

Marked ``integration``: it fetches keyless OKX crypto candles over the
network.
"""

from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
AGENT_DIR = REPO_ROOT / "agent"
RUN_DIR = AGENT_DIR / "runs" / "vt_loop_smoke"  # under an allowed run root

CONFIG = {
    "source": "okx",
    "codes": ["BTC-USDT"],
    "start_date": "2024-01-01",
    "end_date": "2024-06-30",
    "initial_cash": 1000000,
    "commission": 0.001,
    "extra_fields": None,
}

SIGNAL_ENGINE = '''\
"""Minimal MA-crossover strategy for end-to-end verification."""

from typing import Dict

import pandas as pd


class SignalEngine:
    """Long when the fast MA is above the slow MA, flat otherwise."""

    def __init__(self, fast: int = 5, slow: int = 20) -> None:
        self.fast = fast
        self.slow = slow

    def generate(self, data_map: Dict[str, pd.DataFrame]) -> Dict[str, pd.Series]:
        out: Dict[str, pd.Series] = {}
        for code, df in data_map.items():
            fast_ma = df["close"].rolling(self.fast).mean()
            slow_ma = df["close"].rolling(self.slow).mean()
            sig = pd.Series(0.0, index=df.index)
            sig[fast_ma > slow_ma] = 1.0
            out[code] = sig.fillna(0.0)
        return out
'''


@pytest.mark.integration
def test_native_write_then_backtest_produces_metrics() -> None:
    import sys

    sys.path.insert(0, str(AGENT_DIR))
    from src.tools.backtest_tool import run_backtest

    if RUN_DIR.exists():
        shutil.rmtree(RUN_DIR)
    (RUN_DIR / "code").mkdir(parents=True, exist_ok=True)
    (RUN_DIR / "config.json").write_text(json.dumps(CONFIG), encoding="utf-8")
    (RUN_DIR / "code" / "signal_engine.py").write_text(SIGNAL_ENGINE, encoding="utf-8")

    raw = run_backtest(str(RUN_DIR))
    result = json.loads(raw)
    assert result["status"] == "ok", f"backtest failed: {result}"

    metrics_path = RUN_DIR / "artifacts" / "metrics.csv"
    assert metrics_path.exists(), f"metrics.csv not produced; artifacts={result.get('artifacts')}"

    with metrics_path.open(encoding="utf-8") as fh:
        row = next(csv.DictReader(fh))
    assert "sharpe" in row, f"metrics.csv missing 'sharpe' column: {row.keys()}"
    float(row["sharpe"])  # raises ValueError if not numeric
