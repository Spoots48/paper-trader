"""Weekly reports (days 7, 14, 21, 28) and the final day-30 report, as Markdown + HTML.

Reports are generated once, at the first cycle after their as-of session has
closed and been snapshotted. Existing report files are never overwritten.
"""
from __future__ import annotations

import datetime as dt
import html
import json
import subprocess
from pathlib import Path

from .config import REPORTS_DIR, ROOT, load_json
from .ledger import Ledger
from .marketdata import MarketData
from .nyse_calendar import ET, iso, is_session, next_session, prev_session, session_close
from .state import book_state


def _money(x, sign=False):
    if x is None:
        return "n/a"
    return (f"{x:+,.2f}" if sign else f"{x:,.2f}").replace("+", "+$").replace("-", "−$") if sign else f"${x:,.2f}"


def _pct(x):
    return "n/a" if x is None else f"{x:+.2%}".replace("-", "−")


def _rel(p: Path) -> str:
    try:
        return str(p.relative_to(ROOT))
    except ValueError:
        return str(p)


def _as_of(date_n: dt.date, start: dt.date) -> dt.date | None:
    d = date_n
    while d >= start:
        if is_session(d):
            return d
        d -= dt.timedelta(days=1)
    return None


def _snap_on_or_before(snaps: list[dict], session: str) -> dict | None:
    c = [s for s in snaps if s["session"] <= session]
    return c[-1] if c else None


