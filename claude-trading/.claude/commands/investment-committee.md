---
description: Long–short debate → risk review → PM final call: buy-side fund investment committee workflow.
argument-hint: [target] [market]
---

# Investment Committee

Native replacement for the Vibe-Trading `investment_committee` swarm preset. You are the orchestrator. Dispatch each role below as a subagent with the **Agent** tool (`subagent_type` = the agent name shown in backticks), honoring the phase order: **phases run sequentially**, and all agents **within one phase run in parallel** — dispatch a phase's agents together in a single message. Pass each downstream agent the upstream outputs named in its bullet.

**Inputs** (from `$ARGUMENTS`):
- `<target>` = `$1` — Security (e.g., 600519.SH Kweichow Moutai, BTC-USDT, AAPL)
- `<market>` = `$2` — Market (e.g., A-shares, Hong Kong, US, crypto)

## Phase 1 (parallel)
- **`investment-committee-bull-advocate`** — "Conduct full bull-side research on <target> and build a complete bullish investment case. Market: <market>."
- **`investment-committee-bear-advocate`** — "Conduct full bear-side research on <target>, identifying all bearish risks and downside logic. Market: <market>."

## Phase 2
- **`investment-committee-risk-officer`** — "Review bull and bear arguments on <target>; from a risk angle assess validity, suggest position size, and propose risk management."
  - Provide as `bull_report`: the **Bull-side Researcher** (`investment-committee-bull-advocate`) output from an earlier phase.
  - Provide as `bear_report`: the **Bear-side Researcher** (`investment-committee-bear-advocate`) output from an earlier phase.

## Phase 3
- **`investment-committee-portfolio-manager`** — "After the debate and risk review on <target>, make the final investment decision and execution plan."
  - Provide as `full_debate`: the **Chief Risk Officer** (`investment-committee-risk-officer`) output from an earlier phase.

## Final output
Return the **Portfolio Manager** output as the team's deliverable, citing the supporting analysis from earlier phases.
