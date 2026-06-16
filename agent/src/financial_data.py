"""Financial data helpers for MCP tools — Tushare daily_basic, financial statements,
money flow, margin data, and earnings forecasts.

Each ``fetch_*_json()`` function follows the same pattern as
:func:`src.market_data.fetch_market_data_json`: accept codes + date range, call
the Tushare API, return a ``{code: [records]}`` JSON string.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

TUSHARE_TOKEN_PLACEHOLDERS: frozenset[str] = frozenset({"", "your-tushare-token"})


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_tushare_api():
    """Return a tushare pro_api instance, or None if TUSHARE_TOKEN is missing."""
    token = os.getenv("TUSHARE_TOKEN", "").strip()
    if token in TUSHARE_TOKEN_PLACEHOLDERS:
        return None
    try:
        import tushare as ts

        return ts.pro_api(token)
    except Exception as exc:
        logger.warning("Failed to init tushare: %s", exc)
        return None


def _to_date8(date_str: str) -> str:
    """Convert YYYY-MM-DD to YYYYMMDD for Tushare API calls."""
    return date_str.replace("-", "")


def _strip_suffix(code: str) -> str:
    """Strip .SZ/.SH/.BJ suffix for Tushare API calls that prefer bare codes."""
    return code.split(".")[0] if "." in code else code


def _safe_to_json(result: dict[str, list[dict[str, Any]]]) -> str:
    """Serialize a {code: [records]} dict to JSON, with NaN-safe default."""
    return json.dumps(result, default=str, allow_nan=False)


def _empty_result(codes: list[str], message: str) -> str:
    """Return a JSON error envelope when data is unavailable."""
    return _safe_to_json({"_error": message, "_codes": codes})


# ---------------------------------------------------------------------------
# 1. Daily fundamentals (daily_basic)
# ---------------------------------------------------------------------------


def fetch_daily_basic_json(
    codes: list[str],
    start_date: str,
    end_date: str,
    fields: list[str] | None = None,
) -> str:
    """Fetch daily fundamental indicators (PE/PB/ROE/market cap etc.) via Tushare.

    Args:
        codes: A-share symbols, e.g. ``["000636.SZ", "600000.SH"]``.
        start_date: Start date (YYYY-MM-DD).
        end_date: End date (YYYY-MM-DD).
        fields: Optional list of fields to return. ``None`` returns all available.
            Common fields: ``pe_ttm``, ``pb``, ``roe``, ``total_mv``, ``circ_mv``.

    Returns:
        JSON string: ``{code: [{trade_date, pe_ttm, pb, roe, total_mv, ...}, ...]}``.
    """
    api = _get_tushare_api()
    if api is None:
        return _empty_result(codes, "TUSHARE_TOKEN not configured")

    sd = _to_date8(start_date)
    ed = _to_date8(end_date)

    if fields:
        field_str = "ts_code,trade_date," + ",".join(fields)
    else:
        field_str = "ts_code,trade_date,pe_ttm,pb,roe,total_mv,circ_mv"

    results: dict[str, list[dict[str, Any]]] = {}
    unresolved: list[str] = []
    unresolved_errors: dict[str, str] = {}

    for code in codes:
        try:
            df = api.daily_basic(ts_code=code, start_date=sd, end_date=ed, fields=field_str)
            if df is not None and not df.empty:
                df["trade_date"] = df["trade_date"].astype(str)
                results[code] = df.to_dict(orient="records")
            else:
                results[code] = []
        except Exception as exc:
            logger.warning("daily_basic for %s failed: %s", code, exc)
            unresolved.append(code)
            unresolved_errors[code] = str(exc)
            results[code] = []

    if unresolved:
        results["_unresolved"] = unresolved
        results["_unresolved_errors"] = unresolved_errors

    return _safe_to_json(results)


# ---------------------------------------------------------------------------
# 2. Financial statements (income / balancesheet / cashflow / fina_indicator)
# ---------------------------------------------------------------------------

_VALID_TABLES: frozenset[str] = frozenset({"income", "balancesheet", "cashflow", "fina_indicator"})


def fetch_financial_statements_json(
    codes: list[str],
    table: str,
    start_date: str,
    end_date: str,
    fields: list[str] | None = None,
) -> str:
    """Fetch financial statement data via Tushare.

    Reuses :class:`backtest.loaders.tushare_fundamentals.TushareFundamentalProvider`
    for schema definitions and point-in-time filtering.

    Args:
        codes: A-share symbols, e.g. ``["000636.SZ"]``.
        table: One of ``"income"``, ``"balancesheet"``, ``"cashflow"``, ``"fina_indicator"``.
        start_date: Start date (YYYY-MM-DD), used as the PIT ``as_of`` boundary.
        end_date: End date (YYYY-MM-DD), used to filter ``end_date`` periods.
        fields: Optional list of columns to return. ``None`` returns all.

    Returns:
        JSON string: ``{code: [{ts_code, end_date, ann_date, ...}, ...]}``.
    """
    if table not in _VALID_TABLES:
        return _empty_result(codes, f"Unknown table: {table!r}. Valid: {sorted(_VALID_TABLES)}")

    api = _get_tushare_api()
    if api is None:
        return _empty_result(codes, "TUSHARE_TOKEN not configured")

    try:
        from backtest.loaders.tushare_fundamentals import TushareFundamentalProvider
    except Exception as exc:
        return _empty_result(codes, f"Failed to import TushareFundamentalProvider: {exc}")

    provider = TushareFundamentalProvider(api=api)

    try:
        df = provider.query_fundamentals(
            table=table,
            codes=codes,
            as_of=end_date,
            periods=None,
            fields=fields,
        )
    except Exception as exc:
        logger.warning("Financial statements query failed: %s", exc)
        return _empty_result(codes, f"Tushare query error: {exc}")

    if df.empty:
        return _safe_to_json({code: [] for code in codes})

    # Convert dates and group by code
    for col in ("end_date", "ann_date", "f_ann_date"):
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


# ---------------------------------------------------------------------------
# 3. Money flow (北向资金 / 主力资金流向)
# ---------------------------------------------------------------------------


def fetch_money_flow_json(
    codes: list[str],
    start_date: str,
    end_date: str,
) -> str:
    """Fetch daily money flow data (capital flow) via Tushare ``moneyflow``.

    Returns buy/sell volumes for small/medium/large/extra-large orders,
    useful for analysing 主力资金 (institutional money) and 北向资金 flow.

    Args:
        codes: A-share symbols.
        start_date: Start date (YYYY-MM-DD).
        end_date: End date (YYYY-MM-DD).

    Returns:
        JSON string: ``{code: [{trade_date, buy_sm_vol, sell_sm_vol, buy_lg_vol, ...}, ...]}``.
    """
    api = _get_tushare_api()
    if api is None:
        return _empty_result(codes, "TUSHARE_TOKEN not configured")

    sd = _to_date8(start_date)
    ed = _to_date8(end_date)

    results: dict[str, list[dict[str, Any]]] = {}
    unresolved: list[str] = []
    unresolved_errors: dict[str, str] = {}

    for code in codes:
        try:
            df = api.moneyflow(ts_code=code, start_date=sd, end_date=ed)
            if df is not None and not df.empty:
                df["trade_date"] = df["trade_date"].astype(str)
                results[code] = df.to_dict(orient="records")
            else:
                results[code] = []
        except Exception as exc:
            logger.warning("moneyflow for %s failed: %s", code, exc)
            unresolved.append(code)
            unresolved_errors[code] = str(exc)
            results[code] = []

    if unresolved:
        results["_unresolved"] = unresolved
        results["_unresolved_errors"] = unresolved_errors

    return _safe_to_json(results)


# ---------------------------------------------------------------------------
# 4. Margin data (融资融券)
# ---------------------------------------------------------------------------


def fetch_margin_data_json(
    codes: list[str],
    start_date: str,
    end_date: str,
) -> str:
    """Fetch daily margin trading data (融资融券) via Tushare ``margin_detail``.

    Returns margin buy/sell amounts and balances per stock.

    Args:
        codes: A-share symbols.
        start_date: Start date (YYYY-MM-DD).
        end_date: End date (YYYY-MM-DD).

    Returns:
        JSON string: ``{code: [{trade_date, rzye, rqye, rzmre, rqyl, ...}, ...]}``.
    """
    api = _get_tushare_api()
    if api is None:
        return _empty_result(codes, "TUSHARE_TOKEN not configured")

    sd = _to_date8(start_date)
    ed = _to_date8(end_date)

    results: dict[str, list[dict[str, Any]]] = {}
    unresolved: list[str] = []
    unresolved_errors: dict[str, str] = {}

    for code in codes:
        try:
            df = api.margin_detail(ts_code=code, start_date=sd, end_date=ed)
            if df is not None and not df.empty:
                df["trade_date"] = df["trade_date"].astype(str)
                results[code] = df.to_dict(orient="records")
            else:
                results[code] = []
        except Exception as exc:
            logger.warning("margin_detail for %s failed: %s", code, exc)
            unresolved.append(code)
            unresolved_errors[code] = str(exc)
            results[code] = []

    if unresolved:
        results["_unresolved"] = unresolved
        results["_unresolved_errors"] = unresolved_errors

    return _safe_to_json(results)


# ---------------------------------------------------------------------------
# 5. Earnings forecast (盈利预测)
# ---------------------------------------------------------------------------


def fetch_earnings_forecast_json(
    codes: list[str],
    start_date: str,
    end_date: str,
) -> str:
    """Fetch earnings forecast data (盈利预测) via Tushare ``forecast``.

    Returns analyst consensus forecasts: predicted net profit, revenue,
    growth rates, and forecast period.

    Args:
        codes: A-share symbols.
        start_date: Start date (YYYY-MM-DD), filters by ``ann_date``.
        end_date: End date (YYYY-MM-DD), filters by ``ann_date``.

    Returns:
        JSON string: ``{code: [{ts_code, ann_date, end_date, net_profit, ...}, ...]}``.
    """
    api = _get_tushare_api()
    if api is None:
        return _empty_result(codes, "TUSHARE_TOKEN not configured")

    sd = _to_date8(start_date)
    ed = _to_date8(end_date)

    results: dict[str, list[dict[str, Any]]] = {}
    unresolved: list[str] = []
    unresolved_errors: dict[str, str] = {}

    for code in codes:
        try:
            df = api.forecast(ts_code=code, start_date=sd, end_date=ed)
            if df is not None and not df.empty:
                for col in ("ann_date", "end_date"):
                    if col in df.columns:
                        df[col] = df[col].astype(str)
                results[code] = df.to_dict(orient="records")
            else:
                results[code] = []
        except Exception as exc:
            logger.warning("forecast for %s failed: %s", code, exc)
            unresolved.append(code)
            unresolved_errors[code] = str(exc)
            results[code] = []

    if unresolved:
        results["_unresolved"] = unresolved
        results["_unresolved_errors"] = unresolved_errors

    return _safe_to_json(results)
