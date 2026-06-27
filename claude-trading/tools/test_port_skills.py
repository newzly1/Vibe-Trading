"""Corpus contract for the ported Claude Code skills.

Verifies the converter (port_skills.py) and its committed output:
- Every source skill EXCEPT the SKIP set becomes ``vt-<name>/SKILL.md``.
- No generated SKILL.md (or aux ``.md``) references a removed MCP tool as a
  whole word (the 5 I/O tools from Plan 1 + load_skill/list_skills).
- Frontmatter is Claude-Code-shaped (``name: vt-<name>`` + non-empty
  description) and the canonical MCP-capability comment is present.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
REPO_ROOT = TOOLS_DIR.parents[1]
SRC_SKILLS = REPO_ROOT / "agent" / "src" / "skills"
OUT_SKILLS = REPO_ROOT / "claude-trading" / ".claude" / "skills"

sys.path.insert(0, str(TOOLS_DIR))
import port_skills  # noqa: E402

REMOVED_TOOLS = [
    "read_file", "write_file", "read_url", "read_document",
    "web_search", "load_skill", "list_skills",
]
REMOVED_RE = re.compile(r"\b(" + "|".join(REMOVED_TOOLS) + r")\b")


def _expected_names() -> set[str]:
    return {
        p.name for p in SRC_SKILLS.iterdir()
        if p.is_dir() and p.name not in port_skills.SKIP
    }


def test_all_nonskip_skills_ported(tmp_path: Path) -> None:
    """Converter emits vt-<name>/SKILL.md for every non-skipped source skill."""
    port_skills.main(["port_skills", str(SRC_SKILLS), str(tmp_path)])
    expected = _expected_names()
    assert len(expected) == 75, f"expected 75 non-skip source skills, got {len(expected)}"
    for name in expected:
        assert (tmp_path / f"vt-{name}" / "SKILL.md").is_file(), f"missing vt-{name}/SKILL.md"
    for skipped in port_skills.SKIP:
        assert not (tmp_path / f"vt-{skipped}").exists(), f"{skipped} should be skipped"


def test_committed_skills_have_no_removed_tool_refs() -> None:
    """Shipped skills must not re-advertise any removed MCP tool (whole word)."""
    assert OUT_SKILLS.is_dir(), "run port_skills.py to generate claude-trading/.claude/skills/"
    leaks: list[str] = []
    for md in OUT_SKILLS.rglob("*.md"):
        for m in REMOVED_RE.finditer(md.read_text(encoding="utf-8")):
            leaks.append(f"{md.relative_to(OUT_SKILLS)}: {m.group(1)}")
    assert not leaks, "removed-tool references found:\n" + "\n".join(leaks[:40])


def test_committed_frontmatter_and_mcp_comment() -> None:
    """Each committed vt-* SKILL.md has vt-name, a description, and the MCP comment."""
    assert OUT_SKILLS.is_dir()
    for skill_dir in sorted(p for p in OUT_SKILLS.iterdir() if p.is_dir()):
        md = skill_dir / "SKILL.md"
        assert md.is_file(), f"{skill_dir.name} missing SKILL.md"
        text = md.read_text(encoding="utf-8")
        assert text.startswith("---\n"), f"{skill_dir.name}: no frontmatter"
        assert f"name: {skill_dir.name}\n" in text, f"{skill_dir.name}: name != dir"
        assert re.search(r"\ndescription: \S", text), f"{skill_dir.name}: empty description"
        assert "Vibe-Trading MCP tools available to this skill" in text, (
            f"{skill_dir.name}: missing MCP-capability comment"
        )
