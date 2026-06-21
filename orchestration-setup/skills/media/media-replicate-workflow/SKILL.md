---
name: media-replicate-workflow
description: Generate or animate images and videos via Replicate (FLUX, Veo 3, Hailuo, Grok Imagine). Use when the task is to create or transform visual media (image-to-video, text-to-image, text-to-video) and Replicate is the chosen backend. Covers prompt-engineering handoff from OpenRouter, Replicate API gotchas, pricing, and the file-upload-then-poll pattern.
---

# Media generation via Replicate — workflow

End-to-end pattern for **text → image**, **text → video**, and **image → video** through Replicate. This skill is the **shared backend** that the more specific `image-gen` and `video-gen` skills use; load it when the task touches both, or when the user wants the workflow explained rather than just a CLI invocation.

## The 3-stage flow (always the same shape)

1. **Prompt engineering** (OpenRouter): before calling Replicate, ask the LLM to write a detailed, structured English prompt. Replicate models respond dramatically better to prompts with explicit subject, style, lighting, composition, mood. A short human-written prompt wastes the model.
2. **Replicate call** (HTTP): POST to `/v1/predictions` with `{version, input}`. For local images, POST the file to `/v1/files` first to get a URL.
3. **Poll + deliver** (HTTP): GET `/v1/predictions/{id}` every 2 seconds. On `succeeded`, download the output URL and send the file via `MEDIA:/absolute/path`.

## Model menu (June 2026 — pricing per call)

| Model | Type | Duration / size | Cost | Best for |
|-------|------|-----------------|------|----------|
| `black-forest-labs/flux-schnell` | image | 1024×1024 jpg | ~$0.003 | Fast drafts |
| `black-forest-labs/flux-1.1-pro` / `flux-2-pro` | image | 2048px | ~$0.06 | Hero / realism |
| `minimax/video-01` (Hailuo on Replicate) | video | 6s | ~$0.10 | Cute / Pixar-style, no audio |
| `google/veo-3-fast` | video | 8s, 16:9, 4K-quality | ~$0.15 | Image-to-video, cinematic, no audio |
| `google/veo-3` / `google/veo-3.1` | video | 8s, with audio | ~$0.40–$6 | Premium, native audio |
| `xai/grok-imagine-video` | video | 5/10s | varies | Alternative for motion |

Kling (`kwaivgi/kling-video`) — **404 on Replicate** as of June 2026. Don't try.

## Hard-won Replicate gotchas (full detail in `video-gen/references/replicate-curl-pitfalls.md`)

- **URL construction**: always concatenate `https://api.replicate.com/v1/predictions/` + `pred_id` with `+` — never f-string or template literal with the URL. The runtime redactor breaks f-strings that look like token placeholders.
- **Local image → URL**: Replicate rejects data URIs and local paths. POST to `/v1/files` (multipart `content` field) → returns `{urls: {get: "..."}}` valid ~24h.
- **402 Insufficient credit**: means the Replicate account is empty. Tell the user to top up at https://replicate.com/account/billing and try again — don't keep retrying.
- **Polling cadence**: FLUX 1-5s, Veo 3 Fast ~80s, Veo 3.1 1-3 min. Poll every 2s with a 60-90 attempt budget. Exit on `succeeded` / `failed` / `canceled`.
- **Model version pinning**: never hardcode version IDs. Always `GET /v1/models/{owner}/{name}` to read `latest_version.id` first — versions rotate.

## Prompt-engineering handoff (OpenRouter → Replicate)

Pattern that works:

1. Brief the OpenRouter model with: "You are an expert at writing image/video generation prompts for FLUX, Stable Diffusion, Midjourney, Veo. Output ONLY the prompt in English, no commentary."
2. The user request: "Write a detailed image generation prompt for: <human intent>. Include subject, style, colors, composition, mood, lighting, quality tokens."
3. Take the result, optionally append style tokens like `, 4k, ultra high detail, cinematic lighting` for the chosen model.

This produces prompts 3-5x more detailed than what humans write, and Replicate models reward detail.

## When NOT to use Replicate

- The user only wants a quick mockup or low-stakes draft → use `image-gen` skill (OpenRouter gemini-2.5-flash-image, ~$0.003, no setup).
- The user wants native audio in a single pass → only Veo 3.1 has it; Veo 3 Fast and Hailuo do not (ElevenLabs + ffmpeg post-process if needed).
- The user wants Kling → use a different backend; Replicate's `kwaivgi/kling-video` returns 404.
- File size matters (Telegram 20 MB cap) → Hailuo 6s fits, Veo 3 8s may not when stacked with source image. Send files individually or compress.

## Output convention

After a successful generation, always:
- Print the file size and the local path to confirm
- Send the file via `MEDIA:/absolute/path` in the response
- Note the cost when over $0.10 (cost-transparency convention)

See also: `image-gen` (text-to-image CLI), `video-gen` (text-to-video CLI), `references/replicate-curl-pitfalls.md` (URL/polling gotchas).