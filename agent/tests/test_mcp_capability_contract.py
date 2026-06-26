"""Capability-surface contract for the vibe-trading MCP server.

Pins the tool catalogue exposed to Claude Code (the harness):
- Harness-duplicate I/O tools must be ABSENT — Claude Code has native
  Read / Write / WebFetch / WebSearch, so a second copy only confuses the
  model and bloats the tool list.
- No order-placement tool may ever be exposed (port decision #1: live
  trading does not go through Claude Code).
- The research/analysis capability tools must be PRESENT.

NOTE: ``load_skill`` / ``list_skills`` and the swarm/run tools are removed
in later port plans (after native skills / subagents land); they are
intentionally NOT in FORBIDDEN_TOOLS yet.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import time
from pathlib import Path
from queue import Empty, Queue

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
AGENT_DIR = REPO_ROOT / "agent"
LIST_TIMEOUT = 30.0

FORBIDDEN_TOOLS = {"read_file", "write_file", "read_url", "read_document", "web_search"}
ORDER_TOOLS = {
    "place_order",
    "cancel_order",
    "propose_mandate",
    "trading_place_order",
    "trading_cancel_order",
}
REQUIRED_TOOLS = {
    "get_market_data",
    "backtest",
    "factor_analysis",
    "analyze_options",
    "pattern_recognition",
    "alpha_zoo",
    "alpha_bench",
    "alpha_compare",
    "get_fundamentals",
    "get_financial_statements",
    "get_money_flow",
    "get_margin_data",
    "get_earnings_forecast",
    "get_events",
    "analyze_trade_journal",
    "create_hypothesis",
    "search_hypotheses",
    "start_research_goal",
}


def _reader(stream, q: Queue) -> None:
    try:
        for line in iter(stream.readline, b""):
            q.put(line)
    finally:
        q.put(None)


def _send(proc: subprocess.Popen, obj: dict) -> None:
    proc.stdin.write((json.dumps(obj) + "\n").encode("utf-8"))
    proc.stdin.flush()


def _wait_for_id(q: Queue, want_id: int, timeout: float):
    start = time.time()
    while time.time() - start < timeout:
        try:
            line = q.get(timeout=0.5)
        except Empty:
            continue
        if line is None:
            return None
        try:
            obj = json.loads(line.decode("utf-8", errors="replace"))
        except Exception:
            continue
        if obj.get("id") == want_id:
            return obj
    return None


def _list_tool_names() -> set[str]:
    """Spawn the MCP server and return the set of registered tool names."""
    env = os.environ.copy()
    env["PYTHONPATH"] = str(AGENT_DIR) + os.pathsep + env.get("PYTHONPATH", "")
    env["PYTHONUNBUFFERED"] = "1"
    env["FASTMCP_CHECK_FOR_UPDATES"] = "off"
    proc = subprocess.Popen(
        [sys.executable, "-c", "from mcp_server import main; main()"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        bufsize=0,
        env=env,
        cwd=str(AGENT_DIR),
    )
    q: Queue = Queue()
    threading.Thread(target=_reader, args=(proc.stdout, q), daemon=True).start()
    try:
        _send(proc, {
            "jsonrpc": "2.0", "id": 1, "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05", "capabilities": {},
                "clientInfo": {"name": "contract", "version": "1"},
            },
        })
        assert _wait_for_id(q, 1, LIST_TIMEOUT) is not None, "initialize timed out"
        _send(proc, {"jsonrpc": "2.0", "method": "notifications/initialized"})
        _send(proc, {"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        resp = _wait_for_id(q, 2, LIST_TIMEOUT)
        assert resp is not None, "tools/list timed out"
        return {t["name"] for t in (resp.get("result", {}).get("tools") or [])}
    finally:
        try:
            proc.kill()
            proc.wait(timeout=5)
        except Exception:
            pass


@pytest.mark.integration
def test_forbidden_io_tools_absent() -> None:
    leaked = FORBIDDEN_TOOLS & _list_tool_names()
    assert not leaked, f"harness-duplicate tools must not be exposed: {sorted(leaked)}"


@pytest.mark.integration
def test_no_order_placement_tools() -> None:
    leaked = ORDER_TOOLS & _list_tool_names()
    assert not leaked, f"order-placement tools must never be exposed (decision #1): {sorted(leaked)}"


@pytest.mark.integration
def test_required_capability_tools_present() -> None:
    missing = REQUIRED_TOOLS - _list_tool_names()
    assert not missing, f"required capability tools missing: {sorted(missing)}"
