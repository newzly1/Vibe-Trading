---
description: Financial / valuation / quality three-dimensional parallel analysis → research editor consolidates into a buy-side deep research report
argument-hint: [target] [market]
---

# Fundamental Deep Research Team

Native replacement for the Vibe-Trading `fundamental_research_team` swarm preset. You are the orchestrator. Dispatch each role below as a subagent with the **Agent** tool (`subagent_type` = the agent name shown in backticks), honoring the phase order: **phases run sequentially**, and all agents **within one phase run in parallel** — dispatch a phase's agents together in a single message. Pass each downstream agent the upstream outputs named in its bullet.

**Inputs** (from `$ARGUMENTS`):
- `<target>` = `$1` — Research subject (stock code or name, e.g.: 600519 Kweichow Moutai)
- `<market>` = `$2` — Market (e.g.: A-shares, Hong Kong, US equities)

## Phase 1 (parallel)
- **`fundamental-research-team-financial-analyst`** — "Conduct deep financial statement analysis of <target>, focusing on financial quality, profitability, cash flow health, and debt risk."
- **`fundamental-research-team-valuation-analyst`** — "Conduct multi-method cross-validated valuation of <target>, including DCF, comparable company method, and historical valuation method. Provide a target price range."
- **`fundamental-research-team-quality-analyst`** — "Conduct moat assessment, management quality analysis, and competitive landscape research on <target>."

## Phase 2
- **`fundamental-research-team-report-editor`** — "Synthesize the research outputs from all three analysts to produce a complete deep research report on <target>, with a clear investment rating and target price."
  - Provide as `financial`: the **Financial Analyst** (`fundamental-research-team-financial-analyst`) output from an earlier phase.
  - Provide as `valuation`: the **Valuation Analyst** (`fundamental-research-team-valuation-analyst`) output from an earlier phase.
  - Provide as `quality`: the **Quality Analyst** (`fundamental-research-team-quality-analyst`) output from an earlier phase.

## Final output
Return the **Research Report Editor** output as the team's deliverable, citing the supporting analysis from earlier phases.
