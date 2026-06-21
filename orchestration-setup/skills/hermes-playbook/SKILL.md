---
name: hermes-playbook
description: |
  Operating manual for this Hermes instance — model-orchestration lanes,
  connected providers and tools, spend tracking, and working conventions.
  Consult when deciding which model or tool to use for a task, when switching
  lanes, when a paid tool runs, or when troubleshooting the setup.
---

# Hermes Operating Playbook

How this instance is wired and how to route work. Principle: match model + tool
to the task — hard work to strong models, volume to cheap ones. Switch the main
model only **between** tasks; switching mid-conversation breaks the prompt cache,
so use **subagents** for cross-model work within a session.

## Lanes (quick-commands switch the main model)

| Trigger in request | Lane | Model | Tools |
|---|---|---|---|
| chat, "explain" | `/chat` | deepseek-v4-pro | — |
| strategy / "help me think / hypothesis / vision" | `/strategy` | claude-opus-4.8 | load karina-principles skill |
| data / unit-economics / MRR / forecast / chart | `/data` | deepseek-v4-pro | data-analysis skill (code execution) |
| make doc / deck / КП / Excel / contract | — | current | documents skill (docx/pptx/xlsx) |
| large document / 1M-context parse | `/docs` | gemini-2.5-pro | firecrawl-parse |
| audio note / recording in input | auto | STT (whisper/groq) | transcribe → summarize → action items |
| task / reminder / project / CRM | — | — | cron; YouGile MCP (when connected) |
| "find / book / check on a site" | — | current | browser |
| "find / latest / sources / what's now" | `/research` | perplexity sonar | Perplexity, Firecrawl |
| "email / landing / offer / ad / copy" | `/sales` | claude-sonnet-4.6 | Perplexity (facts) |
| "leads / prospects / companies" | via `/sales` | gemini-2.5-flash / deepseek-v4-flash | firecrawl lead-gen, company-directories |
| "competitors / market / SEO audit" | via `/sales` | claude-opus-4.8 / deepseek-v4-pro | firecrawl competitive-intel, seo-audit |
| "article / post / guide" | `/content` | sonnet/opus · gemini (variety) · cheap (volume) | Perplexity |
| "image / banner / cover / logo" | — | gemini-2.5-flash-image (no FAL) | `image-gen` skill → `hermes-image "<prompt>"` |
| "video" | — | FAL (Kling/Veo/Runway) | needs FAL_KEY (not yet connected) |
| "voice / podcast / music" | — | ElevenLabs | ElevenLabs MCP (tts, voice_clone, compose_music) |
| "write code / feature" | `/code` | deepseek-v4-pro → claude-opus-4.8 (xhigh) | GitHub MCP, terminal |
| "review / debug / why bug" | `/review` (opus) or `/reviewlite` (deepseek-r1, cheaper) | a different model than wrote it | /code-review, GitHub MCP |
| "build system / many steps / overnight" | `/agentic` | claude-opus-4.8 xhigh / Fable 5 | all + delegation |
| image/screenshot in input | auto | gemini-2.5-flash | auxiliary.vision |

**Code rule:** write with one model family, review with another — diversity
catches more bugs. **Repurpose pipeline:** top model writes the pillar →
cheap model atomizes → ElevenLabs voices → ffmpeg/Creatomate assembles.

## Connected providers & tools
- **Providers:** OpenRouter (200+ models, default gateway — active default is `minimax/MiniMax-M3`), DeepSeek, Perplexity (sonar), MiniMax. Switch any model with `/model openrouter:<slug>`.
- **MCP servers:** GitHub, Firecrawl, Miro.
- **Audio:** ElevenLabs (`ELEVENLABS_API_KEY`). **Images/video:** Replicate (`REPLICATE_API_TOKEN` in `.env` — FLUX Schnell, Recraft V3, Hailuo, Veo 3, Veo 3 Fast). Prefer the `image-gen` and `video-gen` skill CLI commands (`hermes-image`, `hermes-video`, `hermes-video-kling`); fall back to direct `requests` calls only when the CLI times out. FAL is NOT connected (no `FAL_KEY`).
- **Skills:** 31 Firecrawl skills, `brand-voice` (fill before use), `karina-principles` (strategic persona — load before strategy talks), `find-skills` (triggers on "how do I do X" / "is there a skill for Y" — scans local, built-in, SkillHub, GitHub, ClawHub for matching skills).

## Background (auxiliary) — always on, cheap
- `deepseek-v4-flash`: titles, triage, memory tags, monitor, approval, mcp, skills, profiler.
- `deepseek-v4-pro`: compression, memory curator, task decomposition.
- `gemini-2.5-flash`: vision, web extract.

## Spend tracking
- `/spend` (or `hermes-spend` in terminal): combines agent LLM spend (state.db) + paid tools (spend_ledger). Flags: `--sessions N`, `--audit N`, `--json`.
- `/usage`: tokens + estimated cost of the current session.
- Hook `spend-audit` logs every gateway turn (model, tools, per-turn cost) to `~/.hermes/spend_audit.jsonl`.

## Conventions (always)
- **Cost transparency:** when a paid tool/API runs, surface its cost.
- **Security:** never expose secrets; if an API key is pasted in chat, advise rotating it. Keys live in `~/.hermes/.env` (perms 600).
- **Verify** before claiming done; report failures honestly with evidence.
- **Customer-facing text** follows the `brand-voice` skill.

## Troubleshooting
- After new config/skills/keys → run `hermes gateway restart` so Telegram picks them up.
- Edit config with `hermes config set <key> <val>` or venv python + ruamel (preserves formatting). Note: zsh does NOT word-split `$vars` in `for` loops (bash does) — this once created junk keys.
- Perplexity has no `/v1/models` endpoint — set its model manually.
- MCP servers live in `config.yaml` → `mcp_servers`; the GitHub token rides in its `headers`.
