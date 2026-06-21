"""Perplexity (Sonar) provider profile.

Perplexity's Sonar models are exposed through an OpenAI-compatible Chat
Completions endpoint at ``https://api.perplexity.ai``, so the profile is almost
fully declarative — no transport quirks beyond the base URL and key.

What makes Sonar special is that every model is *web-grounded*: the server runs
a live search before answering and returns ``citations`` / ``search_results``
alongside the completion. That makes Sonar an excellent **auxiliary / grounding
model** (set as ``default_aux_model`` so web-content compression and "what does
the web say about X" calls get fresh answers), and a strong choice for one-shot
research turns. It is a search-answer engine rather than a general agentic
tool-caller, so it is not recommended as the primary model driving long
multi-tool agent loops — prefer it for grounded Q&A and ``sonar-deep-research``
for deep dives.

Model families (Jun 2026):
  - ``sonar``                 — fast, cheap grounded answers
  - ``sonar-pro``             — higher-quality grounded answers, more sources
  - ``sonar-reasoning``       — chain-of-thought + search
  - ``sonar-reasoning-pro``   — reasoning + search, top tier
  - ``sonar-deep-research``   — long-running multi-step research reports

Env var::

    PERPLEXITY_API_KEY=...   # https://www.perplexity.ai/settings/api
"""

from __future__ import annotations

from providers import register_provider
from providers.base import ProviderProfile

perplexity = ProviderProfile(
    name="perplexity",
    aliases=("sonar", "pplx"),
    env_vars=("PERPLEXITY_API_KEY",),
    display_name="Perplexity (Sonar)",
    description="Perplexity Sonar — web-grounded answer models (native API)",
    signup_url="https://www.perplexity.ai/settings/api",
    fallback_models=(
        "sonar",
        "sonar-pro",
        "sonar-reasoning",
        "sonar-reasoning-pro",
        "sonar-deep-research",
    ),
    base_url="https://api.perplexity.ai",
    default_aux_model="sonar",
)

register_provider(perplexity)


def register(ctx) -> None:  # noqa: D401 — plugin entry point
    """Plugin entry point.

    The profile is registered at import time via ``register_provider`` above
    (mirroring the other bundled ``model-provider`` plugins), so this hook is a
    no-op kept for contract symmetry with the plugin loader.
    """
    return None
