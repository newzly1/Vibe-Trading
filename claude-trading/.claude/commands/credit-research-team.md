---
description: Credit quality + interest rate environment + sector credit three-dimensional parallel analysis → fixed income strategist synthesizes a complete bond investment strategy
argument-hint: [target] [market]
---

# Fixed Income Credit Research Team

Native replacement for the Vibe-Trading `credit_research_team` swarm preset. You are the orchestrator. Dispatch each role below as a subagent with the **Agent** tool (`subagent_type` = the agent name shown in backticks), honoring the phase order: **phases run sequentially**, and all agents **within one phase run in parallel** — dispatch a phase's agents together in a single message. Pass each downstream agent the upstream outputs named in its bullet.

**Inputs** (from `$ARGUMENTS`):
- `<target>` = `$1` — Research subject or sector (e.g.: a specific LGFV platform, the property sector, steel bonds, AA-rated credit bond portfolio)
- `<market>` = `$2` — Bond market (default: China bond market; options: credit bonds / LGFV bonds / rate bonds / convertible bonds)

## Phase 1 (parallel)
- **`credit-research-team-credit-analyst`** — "Conduct a deep credit quality analysis of "<target>", assessing debt service capacity, default probability, and credit rating outlook. Market: <market>."
- **`credit-research-team-rate-analyst`** — "Analyze the current <market> interest rate environment, assessing yield curve shape, credit spread trends, and interest rate risk with respect to "<target>"-related bonds."
- **`credit-research-team-sector-credit-analyst`** — "Analyze the credit risk characteristics of the sector / industry where "<target>" operates, assessing sector-level default risk and policy impacts. Market: <market>."

## Phase 2
- **`credit-research-team-fixed-income-strategist`** — "Synthesize the credit, interest rate, and sector credit three-dimensional research to build a complete fixed income investment strategy for <market> targeting "<target>"."
  - Provide as `credit_report`: the **Credit Analyst** (`credit-research-team-credit-analyst`) output from an earlier phase.
  - Provide as `rate_report`: the **Interest Rate Analyst** (`credit-research-team-rate-analyst`) output from an earlier phase.
  - Provide as `sector_credit_report`: the **Sector Credit Analyst** (`credit-research-team-sector-credit-analyst`) output from an earlier phase.

## Final output
Return the **Fixed Income Strategist** output as the team's deliverable, citing the supporting analysis from earlier phases.
