#!/usr/bin/env python3
"""Port Vibe-Trading swarm presets to native Claude Code subagents + commands.

Reads ``agent/src/swarm/presets/*.yaml`` and writes, for each preset:
  * ``claude-trading/.claude/agents/<preset>-<agent_id>.md`` — one subagent
    definition per preset agent (the role/persona + analytical spec).
  * ``claude-trading/.claude/commands/<preset>.md`` — one slash command that
    orchestrates the preset's task DAG by dispatching those subagents in
    dependency order (same-level tasks run in parallel).

``load_skill("x")`` references become ``the **vt-x** skill`` links and removed
MCP / harness-duplicate tool names are rewritten to their native Claude Code
equivalents. Re-runnable: both output dirs are wiped and regenerated.

Usage:
    python port_swarm.py [PRESETS_DIR] [AGENTS_OUT] [COMMANDS_OUT]
"""
from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

import yaml

# Removed MCP / harness-duplicate tool name -> native Claude Code equivalent.
# (Same table as the skills port, for consistent prose across the port.)
TOOL_RENAMES = {
    "read_document": "Read",
    "read_file": "Read",
    "write_file": "Write",
    "edit_file": "Edit",
    "read_url": "WebFetch",
    "web_search": "WebSearch",
    "list_skills": "Skill",
}


