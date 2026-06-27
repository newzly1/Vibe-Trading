"""OAuth token-cache presence check for live broker MCP channels.

Extracted from the removed live-order subsystem (``src.live.registry``) so the
read-only ``trading_*`` connector surface can detect an already-authorized live
channel without depending on ``src.live``. The token VALUE is never read,
returned, or logged — only presence.
"""

from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

#: FastMCP's OAuth token cache collection name (``TokenStorageAdapter``).
_OAUTH_TOKEN_COLLECTION = "mcp-oauth-token"


def has_cached_oauth_token(url: str, cache_dir: str) -> bool:
    """Return whether a cached OAuth token already exists for a live channel.

    FastMCP's OAuth provider persists tokens through the same
    :func:`~src.tools.mcp._build_token_store` (``FileTreeStore``) backend, under
    the ``mcp-oauth-token`` collection. ``FileTreeStore`` lays a collection out
    as ``<cache_dir>/mcp-oauth-token/`` containing one entry file per cached
    token. We detect authorization by the PRESENCE of any token entry file in
    that collection directory rather than by reconstructing FastMCP's exact
    (server-URL-derived) cache key — the key scheme is an internal detail and is
    not stable to reconstruct, so a directory-level presence check is the robust
    signal. The token VALUE is never read, returned, or logged — only presence.

    Args:
        url: The live channel's MCP server URL (unused for the presence scan,
            kept for signature symmetry and future per-URL scoping).
        cache_dir: The configured token cache directory.

    Returns:
        ``True`` when at least one token entry file is present; ``False`` on an
        absent/empty cache or any read error (fail-closed: unreadable = not
        authorized, so a non-interactive run skips rather than blocks).
    """
    try:
        collection = Path(cache_dir).expanduser() / _OAUTH_TOKEN_COLLECTION
        if not collection.is_dir():
            return False
        # Any persisted token entry (FileTreeStore writes one file per key, plus
        # a sidecar ``*-info.json`` at the cache root — not inside the dir).
        return any(p.is_file() for p in collection.iterdir())
    except OSError as exc:
        logger.debug("OAuth token presence check failed for %s: %s", url, exc)
        return False
