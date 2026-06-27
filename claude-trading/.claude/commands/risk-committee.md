---
description: Drawdown, tail risk, and market regime reviews run in parallel; head of risk signs off.
argument-hint: [goal]
---

# Risk Committee

Native replacement for the Vibe-Trading `risk_committee` swarm preset. You are the orchestrator. Dispatch each role below as a subagent with the **Agent** tool (`subagent_type` = the agent name shown in backticks), honoring the phase order: **phases run sequentially**, and all agents **within one phase run in parallel** — dispatch a phase's agents together in a single message. Pass each downstream agent the upstream outputs named in its bullet.

**Inputs** (from `$ARGUMENTS`):
- `<goal>` = `$1` — Audit target (e.g., BTC position risk, CSI 300 strategy risk)

## Phase 1 (parallel)
- **`risk-committee-drawdown-analyst`** — "Analyze historical drawdown behavior and current drawdown risk for <goal>."
- **`risk-committee-tail-risk-analyst`** — "Assess tail risk for <goal> under extreme market conditions."
- **`risk-committee-regime-detector`** — "Determine the current market regime for <goal>."

## Phase 2
- **`risk-committee-aggregator`** — "Integrate the three risk dimensions into a complete risk audit report."
  - Provide as `drawdown`: the **Drawdown Analyst** (`risk-committee-drawdown-analyst`) output from an earlier phase.
  - Provide as `tail_risk`: the **Tail Risk Analyst** (`risk-committee-tail-risk-analyst`) output from an earlier phase.
  - Provide as `regime`: the **Market Regime Analyst** (`risk-committee-regime-detector`) output from an earlier phase.

## Final output
Return the **Head of Risk** output as the team's deliverable, citing the supporting analysis from earlier phases.
