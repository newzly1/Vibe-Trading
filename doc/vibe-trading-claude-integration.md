# Vibe-Trading 功能移植到 Claude Code 操作记录

## 概述

将 Vibe-Trading 的核心金融分析能力（数据加载、回测引擎、Alpha Zoo、因子分析等）移植到 Claude Code，绕过 V-T 自身的 ReAct agent loop 和 Swarm 框架，直接用 Claude Code 的推理能力 + MCP 工具完成金融分析。

## 1. 环境配置修复

**文件**: `agent/.env`

- 切换 LLM provider 从 OpenRouter 到 DeepSeek 官方 API
- 填入真实的 `DEEPSEEK_API_KEY`
- 注释掉 OpenRouter 区块，解注释 DeepSeek 区块

```bash
LANGCHAIN_PROVIDER=deepseek
LANGCHAIN_MODEL_NAME=deepseek-v4-pro
DEEPSEEK_API_KEY=sk-xxx
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
```

## 2. MCP Server 接入

Vibe-Trading 自带 `vibe-trading-mcp` 服务器，暴露 36 个金融工具。大部分工具绕过 V-T 的 agent loop，直接调用底层库。

### 2.1 创建项目 MCP 配置

**文件**: `.mcp.json`

```json
{
  "mcpServers": {
    "vibe-trading": {
      "command": "/home/zly/Vibe-Trading/.venv/bin/vibe-trading-mcp"
    }
  }
}
```

### 2.2 Claude Code 权限配置

**文件**: `~/.claude/settings.json`

添加：
- `"enabledMcpjsonServers": ["vibe-trading"]` — 预批准 MCP server
- `"mcp__vibe_trading__*"` 加入 `permissions.allow` — 允许调用所有 36 个 MCP 工具

## 3. Skills 批量转换

### 3.1 转换逻辑

V-T 的 skill 文件（`agent/src/skills/<name>/SKILL.md`）本质上就是领域知识 prompt 模板，与 Claude Code skill 机制完全一致。

转换工具: Python 脚本

转换内容:
- 77 个 skill 全部从 `agent/src/skills/` 复制到 `.claude/skills/vt-<name>/SKILL.md`
- 名称加 `vt-` 前缀避免与现有 skill 冲突
- `load_skill("xxx")` 引用替换为跨 skill 关联（`See the **vt-xxx** skill guide`）
- 顶部注入可用 MCP 工具列表（HTML 注释，Claude 可见但用户不显示）

### 3.2 落盘位置

```
.claude/skills/
├── vt-data-routing/SKILL.md      # 数据源选择决策树
├── vt-technical-basic/SKILL.md   # 技术指标公式与参数
├── vt-factor-research/SKILL.md   # 因子研究方法论
├── vt-backtest-diagnose/SKILL.md # 回测诊断流程
├── vt-valuation-model/SKILL.md   # 估值模型标准
├── ... (共 77 个)
```

Claude Code 启动时自动发现所有 skill，在需要时自动调用。

### 3.3 注意事项

- Skill 生效范围: **仅当前项目**（`.claude/skills/` = 项目级）
- `skillListingBudgetFraction` 默认 1%，在 1M token 窗口下可容纳所有 skill 的简短描述
- 重启 Claude Code 后生效

## 4. 架构对比

| 组件 | Vibe-Trading | Claude Code 移植后 |
|------|-------------|-------------------|
| LLM 推理 | ReAct agent loop | Claude Code 原生推理 |
| 数据获取 | agent → get_market_data 工具 | MCP 直接调用 get_market_data |
| 回测 | agent → backtest 工具 | MCP 直接调用 backtest |
| 因子分析 | agent → factor_analysis 工具 | MCP 直接调用 factor_analysis |
| Swarm/多agent | SwarmRuntime + Worker ReAct | Claude Code dispatching-parallel-agents + Agent 工具 |
| 领域知识 | load_skill("xxx") 加载 SKILL.md | Claude Code 自动加载 vt-xxx skill |
| 技能库 | 77 个 SKILL.md（需 agent 加载） | 77 个 Claude Code skill（自动） |
| Web UI | React 前端 + FastAPI | 不需要（Claude Code TUI） |

## 5. 可用 MCP 工具清单（36 个）

### 市场数据
- `get_market_data` — 拉取 OHLCV 行情（A 股/港股/美股/加密货币）

### 回测与分析
- `backtest` — 向量化回测引擎
- `factor_analysis` — 因子 IC/收益分析
- `analyze_options` — 期权定价与 Greeks
- `pattern_recognition` — K 线形态识别

### Alpha Zoo
- `alpha_list` — 浏览 452 个预建 alpha
- `alpha_show` — 查看单个 alpha 公式
- `alpha_bench` — 基准测试 alpha zoo
- `alpha_compare` — 多 alpha 对比排名

### 内容工具
- `read_url` / `read_document` / `web_search` — 内容获取
- `read_file` / `write_file` — 文件 I/O
- `list_skills` / `load_skill` — 技能发现

### 交易连接
- `trading_connections` / `trading_select_connection` / `trading_check`
- `trading_account` / `trading_positions` / `trading_orders`
- `trading_quote` / `trading_history`

### Swarm（不推荐使用）
- `run_swarm` — 仍走 V-T 的 agent loop，建议用 Claude Code 的 dispatching-parallel-agents 替代
- `list_swarm_presets` / `get_swarm_status` / `get_run_result` / `list_runs` / `reap_stale_runs` / `retry_run`

### 研究目标
- `start_research_goal` / `get_research_goal` / `add_goal_evidence` / `update_research_goal_status`

## 6. 已知限制

1. **Swarm 不推荐使用**: `run_swarm` 仍走 V-T 的 ReAct agent loop，继承了原有的数据源选择错误、工具幻觉、超时等问题。建议用 Claude Code 的 `dispatching-parallel-agents` skill + `Agent` 工具替代。

2. **A 股数据源**: `get_market_data` 的 `source="auto"` 对 A 股可能路由到 yfinance（不支持）。建议显式指定 `source="akshare"` 或 `source="tushare"`。

3. **回测需要配置目录**: `backtest` 工具需要预先准备好 `config.json` + `code/signal_engine.py` 的目录结构。

4. **Skill 是知识文档，非可执行代码**: 77 个 vt- skill 提供的是公式、参数、方法论参考。实际计算仍需通过 MCP 工具或 Claude Code 生成 Python 代码执行。

## 7. 使用示例

### 拉取行情
> "用 get_market_data 拉取 300274.SZ 最近 6 个月的日线数据，source 用 akshare"

### 因子分析
> "对 300274.SZ 和 000001.SZ 做动量因子分析，周期 2024-2026"

### 回测
> "按 vt-technical-basic 的公式，写一个 20/50 均线交叉策略，用 backtest 对我准备好的 run_dir 跑回测"

### 完整分析（替代 Swarm）
> "用 dispatching-parallel-agents，仿照 investment_committee 流程，并行派发多头和空头分析 agent，分别从技术和基本面角度分析阳光电源 300274.SZ。bull agent 参考 vt-technical-basic 和 vt-fundamental-filter，bear agent 参考 vt-risk-analysis。结果汇总后做综合决策。"
