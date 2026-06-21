# Replicate API — confirmed working pattern (June 2026)

Copy of the proven `video-gen` reference, included so this umbrella skill is self-contained for any agent that loads it without `video-gen` in context.

## URL construction — always concatenate

Anything that involves the runtime redactor / placeholder substitution breaks `predictions/` URLs that look like `predict***{id}`. **Always build URLs with `+`:**

```python
poll_url = "https://api.replicate.com/v1/predictions/" + pred_id
```

NEVER:
```python
poll_url = f"https://api.replicate.com/v1/predictions/{pred_id}"
poll_url = "https://api.replicate.com/v1/predict***" + pred_id
```

## Endpoints that work in this sandbox

| Endpoint | Status |
|----------|--------|
| `GET /v1/models/{owner}/{name}` | 200 — returns `latest_version.id` |
| `GET /v1/models/{owner}/{name}/versions` | 404 here — use the parent endpoint |
| `POST /v1/predictions` with `{version, input}` | 201 on success |
| `GET /v1/predictions/{id}` | 200 — poll until `succeeded`/`failed`/`canceled` |
| `POST /v1/predictions` with `{model, input}` (no version) | 402 here — don't use |

## Local file → Reusable URL

Replicate only accepts HTTP(S) URLs, not local paths. To upload:

```python
with open(local_path, "rb") as f:
    img_data = f.read()
r = requests.post(
    "https://api.replicate.com/v1/files",
    headers={"Authorization": "Token " + api_token},
    files={"content": ("filename.jpg", img_data, "image/jpeg")},
    timeout=30
)
# response: {"id": "...", "urls": {"get": "https://api.replicate.com/v1/files/<id>.jpg"}}
```

URL expires in ~24h. Data URIs are rejected.

## 402 Insufficient credit

Means the account is empty. Tell the user to top up at https://replicate.com/account/billing and retry. Don't keep retrying — it's not a transient error.

## Polling cadence

- FLUX Schnell: 1-5s
- Veo 3 Fast: ~80s
- Veo 3.1: 1-3 min

Poll every 2s, 60-90 attempt budget, exit on terminal state.

## Model discovery (always current)

```python
r = requests.get(
    f"https://api.replicate.com/v1/models/{owner}/{name}",
    headers={"Authorization": "Token " + api_token},
    timeout=15
)
version_id = r.json()["latest_version"]["id"]
```

Never hardcode version IDs — they pin and rotate.
