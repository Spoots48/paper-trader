"""Daily reports: a short, plain-English recap of each calendar day (ET) of the experiment.

One report per day, generated at the first run after midnight ET once every bot has saved its
end-of-day balance (or by noon the next day, with missing data noted). Files are never overwritten.
The weekly and final reports (reporting.py) are unchanged.
"""
from __future__ import annotations

import datetime as dt
import html
import json
from pathlib import Path

from .config import REPORTS_DIR, ROOT, load_json
from .nyse_calendar import ET, is_session, iso
from .reporting import CSS, _md_list, _money, _pct
from .state import book_state

WHY = {
    "ORB_BREAKOUT": "price broke above its first-5-minute high",
    "STOP": "hit its safety stop", "STOP_GAP": "opened below its safety stop",
    "CLOSE_EXIT": "sold at the close (day trades are never held overnight)",
    "PM_ENTRY": "bet placed", "PM_WIN": "bet won", "PM_LOSS": "bet lost",
    "MM_FILL": "our standing bid was filled", "RESIDUAL": "spare cash put into SPY",
}


def _et_time(s: str) -> str:
    try:
        t = dt.datetime.fromisoformat(s.split(" ")[0].replace("Z", "+00:00"))
        return t.astimezone(ET).strftime("%H:%M") if t.tzinfo else t.strftime("%H:%M")
    except ValueError:
        return ""


def _et_date(f: dict) -> str:
    """The New York calendar date a fill actually happened (the ledger's `session` is when it was processed)."""
    try:
        t = dt.datetime.fromisoformat(f["price_time"].split(" ")[0].replace("Z", "+00:00"))
        return (t.astimezone(ET) if t.tzinfo else t).date().isoformat()
    except ValueError:
        return f["session"]


def _on_or_before(snaps: list[dict], day: str) -> dict | None:
    c = [s for s in snaps if s["session"] <= day]
    return c[-1] if c else None


def _stem(day: dt.date) -> str:
    return f"daily_{day.isoformat()}"


