---
description: Feature engineering and model design in parallel; flows into the backtest engineer for strict out-of-sample validation.
argument-hint: [market] [target_variable] [goal]
---

# Machine Learning Quant Lab

Native replacement for the Vibe-Trading `ml_quant_lab` swarm preset. You are the orchestrator. Dispatch each role below as a subagent with the **Agent** tool (`subagent_type` = the agent name shown in backticks), honoring the phase order: **phases run sequentially**, and all agents **within one phase run in parallel** — dispatch a phase's agents together in a single message. Pass each downstream agent the upstream outputs named in its bullet.

**Inputs** (from `$ARGUMENTS`):
- `<market>` = `$1` — Target market (e.g., A-shares, Hong Kong/US equities)
- `<target_variable>` = `$2` — Prediction target (return / direction / volatility)
- `<goal>` = `$3` — Research focus (e.g., build a monthly stock-selection model, forecast daily volatility)

## Phase 1 (parallel)
- **`ml-quant-lab-feature-engineer`** — "Design the feature-engineering plan for predicting <target_variable> in <market>. Objective: <goal>."
- **`ml-quant-lab-data-scientist`** — "Design the ML model plan for predicting <target_variable> in <market>. Objective: <goal>."

## Phase 2
- **`ml-quant-lab-backtest-engineer`** — "Turn the feature and model plans into a backtestable strategy and run strict OOS validation of the <target_variable> signal in <market>. Objective: <goal>."
  - Provide as `feature_plan`: the **Feature Engineer** (`ml-quant-lab-feature-engineer`) output from an earlier phase.
  - Provide as `model_plan`: the **Data Scientist** (`ml-quant-lab-data-scientist`) output from an earlier phase.

## Final output
Return the **Backtest Engineer** output as the team's deliverable, citing the supporting analysis from earlier phases.
