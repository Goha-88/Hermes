---
name: video-gen
description: |
  Generate video from a text prompt — uses Replicate's Google Veo 3 (best
  quality, with native audio). Use when asked to make a video clip, reel, or
  animated scene.
---

# Video generation (Replicate) — three tiers

- **Premium, with audio** (cinematic, final): `hermes-video "<prompt>" [out.mp4]` — **Google Veo 3.1**, native audio, ≈ **$6 / 8s**, render 1–3 min.
- **Standard, no audio, image-to-video** (animating a still frame, e.g. a hero image or AI-generated character): use **Google Veo 3 Fast** via direct Replicate call — ≈ $0.15 / 8s, ~80s render. Input: `first_frame_image` (URL, after uploading local file via `/v1/files`) + `prompt` + `duration` (5 or 8) + `aspect_ratio` (`16:9`, `9:16`, `1:1`) + `negative_prompt`. 16:9 from a 1:1 image works fine.
- **Fast / cheap, no audio** (motion, drafts, reels b-roll): `hermes-video-kling "<prompt>" [duration 5|10] [out.mp4]` — **Kling 2.5 Turbo Pro**, top motion, ≈ **$0.35 / 5s**, render 1–3 min.

All save an MP4 and print the path. Then send/attach the file.

⚠️ **Cost:** video is paid and slow. **Confirm cost with the user before generating**, especially Veo 3.1 (~$6) and Veo 3 Fast image-to-video. Kling is the budget choice (~$0.35). Add audio to Veo 3 Fast / Kling clips via ElevenLabs + ffmpeg if needed. **Telegram has a 20 MB file-send cap** — Hailuo (6s) fits in one message, but Veo 3 (8s, ~3 MB) plus the source image can blow past the cap; send files individually or compress first.

**Always reach for the `hermes-video*` CLI before writing direct Replicate calls** — the CLI is the supported path. Drop to raw `requests` only when:
- You need image-to-video (the CLI currently takes text only).
- The CLI times out on a heavy request (Veo 3.1 8s renders can exceed the 5-min default terminal timeout — switch to `background=true` + `notify_on_complete=true`).
- You need a model the CLI doesn't expose (e.g. Veo 3 Fast, Grok Imagine Video, custom community models).

For Replicate-specific gotchas (URL construction, model discovery, polling cadence), see `references/replicate-curl-pitfalls.md`.

Guidelines:
- Detailed English prompt: scene, subjects, camera motion, lighting, mood, audio.
- For reels: generate clips, voice over with ElevenLabs, assemble with ffmpeg.
- Always surface the cost (cost-transparency convention).
