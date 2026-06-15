"""Event/sentiment data helper for MCP tools — wraps RSSHubEventProvider.

Requires a running RSSHub instance and ``RSSHUB_BASE_URL`` set in ``.env``.
When RSSHub is not configured, the tool returns a clear error message instead of
crashing.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


def _safe_to_json(result: dict[str, list[dict[str, Any]]]) -> str:
    """Serialize a {code: [records]} dict to JSON, with NaN-safe default."""
    return json.dumps(result, default=str, allow_nan=False)


def fetch_events_json(
    codes: list[str],
    start_date: str,
    end_date: str,
    feeds: list[str] | None = None,
) -> str:
    """Fetch structured news/events with sentiment scores via RSSHub.

    Wraps :class:`backtest.loaders.rsshub_events.RSSHubEventProvider` which
    provides point-in-time-safe event retrieval and lexicon-based sentiment
    scoring.

    Requires a self-hosted RSSHub instance. Set ``RSSHUB_BASE_URL`` in ``.env``.
    Without it, this tool returns an error message.

    Args:
        codes: Instrument codes (e.g. ``["000636.SZ", "600519.SH"]``).
        start_date: Start date (YYYY-MM-DD), used as PIT ``as_of`` boundary.
        end_date: End date (YYYY-MM-DD), used as PIT ``as_of`` boundary.
        feeds: Optional list of feed names to query. ``None`` queries all
            registered feeds. Feeds must be configured via the RSSHub provider's
            feed specs (see :class:`FeedSpec`).

    Returns:
        JSON string: ``{code: [{knowable_date, event_type, score, source, summary}, ...]}``.
    """
    try:
        from backtest.loaders.rsshub_events import RSSHubEventProvider
    except Exception as exc:
        return _safe_to_json({"_error": f"Failed to import RSSHubEventProvider: {exc}"})

    provider = RSSHubEventProvider()
    if not provider.is_available():
        return _safe_to_json({
            "_error": (
                "RSSHub is not configured. Set RSSHUB_BASE_URL in .env to a "
                "running RSSHub instance (e.g. http://localhost:1200). "
                "Deploy with: docker run -d --name rsshub -p 1200:1200 diygod/rsshub"
            ),
            "_codes": codes,
        })

    try:
        df = provider.query_events(
            codes=codes,
            as_of=end_date,
            feeds=feeds,
        )
    except Exception as exc:
        logger.warning("RSSHub query failed: %s", exc)
        return _safe_to_json({"_error": f"RSSHub query error: {exc}", "_codes": codes})

    if df.empty:
        return _safe_to_json({code: [] for code in codes})

    # Normalize dates and group by code
    for col in ("knowable_date",):
        if col in df.columns:
            df[col] = df[col].astype(str)

    results: dict[str, list[dict[str, Any]]] = {}
    for code in codes:
        mask = df["ts_code"] == code
        if mask.any():
            results[code] = df[mask].to_dict(orient="records")
        else:
            results[code] = []

    return _safe_to_json(results)