def build(exp: dict, day: dt.date, now: dt.datetime) -> dict:
    cash0 = exp["starting_cash"]
    d, prev = day.isoformat(), (day - dt.timedelta(days=1)).isoformat()
    start = dt.date.fromisoformat(exp["start_date"])
    rows, details, missing, spy = [], [], [], None
    try:
        notes = load_json(ROOT / "config/report_notes.json").get(d, {})
    except OSError:
        notes = {}
    tot_prev = tot_end = 0.0
    for book in exp["books"]:
        b = book_state(book, exp, n_decisions=1)
        name = book["name"]
        b_start = book.get("start_date", exp["start_date"])
        if not b.get("frozen") or b_start > d:
            rows.append({"id": book["id"], "name": name, "status": "not started yet"})
            continue
        snaps = b.get("snapshots") or []
        crypto = load_json(ROOT / book["strategy"]).get("book_type") == "predmarket"
        if (crypto or is_session(day)) and not any(s["session"] == d for s in snaps):
            missing.append(name)
        s_end, s_prev = _on_or_before(snaps, d), _on_or_before(snaps, prev)
        end = s_end["equity"] if s_end else cash0
        before = s_prev["equity"] if s_prev and b_start <= prev else cash0
        fills = [f for f in b["fills"] if _et_date(f) == d]
        sells = [f for f in fills if f["side"] == "SELL" and f["reason_code"] != "RESIDUAL"]
        wins = sum(1 for f in sells if (f["realized_pnl"] or 0) > 0)
        issues = [i for i in b["issues"] if i["severity"] in ("ERROR", "CRITICAL", "WARN")
                  and dt.datetime.fromisoformat(i["occurred_at"].replace("Z", "+00:00")).astimezone(ET).date() == day]
        status = "retired (only settles old bets)" if book.get("retired") else \
                 ("market closed" if not crypto and not is_session(day) else "trading")
        rows.append({"id": book["id"], "name": name, "status": status, "value": end, "change": end - before,
                     "since_start": end - cash0, "trades": len(fills), "wins": wins, "losses": len(sells) - wins})
        tot_prev += before
        tot_end += end
        if book["id"] == "primary" and is_session(day) and s_end and s_end.get("spy_bh_equity"):
            spy_prev = (s_prev or {}).get("spy_bh_equity") or cash0
            spy = {"value": s_end["spy_bh_equity"], "change_pct": s_end["spy_bh_equity"] / spy_prev - 1}
        lines = []
        for f in sorted(fills, key=lambda f: (f["price_time"], f["fill_id"])):
            what = WHY.get(f["reason_code"], (f["reason_code"] or "").replace("_", " ").lower())
            pnl = f" → {_money(f['realized_pnl'], True)}" if f["side"] == "SELL" and f["realized_pnl"] is not None else ""
            lines.append(f"- {_et_time(f['price_time'])} **{f['side']} {f['ticker']}** at {f['fill_price']:.2f}: {what}{pnl}")
        if len(lines) > 30:
            lines = lines[:12] + [f"- … {len(lines) - 24} more trades (see the Trades & orders page) …"] + lines[-12:]
        if sells:
            best = max(sells, key=lambda f: f["realized_pnl"] or 0)
            worst = min(sells, key=lambda f: f["realized_pnl"] or 0)
            lines.append(f"- Best: {best['ticker']} {_money(best['realized_pnl'], True)}; worst: {worst['ticker']} {_money(worst['realized_pnl'], True)}.")
        if notes.get(book["id"]):
            lines.append(f"- {notes[book['id']]}")
        if not fills:
            lines.insert(0, "- No trades today.")
        for i in issues[:4]:
            lines.append(f"- Problem logged ({i['severity'].lower()}): {i['message'][:180]}")
        details.append({"name": name, "status": status, "text": "\n".join(lines)})
    active = [r for r in rows if "value" in r]
    moved = sorted([r for r in active if abs(r["change"]) > 0.005], key=lambda r: r["change"])
    summary = f"All bots together went from {_money(tot_prev)} to {_money(tot_end)} today ({_money(tot_end - tot_prev, True)})."
    if moved and moved[-1]["change"] > 0:
        summary += f" Biggest gain: {moved[-1]['name']} ({_money(moved[-1]['change'], True)})."
    if moved and moved[0]["change"] < 0:
        summary += f" Biggest loss: {moved[0]['name']} ({_money(moved[0]['change'], True)})."
    summary += f" The S&P 500 (SPY) moved {_pct(spy['change_pct'])}." if spy else " The stock market was closed."
    return {"kind": "daily", "date": d, "day": (day - start).days + 1, "weekday": day.strftime("%A"), "generated_at": iso(now),
            "summary": summary, "rows": rows, "details": details, "missing": missing, "spy": spy,
            "total_before": tot_prev, "total_end": tot_end}


def _table_rows(r: dict) -> list[list[str]]:
    out = []
    for x in r["rows"]:
        if "value" not in x:
            out.append([x["name"], "—", "—", "—", "—", "—", x["status"]])
            continue
        out.append([x["name"], _money(x["value"]), f"{_money(x['change'], True)}", f"{_money(x['since_start'], True)}",
                    str(x["trades"]), f"{x['wins']} / {x['losses']}" if x["wins"] or x["losses"] else "—", x["status"]])
    if r["spy"]:
        out.append(["S&P 500 (SPY), for comparison", _money(r["spy"]["value"]), _pct(r["spy"]["change_pct"]), "", "", "", "just holding it"])
    return out


HDR = ["Bot", "End of day", "Today", "Since start", "Trades", "Won / lost", "Status"]
NOTE = ("One day tells you almost nothing about whether a strategy works; luck dominates over a single day. "
        "Paper trading only: no real money. Balances are the saved end-of-day values; crypto bots are valued just after midnight ET.")


