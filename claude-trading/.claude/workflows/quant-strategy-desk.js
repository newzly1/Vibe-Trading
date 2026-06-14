export const meta = {
  name: 'quant-strategy-desk',
  description: 'Quant Strategy Desk — parallel screening + factor mining → backtest → risk audit. Native Claude Code replacement for run_swarm("quant_strategy_desk").',
  phases: [
    { title: 'Screen & Factor', detail: 'Parallel screening and factor research' },
    { title: 'Backtest', detail: 'Strategy construction and backtest' },
    { title: 'Risk Audit', detail: 'Risk review and robustness assessment' },
  ],
  whenToUse: 'When the user asks to develop a quantitative strategy, mine alpha factors, run factor backtests, or says "量化策略" / "因子挖掘" / "alpha research".',
}

const MARKET = args.market || 'A-shares'
const GOAL = args.goal || 'develop a robust quantitative strategy'

// ============================================================
// Phase 1: Parallel screening + factor mining
// ============================================================
phase('Screen & Factor')

const SCREENER_PROMPT = `You are a quant stock-screening specialist. Screen a candidate universe from ${MARKET} for the objective: ${GOAL}.

## Required Outputs
1. **Screening criteria** — Every dimension and threshold explicitly listed
2. **Candidate list** — At least 10-20 candidates (code + name + sector)
3. **Fundamental snapshot** — Core metrics per name (PE/PB/ROE/market cap)
4. **Screening funnel stats** — Initial universe → remaining after each filter step

Use factor_analysis for factor-based screening. Use get_market_data (source="akshare" for A-shares) for fundamental data. Use alpha_zoo to discover relevant pre-built factors. Use load_skill("fundamental-filter") for framework.`

const FACTOR_PROMPT = `You are a quant factor researcher. Mine effective alpha factors for ${MARKET} suited to: ${GOAL}.

## Required Outputs
1. **Candidate factor list** — At least 5 factors (name, formula, economic rationale)
2. **Factor tests** — Mean IC, ICIR, IC hit rate, factor return
3. **Factor correlation** — Correlation matrix; remove highly correlated factors
4. **Factor combination** — Suggest equal-weight or optimized combo of 3-5 factors
5. **Risk notes** — Factor-decay scenarios and cyclicality

Use factor_analysis for IC/IR computations. Use alpha_bench for zoo benchmarking. Use alpha_compare for head-to-head factor comparison. Use load_skill("factor-research") and load_skill("alpha-zoo") for methodology.`

const [screenResult, factorResult] = await parallel([
  () => agent(SCREENER_PROMPT, { label: 'screener', phase: 'Screen & Factor' }),
  () => agent(FACTOR_PROMPT, { label: 'factor_miner', phase: 'Screen & Factor' }),
])

// ============================================================
// Phase 2: Backtest
// ============================================================
phase('Backtest')

const BACKTEST_PROMPT = `You are a strategy backtest specialist. Build a quant strategy from the screening and factor research below and run a backtest.

## Screening Results
${screenResult || '(No screening results)'}

## Factor Research
${factorResult || '(No factor research)'}

## Required Outputs
1. **Strategy logic** — Complete buy/sell rules in prose
2. **Strategy code** — Follow load_skill("strategy-generate") SignalEngine contract
3. **Backtest metrics** — Annualized return, Sharpe, max drawdown, win rate, P/L ratio
4. **Equity curve commentary** — Phase-by-phase vs benchmark excess
5. **Improvement ideas** — Potential optimizations

You MUST:
- Write config.json and code/signal_engine.py via write_file
- Run backtest(run_dir=...) to get real metrics
- Read artifacts/metrics.csv for actual numbers
- Do NOT fabricate any backtest numbers — every metric must come from a real backtest run

Use load_skill("strategy-generate") for the complete backtest workflow and contract.`

const backtestResult = await agent(BACKTEST_PROMPT, { label: 'backtester', phase: 'Backtest' })

// ============================================================
// Phase 3: Risk audit
// ============================================================
phase('Risk Audit')

const RISK_PROMPT = `You are a quant risk auditor. Review the strategy and backtest results below from a risk perspective.

## Backtest Results
${backtestResult || '(No backtest results)'}

## Required Outputs
1. **Drawdown analysis** — Top historical drawdowns: drivers and duration
2. **Volatility assessment** — Annual vol, downside vol, volatility clustering
3. **Tail risk** — VaR/CVaR estimates; behavior in extreme markets
4. **Overfitting checks** — In-sample vs out-of-sample gaps; parameter sensitivity
5. **Risk recommendations** — Position sizing, stops, risk-control improvements

Use load_skill("volatility") and load_skill("risk-analysis") for methodology. Be specific — every recommendation must have concrete parameters.`

const riskResult = await agent(RISK_PROMPT, { label: 'risk_auditor', phase: 'Risk Audit' })

// ============================================================
// Return synthesized result
// ============================================================
return {
  preset: 'quant_strategy_desk',
  market: MARKET,
  goal: GOAL,
  screening: screenResult,
  factors: factorResult,
  backtest: backtestResult,
  risk_audit: riskResult,
}
