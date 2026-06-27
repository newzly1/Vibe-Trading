---
description: Factor mining + factor validation running in parallel → factor combination construction → backtest review: quant fund internal research review workflow
argument-hint: [market] [factor_type]
---

# Factor Research Committee

Native replacement for the Vibe-Trading `factor_research_committee` swarm preset. You are the orchestrator. Dispatch each role below as a subagent with the **Agent** tool (`subagent_type` = the agent name shown in backticks), honoring the phase order: **phases run sequentially**, and all agents **within one phase run in parallel** — dispatch a phase's agents together in a single message. Pass each downstream agent the upstream outputs named in its bullet.

**Inputs** (from `$ARGUMENTS`):
- `<market>` = `$1` — Target market (e.g.: A-shares, Hong Kong, US equities)
- `<factor_type>` = `$2` — Factor type (value / momentum / quality / growth / alternative)

## Phase 1 (parallel)
- **`factor-research-committee-factor-miner`** — "In the <market> market, mine 5–10 candidate Alpha factors of the <factor_type> type; provide detailed definitions and economic logic."
- **`factor-research-committee-factor-validator`** — "Conduct comprehensive statistical validity testing on <factor_type> candidate factors in the <market> market, including IC analysis, quintile backtest, and robustness testing."

## Phase 2
- **`factor-research-committee-factor-combiner`** — "Based on factor mining and validation results, design the optimal factor combination scheme and build a <factor_type> multi-factor stock selection strategy for the <market> market."
  - Provide as `mine_result`: the **Factor Miner** (`factor-research-committee-factor-miner`) output from an earlier phase.
  - Provide as `validate_result`: the **Factor Validator** (`factor-research-committee-factor-validator`) output from an earlier phase.

## Phase 3
- **`factor-research-committee-backtest-reviewer`** — "Review the backtest results of the <factor_type> multi-factor strategy in the <market> market; identify overfitting and data bias risks; provide deployment recommendations."
  - Provide as `combine_result`: the **Factor Combiner** (`factor-research-committee-factor-combiner`) output from an earlier phase.
  - Provide as `mine_result`: the **Factor Miner** (`factor-research-committee-factor-miner`) output from an earlier phase.
  - Provide as `validate_result`: the **Factor Validator** (`factor-research-committee-factor-validator`) output from an earlier phase.

## Final output
Return the **Backtest Reviewer** output as the team's deliverable, citing the supporting analysis from earlier phases.
