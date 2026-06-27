---
description: Stock screening + factor research in parallel → strategy backtest → risk audit.
argument-hint: [market] [goal]
---

# Quant Strategy Desk

Native replacement for the Vibe-Trading `quant_strategy_desk` swarm preset. You are the orchestrator. Dispatch each role below as a subagent with the **Agent** tool (`subagent_type` = the agent name shown in backticks), honoring the phase order: **phases run sequentially**, and all agents **within one phase run in parallel** — dispatch a phase's agents together in a single message. Pass each downstream agent the upstream outputs named in its bullet.

**Inputs** (from `$ARGUMENTS`):
- `<market>` = `$1` — Target market
- `<goal>` = `$2` — Strategy objective (e.g., momentum + value dual factor)

## Phase 1 (parallel)
- **`quant-strategy-desk-screener`** — "Screen <market> for candidates matching the objective '<goal>'."
- **`quant-strategy-desk-factor-miner`** — "Mine alpha factors in <market> suited to strategy '<goal>'."

## Phase 2
- **`quant-strategy-desk-backtester`** — "Build the strategy from screening and factor output and backtest."
  - Provide as `screener_result`: the **Stock Screener** (`quant-strategy-desk-screener`) output from an earlier phase.
  - Provide as `factors`: the **Factor Researcher** (`quant-strategy-desk-factor-miner`) output from an earlier phase.

## Phase 3
- **`quant-strategy-desk-risk-auditor`** — "Audit risk exposures in the backtest and recommend improvements."
  - Provide as `backtest_result`: the **Strategy Backtester** (`quant-strategy-desk-backtester`) output from an earlier phase.

## Final output
Return the **Risk Auditor** output as the team's deliverable, citing the supporting analysis from earlier phases.
