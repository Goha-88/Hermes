"""spend-audit gateway hook.

Пишет одну строку на каждый запрос в gateway (Telegram/Discord/...) в
``~/.hermes/spend_audit.jsonl``: время, платформа, пользователь, модель,
какие инструменты сработали, оценка стоимости запроса и накопительная
стоимость сессии.

Модели и стоимости НЕТ в контексте хука — они дочитываются из ``state.db``
(строка sessions) по ``session_id`` на событии ``agent:end``. Стоимость
запроса = дельта накопительной ``estimated_cost_usd`` сессии с прошлого хода
(хранится в ``_last_cost.json``, переживает рестарты gateway).

Инструменты копятся из событий ``agent:step`` (ключ ``tool_names``) и
сбрасываются на ``agent:end``. Все ошибки проглатываются — хук никогда не
ломает агента.
"""
from __future__ import annotations

import json
import os
import sqlite3
import time
from pathlib import Path


def _home() -> Path:
    return Path(os.environ.get("HERMES_HOME", str(Path.home() / ".hermes")))


_HOOK_DIR = Path(__file__).resolve().parent
_LAST_COST = _HOOK_DIR / "_last_cost.json"

# Накопление инструментов между agent:step (живёт в процессе gateway).
_pending: dict[str, list[str]] = {}


def _audit_log() -> Path:
    return _home() / "spend_audit.jsonl"


def _load_last_cost() -> dict:
    try:
        return json.loads(_LAST_COST.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_last_cost(data: dict) -> None:
    try:
        _LAST_COST.write_text(json.dumps(data), encoding="utf-8")
    except Exception:
        pass


def _session_row(session_id: str) -> dict:
    db = _home() / "state.db"
    if not session_id or not db.exists():
        return {}
    try:
        con = sqlite3.connect(f"file:{db}?mode=ro", uri=True, timeout=2.0)
        con.row_factory = sqlite3.Row
        try:
            cur = con.execute(
                "SELECT model, billing_provider, "
                "COALESCE(actual_cost_usd, estimated_cost_usd, 0) AS cost, "
                "input_tokens, output_tokens "
                "FROM sessions WHERE id = ?",
                (session_id,),
            )
            r = cur.fetchone()
            return dict(r) if r else {}
        finally:
            con.close()
    except Exception:
        return {}


def _dedupe(seq):
    seen, out = set(), []
    for x in seq:
        if x and x not in seen:
            seen.add(x)
            out.append(x)
    return out


async def handle(event_type: str, context: dict):
    sid = context.get("session_id") or ""

    if event_type == "agent:start":
        _pending[sid] = []
        # Фиксируем стоимость сессии ДО хода как базу для дельты. Без этого
        # первый залогированный ход уже существовавшей сессии показал бы всю
        # её накопленную стоимость как "цену запроса" (эффект холодного старта).
        last = _load_last_cost()
        if sid not in last:
            last[sid] = float(_session_row(sid).get("cost", 0) or 0)
            _save_last_cost(last)
        return

    if event_type == "agent:step":
        names = context.get("tool_names") or []
        if isinstance(names, (list, tuple)):
            merged = list(_pending.get(sid, [])) + [str(n) for n in names]
            _pending[sid] = _dedupe(merged)
        return

    if event_type == "agent:end":
        tools = _pending.pop(sid, [])
        row = _session_row(sid)
        cumulative = float(row.get("cost", 0) or 0)

        last = _load_last_cost()
        prev = float(last.get(sid, 0) or 0)
        turn_cost = cumulative - prev
        if turn_cost < 0:  # сессия сброшена / переиспользован id
            turn_cost = cumulative
        last[sid] = cumulative
        _save_last_cost(last)

        entry = {
            "ts": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
            "platform": context.get("platform", ""),
            "user_id": context.get("user_id", ""),
            "session_id": sid,
            "model": row.get("model", "") or "",
            "provider": row.get("billing_provider", "") or "",
            "tools": tools,
            "turn_cost_usd": round(turn_cost, 6),
            "session_cost_usd": round(cumulative, 6),
        }
        try:
            with open(_audit_log(), "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception:
            pass
        return