# ---------------------------------------------------------------------------- content
def build(exp: dict, n: int, date_n: dt.date, as_of: dt.date, prev_as_of: dt.date | None, md: MarketData, now: dt.datetime) -> dict:
    cash0 = exp["starting_cash"]
    books = [book_state(b, exp, n_decisions=5000) for b in exp["books"]]
    final = n == max(exp["report_days"])
    wk_start = prev_as_of.isoformat() if prev_as_of else None
    rows, sections = [], []
    spy_now = spy_prev = None
    for b in books:
        snaps = b.get("snapshots") or []
        s = _snap_on_or_before(snaps, as_of.isoformat())
        p = _snap_on_or_before(snaps, wk_start) if wk_start else None
        if s is None:
            rows.append([b["name"], "no data", "", "", "", ""])
            continue
        base = p["equity"] if p else cash0
        upto = [x for x in snaps if x["session"] <= as_of.isoformat()]
        peak, mdd = cash0, 0.0
        for x in upto:
            peak = max(peak, x["equity"])
            mdd = max(mdd, 1 - x["equity"] / peak)
        rows.append([b["name"], _money(s["equity"]), f"{_money(s['equity'] - base, True)} ({_pct(s['equity'] / base - 1)})",
                     f"{_money(s['equity'] - cash0, True)} ({_pct(s['equity'] / cash0 - 1)})", f"{mdd:.2%}", s["session"]])
        if s.get("spy_bh_equity") and spy_now is None:
            spy_now = s["spy_bh_equity"]
            spy_prev = (p or {}).get("spy_bh_equity") or cash0
    if spy_now:
        rows.append(["SPY buy & hold", _money(spy_now), f"{_money(spy_now - spy_prev, True)} ({_pct(spy_now / spy_prev - 1)})",
                     f"{_money(spy_now - cash0, True)} ({_pct(spy_now / cash0 - 1)})", "—", as_of.isoformat()])
    rows.append(["Cash (do nothing)", _money(cash0), "+$0.00 (+0.00%)", "+$0.00 (+0.00%)", "0.00%", as_of.isoformat()])

    for b in books:
        if not b.get("frozen"):
            continue
        sec = {"title": f"{b['name']} book — {b['subtitle']}", "blocks": []}
        snaps = b.get("snapshots") or []
        s = _snap_on_or_before(snaps, as_of.isoformat())
        hold = (s or {}).get("holdings") or {}
        marks = ((s or {}).get("marks") or {}).get("marks", {})
        prow = []
        for t, h in sorted(hold.items()):
            m = marks.get(t)
            prow.append([t, h["sleeve"], f"{h['qty']:.4f}", _money(h["avg_cost"]), _money(m), _money(h["qty"] * m if m else None),
                         _money((m - h["avg_cost"]) * h["qty"] if m else None, True), _money(h["stop"]) if h.get("stop") else "—",
                         h["entry_session"]])
        sec["blocks"].append(("h3", "Open positions (at the as-of close)"))
        sec["blocks"].append(("table", ["Ticker", "Sleeve", "Qty", "Avg cost", "Close", "Value", "Unrealized", "Stop", "Entered"], prow)
                             if prow else ("p", f"None. Cash: {_money((s or {}).get('cash'))}."))
        wk_fills = [f for f in b["fills"] if (wk_start is None or f["session"] > wk_start) and f["session"] <= as_of.isoformat()]
        frows = [[f["session"], f["side"], f["ticker"], f["sleeve"], f"{f['qty']:.4f}", _money(f["fill_price"]), f"{f['cost_bps']:.1f} bp",
                  _money(f["realized_pnl"], True) if f["side"] == "SELL" else "", f["reason_code"], f["price_source"]] for f in reversed(wk_fills)]
        sec["blocks"].append(("h3", "Executions this period"))
        sec["blocks"].append(("table", ["Session", "Side", "Ticker", "Sleeve", "Qty", "Fill", "Cost", "Realized", "Reason", "Price source"], frows)
                             if frows else ("p", "No executions this period."))
        upto_fills = [f for f in b["fills"] if f["session"] <= as_of.isoformat()]
        wk_cost = sum(f["cost_usd"] for f in wk_fills)
        tot_cost = sum(f["cost_usd"] for f in upto_fills)
        closed = [f for f in upto_fills if f["side"] == "SELL" and f["sleeve"] != "residual"]
        wins = [f for f in closed if (f["realized_pnl"] or 0) > 0]
        risk = b.get("risk") or {}
        sec["blocks"].append(("p", f"Modeled trading costs: {_money(wk_cost)} this period, {_money(tot_cost)} cumulative. "
                                   f"Closed single-stock trades to date: {len(closed)} ({len(wins)} winners). "
                                   f"Regime at last decision: {b.get('regime') or 'n/a'}. "
                                   f"Drawdown controls: pause until {risk.get('pause_until') or '—'}, halt until {risk.get('halt_until') or '—'}."))
        # decisions with reasons and news evidence
        decs = [d for d in b["decisions"] if (wk_start is None or d["session"] > wk_start) and d["session"] <= next_session(as_of).isoformat()]
        major = [d for d in decs if d["action"] in ("BUY", "SELL") or d["reason_code"].startswith("NEWS_")
                 or d["reason_code"] in ("MISSED_WINDOW", "REGIME_OFF", "DD_HALT", "DD_PAUSE", "NO_SLOT")]
        sec["blocks"].append(("h3", "Major decisions (with evidence)"))
        if major:
            items = []
            for d in reversed(major):
                ev = []
                for nid in d["news_ids"][:4]:
                    nw = b["news"].get(nid)
                    if nw:
                        ev.append(f"    - \"{nw['title'][:120]}\" — {nw['provider'] or nw['source']}; published {nw['published_at']}; "
                                  f"retrieved {nw['retrieved_at']}" + (f"; {nw['url']}" if nw.get("url") else ""))
                items.append(f"- **{d['session']} {d['action']} {d['ticker']}** ({d['sleeve']}, {d['reason_code']}; decided {d['created_at']}, "
                             f"data through {d['data_through']}): {d['reason']}" + ("\n" + "\n".join(ev) if ev else ""))
            sec["blocks"].append(("md", "\n".join(items)))
        else:
            sec["blocks"].append(("p", "No buy/sell decisions this period."))
        # shadow tracking of skipped research signals (evidence about the filters)
        skipped = [d for d in decs if d["action"] == "SKIP" and d["sleeve"] == "catalyst" and d["reason_code"] != "CRITERIA"]
        if skipped:
            srows = []
            for d in skipped:
                t = d["ticker"]
                entry = md.bar(t, dt.date.fromisoformat(d["session"]))
                last = md.bar(t, as_of)
                r = (last["close"] / entry["open"] - 1) if entry and last and entry.get("open") and last.get("close") else None
                srows.append([d["session"], t, d["reason_code"], _pct(r), d["reason"][:90]])
            sec["blocks"].append(("h3", "Skipped catalyst signals — what happened next (shadow tracking)"))
            sec["blocks"].append(("table", ["Would-be entry", "Ticker", "Skip reason", "Open→as-of close", "Detail"], srows))
        # what worked / failed
        ww = []
        if closed:
            best = max(closed, key=lambda f: f["realized_pnl"] or 0)
            worst = min(closed, key=lambda f: f["realized_pnl"] or 0)
            ww.append(f"- Best closed trade: {best['ticker']} {_money(best['realized_pnl'], True)} ({best['reason_code']}); "
                      f"worst: {worst['ticker']} {_money(worst['realized_pnl'], True)} ({worst['reason_code']}).")
            by = {}
            for f in closed:
                by.setdefault(f["sleeve"], 0.0)
                by[f["sleeve"]] += f["realized_pnl"] or 0
            ww.append("- Realized P&L by sleeve: " + ", ".join(f"{k} {_money(v, True)}" for k, v in by.items()) + ".")
            stops = [f for f in closed if f["reason_code"].startswith("STOP")]
            if stops:
                ww.append(f"- Stop-outs: {len(stops)} ({', '.join(f['ticker'] for f in stops)}).")
        if s and spy_now:
            diff = s["equity"] - spy_now
            ww.append(f"- Versus SPY buy & hold: {_money(diff, True)} ({'ahead' if diff >= 0 else 'behind'}).")
        missed = [d for d in b["decisions"] if d["reason_code"] == "MISSED_WINDOW" and d["session"] <= as_of.isoformat()]
        if missed:
            ww.append(f"- Missed decision windows to date: {len(missed)} (Mac off/asleep/offline): {', '.join(d['session'] for d in missed)}.")
        n_closed = len(closed)
        ww.append(f"- **Evidence for rule changes:** {n_closed} closed single-stock trades so far. "
                  + ("That is far too few to separate skill from luck (roughly 30+ independent trades would be needed even to "
                     "detect a large edge), so no rule change is supported. Observations are logged for separate testing only."
                     if n_closed < 30 else "Enough trades for a rough look, but still one market regime; any change must be backtested "
                                           "separately and logged, never applied retroactively."))
        sec["blocks"].append(("h3", "What worked, what failed"))
        sec["blocks"].append(("md", "\n".join(ww) if ww else "- Nothing to evaluate yet."))
        sections.append(sec)

    # operations & data quality
    ops = []
    for b in books:
        if not b.get("frozen"):
            continue
        runs = [r for r in b["runs"] if (wk_start is None or r["started_at"][:10] > wk_start)]
        errs = [r for r in runs if r["status"] == "ERROR"]
        iss = [i for i in b["issues"] if (wk_start is None or i["occurred_at"][:10] > wk_start)]
        derived = sum(1 for s in (b.get("snapshots") or []) if (s.get("marks") or {}).get("flags"))
        ops.append(f"- {b['name']}: {len(runs)} runs this period ({len(errs)} with errors); {len(iss)} data/system issues logged; "
                   f"{derived} snapshots used derived or stale prices; audit chain: {b['audit']['detail']} "
                   f"({'OK' if b['audit']['chain_ok'] else 'BROKEN'}); strategy file matches frozen hash: "
                   f"{b['audit'].get('strategy_file_matches_frozen')}.")
        for i in iss[:12]:
            ops.append(f"    - {i['occurred_at']} [{i['severity']}] {i['component']}{' ' + i['ticker'] if i['ticker'] else ''}: {i['message'][:160]}")
    cfg = load_json(ROOT / exp["books"][0]["strategy"])
    c = cfg["costs"]
    assumptions = [
        "Paper trading only; no brokerage account, no real orders, no money.",
        f"Start ${cash0:.0f} per book, fractional shares (6 decimals), no leverage, shorts or options.",
        f"Costs per side as adverse price adjustment: SPY {c['etf_bps']} bp; stocks {c['stock_bps_adv_ge_1b']}/{c['stock_bps_adv_ge_200m']}/"
        f"{c['stock_bps_other']} bp by liquidity; +{c['open_auction_extra_bps']} bp at the open; +{c['stop_fill_extra_bps']} bp on stop fills; "
        f"+{c['sec_fee_bps_on_sells']} bp SEC fee on sells; $0 commission.",
        "Orders decided before the open fill at the official open; orders decided intraday fill at the open of the next 5-minute bar "
        "after the decision; stops are standing orders filled at the stop (or the bar open if it gaps through).",
        "Prices: Yahoo Finance (free, unofficial). When the official daily close is missing 30 min after the close, the bar is "
        "rebuilt from 5-minute bars and flagged.",
        "News (research book only): Yahoo Finance ticker news + Google News RSS, keyword classification, used only to confirm or veto.",
        "Dividends credited on the ex-date; settlement timing and taxes ignored.",
    ]
    limitations = [
        "One month (~21 sessions) is far too short to establish an edge: in the backtest the month-to-month spread of excess returns "
        "vs SPY was about ±3.5–4.4 percentage points (1 s.d.).",
        "The strategies were designed and frozen on 2026-09-22; the backtest showed the catalyst and momentum sleeves failing the "
        "pre-registered in-sample test (see research/PREREGISTRATION.md).",
        "Free data can be delayed, revised or missing; the Mac must be on and online for decisions.",
        "Not investment advice; the author is not a licensed advisor.",
    ]
    return {"n": n, "final": final, "date": date_n.isoformat(), "as_of": as_of.isoformat(), "prev_as_of": wk_start,
            "generated_at": iso(now), "headline": rows, "sections": sections, "ops": ops,
            "assumptions": assumptions, "limitations": limitations}


