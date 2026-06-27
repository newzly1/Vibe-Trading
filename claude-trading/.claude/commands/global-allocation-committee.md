---
description: Parallel A-shares + crypto + HK/US analysts; allocator synthesizes cross-market allocation with data-driven weighting, scenario analysis, and rebalancing rules.
argument-hint: [goal] [risk_tolerance]
---

# Global Allocation Committee

Native replacement for the Vibe-Trading `global_allocation_committee` swarm preset. You are the orchestrator. Dispatch each role below as a subagent with the **Agent** tool (`subagent_type` = the agent name shown in backticks), honoring the phase order: **phases run sequentially**, and all agents **within one phase run in parallel** — dispatch a phase's agents together in a single message. Pass each downstream agent the upstream outputs named in its bullet.

**Inputs** (from `$ARGUMENTS`):
- `<goal>` = `$1` — Investment objective (e.g., Q2 2026 multi-asset allocation)
- `<risk_tolerance>` = `$2` — Risk tolerance (conservative / moderate / aggressive)

## Phase 1 (parallel)
- **`global-allocation-committee-a-share-analyst`** — "Analyze the current A-share market with focus on: <goal>. Provide sector rotation view, Northbound flow signal, and 3-5 top picks."
- **`global-allocation-committee-crypto-analyst`** — "Analyze major crypto assets with focus on: <goal>. Cover funding rates, stablecoin flows, and 3-5 top picks."
- **`global-allocation-committee-us-hk-analyst`** — "Analyze HK and US opportunities with focus on: <goal>. Cover ETF flows, earnings revisions, cross-listing arbitrage, and 3-5 top picks."

## Phase 2
- **`global-allocation-committee-allocator`** — "Synthesize the three regional reports into cross-market allocation guidance. Risk tolerance: <risk_tolerance>. Goal: <goal>."
  - Provide as `a_share`: the **A-Share Analyst** (`global-allocation-committee-a-share-analyst`) output from an earlier phase.
  - Provide as `crypto`: the **Crypto Analyst** (`global-allocation-committee-crypto-analyst`) output from an earlier phase.
  - Provide as `us_hk`: the **HK / US Analyst** (`global-allocation-committee-us-hk-analyst`) output from an earlier phase.

## Final output
Return the **Allocation Strategist** output as the team's deliverable, citing the supporting analysis from earlier phases.
