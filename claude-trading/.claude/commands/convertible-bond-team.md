---
description: Parallel three-dimensional analysis — bond floor, equity optionality, and embedded option value — synthesized into a convertible bond investment strategy
argument-hint: [market] [goal] [strategy_type]
---

# Convertible Bond Research Team

Native replacement for the Vibe-Trading `convertible_bond_team` swarm preset. You are the orchestrator. Dispatch each role below as a subagent with the **Agent** tool (`subagent_type` = the agent name shown in backticks), honoring the phase order: **phases run sequentially**, and all agents **within one phase run in parallel** — dispatch a phase's agents together in a single message. Pass each downstream agent the upstream outputs named in its bullet.

**Inputs** (from `$ARGUMENTS`):
- `<market>` = `$1` — Target market (default: A-share convertible bonds)
- `<goal>` = `$2` — Research focus (e.g.: uncover undervalued convertibles, position for conversion price reset candidates)
- `<strategy_type>` = `$3` — Strategy type (low-price / dual-low / high-convexity / rotation; leave blank for strategist's discretion)

## Phase 1 (parallel)
- **`convertible-bond-team-bond-analyst`** — "Conduct a bond-floor value analysis of the <market> convertible bond market, assessing downside protection strength and credit risk, with a focus on <goal>."
- **`convertible-bond-team-equity-analyst`** — "Analyze the fundamentals and technicals of underlying equities for <market> convertible bonds, assessing conversion value and reset potential, with a focus on <goal>."
- **`convertible-bond-team-option-analyst`** — "Analyze the option characteristics of <market> convertible bonds, evaluating implied volatility and Greeks metrics, with a focus on <goal>."

## Phase 2
- **`convertible-bond-team-cb-strategist`** — "Synthesize the three-dimensional analysis — bond floor, equity optionality, and embedded option value — to design a <strategy_type> strategy and validate through backtesting. Target market: <market>. Research focus: <goal>."
  - Provide as `bond_analysis`: the **Bond Floor Analyst** (`convertible-bond-team-bond-analyst`) output from an earlier phase.
  - Provide as `equity_analysis`: the **Underlying Equity Analyst** (`convertible-bond-team-equity-analyst`) output from an earlier phase.
  - Provide as `option_analysis`: the **Embedded Option Analyst** (`convertible-bond-team-option-analyst`) output from an earlier phase.

## Final output
Return the **Convertible Bond Strategist** output as the team's deliverable, citing the supporting analysis from earlier phases.
