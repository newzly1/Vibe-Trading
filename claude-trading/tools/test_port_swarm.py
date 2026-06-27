"""Corpus test for the swarm preset -> subagents+commands converter.

Asserts the committed generated artifacts (and a fresh tmp regeneration) cover
every preset, reference only existing agents, carry valid frontmatter, and
contain no references to removed/harness-duplicate MCP tools.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest
import yaml

HERE = Path(__file__).resolve().parent          # claude-trading/tools
CT = HERE.parent                                 # claude-trading
REPO = CT.parent                                 # repo root
PRESETS = REPO / "agent" / "src" / "swarm" / "presets"
AGENTS = CT / ".claude" / "agents"
COMMANDS = CT / ".claude" / "commands"

sys.path.insert(0, str(HERE))
import port_swarm  # noqa: E402

# Tokens that must never survive into generated artifacts — removed MCP tools
# and harness-duplicate I/O tools (Claude Code has native equivalents).
REMOVED_RE = re.compile(
    r"\b(read_url|read_file|write_file|read_document|web_search|load_skill|list_skills)\b"
)


def _presets() -> list[Path]:
    return sorted(PRESETS.glob("*.yaml"))


def _load(f: Path) -> dict:
    return yaml.safe_load(f.read_text(encoding="utf-8"))


def test_presets_exist() -> None:
    assert len(_presets()) == 29


def test_command_count_matches_presets() -> None:
    assert len(list(COMMANDS.glob("*.md"))) == len(_presets())


def test_every_preset_has_a_command() -> None:
    for f in _presets():
        ps = port_swarm.slug(_load(f)["name"])
        assert (COMMANDS / f"{ps}.md").exists(), f"missing command for {ps}"


def test_agent_count_matches_total_preset_agents() -> None:
    total = sum(len(_load(f)["agents"]) for f in _presets())
    assert len(list(AGENTS.glob("*.md"))) == total


def test_every_preset_agent_has_a_file() -> None:
    have = {p.stem for p in AGENTS.glob("*.md")}
    expected = set()
    for f in _presets():
        d = _load(f)
        ps = port_swarm.slug(d["name"])
        for a in d["agents"]:
            expected.add(f"{ps}-{port_swarm.slug(a['id'])}")
    missing = expected - have
    assert not missing, f"missing agent files: {sorted(missing)[:10]}"


def test_command_references_each_of_its_agents() -> None:
    for f in _presets():
        d = _load(f)
        ps = port_swarm.slug(d["name"])
        text = (COMMANDS / f"{ps}.md").read_text(encoding="utf-8")
        for a in d["agents"]:
            name = f"{ps}-{port_swarm.slug(a['id'])}"
            assert name in text, f"{ps}.md does not reference agent {name}"


def test_committed_agent_frontmatter() -> None:
    for p in AGENTS.glob("*.md"):
        text = p.read_text(encoding="utf-8")
        assert text.startswith("---\n"), f"{p.name}: no frontmatter"
        fm = text.split("---", 2)[1]
        assert f"name: {p.stem}" in fm, f"{p.name}: name mismatch"
        assert "description:" in fm, f"{p.name}: no description"


def test_committed_command_frontmatter() -> None:
    for p in COMMANDS.glob("*.md"):
        text = p.read_text(encoding="utf-8")
        assert text.startswith("---\n"), f"{p.name}: no frontmatter"
        fm = text.split("---", 2)[1]
        assert "description:" in fm, f"{p.name}: no description"
        assert "argument-hint:" in fm, f"{p.name}: no argument-hint"


def test_no_removed_tool_tokens_in_committed() -> None:
    for p in list(AGENTS.glob("*.md")) + list(COMMANDS.glob("*.md")):
        m = REMOVED_RE.search(p.read_text(encoding="utf-8"))
        assert not m, f"{p.name}: residual removed-tool token {m.group()!r}"


def test_fresh_generation_is_clean(tmp_path) -> None:
    a = tmp_path / "agents"
    c = tmp_path / "commands"
    port_swarm.main(["port_swarm.py", str(PRESETS), str(a), str(c)])
    assert len(list(c.glob("*.md"))) == len(_presets())
    total = sum(len(_load(f)["agents"]) for f in _presets())
    assert len(list(a.glob("*.md"))) == total
    for p in list(a.glob("*.md")) + list(c.glob("*.md")):
        m = REMOVED_RE.search(p.read_text(encoding="utf-8"))
        assert not m, f"{p.name}: residual removed-tool token {m.group()!r}"
