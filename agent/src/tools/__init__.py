"""Tool registry: auto-discovery via BaseTool.__subclasses__().

Adding a new tool:
  1. Create a file in src/tools/ with a class extending BaseTool
  2. Done. It's automatically discovered and registered.

Tools with missing dependencies can override check_available() → False
to be silently excluded from the registry.
"""

from __future__ import annotations

import importlib
import logging
import pkgutil
from collections.abc import Mapping
from collections import deque
from pathlib import Path
from typing import TYPE_CHECKING, Callable

from src.agent.tools import BaseTool, ToolRegistry

if TYPE_CHECKING:
    from src.config.schema import AgentConfig

logger = logging.getLogger(__name__)

_SUBCLASSES_CACHE: list[type[BaseTool]] | None = None
_SHELL_TOOL_NAMES = {"bash", "background_run"}


def _discover_subclasses() -> list[type[BaseTool]]:
    """Import all modules in this package, then collect BaseTool subclasses.

    Results are cached after the first call.

    Returns:
        List of concrete BaseTool subclasses with a non-empty name.
    """
    global _SUBCLASSES_CACHE
    if _SUBCLASSES_CACHE is not None:
        return _SUBCLASSES_CACHE

    pkg_dir = str(Path(__file__).parent)
    for _, module_name, _ in pkgutil.iter_modules([pkg_dir]):
        if module_name.startswith("_"):
            continue
        try:
            importlib.import_module(f"src.tools.{module_name}")
        except Exception as exc:
            logger.warning("Skipped src.tools.%s: %s", module_name, exc)

    classes: list[type[BaseTool]] = []
    queue = deque(BaseTool.__subclasses__())
    while queue:
        cls = queue.popleft()
        if cls.name:
            classes.append(cls)
        queue.extend(cls.__subclasses__())

    _SUBCLASSES_CACHE = classes
    return classes


def build_registry(
    *,
    include_shell_tools: bool = False,
    agent_config: "AgentConfig | None" = None,
    session_id: str | None = None,
    event_callback: Callable[[str, dict], None] | None = None,
    warn_callback: Callable[[str], None] | None = None,
    _mcp_server_tool_name_segments: Mapping[str, str] | None = None,
) -> ToolRegistry:
    """Build the tool registry via auto-discovery, optionally enriched with MCP tools.

    Local tools are discovered and registered first. When ``agent_config``
    provides one or more MCP server definitions, remote tools are appended
    after the local tools. Each MCP server is isolated: a failure to connect
    or discover tools for one server emits a warning and skips that server
    without affecting local tools or other MCP servers.

    Args:
        include_shell_tools: Whether to include tools that execute shell
            commands. Local CLI/stdin entry points can enable this; networked
            server entry points should keep it disabled unless explicitly
            opted in.
        agent_config: Optional structured agent config. When provided and
            non-empty, MCP tools are appended to the registry after local
            tool discovery. Pass ``None`` (default) to preserve existing
            behavior with no MCP integration.
        session_id: Optional current session id injected into local tools that
            persist per-session state.
        event_callback: Optional event callback injected into local tools that
            mutate session-scoped state.
        warn_callback: Optional callable invoked with operator-facing warning
            messages. When provided, server-name collision warnings are passed
            to this callback in addition to the standard logger so CLI and
            SessionService can surface them to operators.

    Returns:
        ToolRegistry containing all available local tools followed by any
        successfully discovered MCP tools.
    """
    from src.tools.goal_tool import (
        AddGoalEvidenceTool,
        GetResearchGoalTool,
        StartResearchGoalTool,
        UpdateResearchGoalStatusTool,
    )

    goal_tool_classes = {
        StartResearchGoalTool,
        GetResearchGoalTool,
        AddGoalEvidenceTool,
        UpdateResearchGoalStatusTool,
    }
    registry = ToolRegistry()
    for cls in _discover_subclasses():
        try:
            if cls.name in _SHELL_TOOL_NAMES and not include_shell_tools:
                logger.info("Tool %s disabled by shell tool policy", cls.name)
                continue
            if not cls.check_available():
                logger.info("Tool %s unavailable, skipping", cls.name)
                continue
            if cls in goal_tool_classes:
                registry.register(cls(default_session_id=session_id, event_callback=event_callback))
            else:
                registry.register(cls())
        except Exception as exc:
            logger.warning("Failed to register tool %s: %s", cls.name, exc)

    if agent_config and agent_config.mcp_servers:
        from src.tools.mcp import build_mcp_tool_wrappers, resolve_mcp_server_tool_name_segments

        if _mcp_server_tool_name_segments is None:
            local_server_names = resolve_mcp_server_tool_name_segments(
                agent_config.mcp_servers.keys(),
                warn_callback=warn_callback,
            )
        else:
            local_server_names = {
                server_name: _mcp_server_tool_name_segments[server_name]
                for server_name in agent_config.mcp_servers
            }

        for server_name, server_config in agent_config.mcp_servers.items():
            try:
                wrappers = build_mcp_tool_wrappers(
                    server_name,
                    server_config,
                    local_server_name=local_server_names[server_name],
                )
                for tool in wrappers:
                    registry.register(tool)
                logger.info(
                    "Registered %d MCP tool(s) from server '%s'",
                    len(wrappers),
                    server_name,
                )
            except Exception as exc:
                skip_msg = f"MCP server '{server_name}' skipped: {exc}"
                logger.warning("Skipped MCP server '%s': %s", server_name, exc)
                if warn_callback is not None:
                    warn_callback(skip_msg)

    return registry


__all__ = ["build_registry"]
