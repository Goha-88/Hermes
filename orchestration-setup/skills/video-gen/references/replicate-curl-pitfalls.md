# Replicate API gotchas (learned the hard way)

When the video-gen / image-gen scripts break, check this first.

## URL construction — never inline `predictions/{id}` with shell

Anything that involves the runtime redactor / placeholder substitution has a tendency to break `predictions/` URLs that look like `predict***{id}` or `predict__{id}`. **Always build the URL with string concatenation:**

```python
poll_url = "https://api.replicate.com/v1/predictions/" + pred_id
```

NOT:

```python
poll_url = f"https://api.replicate.com/v1/predictions/{pred_id}"  # breaks in this sandbox
poll_url = "https://api.replicate.com/v1/predict***" + pred_id   # breaks — placeholder substitution
```

Same pattern when calling `bash` with `curl` — never embed `r8_***` style tokens
directly. Read from `~/.hermes/.env` and pass through `os.environ` in Python.

## Replicate API endpoints that work (June 2026)

| Endpoint | Status | Note |
|----------|--------|------|
| `GET /v1/models/{owner}/{name}` | ✅ 200 | Returns model info + `latest_version.id` |
| `GET /v1/models/{owner}/{name}/versions` | ❌ 404 in this sandbox | Use the parent endpoint above instead |
| `POST /v1/predictions` (body=`{version, input}`) | ✅ 201 on success | Returns `{id, status: "starting"}` |
| `GET /v1/predictions/{id}` | ✅ 200 | Poll until `succeeded`/`failed`/`canceled` |
| `POST /v1/predictions` (body=`{model, input}`) | ❌ 402 here | The bare-`model` form doesn't work even with credit |

## Insufficient credit (402)

If the user reports balance topped up but generation still 402s, the script likely
cached the token string. Re-read the token from `.env` on every invocation. Most
often it's the script using a stale token (rotate first).

## Polling cadence

FLUX Schnell: 1–5 seconds. Veo 3.1: 30–180 seconds. Poll every 2 seconds with a
60–90 attempt budget. Exit on `succeeded` / `failed` / `canceled`.

## Common model identifiers

- Image (fast): `black-forest-labs/flux-schnell`
- Image (pro): `black-forest-labs/flux-1.1-pro` or `flux-2-pro`
- Video (premium, audio): `google/veo-3.1`
- Video (image-to-video, cheap): `google/veo-3-fast` — use this when animating a still frame; supports `first_frame_image`, `duration` 5/8, `aspect_ratio`, `negative_prompt`, `generate_audio`. ~$0.15/8s, ~80s render.
- Video (cheap, text-only): `minimax/video-01` (MiniMax Hailuo on Replicate) — 6s, ~$0.10, Pixar/cute style
- Video (budget motion): `xai/grok-imagine-video` (Replicate) — 5/10s, takes `image` + `prompt` + `duration` + `aspect_ratio`

Always fetch the latest version id via `GET /v1/models/{owner}/{name}` — versions
are pinned and rotate.

## Local files → Replicate input

Replicate only accepts HTTP(S) URLs as image inputs, not local paths. To use a
local file:

1. POST to `https://api.replicate.com/v1/files` with `files={"content": (...)}` — returns `{urls: {get: "https://api.replicate.com/v1/files/<id>.jpg"}}`.
2. Pass that URL as the `image` / `first_frame_image` field.
3. The URL expires in ~24h — re-upload if you need to reuse later.

Don't try to base64-encode into a data URI — Replicate rejects data URIs.