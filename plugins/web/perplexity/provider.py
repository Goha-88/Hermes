"""Perplexity web search — plugin form.

Routes ``web_search`` tool calls through Perplexity's Search API
(``POST https://api.perplexity.ai/search``), which returns ranked,
web-grounded pages with titles, URLs, snippets and publication dates. We map
those rows onto the same ``{title, url, description, position}`` shape every
other Hermes web provider produces.

Reference: https://docs.perplexity.ai/api-reference/search-post

Search-only: Perplexity's Search API has no per-URL extract endpoint, so this
provider advertises ``supports_search`` but not ``supports_extract``. Pair it
with another extract backend (e.g. ``web.extract_backend: "firecrawl"``) if you
need page extraction.

Config keys this provider responds to::

    web:
      search_backend: "perplexity"   # explicit per-capability
      backend: "perplexity"          # shared fallback

Optional knobs (under ``web.perplexity`` in ``config.yaml``)::

    web:
      perplexity:
        country: "US"                  # ISO 3166-1 alpha-2 — bias results by country
        recency: "week"               # hour | day | week | month | year
        domains: ["arxiv.org"]        # search_domain_filter (max 20)
        languages: ["en"]             # ISO 639-1 codes (max 20)
        timeout: 60                    # seconds (default 60)

Env vars::

    PERPLEXITY_API_KEY=...           # https://www.perplexity.ai/settings/api (required)
    PERPLEXITY_BASE_URL=...          # optional override of https://api.perplexity.ai
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, List

from agent.web_search_provider import WebSearchProvider

logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = "https://api.perplexity.ai"
DEFAULT_TIMEOUT = 60
_MAX_RESULTS = 20  # Perplexity hard cap on max_results
_MAX_DOMAIN_FILTERS = 20  # Perplexity cap on search_domain_filter
_MAX_LANGUAGE_FILTERS = 20  # Perplexity cap on search_language_filter
_VALID_RECENCY = {"hour", "day", "week", "month", "year"}


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------


def _load_perplexity_web_config() -> Dict[str, Any]:
    """Read ``web.perplexity`` from config.yaml (returns {} on miss)."""
    try:
        from hermes_cli.config import load_config

        cfg = load_config()
        web_section = cfg.get("web") if isinstance(cfg, dict) else None
        pplx_section = web_section.get("perplexity") if isinstance(web_section, dict) else None
        return pplx_section if isinstance(pplx_section, dict) else {}
    except Exception as exc:  # noqa: BLE001
        logger.debug("Could not load web.perplexity config: %s", exc)
        return {}


def _coerce_str_list(value: Any, cap: int) -> List[str]:
    """Coerce a config value to a clean list of <=cap stripped strings."""
    if not isinstance(value, list):
        return []
    cleaned: List[str] = []
    for item in value:
        if isinstance(item, str) and item.strip():
            cleaned.append(item.strip())
        if len(cleaned) >= cap:
            break
    return cleaned


# ---------------------------------------------------------------------------
# HTTP
# ---------------------------------------------------------------------------


def _perplexity_search_request(payload: Dict[str, Any]) -> Dict[str, Any]:
    """POST to the Perplexity Search API and return the parsed JSON response.

    Auth is sent as a Bearer token in the ``Authorization`` header (unlike
    Tavily, which puts the key in the body). Raises ``ValueError`` when
    ``PERPLEXITY_API_KEY`` is unset; the caller catches and surfaces it as a
    typed error response.
    """
    import httpx

    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        raise ValueError(
            "PERPLEXITY_API_KEY environment variable not set. "
            "Get your API key at https://www.perplexity.ai/settings/api"
        )

    base_url = os.getenv("PERPLEXITY_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
    url = f"{base_url}/search"
    timeout = payload.pop("_timeout", DEFAULT_TIMEOUT)
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    logger.info("Perplexity search request to %s", url)

    response = httpx.post(url, json=payload, headers=headers, timeout=timeout)
    response.raise_for_status()
    return response.json()


def _normalize_search_results(response: Dict[str, Any]) -> Dict[str, Any]:
    """Map Perplexity ``/search`` response to ``{success, data: {web: [...]}}``.

    The Search API returns ``{"results": [{"title", "url", "snippet",
    "date"}], "id", "server_time"}``; we project each row onto the standard
    Hermes search row and append the publication date to the description when
    present so date-sensitive queries surface it.
    """
    web_results = []
    for i, result in enumerate(response.get("results", [])):
        if not isinstance(result, dict):
            continue
        snippet = result.get("snippet", "") or ""
        date = result.get("date", "") or ""
        description = f"{snippet} ({date})".strip() if date else snippet
        web_results.append(
            {
                "title": result.get("title", "") or "",
                "url": result.get("url", "") or "",
                "description": description,
                "position": i + 1,
            }
        )
    return {"success": True, "data": {"web": web_results}}


# ---------------------------------------------------------------------------
# Provider
# ---------------------------------------------------------------------------


class PerplexityWebSearchProvider(WebSearchProvider):
    """Perplexity Search API provider — search only."""

    @property
    def name(self) -> str:
        return "perplexity"

    @property
    def display_name(self) -> str:
        return "Perplexity"

    def is_available(self) -> bool:
        """Return True when ``PERPLEXITY_API_KEY`` is set to a non-empty value."""
        return bool(os.getenv("PERPLEXITY_API_KEY", "").strip())

    def supports_search(self) -> bool:
        return True

    def supports_extract(self) -> bool:
        # Perplexity's Search API has no per-URL extract endpoint.
        return False

    def search(self, query: str, limit: int = 5) -> Dict[str, Any]:
        """Execute a Perplexity Search API query.

        Returns ``{"success": True, "data": {"web": [...]}}`` on success,
        ``{"success": False, "error": str}`` on failure (incl. missing API
        key and HTTP errors).
        """
        try:
            from tools.interrupt import is_interrupted

            if is_interrupted():
                return {"success": False, "error": "Interrupted"}

            cfg = _load_perplexity_web_config()
            payload: Dict[str, Any] = {
                "query": query,
                "max_results": max(1, min(limit, _MAX_RESULTS)),
            }

            country = cfg.get("country")
            if isinstance(country, str) and country.strip():
                payload["country"] = country.strip()

            recency = cfg.get("recency")
            if isinstance(recency, str) and recency.strip().lower() in _VALID_RECENCY:
                payload["search_recency_filter"] = recency.strip().lower()

            domains = _coerce_str_list(cfg.get("domains"), _MAX_DOMAIN_FILTERS)
            if domains:
                payload["search_domain_filter"] = domains

            languages = _coerce_str_list(cfg.get("languages"), _MAX_LANGUAGE_FILTERS)
            if languages:
                payload["search_language_filter"] = languages

            timeout = cfg.get("timeout")
            payload["_timeout"] = timeout if isinstance(timeout, (int, float)) else DEFAULT_TIMEOUT

            logger.info("Perplexity search: '%s' (limit=%d)", query, limit)
            raw = _perplexity_search_request(payload)
            return _normalize_search_results(raw)
        except ValueError as exc:
            # Raised when PERPLEXITY_API_KEY is missing.
            return {"success": False, "error": str(exc)}
        except Exception as exc:  # noqa: BLE001 — including httpx errors
            logger.warning("Perplexity search error: %s", exc)
            return {"success": False, "error": f"Perplexity search failed: {exc}"}

    def get_setup_schema(self) -> Dict[str, Any]:
        return {
            "name": "Perplexity",
            "badge": "paid",
            "tag": "Real-time, web-grounded search with domain + recency filters.",
            "env_vars": [
                {
                    "key": "PERPLEXITY_API_KEY",
                    "prompt": "Perplexity API key",
                    "url": "https://www.perplexity.ai/settings/api",
                },
            ],
        }
