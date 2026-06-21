#!/usr/bin/env python3
"""Perplexity Deep Research CLI — long-form, cited research via the async Sonar API.

Wraps Perplexity's asynchronous ``sonar-deep-research`` endpoints:
    POST /v1/async/sonar          submit a job        -> request id
    GET  /v1/async/sonar/{id}     poll status/result

Auth: set ``PERPLEXITY_API_KEY`` in the environment. Stdlib only — no installs.

Usage:
    python3 deep_research.py run "<query>" [options]      # submit + poll + print
    python3 deep_research.py submit "<query>" [options]   # submit, print request id
    python3 deep_research.py status <request_id>          # print status
    python3 deep_research.py get <request_id> [options]   # print finished report

Options (run / submit / get where applicable):
    --system "<prompt>"      Optional system prompt to steer the report.
    --mode web|academic|sec  Restrict source type (default: web).
    --domains a.com,b.com    Limit search to specific domains (comma-separated).
    --timeout SECONDS        run: max seconds to wait (default 600).
    --poll SECONDS           run: seconds between status checks (default 10).
    --raw                    Keep the model's <think> reasoning block.
    --json                   Emit a machine-readable JSON object.
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

BASE_URL = os.environ.get("PERPLEXITY_BASE_URL", "https://api.perplexity.ai").rstrip("/")
MODEL = "sonar-deep-research"
_THINK_RE = re.compile(r"<think>.*?</think>", re.DOTALL | re.IGNORECASE)


# ─── HTTP ────────────────────────────────────────────────────────────────────

def _api_key() -> str:
    key = os.environ.get("PERPLEXITY_API_KEY", "").strip()
    if not key:
        print(
            "PERPLEXITY_API_KEY environment variable not set.\n"
            "Get your API key at https://www.perplexity.ai/settings/api",
            file=sys.stderr,
        )
        sys.exit(2)
    return key


def _request(method: str, path: str, payload: dict | None = None) -> dict:
    """Send an authenticated JSON request and return the parsed response."""
    url = f"{BASE_URL}{path}"
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {_api_key()}")
    req.add_header("Accept", "application/json")
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode()
        except Exception:  # noqa: BLE001
            pass
        print(f"HTTP {e.code}: {e.reason}\n{body}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Connection error: {e.reason}", file=sys.stderr)
        sys.exit(1)


# ─── API calls ───────────────────────────────────────────────────────────────

def submit(query: str, system: str | None, mode: str, domains: list[str]) -> dict:
    """Submit an async deep-research job; return the create response (with id)."""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": query})

    inner: dict = {"model": MODEL, "messages": messages}
    if mode in ("web", "academic", "sec"):
        inner["search_mode"] = mode
    if domains:
        inner["search_domain_filter"] = domains

    return _request("POST", "/v1/async/sonar", {"request": inner})


def fetch(request_id: str) -> dict:
    """Fetch the current state (status + result when done) of a job."""
    return _request("GET", f"/v1/async/sonar/{request_id}")


# ─── Result shaping ──────────────────────────────────────────────────────────

def _extract_response(job: dict) -> dict | None:
    """Return the inner completion object regardless of field naming."""
    return job.get("response") or job.get("result") or None


def _report_text(job: dict, raw: bool) -> str:
    """Pull the assistant's report text out of a completed job."""
    resp = _extract_response(job) or {}
    content = ""
    choices = resp.get("choices") or []
    if choices:
        content = (choices[0].get("message") or {}).get("content", "") or ""
    if not content:
        content = resp.get("content", "") or ""
    if not raw:
        content = _THINK_RE.sub("", content).strip()
    return content


def _sources(job: dict) -> list[str]:
    """Collect citation URLs from citations and/or search_results."""
    resp = _extract_response(job) or {}
    out: list[str] = []
    for c in resp.get("citations") or []:
        if isinstance(c, str):
            out.append(c)
        elif isinstance(c, dict) and c.get("url"):
            out.append(c["url"])
    for r in resp.get("search_results") or []:
        if isinstance(r, dict) and r.get("url") and r["url"] not in out:
            title = r.get("title", "")
            out.append(f"{r['url']}  {title}".strip())
    return out


