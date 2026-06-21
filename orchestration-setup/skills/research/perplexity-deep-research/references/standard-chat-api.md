# Perplexity Standard Chat API (Non-Async)

Complementary to the async `sonar-deep-research` flow. Use the standard chat completions
API for **quick, cited research** that returns in seconds, not minutes.

## When to Use This Instead of Deep Research

| Standard API (`sonar`/`sonar-pro`) | Async Deep Research (`sonar-deep-research`) |
|---|---|
| Single question, quick answer | Multi-step investigation, formal report |
| 1-5 seconds response | 30s – 5 minutes |
| ~$0.005-0.01 per query | ~$0.05-0.50 per job |
| Citations inline + search results | Full report with sections |
| Real-time search context | Dozens of searches + synthesis |

## Quickest Path — curl

```bash
curl -s https://api.perplexity.ai/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $PERPLEXITY_API_KEY" \
  -d '{
    "model": "sonar-pro",
    "messages": [
      {"role": "user", "content": "Your research question here"}
    ]
  }' | python3 -m json.tool
```

## Model Selection

| Model | Use Case | Cost |
|-------|----------|------|
| `sonar` | Simple factual questions | Cheapest |
| `sonar-pro` | Research with deep citations | ~$0.01/query |
| `sonar-reasoning-pro` | Complex reasoning + research | More expensive |
| `sonar-deep-research` | Multi-minute investigations | Most expensive (use async) |

## Via Python (execute_code)

```python
import json, os, subprocess

api_key = os.environ["PERPLEXITY_API_KEY"]

payload = {
    "model": "sonar-pro",
    "messages": [{"role": "user", "content": "..."}]
}

result = subprocess.run(
    ["curl", "-s", "https://api.perplexity.ai/chat/completions",
     "-H", "Content-Type: application/json",
     "-H", f"Authorization: Bearer {api_key}",
     "-d", json.dumps(payload)],
    capture_output=True, text=True, timeout=60
)

data = json.loads(result.stdout)
content = data["choices"][0]["message"]["content"]
citations = data.get("citations", [])

print(content)
print("\n=== SOURCES ===")
for i, c in enumerate(citations):
    print(f"[{i+1}] {c}")
```

## Response Structure

The standard API response includes:
- `choices[0].message.content` — the answer text with inline citations
- `citations` — array of source URLs
- `search_results` — detailed search result objects with snippets, titles, URLs
- `usage` — token counts and cost breakdown

## Tips for Russian-Language Research

- `sonar-pro` handles Russian queries well
- For RU-specific topics, add "на русском" or "отвечай на русском" to the prompt
- Citations will include both RU and EN sources
- Cost is the same regardless of language

## Pitfalls

- ❌ **Using this for single-fact lookups** — use `web_search` instead (cheaper)
- ❌ **Expecting structured data** — this returns prose, not JSON tables. Use `firecrawl_extract` for structured extraction
- ❌ **Forgetting to handle the API key securely** — always read from env, never hardcode
- ❌ **Not checking citations** — Perplexity sometimes hallucinates URLs. Verify important claims
