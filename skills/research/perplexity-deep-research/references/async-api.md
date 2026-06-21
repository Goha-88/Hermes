# Perplexity Async Sonar API Reference

Endpoints used by `sonar-deep-research`. All requests are authenticated with a
Bearer token: `Authorization: Bearer $PERPLEXITY_API_KEY`. Base URL:
`https://api.perplexity.ai` (override with `PERPLEXITY_BASE_URL`).

Async jobs have a **7-day TTL** — fetch and persist anything you need to keep.

## Submit a job

```
POST /v1/async/sonar
```

Request body — the chat-completion request is nested under `request`:

```json
{
  "request": {
    "model": "sonar-deep-research",
    "messages": [
      {"role": "system", "content": "Optional steering prompt"},
      {"role": "user", "content": "Your research question"}
    ],
    "search_mode": "web",
    "search_domain_filter": ["example.com"]
  },
  "idempotency_key": "optional-unique-key"
}
```

- `search_mode` (optional): `web` | `academic` | `sec`.
- `search_domain_filter` (optional): restrict sources to listed domains.

Response (job created):

```json
{
  "id": "asyn_xxxxxxxxxxxxxxxxx",
  "model": "sonar-deep-research",
  "created_at": 1717988400,
  "status": "pending"
}
```

```bash
curl https://api.perplexity.ai/v1/async/sonar \
  -H "Authorization: Bearer $PERPLEXITY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"request":{"model":"sonar-deep-research","messages":[{"role":"user","content":"..."}]}}'
```

## Poll a job

```
GET /v1/async/sonar/{request_id}
```

Response (in progress):

```json
{ "id": "asyn_...", "status": "processing", "response": null }
```

Response (completed) — the completion lives under `response`:

```json
{
  "id": "asyn_...",
  "model": "sonar-deep-research",
  "created_at": 1717988400,
  "started_at": 1717988405,
  "completed_at": 1717988620,
  "status": "completed",
  "failed_at": null,
  "error_message": null,
  "response": {
    "id": "cmpl_...",
    "model": "sonar-deep-research",
    "choices": [
      {
        "index": 0,
        "message": { "role": "assistant", "content": "# Report...\n..." },
        "finish_reason": "stop"
      }
    ],
    "citations": ["https://example.com/source1"],
    "search_results": [
      { "title": "Source title", "url": "https://example.com/s1", "date": "2026-01-10" }
    ],
    "usage": { "prompt_tokens": 100, "completion_tokens": 4000, "total_tokens": 4100 }
  }
}
```

### Status lifecycle

`pending` → `processing` → `completed` (or `failed`).

- Read the report from `response.choices[0].message.content`.
- Read citations from `response.citations` (URL strings) and/or
  `response.search_results` (objects with `title`/`url`/`date`).
- On `failed`, the reason is in the top-level `error_message`.

## List jobs

```
GET /v1/async/sonar
```

Lists all async requests for the authenticated user.

## Notes

- `sonar-deep-research` reasons before answering; the `content` may include a
  leading `<think>…</think>` block. The helper script strips it by default
  (`--raw` keeps it).
- Deep research is the slowest and most expensive Sonar tier — use it only when
  a thorough, cited report is wanted. For quick answers use `sonar`/`sonar-pro`
  (sync `POST /v1/chat/completions`) or the `web_search` tool.