def _print_report(job: dict, raw: bool, as_json: bool) -> None:
    if as_json:
        print(json.dumps(
            {
                "status": job.get("status"),
                "report": _report_text(job, raw),
                "sources": _sources(job),
            },
            indent=2,
            ensure_ascii=False,
        ))
        return
    report = _report_text(job, raw)
    print(report if report else "(empty report)")
    sources = _sources(job)
    if sources:
        print("\n## Sources\n")
        for i, s in enumerate(sources, 1):
            print(f"[{i}] {s}")


# ─── Arg parsing (lightweight, matches sibling skill scripts) ─────────────────

def _opt(args: list[str], name: str, default=None):
    if name in args:
        idx = args.index(name)
        return args[idx + 1] if idx + 1 < len(args) else default
    return default


def _positional(args: list[str]) -> list[str]:
    """Return args that are not flags or flag-values."""
    flags_with_value = {"--system", "--mode", "--domains", "--timeout", "--poll"}
    out, skip = [], False
    for i, a in enumerate(args):
        if skip:
            skip = False
            continue
        if a in flags_with_value:
            skip = True
            continue
        if a in ("--raw", "--json"):
            continue
        out.append(a)
    return out


# ─── Commands ────────────────────────────────────────────────────────────────

def cmd_submit(args: list[str]) -> None:
    pos = _positional(args)
    if not pos:
        print("submit requires a query string", file=sys.stderr)
        sys.exit(2)
    query = pos[0]
    domains = [d.strip() for d in (_opt(args, "--domains", "") or "").split(",") if d.strip()]
    job = submit(query, _opt(args, "--system"), _opt(args, "--mode", "web"), domains)
    rid = job.get("id", "")
    if "--json" in args:
        print(json.dumps(job, indent=2, ensure_ascii=False))
    else:
        print(f"Submitted. request_id: {rid}")
        print(f"Status:     {job.get('status', 'unknown')}")
        print(f"Poll with:  python3 deep_research.py get {rid}")


def cmd_status(args: list[str]) -> None:
    pos = _positional(args)
    if not pos:
        print("status requires a request_id", file=sys.stderr)
        sys.exit(2)
    job = fetch(pos[0])
    if "--json" in args:
        print(json.dumps(job, indent=2, ensure_ascii=False))
    else:
        print(job.get("status", "unknown"))


def cmd_get(args: list[str]) -> None:
    pos = _positional(args)
    if not pos:
        print("get requires a request_id", file=sys.stderr)
        sys.exit(2)
    job = fetch(pos[0])
    status = job.get("status")
    if status != "completed":
        if status == "failed":
            print(f"Job failed: {job.get('error_message', 'unknown error')}", file=sys.stderr)
            sys.exit(1)
        print(f"Not ready yet (status: {status}). Try again later.", file=sys.stderr)
        sys.exit(3)
    _print_report(job, raw="--raw" in args, as_json="--json" in args)


def cmd_run(args: list[str]) -> None:
    pos = _positional(args)
    if not pos:
        print("run requires a query string", file=sys.stderr)
        sys.exit(2)
    query = pos[0]
    timeout = int(_opt(args, "--timeout", "600"))
    poll = max(2, int(_opt(args, "--poll", "10")))
    domains = [d.strip() for d in (_opt(args, "--domains", "") or "").split(",") if d.strip()]

    job = submit(query, _opt(args, "--system"), _opt(args, "--mode", "web"), domains)
    rid = job.get("id", "")
    print(f"Deep research submitted (request_id: {rid}). Researching…", file=sys.stderr)

    deadline = time.time() + timeout
    while time.time() < deadline:
        time.sleep(poll)
        job = fetch(rid)
        status = job.get("status")
        if status == "completed":
            _print_report(job, raw="--raw" in args, as_json="--json" in args)
            return
        if status == "failed":
            print(f"Job failed: {job.get('error_message', 'unknown error')}", file=sys.stderr)
            sys.exit(1)
        print(f"  …{status}", file=sys.stderr)

    print(
        f"Timed out after {timeout}s. The job is still running — fetch later with:\n"
        f"  python3 deep_research.py get {rid}",
        file=sys.stderr,
    )
    sys.exit(3)


def main() -> None:
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(0)
    cmd, rest = args[0], args[1:]
    dispatch = {
        "run": cmd_run,
        "submit": cmd_submit,
        "status": cmd_status,
        "get": cmd_get,
    }
    handler = dispatch.get(cmd)
    if handler is None:
        print(f"Unknown command: {cmd}\n", file=sys.stderr)
        print(__doc__)
        sys.exit(2)
    handler(rest)


if __name__ == "__main__":
    main()
