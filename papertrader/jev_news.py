"""Jev (TypeSafe System One) news reviewer: SHADOW MODE. It reads headlines already stored in the ledgers and records Jev's judgments
in state/jev_reviews.jsonl. It never gates, sizes or places an order, and nothing in the engines reads its output. A failure here
(no key, network, quota) is recorded in state/jev_status.json and never raises into the cycle.

Cost control: each headline is reviewed once; at most MAX_PER_RUN calls per run and MAX_PER_DAY per UTC day. The first live evaluation
should compare these judgments with what prices did afterwards, net of costs, before any use beyond logging."""
from __future__ import annotations

import datetime as dt
import json
import os
import sys
from pathlib import Path

from .config import ROOT
from .laya_news import load_news

SCHEMA = "jev-news-1"
MAX_PER_RUN = 25
MAX_PER_DAY = 150
MAX_AGE_DAYS = 3
MAX_CONSECUTIVE_ERRORS = 3
OUT = "state/jev_reviews.jsonl"
STATUS = "state/jev_status.json"


def questions():
    from typesafe_sdk import Choice, Noul
    return {
        "material_adverse": Noul(instructions="Does the headline report a new, material negative development for the company itself (for example a "
                                              "fraud or regulatory probe, a lawsuit, a guidance cut, a product failure, an executive scandal), as opposed "
                                              "to commentary, an analyst opinion, or only a description of the stock price moving?"),
        "material_positive": Noul(instructions="Does the headline report a new, material positive development for the company itself (for example "
                                               "better-than-expected results, raised guidance, a major contract, an approval), as opposed to commentary "
                                               "or only a description of the stock price moving?"),
        "price_move_only": Noul(instructions="Does the headline only describe the stock price or market move, without reporting any new company-specific information?"),
        "tone": Choice(instructions="What is the tone of the headline towards the company?",
                       criteria={"negative": None, "neutral": None, "positive": None}),
    }


def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def judge(client, row: dict) -> dict:
    resp = client.system_one(state={"ticker": row["ticker"], "headline": row["title"], "provider": row.get("provider") or row.get("source")},
                             questions=questions())
    return {"material_adverse": _num(resp.nouls["material_adverse"].noul), "material_positive": _num(resp.nouls["material_positive"].noul),
            "price_move_only": _num(resp.nouls["price_move_only"].noul), "tone": resp.choices["tone"].choice}


def _done(path: Path) -> tuple[set, int]:
    uids, today = set(), 0
    day = dt.datetime.now(dt.timezone.utc).date().isoformat()
    if path.exists():
        for line in path.read_text().splitlines():
            try:
                r = json.loads(line)
            except ValueError:
                continue
            uids.add(r.get("uid"))
            today += str(r.get("reviewed_at", ""))[:10] == day
    return uids, today


def run(root: Path = ROOT, now: dt.datetime | None = None, client_factory=None) -> dict:
    now = now or dt.datetime.now(dt.timezone.utc)
    status = {"role": "advisory only: never gates, sizes or places orders", "schema": SCHEMA, "at": now.isoformat(timespec="seconds"), "state": "idle"}
    out = root / OUT
    try:
        if client_factory is None:
            if not os.environ.get("TYPESAFE_API_KEY"):
                status.update(state="skipped", reason="TYPESAFE_API_KEY not set")
                return status
            from typesafe_sdk import TypeSafeClient
            client_factory = TypeSafeClient
        rows, skipped = load_news(root, now, MAX_AGE_DAYS)
        done, today = _done(out)
        pending = [r for r in rows if r["uid"] not in done]
        budget = max(0, min(MAX_PER_RUN, MAX_PER_DAY - today))
        status.update(candidates=len(rows), pending=len(pending), budget=budget, reviewed_today=today)
        if not pending or budget == 0:
            status["state"] = "idle" if not pending else "daily cap reached"
            return status
        out.parent.mkdir(parents=True, exist_ok=True)
        n = errors = 0
        with client_factory() as client, open(out, "a") as f:
            for r in pending[:budget]:
                try:
                    j = judge(client, r)
                    errors = 0
                except Exception as e:  # network, quota, billing: stop quietly, keep what we have
                    errors += 1
                    status["last_error"] = f"{type(e).__name__}: {e}"[:200]
                    if errors >= MAX_CONSECUTIVE_ERRORS:
                        break
                    continue
                f.write(json.dumps({"uid": r["uid"], "ticker": r["ticker"], "published_at": r["published_at"], "title": r["title"],
                                    "reviewed_at": now.isoformat(timespec="seconds"), "schema": SCHEMA, **j}) + "\n")
                n += 1
        status.update(state="done" if errors < MAX_CONSECUTIVE_ERRORS else "stopped after repeated errors", reviewed_now=n)
    except Exception as e:
        status.update(state="error", reason=f"{type(e).__name__}: {e}"[:200])
    finally:
        try:
            (root / STATUS).write_text(json.dumps(status, indent=1))
        except OSError:
            pass
    return status


if __name__ == "__main__":
    print(json.dumps(run()))
    sys.exit(0)
