---
description: Earnings-focused research team: fundamental analyst + earnings revision tracker + options/event analyst + earnings strategist. Deep-dives into company financials, consensus revisions, earnings event trades, and post-earnings drift.
argument-hint: [target]
---

# Earnings Research Desk

Native replacement for the Vibe-Trading `earnings_research_desk` swarm preset. You are the orchestrator. Dispatch each role below as a subagent with the **Agent** tool (`subagent_type` = the agent name shown in backticks), honoring the phase order: **phases run sequentially**, and all agents **within one phase run in parallel** — dispatch a phase's agents together in a single message. Pass each downstream agent the upstream outputs named in its bullet.

**Inputs** (from `$ARGUMENTS`):
- `<target>` = `$1` — Target stock (e.g., AAPL.US, NVDA.US, 700.HK, 600519.SH)

## Phase 1 (parallel)
- **`earnings-research-desk-fundamental-analyst`** — "Conduct deep fundamental and filing analysis on <target>. Focus on earnings quality, financial health, and peer comparison."
- **`earnings-research-desk-revision-tracker`** — "Track consensus revisions, earnings surprise history, and PEAD status for <target>."
- **`earnings-research-desk-event-options-analyst`** — "Analyze options positioning, implied move vs realized, and event trade setups for <target> around earnings."

## Phase 2
- **`earnings-research-desk-earnings-strategist`** — "Synthesize all analyses and deliver the final earnings trade recommendation for <target> with position sizing and decision tree."
  - Provide as `fundamentals`: the **Fundamental & Filing Analyst** (`earnings-research-desk-fundamental-analyst`) output from an earlier phase.
  - Provide as `revisions`: the **Earnings Revision & Consensus Tracker** (`earnings-research-desk-revision-tracker`) output from an earlier phase.
  - Provide as `options_event`: the **Earnings Event & Options Analyst** (`earnings-research-desk-event-options-analyst`) output from an earlier phase.

## Final output
Return the **Earnings Desk Strategist** output as the team's deliverable, citing the supporting analysis from earlier phases.
