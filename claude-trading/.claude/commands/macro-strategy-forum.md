---
description: Global + domestic + policy perspectives run in parallel; chief strategist delivers integrated cross-asset allocation guidance.
argument-hint: [market] [horizon]
---

# Macro Strategy Forum

Native replacement for the Vibe-Trading `macro_strategy_forum` swarm preset. You are the orchestrator. Dispatch each role below as a subagent with the **Agent** tool (`subagent_type` = the agent name shown in backticks), honoring the phase order: **phases run sequentially**, and all agents **within one phase run in parallel** — dispatch a phase's agents together in a single message. Pass each downstream agent the upstream outputs named in its bullet.

**Inputs** (from `$ARGUMENTS`):
- `<market>` = `$1` — Focus market (e.g., A-shares, Hong Kong, global multi-asset, crypto)
- `<horizon>` = `$2` — Horizon (e.g., monthly, quarterly, annual)

## Phase 1 (parallel)
- **`macro-strategy-forum-global-economist`** — "Analyze the global macro environment; focus on major central banks and implications for <market>. Horizon: <horizon>."
- **`macro-strategy-forum-domestic-economist`** — "Analyze China domestic macro and policy stance; implications for <market>. Horizon: <horizon>."
- **`macro-strategy-forum-policy-analyst`** — "Analyze current regulatory and industrial policy changes affecting <market>. Horizon: <horizon>."

## Phase 2
- **`macro-strategy-forum-chief-strategist`** — "Integrate global, domestic, and policy dimensions into cross-asset allocation and market outlook for <market> over <horizon>."
  - Provide as `global_macro`: the **Global Economist** (`macro-strategy-forum-global-economist`) output from an earlier phase.
  - Provide as `domestic_macro`: the **China Economist** (`macro-strategy-forum-domestic-economist`) output from an earlier phase.
  - Provide as `policy_analysis`: the **Policy Analyst** (`macro-strategy-forum-policy-analyst`) output from an earlier phase.

## Final output
Return the **Chief Strategist** output as the team's deliverable, citing the supporting analysis from earlier phases.
