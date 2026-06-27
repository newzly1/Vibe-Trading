---
description: Classic TA + Ichimoku + harmonic patterns + Elliott Wave + SMC run in parallel → signal aggregator scores consensus and resonance.
argument-hint: [target] [timeframe]
---

# Technical Analysis Panel

Native replacement for the Vibe-Trading `technical_analysis_panel` swarm preset. You are the orchestrator. Dispatch each role below as a subagent with the **Agent** tool (`subagent_type` = the agent name shown in backticks), honoring the phase order: **phases run sequentially**, and all agents **within one phase run in parallel** — dispatch a phase's agents together in a single message. Pass each downstream agent the upstream outputs named in its bullet.

**Inputs** (from `$ARGUMENTS`):
- `<target>` = `$1` — Symbol (e.g. 600519.SH Kweichow Moutai, BTC-USDT, AAPL)
- `<timeframe>` = `$2` — Interval (e.g. daily, weekly, monthly, 4H)

## Phase 1 (parallel)
- **`technical-analysis-panel-classic-ta-analyst`** — "Classic TA on <target> at <timeframe>: direction and key levels."
- **`technical-analysis-panel-ichimoku-analyst`** — "Ichimoku on <target> at <timeframe>: cloud, TK, Chikou, time theory."
- **`technical-analysis-panel-harmonic-analyst`** — "Harmonic scan on <target> at <timeframe>: PRZ and setups."
- **`technical-analysis-panel-wave-analyst`** — "Elliott wave count on <target> at <timeframe>: position and targets."
- **`technical-analysis-panel-smc-analyst`** — "SMC on <target> at <timeframe>: order blocks, FVG, liquidity."

## Phase 2
- **`technical-analysis-panel-signal-aggregator`** — "Aggregate five TA schools on <target> at <timeframe>: resonance and final call."
  - Provide as `classic_ta`: the **Classic Technical Analyst** (`technical-analysis-panel-classic-ta-analyst`) output from an earlier phase.
  - Provide as `ichimoku`: the **Ichimoku Analyst** (`technical-analysis-panel-ichimoku-analyst`) output from an earlier phase.
  - Provide as `harmonic`: the **Harmonic Pattern Analyst** (`technical-analysis-panel-harmonic-analyst`) output from an earlier phase.
  - Provide as `wave`: the **Elliott Wave Analyst** (`technical-analysis-panel-wave-analyst`) output from an earlier phase.
  - Provide as `smc`: the **SMC / Order-Flow Analyst** (`technical-analysis-panel-smc-analyst`) output from an earlier phase.

## Final output
Return the **Signal Aggregator (Judge)** output as the team's deliverable, citing the supporting analysis from earlier phases.
