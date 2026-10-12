"""After-close review: what happened in each book today, what looks wrong, and what the evidence does and does not support changing.

Diagnostic only. It reads the ledgers read-only and writes reports/review_<date>.md. It NEVER edits a strategy: rules are frozen,
and one day (or one week) of trades is far too small a sample to tune on. A rule change needs a logged change (run.py log-change)
backed by a test on history with an out-of-sample split, and at least MIN_TRADES closed trades of live evidence."""
from __future__ import annotations

import datetime as dt
import sqlite3
from pathlib import Path

from .config import REPORTS_DIR, ROOT
from .nyse_calendar import ET, is_session, session_close

MIN_TRADES = 30
REVIEW_AFTER = dt.time(16, 40)


def _ro(path: Path) -> sqlite3.Connection:
    c = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    c.row_factory = sqlite3.Row
    return c


def _pair_trades(fills: list[dict]) -> list[dict]:
    """Closed round trips: a SELL matched to the average cost it carries (realized_pnl is recorded on SELL fills)."""
    return [{"session": f["session"], "ticker": f["ticker"], "reason": f["reason_code"], "pnl": f["realized_pnl"] or 0.0}
            for f in fills if f["side"] == "SELL" and f["realized_pnl"] is not None]


def review_book(book: dict, day: dt.date) -> dict:
    path = ROOT / book["ledger"]
    out = {"id": book["id"], "name": book["name"], "flags": [], "notes": []}
    if not path.exists():
        out["flags"].append("ledger missing")
        return out
    c = _ro(path)
    d = day.isoformat()
    snaps = [dict(r) for r in c.execute("SELECT session, equity, spy_bh_equity FROM snapshots ORDER BY session")]
    upto = [s for s in snaps if s["session"] <= d]  # prediction-market books snapshot on their own schedule: use the last two
    if len(upto) >= 2:
        today, prev = upto[-1], upto[-2]
        out["as_of"] = today["session"]
        out["day_pnl"] = today["equity"] - prev["equity"]
        out["day_pct"] = out["day_pnl"] / prev["equity"]
        if today.get("spy_bh_equity") and prev.get("spy_bh_equity"):
            out["spy_pct"] = today["spy_bh_equity"] / prev["spy_bh_equity"] - 1
    out["equity"] = snaps[-1]["equity"] if snaps else None
    fills = [dict(r) for r in c.execute("SELECT * FROM fills ORDER BY fill_id")]
    todays = [f for f in fills if f["session"] == d]
    trades_today = _pair_trades(todays)
    trades_all = _pair_trades(fills)
    out["fills_today"] = len(todays)
    out["trades_today"] = trades_today
    out["cost_today"] = sum(f["cost_usd"] or 0.0 for f in todays)
    info = [r["reason"] for r in c.execute("SELECT reason FROM decisions WHERE action='INFO' AND substr(created_at,1,10)>=? ORDER BY decision_id DESC LIMIT 1", (d,))]
    out["last_info"] = info[0][:160] if info else None
    issues = [dict(r) for r in c.execute("SELECT severity, component, message FROM data_issues WHERE substr(occurred_at,1,10)=?", (d,))]
    errors = [i for i in issues if i["severity"] in ("ERROR", "CRITICAL")]
    out["errors"] = errors[:3]
    n = len(trades_all)
    wins = [t["pnl"] for t in trades_all if t["pnl"] > 0]
    losses = [t["pnl"] for t in trades_all if t["pnl"] <= 0]
    stops = [t for t in trades_all if str(t["reason"]).startswith("STOP")]
    out["rolling"] = {"n": n, "win_rate": len(wins) / n if n else None, "avg_win": sum(wins) / len(wins) if wins else None,
                      "avg_loss": sum(losses) / len(losses) if losses else None, "stop_share": len(stops) / n if n else None,
                      "total": sum(t["pnl"] for t in trades_all)}
    # deterministic flags: things worth a human look, never an automatic change
    if out.get("day_pct") is not None and out["day_pct"] < -0.005:
        worst = min(trades_today, key=lambda t: t["pnl"], default=None)
        out["flags"].append(f"lost {out['day_pct']:.2%} today" + (f"; worst closed trade {worst['ticker']} {worst['pnl']:+.2f} ({worst['reason']})" if worst else ""))
    st = [t for t in trades_today if str(t["reason"]).startswith("STOP")]
    if len(st) >= 3 and not any(t["pnl"] > 0 for t in trades_today):
        out["flags"].append(f"{len(st)} stop-outs and no winners today")
    if todays and out["cost_today"] > 0 and abs(out.get("day_pnl", 0.0)) < out["cost_today"] * 2:
        out["flags"].append(f"modeled costs ${out['cost_today']:.2f} are large relative to today's P&L")
    if errors:
        out["flags"].append(f"{len(errors)} engine/data error(s) logged: {errors[0]['message'][:100]}")
    if n >= 15 and out["rolling"]["stop_share"] is not None and out["rolling"]["stop_share"] > 0.6 and out["rolling"]["total"] < 0:
        out["notes"].append(f"{out['rolling']['stop_share']:.0%} of {n} closed trades ended at the stop and the total is {out['rolling']['total']:+.2f}: "
                            "stops may be too tight for this book's entries, or the entries have no edge. Do not change on this alone; test on history first.")
    out["gate"] = ("enough closed trades to consider a tested change" if n >= MIN_TRADES
                   else f"only {n} closed trades (need {MIN_TRADES}+ and an out-of-sample test): no rule change is supported yet")
    c.close()
    return out