# ---------------------------------------------------------------------------- rendering
def to_markdown(r: dict) -> str:
    t = "Final report" if r["final"] else f"Week {r['n'] // 7} report"
    out = [f"# {t} — Day {r['n']} of 30", "",
           f"As of the close on **{r['as_of']}** (report date {r['date']}). Period starts after {r['prev_as_of'] or 'experiment start'}. "
           f"Generated {r['generated_at']}.", "", "## Results", "",
           "| | Value | This period | Cumulative | Max drawdown | As of |", "|---|---|---|---|---|---|"]
    out += ["| " + " | ".join(row) + " |" for row in r["headline"]]
    for s in r["sections"]:
        out += ["", f"## {s['title']}"]
        for kind, *rest in s["blocks"]:
            if kind == "h3":
                out += ["", f"### {rest[0]}"]
            elif kind in ("p", "md"):
                out += ["", rest[0]]
            elif kind == "table":
                hdr, rows = rest
                out += ["", "| " + " | ".join(hdr) + " |", "|" + "---|" * len(hdr)]
                out += ["| " + " | ".join(str(c).replace("|", "/") for c in row) + " |" for row in rows]
    out += ["", "## Data, operations and outages", ""] + (r["ops"] or ["- none"])
    out += ["", "## Execution assumptions", ""] + [f"- {a}" for a in r["assumptions"]]
    out += ["", "## Limitations", ""] + [f"- {a}" for a in r["limitations"]]
    return "\n".join(out) + "\n"


