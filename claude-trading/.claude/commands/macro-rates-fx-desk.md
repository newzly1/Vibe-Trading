---
description: Cross-asset macro desk: global rates analyst + FX strategist + commodity/inflation analyst + macro portfolio manager. Covers central bank policy, yield curve dynamics, currency positioning, and macro-driven asset allocation.
argument-hint: [goal] [timeframe]
---

# Macro / Rates / FX Desk

Native replacement for the Vibe-Trading `macro_rates_fx_desk` swarm preset. You are the orchestrator. Dispatch each role below as a subagent with the **Agent** tool (`subagent_type` = the agent name shown in backticks), honoring the phase order: **phases run sequentially**, and all agents **within one phase run in parallel** — dispatch a phase's agents together in a single message. Pass each downstream agent the upstream outputs named in its bullet.

**Inputs** (from `$ARGUMENTS`):
- `<goal>` = `$1` — Macro investment objective (e.g., Q2 2026 cross-asset positioning, rate cycle trade)
- `<timeframe>` = `$2` — Investment horizon (tactical 1-3 months / strategic 6-12 months)

## Phase 1 (parallel)
- **`macro-rates-fx-desk-rates-analyst`** — "Analyze the global rates environment: Fed path, yield curve signals, China-US rate differential, and cross-asset rate implications. Goal: <goal>. Horizon: <timeframe>."
- **`macro-rates-fx-desk-fx-strategist`** — "Analyze the FX landscape: DXY, USD/CNY, HKD peg, major crosses, and portfolio hedging implications. Goal: <goal>. Horizon: <timeframe>."
- **`macro-rates-fx-desk-commodity-inflation-analyst`** — "Analyze commodity and inflation dynamics: energy, metals, inflation indicators, and asset allocation implications. Goal: <goal>. Horizon: <timeframe>."

## Phase 2
- **`macro-rates-fx-desk-macro-pm`** — "Synthesize rates, FX, and commodity/inflation analyses into a macro-driven cross-asset allocation recommendation. Goal: <goal>. Horizon: <timeframe>."
  - Provide as `rates`: the **Global Rates & Yield Curve Analyst** (`macro-rates-fx-desk-rates-analyst`) output from an earlier phase.
  - Provide as `fx`: the **FX Strategist** (`macro-rates-fx-desk-fx-strategist`) output from an earlier phase.
  - Provide as `commodity_inflation`: the **Commodity & Inflation Analyst** (`macro-rates-fx-desk-commodity-inflation-analyst`) output from an earlier phase.

## Final output
Return the **Macro Portfolio Manager** output as the team's deliverable, citing the supporting analysis from earlier phases.
