"""Tests for the Perplexity web backend integration.

Coverage:
  _perplexity_search_request() — API key handling, Bearer auth header,
    endpoint + base-URL override, error propagation.
  _normalize_search_results() — search response normalization (snippet/date
    projection, missing fields, empty results).
  PerplexityWebSearchProvider — capability flags, availability, typed errors,
    config-driven filters (recency/domains/languages/country).
  web_search_tool — Perplexity dispatch path.

Unlike Tavily, Perplexity's plugin helpers are NOT re-exported through
``tools.web_tools`` — they are imported directly from
``plugins.web.perplexity.provider``. The provider does a function-local
``import httpx``, so HTTP is mocked by patching ``httpx.post`` on the real
httpx module (the same object the local import binds to).
"""

import json
import os
import pytest
from unittest.mock import patch, MagicMock

from tests.tools.conftest import register_all_web_providers


# ─── _perplexity_search_request ──────────────────────────────────────────────

class TestPerplexitySearchRequest:
    """Test suite for the _perplexity_search_request helper."""

    def test_raises_without_api_key(self):
        """No PERPLEXITY_API_KEY → ValueError with guidance."""
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("PERPLEXITY_API_KEY", None)
            from plugins.web.perplexity.provider import _perplexity_search_request
            with pytest.raises(ValueError, match="PERPLEXITY_API_KEY"):
                _perplexity_search_request({"query": "test"})

    def test_posts_with_bearer_auth_header(self):
        """api_key is sent as a Bearer token in the Authorization header, not the body."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"results": []}
        mock_response.raise_for_status = MagicMock()

        with patch.dict(os.environ, {"PERPLEXITY_API_KEY": "pplx-test-key"}):
            with patch("httpx.post", return_value=mock_response) as mock_post:
                from plugins.web.perplexity.provider import _perplexity_search_request
                _perplexity_search_request({"query": "hello"})

                mock_post.assert_called_once()
                call = mock_post.call_args
                headers = call.kwargs.get("headers") or {}
                payload = call.kwargs.get("json") or {}
                assert headers["Authorization"] == "Bearer pplx-test-key"
                # Key must NOT leak into the request body.
                assert "api_key" not in payload
                assert payload["query"] == "hello"
                assert "api.perplexity.ai/search" in call.args[0]

    def test_respects_base_url_override(self):
        """PERPLEXITY_BASE_URL overrides the default endpoint host."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"results": []}
        mock_response.raise_for_status = MagicMock()

        env = {"PERPLEXITY_API_KEY": "pplx-test", "PERPLEXITY_BASE_URL": "https://proxy.example.com/"}
        with patch.dict(os.environ, env):
            with patch("httpx.post", return_value=mock_response) as mock_post:
                from plugins.web.perplexity.provider import _perplexity_search_request
                _perplexity_search_request({"query": "x"})
                assert mock_post.call_args.args[0] == "https://proxy.example.com/search"

    def test_strips_internal_timeout_key(self):
        """The internal ``_timeout`` knob is popped from the payload and passed to httpx."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"results": []}
        mock_response.raise_for_status = MagicMock()

        with patch.dict(os.environ, {"PERPLEXITY_API_KEY": "pplx-test"}):
            with patch("httpx.post", return_value=mock_response) as mock_post:
                from plugins.web.perplexity.provider import _perplexity_search_request
                _perplexity_search_request({"query": "x", "_timeout": 12})
                call = mock_post.call_args
                assert "_timeout" not in (call.kwargs.get("json") or {})
                assert call.kwargs.get("timeout") == 12

    def test_raises_on_http_error(self):
        """Non-2xx responses propagate as httpx.HTTPStatusError."""
        import httpx as _httpx
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = _httpx.HTTPStatusError(
            "401 Unauthorized", request=MagicMock(), response=mock_response
        )

        with patch.dict(os.environ, {"PERPLEXITY_API_KEY": "pplx-bad-key"}):
            with patch("httpx.post", return_value=mock_response):
                from plugins.web.perplexity.provider import _perplexity_search_request
                with pytest.raises(_httpx.HTTPStatusError):
                    _perplexity_search_request({"query": "test"})


# ─── _normalize_search_results ───────────────────────────────────────────────

class TestNormalizeSearchResults:
    """Test search result normalization."""

    def test_basic_normalization_appends_date(self):
        from plugins.web.perplexity.provider import _normalize_search_results
        raw = {
            "results": [
                {"title": "AI 2026", "url": "https://a.com", "snippet": "Breakthroughs", "date": "06/21/2026"},
                {"title": "Tutorial", "url": "https://b.com", "snippet": "A tutorial", "date": ""},
            ],
            "id": "search_abc",
        }
        result = _normalize_search_results(raw)
        assert result["success"] is True
        web = result["data"]["web"]
        assert len(web) == 2
        assert web[0]["title"] == "AI 2026"
        assert web[0]["url"] == "https://a.com"
        # Date is appended to the description when present.
        assert web[0]["description"] == "Breakthroughs (06/21/2026)"
        assert web[0]["position"] == 1
        # No date → plain snippet, no trailing parens.
        assert web[1]["description"] == "A tutorial"
        assert web[1]["position"] == 2

    def test_empty_results(self):
        from plugins.web.perplexity.provider import _normalize_search_results
        result = _normalize_search_results({"results": []})
        assert result["success"] is True
        assert result["data"]["web"] == []

    def test_missing_fields(self):
        from plugins.web.perplexity.provider import _normalize_search_results
        result = _normalize_search_results({"results": [{}]})
        web = result["data"]["web"]
        assert web[0]["title"] == ""
        assert web[0]["url"] == ""
        assert web[0]["description"] == ""
        assert web[0]["position"] == 1

    def test_skips_non_dict_rows(self):
        from plugins.web.perplexity.provider import _normalize_search_results
        result = _normalize_search_results({"results": [None, "junk", {"title": "ok", "url": "https://ok.com"}]})
        web = result["data"]["web"]
        assert len(web) == 1
        assert web[0]["title"] == "ok"


# ─── PerplexityWebSearchProvider ─────────────────────────────────────────────

class TestPerplexityProvider:
    """Provider-level behavior: capabilities, availability, typed errors, filters."""

    def test_capabilities(self):
        from plugins.web.perplexity.provider import PerplexityWebSearchProvider
        p = PerplexityWebSearchProvider()
        assert p.name == "perplexity"
        assert p.display_name == "Perplexity"
        assert p.supports_search() is True
        # Search API has no per-URL extract endpoint.
        assert p.supports_extract() is False

    def test_is_available_tracks_api_key(self):
        from plugins.web.perplexity.provider import PerplexityWebSearchProvider
        p = PerplexityWebSearchProvider()
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("PERPLEXITY_API_KEY", None)
            assert p.is_available() is False
        with patch.dict(os.environ, {"PERPLEXITY_API_KEY": "pplx-x"}):
            assert p.is_available() is True

    def test_search_returns_typed_error_without_key(self):
        from plugins.web.perplexity.provider import PerplexityWebSearchProvider
        p = PerplexityWebSearchProvider()
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("PERPLEXITY_API_KEY", None)
            with patch("plugins.web.perplexity.provider._load_perplexity_web_config", return_value={}), \
                 patch("tools.interrupt.is_interrupted", return_value=False):
                result = p.search("hello")
        assert result["success"] is False
        assert "PERPLEXITY_API_KEY" in result["error"]

    def test_search_clamps_limit_to_cap(self):
        """limit above the API cap (20) is clamped; floor of 1 is enforced."""
        from plugins.web.perplexity.provider import PerplexityWebSearchProvider
        p = PerplexityWebSearchProvider()
        mock_response = MagicMock()
        mock_response.json.return_value = {"results": []}
        mock_response.raise_for_status = MagicMock()

        with patch.dict(os.environ, {"PERPLEXITY_API_KEY": "pplx-test"}), \
             patch("plugins.web.perplexity.provider._load_perplexity_web_config", return_value={}), \
             patch("tools.interrupt.is_interrupted", return_value=False), \
             patch("httpx.post", return_value=mock_response) as mock_post:
            p.search("q", limit=99)
            assert mock_post.call_args.kwargs["json"]["max_results"] == 20

    def test_search_applies_config_filters(self):
        """web.perplexity config drives recency/domains/languages/country filters."""
        from plugins.web.perplexity.provider import PerplexityWebSearchProvider
        p = PerplexityWebSearchProvider()
        mock_response = MagicMock()
        mock_response.json.return_value = {"results": []}
        mock_response.raise_for_status = MagicMock()

        cfg = {
            "country": "US",
            "recency": "week",
            "domains": ["arxiv.org", "nature.com"],
            "languages": ["en"],
            "timeout": 30,
        }
        with patch.dict(os.environ, {"PERPLEXITY_API_KEY": "pplx-test"}), \
             patch("plugins.web.perplexity.provider._load_perplexity_web_config", return_value=cfg), \
             patch("tools.interrupt.is_interrupted", return_value=False), \
             patch("httpx.post", return_value=mock_response) as mock_post:
            p.search("q", limit=5)
            payload = mock_post.call_args.kwargs["json"]
            assert payload["country"] == "US"
            assert payload["search_recency_filter"] == "week"
            assert payload["search_domain_filter"] == ["arxiv.org", "nature.com"]
            assert payload["search_language_filter"] == ["en"]
            assert mock_post.call_args.kwargs["timeout"] == 30

    def test_search_ignores_invalid_recency(self):
        from plugins.web.perplexity.provider import PerplexityWebSearchProvider
        p = PerplexityWebSearchProvider()
        mock_response = MagicMock()
        mock_response.json.return_value = {"results": []}
        mock_response.raise_for_status = MagicMock()

        with patch.dict(os.environ, {"PERPLEXITY_API_KEY": "pplx-test"}), \
             patch("plugins.web.perplexity.provider._load_perplexity_web_config", return_value={"recency": "decade"}), \
             patch("tools.interrupt.is_interrupted", return_value=False), \
             patch("httpx.post", return_value=mock_response) as mock_post:
            p.search("q")
            assert "search_recency_filter" not in mock_post.call_args.kwargs["json"]

    def test_search_returns_error_on_http_failure(self):
        import httpx as _httpx
        from plugins.web.perplexity.provider import PerplexityWebSearchProvider
        p = PerplexityWebSearchProvider()
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = _httpx.HTTPStatusError(
            "500", request=MagicMock(), response=mock_response
        )
        with patch.dict(os.environ, {"PERPLEXITY_API_KEY": "pplx-test"}), \
             patch("plugins.web.perplexity.provider._load_perplexity_web_config", return_value={}), \
             patch("tools.interrupt.is_interrupted", return_value=False), \
             patch("httpx.post", return_value=mock_response):
            result = p.search("q")
        assert result["success"] is False
        assert "Perplexity search failed" in result["error"]

    def test_setup_schema_shape(self):
        from plugins.web.perplexity.provider import PerplexityWebSearchProvider
        schema = PerplexityWebSearchProvider().get_setup_schema()
        assert schema["name"] == "Perplexity"
        assert schema["env_vars"][0]["key"] == "PERPLEXITY_API_KEY"


# ─── web_search_tool (Perplexity dispatch) ───────────────────────────────────

class TestWebSearchPerplexity:
    """Test web_search_tool dispatch to Perplexity."""

    _register_providers = staticmethod(register_all_web_providers)

    @pytest.fixture(autouse=True)
    def _populate_web_registry(self):
        self._register_providers()
        yield
        from agent.web_search_registry import _reset_for_tests
        _reset_for_tests()

    def test_search_dispatches_to_perplexity(self):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "results": [{"title": "Result", "url": "https://r.com", "snippet": "desc", "date": "06/01/2026"}],
            "id": "s1",
        }
        mock_response.raise_for_status = MagicMock()

        with patch("tools.web_tools._get_backend", return_value="perplexity"), \
             patch.dict(os.environ, {"PERPLEXITY_API_KEY": "pplx-test"}), \
             patch("plugins.web.perplexity.provider._load_perplexity_web_config", return_value={}), \
             patch("httpx.post", return_value=mock_response), \
             patch("tools.interrupt.is_interrupted", return_value=False):
            from tools.web_tools import web_search_tool
            result = json.loads(web_search_tool("test query", limit=3))
            assert result["success"] is True
            assert len(result["data"]["web"]) == 1
            assert result["data"]["web"][0]["title"] == "Result"
            assert result["data"]["web"][0]["description"] == "desc (06/01/2026)"
