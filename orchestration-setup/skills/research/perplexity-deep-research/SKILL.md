---
name: perplexity-deep-research
description: "Run long-form, multi-step web research with Perplexity sonar-deep-research (async API): submit a question, poll, get a cited report."
version: 1.0.0
author: Hermes Agent
tags: [perplexity, sonar, deep-research, research, web-search, citations, async]
platforms: [linux, macos, windows]
---

# Perplexity Deep Research

Run **long-running, multi-step research** with Perplexity's `sonar-deep-research`
model through its **asynchronous API**. Unlike a normal chat turn, the model
performs dozens of searches, reads sources, and synthesizes a structured,
**cited** report — taking anywhere from ~30 seconds to several minutes.

Because it is long-running, the job is submitted to an async endpoint and polled
to completion. Results have a 7-day TTL on Perplexity's side.

This skill complements the regular `web_search` tool (quick lookups) and the
`sonar` chat models (fast grounded answers). Reach for it when the user wants a
**thorough, sourced write-up**, not a one-line answer.

## When to Use

- "Do deep research on X", "write me a researched report on…", "literature
  review of…", "comprehensive analysis of…"
- The question needs many sources synthesized, not a single fact
- Comparisons across many options, market/landscape scans, due diligence
- Anything the user expects to take minutes and come back with citations

Do **not** use for quick factual lookups — use the `web_search` tool or a
`sonar`/`sonar-pro` chat turn instead (cheaper and instant).

## Prerequisites

- `PERPLEXITY_API_KEY` must be set in the environment (the same key used by the
  Perplexity Search web backend and the Sonar model provider). Get one at
  https://www.perplexity.ai/settings/api.

The helper script uses only the Python standard library — no extra installs.

## Quickest Path — `run`

One command submits the job, polls until it finishes, and prints the report:

```bash
python3 scripts/deep_research.py run "Compare the leading open-weight LLMs released in 2026 for agentic tool use, with benchmarks and licensing"
```

Useful flags:

- `--system "<prompt>"` — steer tone/format (e.g. "Answer as a McKinsey-style brief").
- `--mode web|academic|sec` — restrict sources (academic = papers, sec = filings).
- `--domains a.com,b.com` — limit search to specific domains.
- `--timeout 900` — max seconds to wait before giving up (default 600).
- `--poll 10` — seconds between status checks (default 10).
- `--raw` — keep the model's `<think>` reasoning block (stripped by default).
- `--json` — emit a machine-readable JSON object instead of formatted text.

## Long Jobs — submit then come back later

For very long research, or to run it as a scheduled/background task, split the
two phases so you are not blocking on a single command:

```bash
# 1) Submit — prints the request id (save it)
python3 scripts/deep_research.py submit "Full competitive landscape of EU carbon-credit registries"

# 2) Check status anytime (pending | processing | completed | failed)
python3 scripts/deep_research.py status <REQUEST_ID>

# 3) Fetch the finished report (only when status is completed)
python3 scripts/deep_research.py get <REQUEST_ID>
```

This pairs naturally with Hermes cron (`hermes cron`) and background delegation:
kick off the research, do other work, then `get` the result. Jobs expire after
7 days.

## Workflow for the Agent

1. Confirm the scope is genuinely "deep" — otherwise prefer `web_search`.
2. Run `run` (or `submit`) with a **specific, well-scoped** query. Vague queries
   waste minutes; include the angle, timeframe, and what a good answer contains.
3. While waiting, tell the user it's running (it can take minutes).
4. Present the returned report. **Always keep the Sources section** — cited URLs
   are the main value of deep research; never strip them.
5. If `status` is `failed`, surface `error_message` and offer to retry with a
   narrower query.

## Presenting Results

- Lead with the synthesized answer; preserve the model's structure (headings,
  bullets) — it is already report-shaped.
- Keep the **Sources** list the script appends. Optionally renumber `[1]`,`[2]`
  inline if the user wants tighter citation formatting.
- If the report is very long, offer a TL;DR but link/keep the full text.

## See Also

- `references/async-api.md` — exact endpoints, request/response shapes, status lifecycle, and curl examples.
- `references/standard-chat-api.md` — quick cited research via the standard (non-async) chat API with `sonar`/`sonar-pro`. Use for single-turn questions that need citations in seconds, not minutes.
  lifecycle, and curl examples.

## Limitations

- `sonar-deep-research` is the most expensive Sonar model and the slowest — only
  use it when depth is actually wanted.
- Async results expire after **7 days** (TTL); fetch and persist anything you
  need to keep.
- Output is a written report, not structured data; use `--json` if you need to
  post-process the text + citations programmatically.
