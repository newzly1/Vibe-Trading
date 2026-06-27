---
description: Performance attribution, risk review, and execution quality in parallel; CIO synthesizes into rebalance decisions.
argument-hint: [portfolio] [review_period] [goal]
---

# Portfolio Review Board

Native replacement for the Vibe-Trading `portfolio_review_board` swarm preset. You are the orchestrator. Dispatch each role below as a subagent with the **Agent** tool (`subagent_type` = the agent name shown in backticks), honoring the phase order: **phases run sequentially**, and all agents **within one phase run in parallel** — dispatch a phase's agents together in a single message. Pass each downstream agent the upstream outputs named in its bullet.

**Inputs** (from `$ARGUMENTS`):
- `<portfolio>` = `$1` — Portfolio name or description (e.g., value-growth blend, CSI 300 enhanced)
- `<review_period>` = `$2` — Review cadence (monthly / quarterly)
- `<goal>` = `$3` — Focus of this review (e.g., assess Q1 performance, diagnose recent NAV drawdown)

## Phase 1 (parallel)
- **`portfolio-review-board-attribution-analyst`** — "Performance attribution for portfolio <portfolio>, <review_period>, with emphasis on <goal>."
- **`portfolio-review-board-risk-inspector`** — "Risk health check for portfolio <portfolio>, <review_period>, with emphasis on <goal>."
- **`portfolio-review-board-execution-analyst`** — "Execution quality analysis for portfolio <portfolio> over <review_period>, with emphasis on <goal>."

## Phase 2
- **`portfolio-review-board-chief-investment-officer`** — "Chair the <review_period> review for portfolio <portfolio>; synthesize the three reports into position decisions, emphasizing <goal>."
  - Provide as `attribution_report`: the **Performance Attribution Analyst** (`portfolio-review-board-attribution-analyst`) output from an earlier phase.
  - Provide as `risk_report`: the **Risk Inspector** (`portfolio-review-board-risk-inspector`) output from an earlier phase.
  - Provide as `execution_report`: the **Execution Quality Analyst** (`portfolio-review-board-execution-analyst`) output from an earlier phase.

## Final output
Return the **Chief Investment Officer** output as the team's deliverable, citing the supporting analysis from earlier phases.
