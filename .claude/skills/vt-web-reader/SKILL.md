---
name: vt-web-reader
description: Read web pages, articles, and document links by converting URLs into Markdown text. Use the `read_url` tool directly, without bash. Sends the full URL to the third-party Jina Reader (r.jina.ai).
---

<!--
Available Vibe-Trading MCP tools for this skill:
  - get_market_data(codes, start_date, end_date, source, interval) — fetch OHLCV
  - backtest(run_dir) — run backtest from config.json + signal_engine.py
  - factor_analysis(codes, factor_name, start_date, end_date, ...) — factor IC/returns
  - analyze_options(...) — options pricing & greeks
  - pattern_recognition(run_dir) — chart pattern detection
  - read_url(url) / read_document(path) / web_search(query) — content tools
  - write_file(path, content) / read_file(path) — file I/O
  - list_skills() / load_skill(name) — skill discovery
-->

# Web Reading

## Purpose

Converts any URL into clean Markdown text, removing ads, navigation, styling, and other distractions. Suitable for:
- Reading API documentation (`tushare`, `OKX`, `yfinance`, and similar)
- Reading technical articles and blogs
- Retrieving research reports and announcements
- Reading GitHub README / Wiki pages

## Usage

**Call the `read_url` tool directly (do not use bash + requests, call the tool directly):**

```
read_url(url="https://tushare.pro/document/2?doc_id=27")
```

Returns JSON:
```json
{
  "status": "ok",
  "title": "Page title",
  "url": "Original URL",
  "content": "Page content in Markdown format",
  "length": 12345
}
```

## Notes

- Content longer than 8000 characters will be truncated, with the total length noted at the end
- Dynamically rendered SPA pages may return only skeleton HTML
- Chinese content is supported normally

## Privacy & freshness

- **Third-party dependency:** `read_url` forwards the full target URL
  (including any query string) to the external Jina Reader service
  (`r.jina.ai`). Do **not** pass URLs containing credentials, tokens, or
  private/internal addresses — they would leave this host.
- **Caching/staleness:** results may be a cached snapshot, not live data.
  When stale, the JSON includes `"cached": true`; pass `no_cache=true` to
  force a fresh fetch (slower — use only when freshness matters).
- **Bash fallback caveat:** if a site blocks the reader (e.g. HTTP 451) a
  manual `bash + requests` fetch is possible, but it **bypasses this
  tool's URL safety guard and the Jina layer** — use sparingly and never
  for internal/authenticated URLs.

## Common Usage

### Read API Documentation
```
read_url(url="https://tushare.pro/document/2?doc_id=27")
```

### Read Technical Articles
```
read_url(url="https://blog.example.com/quantitative-trading-guide")
```

### Retrieve GitHub Project Information
```
read_url(url="https://github.com/PaddlePaddle/PaddleOCR")
```
