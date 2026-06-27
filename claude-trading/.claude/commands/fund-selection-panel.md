---
description: Multi-dimensional quantitative screening → Brinson performance attribution and style analysis → FOF portfolio weight optimization, sequential professional review chain
argument-hint: [fund_type] [goal]
---

# Fund Selection Panel

Native replacement for the Vibe-Trading `fund_selection_panel` swarm preset. You are the orchestrator. Dispatch each role below as a subagent with the **Agent** tool (`subagent_type` = the agent name shown in backticks), honoring the phase order: **phases run sequentially**, and all agents **within one phase run in parallel** — dispatch a phase's agents together in a single message. Pass each downstream agent the upstream outputs named in its bullet.

**Inputs** (from `$ARGUMENTS`):
- `<fund_type>` = `$1` — Fund type, e.g.: equity / bond / balanced / index-enhanced / quant hedge / QDII
- `<goal>` = `$2` — Investment objective, e.g.: build a steady FOF portfolio with annualized return >10% and max drawdown <15%

## Phase 1
- **`fund-selection-panel-fund-screener`** — "Conduct systematic multi-dimensional screening of <fund_type> funds with the objective: <goal>. Apply the six-dimensional screening framework (scale / performance / risk / manager / holdings / operations) and output the candidate fund list, screening funnel report, and preliminary ranking."

## Phase 2
- **`fund-selection-panel-attribution-analyst`** — "Conduct deep performance attribution analysis on candidate funds: Brinson three-effect decomposition, Barra style factor exposure, excess return quality rating, up/down capture rate comparison. Output attribution report and shortlist for FOF construction. Objective: <goal>."
  - Provide as `candidate_funds`: the **Fund Screener** (`fund-selection-panel-fund-screener`) output from an earlier phase.

## Phase 3
- **`fund-selection-panel-fof-optimizer`** — "Construct and optimize an FOF portfolio from the shortlisted funds. Compare mean-variance / risk parity / equal-weight schemes, run historical stress tests, and output the recommended weight scheme, expected performance metrics, and rebalancing rulebook. Objective: <goal>."
  - Provide as `selected_funds`: the **Performance Attribution Analyst** (`fund-selection-panel-attribution-analyst`) output from an earlier phase.
  - Provide as `candidate_funds`: the **Fund Screener** (`fund-selection-panel-fund-screener`) output from an earlier phase.

## Final output
Return the **FOF Portfolio Optimizer** output as the team's deliverable, citing the supporting analysis from earlier phases.
