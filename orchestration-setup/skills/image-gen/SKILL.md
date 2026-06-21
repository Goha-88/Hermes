---
name: image-gen
description: |
  Generate images from a text prompt without FAL — uses OpenRouter's
  gemini-2.5-flash-image. Use whenever asked to create a picture, logo,
  banner, cover, illustration, mockup, or any visual asset.
---

# Image generation (no FAL needed)

To create an image, run in the terminal:

```bash
hermes-image "<detailed English prompt>" [optional/output/path.png]
```

It calls `google/gemini-2.5-flash-image` via OpenRouter, saves a 1024×1024 PNG,
and prints the file path to stdout. Then **send/attach that file to the user.**

## Three tiers — pick the best model for the job
- **Fast / cheap** (drafts, bulk): `hermes-image "<prompt>" [out.png]` — gemini-2.5-flash-image, 1024px, ≈ **$0.003**.
- **Best photo / realism** (hero visuals, scenes): `hermes-image-pro "<prompt>" [aspect_ratio] [out.png]` — **FLUX 1.1 Pro Ultra**, 2048px, ≈ **$0.06**. aspect: 1:1, 16:9, 9:16, 3:2, 4:5.
- **Logos / text-in-image / brand / vector** (the best for design): `hermes-image-brand "<prompt>" [style] [out]` — **Recraft V3**, ≈ **$0.04**. Valid `style`: `any` (default), `realistic_image`, `digital_illustration`, `vector_illustration` (returns SVG). Use `vector_illustration` for scalable logos.

Routing: photo/realism → `pro` (FLUX); logo/brand/text → `brand` (Recraft); quick draft/bulk → `fast` (gemini).

Guidelines:
- Write a **detailed visual prompt** in English: subject, style, colors, composition, mood. Detail → better result.
- Surface the cost (cost-transparency convention).
- For brand assets, follow the `brand-voice` skill's palette/style.

For video, see the `video-gen` skill (`hermes-video`, Veo 3).