def slug(s: str) -> str:
    """kebab-case slug: lowercase, ``_``/space -> ``-``, drop other chars."""
    s = s.strip().lower().replace("_", "-").replace(" ", "-")
    s = re.sub(r"[^a-z0-9-]", "", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s


def rewrite_text(text: str) -> str:
    """Rewrite load_skill() calls and removed-tool references to native forms."""
    # load_skill("x") -> the **vt-x** skill  (swallow optional wrapping backticks)
    text = re.sub(r'`?load_skill\(\s*["\']([\w-]+)["\']\s*\)`?', r"the **vt-\1** skill", text)
    text = re.sub(r"\bload_skill\b", "the Skill tool", text)
    for old, new in TOOL_RENAMES.items():
        text = re.sub(r"\b" + re.escape(old) + r"\b", new, text)
    return text


def naturalize_vars(text: str) -> str:
    """Turn ``{var}`` placeholders into readable prose for a static role file.

    A subagent definition is a fixed system prompt; concrete values arrive
    per-dispatch from the orchestration command. ``{upstream_context}`` becomes
    a standard sentence; any other ``{x}`` becomes ``the x`` (underscores -> spaces).
    """
    text = text.replace(
        "{upstream_context}",
        "Any upstream analysis you depend on is included in the task prompt you receive.",
    )
    return re.sub(r"\{(\w+)\}", lambda m: "the " + m.group(1).replace("_", " "), text)


def build_agent_md(preset_slug: str, agent: dict) -> tuple[str, str]:
    """Return ``(filename, content)`` for one subagent definition."""
    name = f"{preset_slug}-{slug(agent['id'])}"
    role = (agent.get("role") or agent["id"]).strip().replace("\n", " ")
    body = naturalize_vars(rewrite_text((agent.get("system_prompt") or "").rstrip()))
    skills = agent.get("skills") or []
    skill_line = ""
    if skills:
        refs = ", ".join(f"vt-{slug(s)}" for s in skills)
        skill_line = (
            f"\n\n**Relevant skills:** {refs} — consult these via the Skill tool "
            "for methodology before producing your analysis."
        )
    desc = f"{role} for the {preset_slug} team; dispatched by the /{preset_slug} command."
    content = f"---\nname: {name}\ndescription: {desc}\n---\n\n{body}{skill_line}\n"
    return f"{name}.md", content


def phases(tasks: list[dict]) -> list[list[dict]]:
    """Group tasks into dependency levels (Kahn layering); same level => parallel."""
    by_id = {t["id"]: t for t in tasks}
    level: dict[str, int] = {}

    def lvl(tid: str) -> int:
        if tid in level:
            return level[tid]
        deps = by_id[tid].get("depends_on") or []
        level[tid] = 0 if not deps else 1 + max(lvl(d) for d in deps)
        return level[tid]

    for t in tasks:
        lvl(t["id"])
    groups: dict[int, list[dict]] = {}
    for t in tasks:  # preserve original task order within a level
        groups.setdefault(level[t["id"]], []).append(t)
    return [groups[k] for k in sorted(groups)]


def build_command_md(preset: dict) -> str:
    """Return the slash-command content for one preset."""
    ps = slug(preset["name"])
    title = preset.get("title") or preset["name"]
    desc = (preset.get("description") or title).replace("\n", " ").strip()
    agents = {a["id"]: a for a in preset["agents"]}
    tasks = preset.get("tasks") or []
    by_task = {t["id"]: t for t in tasks}
    variables = preset.get("variables") or []

    # $1.. positional mapping for variables, plus argument-hint + Inputs lines.
    hint = " ".join(f"[{v['name']}]" for v in variables)
    pos = {v["name"]: f"${i + 1}" for i, v in enumerate(variables)}
    input_lines = "\n".join(
        f"- `<{v['name']}>` = `{pos[v['name']]}` — {(v.get('description') or '').strip()}"
        for v in variables
    )

    def fill(template: str) -> str:
        """Render a prompt_template: ``{var}`` -> ``<var>`` (resolved in Inputs)."""
        return re.sub(r"\{(\w+)\}", lambda m: f"<{m.group(1)}>", template or "")

    out: list[str] = []
    out.append("---")
    out.append(f"description: {desc}")
    out.append(f"argument-hint: {hint}")
    out.append("---")
    out.append("")
    out.append(f"# {title}")
    out.append("")
    out.append(
        f"Native replacement for the Vibe-Trading `{preset['name']}` swarm preset. "
        "You are the orchestrator. Dispatch each role below as a subagent with the "
        "**Agent** tool (`subagent_type` = the agent name shown in backticks), honoring "
        "the phase order: **phases run sequentially**, and all agents **within one phase "
        "run in parallel** — dispatch a phase's agents together in a single message. "
        "Pass each downstream agent the upstream outputs named in its bullet."
    )
    out.append("")
    out.append("**Inputs** (from `$ARGUMENTS`):")
    out.append(input_lines if input_lines else "- (no variables)")
    out.append("")

    for i, group in enumerate(phases(tasks), start=1):
        parallel = " (parallel)" if len(group) > 1 else ""
        out.append(f"## Phase {i}{parallel}")
        for t in group:
            agent = agents[t["agent_id"]]
            aname = f"{ps}-{slug(agent['id'])}"
            prompt = fill(t.get("prompt_template") or "")
            out.append(f"- **`{aname}`** — \"{prompt}\"")
            for label, src_task_id in (t.get("input_from") or {}).items():
                src_agent = agents[by_task[src_task_id]["agent_id"]]
                src_role = (src_agent.get("role") or src_agent["id"]).strip()
                out.append(
                    f"  - Provide as `{label}`: the **{src_role}** "
                    f"(`{ps}-{slug(src_agent['id'])}`) output from an earlier phase."
                )
        out.append("")

    # Final output = the deepest phase's task(s).
    last = phases(tasks)[-1]
    finals = ", ".join(
        f"**{(agents[t['agent_id']].get('role') or t['agent_id']).strip()}**" for t in last
    )
    out.append("## Final output")
    out.append(
        f"Return the {finals} output as the team's deliverable, citing the supporting "
        "analysis from earlier phases."
    )
    out.append("")
    return "\n".join(out)


def main(argv: list[str]) -> None:
    presets_dir = Path(argv[1]) if len(argv) > 1 else Path("agent/src/swarm/presets")
    agents_out = Path(argv[2]) if len(argv) > 2 else Path("claude-trading/.claude/agents")
    commands_out = Path(argv[3]) if len(argv) > 3 else Path("claude-trading/.claude/commands")
    for d in (agents_out, commands_out):
        if d.exists():
            shutil.rmtree(d)
        d.mkdir(parents=True)

    n_agents = 0
    presets = sorted(p for p in presets_dir.glob("*.yaml"))
    for f in presets:
        preset = yaml.safe_load(f.read_text(encoding="utf-8"))
        ps = slug(preset["name"])
        for agent in preset["agents"]:
            fname, content = build_agent_md(ps, agent)
            (agents_out / fname).write_text(content, encoding="utf-8")
            n_agents += 1
        (commands_out / f"{ps}.md").write_text(build_command_md(preset), encoding="utf-8")
    print(f"ported {len(presets)} presets -> {n_agents} agents, {len(presets)} commands")


if __name__ == "__main__":
    main(sys.argv)