CSS = """
:root{--bg:#f7f7f5;--card:#fff;--ink:#1d1d1f;--muted:#6e6e73;--line:#e3e3e0;--accent:#2f6f4f}
@media (prefers-color-scheme:dark){:root{--bg:#161617;--card:#1f1f21;--ink:#f2f2f2;--muted:#a1a1a6;--line:#333336;--accent:#7cc4a0}}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 -apple-system,BlinkMacSystemFont,"SF Pro Text",system-ui,sans-serif}
main{max-width:1000px;margin:0 auto;padding:28px 16px 64px}
h1{font-size:26px;margin:0 0 6px}h2{font-size:19px;margin:34px 0 10px;border-top:1px solid var(--line);padding-top:22px}h3{font-size:15px;margin:22px 0 8px}
p,li{color:var(--ink)}.meta{color:var(--muted)}
.tw{overflow-x:auto;background:var(--card);border:1px solid var(--line);border-radius:10px}
table{border-collapse:collapse;width:100%;font-size:13px;font-variant-numeric:tabular-nums}
th,td{padding:7px 10px;border-bottom:1px solid var(--line);text-align:left;white-space:nowrap}th{color:var(--muted);font-weight:600}
tr:last-child td{border-bottom:0}a{color:var(--accent)}code{font-size:12px}
"""


