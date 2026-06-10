# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Essential Commands

```bash
# Install (editable + dev deps)
pip install -e ".[dev]"

# Full test suite (exclude e2e and live-LLM tests)
pytest --ignore=agent/tests/e2e_backtest --ignore=agent/tests/test_e2e_harness_v2.py --tb=short -q

# Factor/alpha zoo gates only
pytest agent/tests/factors/test_alpha_purity.py agent/tests/factors/test_lookahead.py -q

# Live trading safety tests
pytest agent/tests/test_sdk_order_gate.py agent/tests/test_mandate_enforcement.py agent/tests/test_killswitch_blocks_orders.py agent/tests/test_readonly_default.py -q

# Syntax check (before running tests)
cd agent && python -m compileall -q cli && python -m py_compile api_server.py mcp_server.py

# Frontend
cd frontend && npm ci && npm run build      # build
cd frontend && npx vitest run               # test
cd frontend && npm run dev                   # dev server (port 5899)

# Lint (ruff config in pyproject.toml)
ruff check agent/

# Docker
docker compose up --build
```

## Architecture

### Package Layout

`pyproject.toml` maps `package-dir = {"" = "agent"}` — **`agent/` is the Python package root**. Inside it, `src/`, `backtest/`, and `cli/` are top-level packages. The CLI entry points are `vibe-trading` → `cli:main` and `vibe-trading-mcp` → `mcp_server:main`.

### Agent Loop (`agent/src/agent/loop.py`)

ReAct loop with 5-layer context compression (microcompact, context_collapse, auto_compact, compact tool, iterative update). Estimates tokens at ~4 chars/token. Batches consecutive read-only tools for parallel execution via threads. Shell tools (`bash`, `background_run`) are gated by `include_shell_tools` — disabled in networked server entry points. The loop emits heartbeats (3s default) and per-tool progress events for live UI feedback.

### Tool Auto-Discovery (`agent/src/tools/__init__.py`)

**No manual registration.** Tools are discovered by scanning `BaseTool.__subclasses__()`. To add a tool: create a file in `agent/src/tools/` with a class extending `BaseTool`, give it a non-empty `name`, implement `execute(**kwargs) -> str` (returns JSON). Missing deps are handled via `check_available() -> False` — the tool is silently skipped.

`build_registry()` wires local tools first, then optionally appends MCP tools from `AgentConfig.mcp_servers`. Shell tools, goal tools, and swarm tools receive special constructor injection (persistent memory, session_id, event_callbacks). Live-broker MCP channels route through the `trading_*` connector surface, not raw `mcp_<broker>_*` wrappers.

### Backtest System (`agent/backtest/`)

- **`runner.py`**: Fixed entry point that reads `config.json` from a run directory, resolves the loader (by source/market), imports the signal engine, and runs the backtest engine.
- **`loaders/`**: DataLoader Protocol (`base.py`) with 7 sources and auto-fallback chains (`registry.py`). Retry/budget helpers (`check_budget`, `retry_with_budget`) are the canonical pattern for flaky external APIs.
- **`engines/`**: 7 asset-class engines + `CompositeEngine` (cross-market with shared capital pool) + options portfolio engine. Market detection lives in `engines/_market_hooks.py`, shared between `runner.py` and composite.
- Config validation uses Pydantic (`BacktestConfigSchema`). The `--interval` flag supports `1m`/`5m`/`15m`/`30m`/`1H`/`4H`/`1D`.

### Swarm (`agent/src/swarm/`)

DAG execution engine. 29 presets defined as YAML in `presets/`. `runtime.py` orchestrates workers, each with a filtered tool registry (`build_swarm_registry`). Status reconciles from live task files (crash recovery). `retry_run` relaunches failed/stale runs. Workers can call operator-configured external MCP tools via `mcp_<server>_<tool>` naming.

### Live Trading Safety (`agent/src/live/`)

All broker order paths pass through: mandate (symbol universe, size, exposure, leverage, daily cap), kill switch (filesystem, instant halt), pre-trade order guard (fail-closed), and audit ledger. Paper/live is a structural per-broker guard (account-id format, host, demo flag, trade environment). Connectors without a runtime paper/live discriminator are capped at paper + read-only.

### Frontend (`frontend/`)

React 19 + Vite + TypeScript + Tailwind CSS. Zustand for state management (`stores/agent.ts` is the main agent store). ECharts for charts. React Router v7 with pages: Agent (chat), AlphaZoo, RunDetail, Compare, Correlation, Home, Settings. The Vite dev server proxies `/api`, `/runs`, `/sessions`, `/alpha`, `/swarm`, `/settings`, `/uploads`, `/correlation` to `localhost:8899`.

### Session Layer (`agent/src/session/`)

Multi-turn chat stored as JSONL files (`session_id/messages.jsonl`) with `flush + fsync` on each append for crash safety. FTS5-backed cross-session search (`search.py`). SSE event streaming via `sse-starlette`. Corrupted JSONL lines are skipped with first-200-char logging.

### MCP Dual Role

1. **Server**: `vibe-trading-mcp` exposes 36+ tools via stdio (default) or SSE. Tools are read from the same auto-discovered registry.
2. **Client**: The agent can call external MCP tools configured in `~/.vibe-trading/agent.json`. Tools appear as `mcp_<server>_<tool>`. Supports stdio, SSE, and streamable HTTP transports.

### Key Environment Variables

| Variable | Role |
|----------|------|
| `LANGCHAIN_PROVIDER` | LLM provider name (openrouter, deepseek, groq, ollama, etc.) |
| `<PROVIDER>_API_KEY` / `<PROVIDER>_BASE_URL` | Per-provider credentials |
| `LANGCHAIN_MODEL_NAME` | Model name |
| `API_AUTH_KEY` | Required for non-loopback API access |
| `VIBE_TRADING_ENABLE_SHELL_TOOLS` | Opt-in for shell tools in remote deployments |
| `VIBE_TRADING_ALLOWED_FILE_ROOTS` | Extra paths for document imports |
| `VIBE_TRADING_DATA_CACHE` | Opt-in local data caching (`~/.vibe-trading/cache`) |
| `TUSHARE_TOKEN` | Optional A-share data token (falls back to mootdx/AKShare) |

### Test Organization

Tests live in `agent/tests/`. `conftest.py` provides shared fixtures. Test files are named by feature (not by source module). Key markers: `@pytest.mark.unit` (fast, no network), `@pytest.mark.integration` (may need network). `test_e2e_harness_v2.py` is gated behind `VIBE_TRADING_RUN_LIVE_E2E=1` (real LLM calls).

### Code Style

- Black for formatting, ruff for linting (E/F/W rules, 120-char lines)
- Type annotations on public function/method signatures
- No `Co-Authored-By:` or AI-assistant trailers in commits
- Community commits require DCO `Signed-off-by:` trailer (`git commit -s`)
- Alpha zoo files (`src/factors/zoo/**/*.py`) are exempt from `F401` (unused-import) — the full `base.py` surface is imported verbatim to match research formulas
