# Integration Test: Swarm Replacement Verification

验证 Claude Code 在收到金融分析请求时，正确使用新的 `vt-swarm-*` skills + MCP 工具 + Workflow，而非旧的 `run_swarm`。

## Test 1: A 股个股分析（最核心场景）

### 输入

```
分析阳光电源 300274.SZ 的投资价值，我现在持有 6 手。
```

### 检查点

| # | 检查项 | 预期 | 严重程度 |
|---|--------|------|---------|
| 1 | 调用 `get_market_data` | ✅ 必须调用，且 `source="akshare"` | 🔴 致命 |
| 2 | 数据在分析之前拉取 | ✅ `get_market_data` 在输出结论之前调用 | 🔴 致命 |
| 3 | 调用 `run_swarm` | ❌ 必须不调用 | 🔴 致命 |
| 4 | 调用 `list_swarm_presets` | ❌ 必须不调用 | 🔴 致命 |
| 5 | 加载 vt-swarm-* skill | ✅ 可加载，但非必须（workflow 自动处理） | 🟡 |
| 6 | 输出含真实价格数据 | ✅ 报告中的价格/PE/MA 等数据可追溯到 `get_market_data` | 🟡 |
| 7 | 引用 6 手持仓 | ✅ 策略考虑了当前持仓 | 🟡 |
| 8 | 使用 `web_search` 替代数据 | ❌ `web_search` 只能用于新闻/定性分析，不能替代价格数据 | 🟡 |

### 判定标准

- 全部 🔴 项通过 = **测试通过**
- 任一项 🔴 失败 = **回归**，需修复
- 🟡 项失败 = **改进项**，不阻塞

---

## Test 2: 量化策略回测（验证 Workflow 路径）

### 输入

```
/workflow quant-strategy-desk market="A-shares" goal="构建一个 A 股光伏板块的低波动动量策略"
```

或者手动方式：

```
为 A 股光伏板块（阳光电源 300274.SZ、通威股份 600438.SH、隆基绿能 601012.SH）构建一个低波动动量策略，做回测验证。
```

### 检查点

| # | 检查项 | 预期 | 严重程度 |
|---|--------|------|---------|
| 1 | 调用 `get_market_data` | ✅ 拉取三只股票的数据 | 🔴 |
| 2 | 调用 `factor_analysis` | ✅ 因子 IC/IR 分析 | 🟡 |
| 3 | 写 `config.json` + `signal_engine.py` | ✅ 通过 `write_file` | 🔴 |
| 4 | 调用 `backtest` | ✅ 执行回测并产出指标 | 🔴 |
| 5 | 读 `artifacts/metrics.csv` | ✅ 验证回测输出 | 🟡 |
| 6 | 回测指标非编造 | ✅ 夏普/回撤/胜率来自实际回测 | 🔴 |
| 7 | 调用 `run_swarm` | ❌ | 🔴 |

---

## Test 3: 多空辩论（验证 Investment Committee Workflow）

### 输入

```
/workflow investment-committee target="300274.SZ" market="A-shares"
```

### 检查点

| # | 检查项 | 预期 | 严重程度 |
|---|--------|------|---------|
| 1 | 并行派发 bull_advocate + bear_advocate | ✅ 两个 agent 同时运行 | 🟡 |
| 2 | bull agent 调了 `get_market_data` | ✅ | 🔴 |
| 3 | bear agent 调了 `get_market_data` | ✅ | 🔴 |
| 4 | risk_officer 在 bull+bear 之后运行 | ✅ 串行顺序正确 | 🟡 |
| 5 | portfolio_manager 产出可执行决策 | ✅ 含具体价位/仓位/止损 | 🔴 |
| 6 | 调用 `run_swarm` | ❌ | 🔴 |

---

## Test 4: run_swarm 默认禁用

### 输入

```
list_swarm_presets()
```

### 预期输出

```json
{
  "status": "deprecated",
  "error": "Swarm is DEPRECATED in the Claude Code integration..."
}
```

### 判定

- 返回 deprecated 错误 = **通过**
- 返回 preset 列表 = **失败**（`VIBE_TRADING_ENABLE_SWARM` 未正确设置）

---

## 运行方式

### 手动运行

在 Claude Code 会话中依次输入上述测试 prompt，观察工具调用链。

### 自动验证（推荐）

```bash
# 确认 MCP server 的 swarm gate 生效
VIBE_TRADING_ENABLE_SWARM=0 python -c "
from agent.mcp_server import _env_swarm_enabled
print('Swarm enabled:', _env_swarm_enabled())  # Should print False
"

# 确认 MCP server 语法正确
cd agent && python -m compileall -q cli && python -m py_compile mcp_server.py
echo 'Syntax OK'
```

### 回归检查清单

每次修改 MCP server 或 CLAUDE.md 后，至少运行 Test 1（A 股个股分析）确认无回归。

---

## 已知问题记录

| 日期 | 测试 | 问题 | 状态 |
|------|------|------|------|
| 2026-06-11 | Test 1 | Subagent 未调用 `get_market_data`，用 `web_search` 替代 | 已修复（CLAUE.md + vt-data-routing skill 强化） |
| 2026-06-11 | Test 1 | Subagent 不知道如何派发 Agent | 已修复（新增 3 个 vt-swarm-* skills + workflows） |
| 2026-06-11 | Test 4 | `run_swarm` 可直接调用 | 已修复（`VIBE_TRADING_ENABLE_SWARM=1` gate） |