def _inline(s: str) -> str:
    import re
    s = html.escape(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(https?://[^\s;<]+)", r'<a href="\1" target="_blank" rel="noopener">source</a>', s)
    return s


def _md_list(text: str) -> str:
    out, depth = [], 0
    for line in text.splitlines():
        lvl = 2 if line.startswith("    - ") else (1 if line.startswith("- ") else 0)
        body = line.strip()[2:] if lvl else line
        while depth < lvl:
            out.append("<ul>")
            depth += 1
        while depth > lvl:
            out.append("</ul>")
            depth -= 1
        out.append(f"<li>{_inline(body)}</li>" if lvl else f"<p>{_inline(body)}</p>")
    out += ["</ul>"] * depth
    return "\n".join(out)


def to_html(r: dict) -> str:
    t = "Final report" if r["final"] else f"Week {r['n'] // 7} report"

    def table(hdr, rows):
        return ('<div class="tw"><table><thead><tr>' + "".join(f"<th>{html.escape(h)}</th>" for h in hdr) + "</tr></thead><tbody>"
                + "".join("<tr>" + "".join(f"<td>{html.escape(str(c))}</td>" for c in row) + "</tr>" for row in rows) + "</tbody></table></div>")

    parts = [f"<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
             f"<title>Day {r['n']} report</title><style>{CSS}</style></head><body><main>",
             f"<h1>{t} — Day {r['n']} of 30</h1><p class='meta'>As of the close on <strong>{r['as_of']}</strong> (report date {r['date']}). "
             f"Period starts after {r['prev_as_of'] or 'experiment start'}. Generated {r['generated_at']}. Paper trading only.</p>",
             "<h2>Results</h2>", table(["", "Value", "This period", "Cumulative", "Max drawdown", "As of"], r["headline"])]
    for s in r["sections"]:
        parts.append(f"<h2>{html.escape(s['title'])}</h2>")
        for kind, *rest in s["blocks"]:
            if kind == "h3":
                parts.append(f"<h3>{html.escape(rest[0])}</h3>")
            elif kind == "p":
                parts.append(f"<p>{_inline(rest[0])}</p>")
            elif kind == "md":
                parts.append(_md_list(rest[0]))
            elif kind == "table":
                parts.append(table(*rest))
    parts += ["<h2>Data, operations and outages</h2>", _md_list("\n".join(r["ops"]) or "- none"),
              "<h2>Execution assumptions</h2>", _md_list("\n".join(f"- {a}" for a in r["assumptions"])),
              "<h2>Limitations</h2>", _md_list("\n".join(f"- {a}" for a in r["limitations"])), "</main></body></html>"]
    return "\n".join(parts)


# ---------------------------------------------------------------------------- scheduling
def notify(title: str, message: str) -> None:
    try:
        subprocess.run(["osascript", "-e", f'display notification {json.dumps(message)} with title {json.dumps(title)} sound name "Glass"'],
                       timeout=10, capture_output=True)
    except Exception:  # notifications are best-effort; the report itself is already saved
        pass


def generate(exp: dict, n: int, md: MarketData, now: dt.datetime, registry: Ledger | None = None, suffix: str = "") -> dict:
    start = dt.date.fromisoformat(exp["start_date"])
    date_n = start + dt.timedelta(days=n - 1)
    as_of = _as_of(date_n, start)
    days = sorted(exp["report_days"])
    prev_n = max([d for d in days if d < n], default=None)
    prev_as_of = _as_of(start + dt.timedelta(days=prev_n - 1), start) if prev_n else None
    r = build(exp, n, date_n, as_of, prev_as_of, md, now)
    REPORTS_DIR.mkdir(exist_ok=True)
    stem = f"day{n:02d}_{date_n.isoformat()}{suffix}"
    md_path, html_path = REPORTS_DIR / f"{stem}.md", REPORTS_DIR / f"{stem}.html"
    if md_path.exists() or html_path.exists():
        raise FileExistsError(f"{stem} already exists; reports are never overwritten")
    md_path.write_text(to_markdown(r))
    html_path.write_text(to_html(r))
    late = (now - (session_close(as_of) + dt.timedelta(hours=1))).total_seconds() / 3600
    meta = {"day": n, "date": date_n.isoformat(), "as_of": as_of.isoformat(), "generated_at": r["generated_at"],
            "late_by_hours": round(max(late, 0), 1), "final": r["final"], "headline": r["headline"]}
    (REPORTS_DIR / f"{stem}.json").write_text(json.dumps(meta, indent=1))
    if registry is not None:
        registry.db.execute("INSERT INTO reports (report_key, day_number, report_date, as_of_session, generated_at, path_md, path_html, "
                            "late_by_hours) VALUES (?,?,?,?,?,?,?,?)",
                            (f"day{n:02d}", n, date_n.isoformat(), as_of.isoformat(), r["generated_at"], _rel(md_path), _rel(html_path),
                             meta["late_by_hours"]))
        registry.event("report", {"key": f"day{n:02d}", "as_of": as_of.isoformat()})
    return {"stem": stem, "html": html_path, "meta": meta, "report": r}


def maybe_generate_reports(exp: dict, registry: Ledger, md: MarketData, now: dt.datetime) -> list[str]:
    """Generate any due report exactly once. `registry` is the primary book's ledger."""
    start = dt.date.fromisoformat(exp["start_date"])
    today = now.astimezone(ET).date()
    made = []
    snaps = {s["session"] for s in registry.snapshots()}
    for n in sorted(exp["report_days"]):
        key = f"day{n:02d}"
        if registry.db.execute("SELECT 1 FROM reports WHERE report_key=?", (key,)).fetchone():
            continue
        date_n = start + dt.timedelta(days=n - 1)
        as_of = _as_of(date_n, start)
        if as_of is None or today < date_n or now < session_close(as_of):
            continue
        if as_of.isoformat() not in snaps:
            continue  # wait until that session is closed out (e.g. the Mac was off)
        out = generate(exp, n, md, now, registry)
        h = out["report"]["headline"]
        notify("Paper Trader", f"Day {n} report ready — {h[0][0]}: {h[0][1]} ({h[0][3].split(' ')[-1]}), SPY {h[2][3].split(' ')[-1] if len(h) > 3 else 'n/a'}")
        registry.db.execute("UPDATE reports SET notified=1 WHERE report_key=?", (key,))
        if n == max(exp["report_days"]):
            registry.set_state("experiment_finished", iso(now))
        made.append(out["stem"])
    return made
