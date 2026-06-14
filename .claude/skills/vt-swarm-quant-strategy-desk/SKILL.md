---
name: vt-swarm-quant-strategy-desk
description: Quant strategy desk pattern — parallel screening + factor mining → backtest → risk audit. Replaces the deprecated run_swarm("quant_strategy_desk") preset with native Claude Code Agent dispatch.
---

<!--
Available Vibe-Trading MCP tools for this skill:
  - get_market_data(codes, start_date, end_date, source, interval) — fetch OHLCV. A-shares MUST use source="akshare" or source="tushare"
  - backtest(run_dir) — run backtest from config.json + signal_engine.py
  - factor_analysis(codes, factor_name, start_date, end_date, ...) — factor IC/returns
  - alpha_zoo(query) — browse 452 pre-built alphas
  - alpha_bench(zoo, codes, start_date, end_date) — benchmark alpha zoo
  - alpha_compare(alphas, codes, start_date, end_date) — head-to-head alpha comparison
  - write_file(path, content) / read_file(path) — file I/O

IMPORTANT: Do NOT call run_swarm. Use the Agent tool dispatch pattern below instead.
-->

# Quant Strategy Desk (Native Claude Code)

## Purpose

代替已弃用的 `run_swarm("quant_strategy_desk")`。使用 Claude Code 原生 `Agent` 工具实现**并行选股+因子挖掘 → 策略回测 → 风险审计**的量化策略研发流程。

## DAG Structure

```
screener ──────┐
                ├──→ backtester ──→ risk_auditor (最终审计)
factor_miner ──┘
```

- **Layer 1 (并行)**: 股票筛选 + 因子挖掘同时进行
- **Layer 2**: 策略回测（整合筛选结果和因子研究）
- **Layer 3**: 风险审计（审查回测结果，评估稳健性）

## 变量

| 变量 | 说明 | 示例 |
|------|------|------|
| `market` | 目标市场 | `A-shares`、`US`、`crypto` |
| `goal` | 策略目标 | `动量+价值双因子选股`、`低波动高质量策略` |

## Agent 角色定义

### 1. screener — 股票筛选员

多维度筛选候选池，按策略目标过滤出符合条件的标的。

**必须产出的 4 项**：
1. 筛选标准 — 列出每个筛选维度和阈值
2. 候选列表 — 至少 10-20 个候选标的（代码+名称+行业）
3. 基本面快照 — 每个标的的核心指标 (PE/PB/ROE/市值等)
4. 筛选漏斗统计 — 初始池大小 → 每一步过滤后的剩余数量

**参考技能**: `vt-fundamental-filter`, `vt-multi-factor`

**MCP 工具**: `factor_analysis`, `get_market_data`, `alpha_zoo`

---

### 2. factor_miner — 因子研究员

挖掘有效的 alpha 因子，进行因子测试和组合优化。

**必须产出的 5 项**：
1. 候选因子列表 — 至少 5 个因子（名称、公式、经济学逻辑）
2. 因子测试 — Mean IC、ICIR、IC 胜率、因子收益
3. 因子相关性 — 相关性矩阵，剔除高相关因子
4. 因子组合 — 建议 3-5 个因子的等权或优化组合
5. 风险提示 — 因子衰减场景和周期性

**参考技能**: `vt-factor-research`, `vt-alpha-zoo`

**MCP 工具**: `factor_analysis`, `alpha_bench`, `alpha_compare`

---

### 3. backtester — 策略回测员

将筛选逻辑和因子信号转化为可回测的策略代码，执行回测并产出指标。

**必须产出的 5 项**：
1. 策略逻辑 — 完整的买卖规则（文字描述）
2. 策略代码 — 遵循 `vt-strategy-generate` 的 `SignalEngine` 合约
3. 回测指标 — 年化收益率、夏普比率、最大回撤、胜率、盈亏比
4. 权益曲线分析 — 分阶段表现 vs 基准超额
5. 改进思路 — 潜在优化方向

**关键约束**：必须运行 `backtest` 产出真实数据，不得编造数字。

**参考技能**: `vt-strategy-generate`, `vt-technical-basic`

**MCP 工具**: `backtest`, `write_file`, `read_file`

---

### 4. risk_auditor — 风险审计员

从风险角度审查回测结果，评估策略稳健性和过拟合风险。

**必须产出的 5 项**：
1. 回撤分析 — 历史最大回撤的驱动因素和持续时间
2. 波动率评估 — 年化波动率、下行波动率、波动率聚类
3. 尾部风险 — VaR/CVaR 估计，极端市场中的行为
4. 过拟合检查 — 样本内 vs 样本外差距，参数敏感性
5. 风险建议 — 仓位管理、止损、风险控制改进

**参考技能**: `vt-risk-analysis`, `vt-volatility`

---

## 派发方式（推荐用 Workflow）

```
/workflow quant-strategy-desk
```

对于手动执行：

```
Step 1 (并行): 
  Agent("screener", prompt="在 {market} 按 {goal} 筛选候选池...")
  Agent("factor_miner", prompt="为 {market} 的 {goal} 挖掘 alpha 因子...")

Step 2 (等 Step 1 返回后):
  Agent("backtester", prompt="整合筛选和因子输出构建策略并回测...\n\n筛选结果: {screen}\n因子研究: {factor}")

Step 3 (等 Step 2 返回后):
  Agent("risk_auditor", prompt="审计回测结果的风险暴露...\n\n回测结果: {backtest}")
```

## 数据拉取前置步骤

```
get_market_data(codes="{候选池代码列表}", source="akshare", start_date="...", end_date="...")
```

A 股**必须**用 `source="akshare"` 或 `source="tushare"`。
