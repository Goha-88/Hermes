"""Perplexity web search plugin — bundled, auto-loaded.

Mirrors the ``plugins/web/tavily/`` layout: ``provider.py`` holds the
provider class, ``__init__.py::register(ctx)`` registers an instance.

Backed by Perplexity's Search API (``POST https://api.perplexity.ai/search``)
called over plain ``httpx`` — no extra SDK dependency. Search-only; Perplexity
has no per-URL extract endpoint, so the provider advertises ``supports_search``
but not ``supports_extract``.
"""

from __future__ import annotations

from plugins.web.perplexity.provider import PerplexityWebSearchProvider


def register(ctx) -> None:
    """Register the Perplexity Search provider with the plugin context."""
    ctx.register_web_search_provider(PerplexityWebSearchProvider())