def to_markdown(r: dict) -> str:
    out = [f"# Daily report — {r['weekday']} {r['date']} (day {r['day']} of 30)", "", r["summary"], "",
           "| " + " | ".join(HDR) + " |", "|" + "---|" * len(HDR)]
    out += ["| " + " | ".join(c.replace("|", "/") for c in row) + " |" for row in _table_rows(r)]
    for dd in r["details"]:
        out += ["", f"## {dd['name']} — {dd['status']}", "", dd["text"]]
    if r["missing"]:
        out += ["", f"_Missing end-of-day data for: {', '.join(r['missing'])} (their last saved value is shown)._"]
    out += ["", f"_{NOTE} Generated {r['generated_at']}._"]
    return "\n".join(out) + "\n"


def to_html(r: dict) -> str:
    tbl = ('<div class="tw"><table><thead><tr>' + "".join(f"<th>{h}</th>" for h in HDR) + "</tr></thead><tbody>"
           + "".join("<tr>" + "".join(f"<td>{html.escape(c)}</td>" for c in row) + "</tr>" for row in _table_rows(r)) + "</tbody></table></div>")
    parts = ["<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>",
             f"<title>Daily report {r['date']}</title><style>{CSS}</style></head><body><main>",
             f"<h1>Daily report — {r['weekday']} {r['date']}</h1><p class='meta'>Day {r['day']} of 30 · generated {r['generated_at']} · paper trading only</p>",
             f"<p>{html.escape(r['summary'])}</p>", tbl]
    for dd in r["details"]:
        parts += [f"<h2>{html.escape(dd['name'])} — {html.escape(dd['status'])}</h2>", _md_list(dd["text"])]
    if r["missing"]:
        parts.append(f"<p class='meta'>Missing end-of-day data for: {html.escape(', '.join(r['missing']))} (their last saved value is shown).</p>")
    parts += [f"<p class='meta'>{html.escape(NOTE)}</p>", "</main></body></html>"]
    return "\n".join(parts)


def generate(exp: dict, day: dt.date, now: dt.datetime, out_dir: Path = REPORTS_DIR, r: dict | None = None) -> dict:
    r = r or build(exp, day, now)
    out_dir.mkdir(exist_ok=True)
    stem = _stem(day)
    paths = [out_dir / f"{stem}.{x}" for x in ("md", "html", "json")]
    if any(p.exists() for p in paths):
        raise FileExistsError(f"{stem} already exists; reports are never overwritten")
    due = dt.datetime.combine(day + dt.timedelta(days=1), dt.time(1), ET)
    meta = {k: r[k] for k in ("kind", "date", "day", "weekday", "generated_at", "summary", "rows", "spy", "missing", "total_before", "total_end")}
    meta["late_by_hours"] = round(max((now - due).total_seconds() / 3600, 0), 1)
    paths[0].write_text(to_markdown(r))
    paths[1].write_text(to_html(r))
    paths[2].write_text(json.dumps(meta, indent=1))
    return meta


def maybe_generate_daily(exp: dict, now: dt.datetime, out_dir: Path = REPORTS_DIR) -> list[str]:
    """Generate every finished day's report that doesn't exist yet (so missed days are backfilled, marked late)."""
    start, end = dt.date.fromisoformat(exp["start_date"]), dt.date.fromisoformat(exp["end_date"])
    now_et = now.astimezone(ET)
    made = []
    day = start
    while day <= min(end, now_et.date() - dt.timedelta(days=1)):
        if not (out_dir / f"{_stem(day)}.json").exists():
            waited_enough = now_et >= dt.datetime.combine(day + dt.timedelta(days=1), dt.time(12), ET)
            r = build(exp, day, now)
            if waited_enough or not r["missing"]:
                generate(exp, day, now, out_dir, r)
                made.append(_stem(day))
        day += dt.timedelta(days=1)
    return made


def daily_list(out_dir: Path = REPORTS_DIR) -> list[dict]:
    out = []
    for p in sorted(out_dir.glob("daily_*.json"), reverse=True):
        try:
            m = json.loads(p.read_text())
        except (OSError, ValueError):
            continue
        out.append({"file": p.with_suffix(".html").name, "md": p.with_suffix(".md").name, **m})
    return out