def render(day: dt.date, books: list[dict], extra: list[str] | None = None) -> str:
    lines = [f"# After-close review: {day.isoformat()}", "",
             "Diagnostic only. No strategy was changed. A change needs a logged `run.py log-change` backed by a history test with an out-of-sample split.", "",
             "| Book | Equity | Today | SPY today | Fills | Flags |", "|---|---|---|---|---|---|"]
    for b in books:
        eq = f"${b['equity']:.2f}" if b.get("equity") is not None else "n/a"
        d = f"{b['day_pct']:+.2%}" if b.get("day_pct") is not None else "n/a"
        s = f"{b['spy_pct']:+.2%}" if b.get("spy_pct") is not None else "n/a"
        lines.append(f"| {b['name']} | {eq} | {d} | {s} | {b.get('fills_today', 0)} | {len(b['flags'])} |")
    for b in books:
        lines += ["", f"## {b['name']}"]
        if b.get("trades_today"):
            lines.append("Closed today: " + ", ".join(f"{t['ticker']} {t['pnl']:+.2f} ({t['reason']})" for t in b["trades_today"]))
        elif not b.get("fills_today"):
            lines.append("No trades today." + (f" Why: {b['last_info']}" if b.get("last_info") else ""))
        r = b.get("rolling") or {}
        if r.get("n"):
            wr = f"{r['win_rate']:.0%}" if r["win_rate"] is not None else "n/a"
            aw = f"{r['avg_win']:+.2f}" if r["avg_win"] is not None else "n/a"
            al = f"{r['avg_loss']:+.2f}" if r["avg_loss"] is not None else "n/a"
            lines.append(f"All closed trades so far: {r['n']}, win rate {wr}, average win {aw}, average loss {al}, total {r['total']:+.2f}.")
        lines += [f"- WHAT LOOKS WRONG: {f}" for f in b["flags"]] or []
        lines += [f"- NOTE: {n}" for n in b["notes"]]
        lines.append(f"- Evidence gate: {b.get('gate', 'n/a')}")
    lines += extra or []
    return "\n".join(lines) + "\n"


def maybe_generate_review(exp: dict, now: dt.datetime, out_dir: Path = REPORTS_DIR) -> str | None:
    """Once per session day, after the close. Idempotent: returns the file stem when it wrote one."""
    now_et = now.astimezone(ET)
    day = now_et.date()
    if not is_session(day) or now_et.time() < REVIEW_AFTER or now < session_close(day):
        return None
    if dt.date.fromisoformat(exp["start_date"]) > day or day > dt.date.fromisoformat(exp["end_date"]):
        return None
    path = out_dir / f"review_{day.isoformat()}.md"
    if path.exists():
        return None
    books = [review_book(b, day) for b in exp["books"] if dt.date.fromisoformat(b.get("start_date", exp["start_date"])) <= day]
    out_dir.mkdir(parents=True, exist_ok=True)
    path.write_text(render(day, books, _jev_section(exp, day)))
    return path.stem


def _jev_section(exp: dict, day: dt.date) -> list[str]:
    """Jev calibration lines for the speed book, or nothing. Never raises: a data hiccup must not cost the day's review."""
    try:
        import json
        from . import jev_calibration as jc
        book = next((b for b in exp["books"] if b["id"] == "speed"), None)
        if book is None:
            return []
        cfg = json.loads((ROOT / book["strategy"]).read_text())["speed"]
        today = jc.run_for_day(day, cfg["take_profit_pct"], cfg["stop_pct"], cfg["max_hold_minutes"])
        return jc.render(today, jc.totals())
    except Exception as e:  # noqa: BLE001
        return ["", f"## Jev's speed-trader probabilities vs what happened", f"Not scored today: {type(e).__name__}: {str(e)[:120]}"]
