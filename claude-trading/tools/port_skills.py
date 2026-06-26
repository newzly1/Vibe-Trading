#!/usr/bin/env python3
"""Port Vibe-Trading domain skills to Claude Code skills.

Reads ``agent/src/skills/<name>/`` and writes
``claude-trading/.claude/skills/vt-<name>/``, rewriting references to removed
MCP tools into native Claude Code tools and ``load_skill()`` calls into
cross-skill links. Idempotent and re-runnable.

Usage:
    python port_skills.py [SRC_ROOT] [OUT_ROOT]
"""
from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

# Skills that document now-removed / natively-replaced tools — not ported.
# (web-reader -> read_url -> native WebFetch; doc-reader -> read_document -> native Read)
SKIP = {"web-reader", "doc-reader"}

# Removed MCP tool name -> native Claude Code equivalent (whole-word rename).
TOOL_RENAMES = {
    "read_document": "Read",
    "read_file": "Read",
    "write_file": "Write",
    "edit_file": "Edit",
    "read_url": "WebFetch",
    "web_search": "WebSearch",
    "list_skills": "Skill",
}

MCP_COMMENT = """<!--
Vibe-Trading MCP tools available to this skill (Claude Code is the harness; key tools):
  Market data:    get_market_data
  A-share data:   get_fundamentals, get_financial_statements, get_money_flow,
                  get_margin_data, get_earnings_forecast, get_events
  Backtest/anlys: backtest, factor_analysis, analyze_options, pattern_recognition
  Alpha Zoo:      alpha_zoo, alpha_bench, alpha_compare
  Hypotheses:     create_hypothesis, update_hypothesis, link_backtest, search_hypotheses
  Research goals: start_research_goal, get_research_goal, add_goal_evidence, update_research_goal_status
  Journal/shadow: analyze_trade_journal, extract_shadow_strategy, run_shadow_backtest,
                  render_shadow_report, scan_shadow_signals
  Trading (read-only): trading_connections, trading_select_connection, trading_check,
                  trading_account, trading_positions, trading_orders, trading_quote, trading_history
Native Claude Code tools (use directly, NOT an MCP tool): Read, Write, Edit, WebFetch, WebSearch, Skill.
-->"""


def rewrite_text(text: str) -> str:
    """Rewrite removed-tool references and load_skill() calls to native forms."""
    # `load_skill("x")` -> the **vt-x** skill  (swallow optional wrapping backticks)
    text = re.sub(r'`?load_skill\(\s*["\']([\w-]+)["\']\s*\)`?', r"the **vt-\1** skill", text)
    # any remaining bare load_skill -> the Skill tool
    text = re.sub(r"\bload_skill\b", "the Skill tool", text)
    # removed tool names -> native equivalents (whole word)
    for old, new in TOOL_RENAMES.items():
        text = re.sub(r"\b" + re.escape(old) + r"\b", new, text)
    return text


def split_frontmatter(content: str) -> tuple[str, str]:
    """Split leading ``---\\n...\\n---`` frontmatter from the body."""
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) == 3:
            return parts[1], parts[2]
    return "", content


def convert_frontmatter(fm: str, name: str) -> str:
    """Emit Claude Code frontmatter: vt-prefixed name + original description."""
    desc = ""
    for line in fm.splitlines():
        if line.startswith("description:"):
            desc = line[len("description:") :].strip()
    return f"---\nname: vt-{name}\ndescription: {desc}\n---"


def port_skill(src_dir: Path, out_root: Path) -> None:
    """Port one skill directory to ``out_root/vt-<name>/``."""
    name = src_dir.name
    out_dir = out_root / f"vt-{name}"
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)
    for f in sorted(src_dir.iterdir()):
        if not f.is_file():
            continue
        if f.name == "SKILL.md":
            fm, body = split_frontmatter(f.read_text(encoding="utf-8"))
            out = convert_frontmatter(fm, name) + "\n\n" + MCP_COMMENT + rewrite_text(body)
            (out_dir / "SKILL.md").write_text(out, encoding="utf-8")
        elif f.suffix == ".md":
            (out_dir / f.name).write_text(rewrite_text(f.read_text(encoding="utf-8")), encoding="utf-8")
        else:
            shutil.copy2(f, out_dir / f.name)


def main(argv: list[str]) -> None:
    src_root = Path(argv[1]) if len(argv) > 1 else Path("agent/src/skills")
    out_root = Path(argv[2]) if len(argv) > 2 else Path("claude-trading/.claude/skills")
    out_root.mkdir(parents=True, exist_ok=True)
    count = 0
    for src_dir in sorted(p for p in src_root.iterdir() if p.is_dir()):
        if src_dir.name in SKIP:
            continue
        port_skill(src_dir, out_root)
        count += 1
    print(f"ported {count} skills to {out_root}")


if __name__ == "__main__":
    main(sys.argv)
