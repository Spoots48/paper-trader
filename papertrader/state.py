"""Read-only aggregation of ledger state for the app UI, the static dashboard and the reports."""
from __future__ import annotations

import datetime as dt
import json
import os
import subprocess
from pathlib import Path

from .config import DATA_DIR, REPORTS_DIR, RESEARCH_DIR, ROOT, load_experiment, load_json, sha256_file
from .ledger import Ledger
from .nyse_calendar import ET, current_session, iso, last_completed_session, now_utc, sessions_between

LABEL = "com.papertradingsim.cycle"
PLIST = Path.home() / "Library" / "LaunchAgents" / f"{LABEL}.plist"
PAUSE_FLAG = DATA_DIR / "PAUSED"
HEARTBEAT = DATA_DIR / "heartbeat.json"


def scheduler_status() -> dict:
    from .cloud import cloud_viewer, status as cloud_status
    if cloud_viewer():
        c = dict(cloud_status(max_age=float("inf")))
        from .cloud import last_sync
        c["last_sync"] = last_sync()
        runs = c.get("runs") or []
        done = [r for r in runs if r.get("status") == "completed"]
        last = done[0] if done else None
        hb = None
        try:
            hb = json.loads(HEARTBEAT.read_text())
        except (OSError, ValueError):
            pass
        return {"mode": "cloud", "installed": True, "loaded": bool(c.get("enabled")), "paused": c.get("enabled") is False,
                "enabled": c.get("enabled"), "running": c.get("running"), "runs": runs[:15], "url": c.get("url"),
                "repo": c.get("repo"), "last_run": last, "last_exit": (last or {}).get("conclusion"),
                "detail": "GitHub Actions" + ("" if c.get("enabled") is not False else " (disabled)"),
                "error": c.get("error"), "last_sync": c.get("last_sync"), "heartbeat": hb, "pending": c.get("pending")}
    st = {"mode": "local", "installed": PLIST.exists(), "loaded": False, "paused": PAUSE_FLAG.exists(), "last_exit": None, "detail": ""}
    try:
        out = subprocess.run(["launchctl", "print", f"gui/{os.getuid()}/{LABEL}"], capture_output=True, text=True, timeout=5)
        if out.returncode == 0:
            st["loaded"] = True
            for line in out.stdout.splitlines():
                line = line.strip()
                if line.startswith("last exit code"):
                    st["last_exit"] = line.split("=", 1)[1].strip()
                if line.startswith("state ="):
                    st["detail"] = line.split("=", 1)[1].strip()
    except Exception as e:  # launchctl missing/unavailable: report rather than fail the UI
        st["detail"] = f"launchctl unavailable: {e}"
    try:
        st["heartbeat"] = json.loads(HEARTBEAT.read_text())
    except (OSError, ValueError):
        st["heartbeat"] = None
    return st


def perf(snaps: list[dict], cash0: float) -> dict:
    if not snaps:
        return {"equity": cash0, "ret": 0.0, "pnl": 0.0, "max_dd": 0.0, "spy_equity": None, "spy_ret": None}
    eq = [s["equity"] for s in snaps]
    peak, mdd = cash0, 0.0
    for e in eq:
        peak = max(peak, e)
        mdd = max(mdd, 1 - e / peak)
    last = snaps[-1]
    spy = last.get("spy_bh_equity")
    return {"equity": last["equity"], "ret": last["equity"] / cash0 - 1, "pnl": last["equity"] - cash0, "max_dd": mdd,
            "spy_equity": spy, "spy_ret": (spy / cash0 - 1) if spy else None, "as_of": last["session"]}


def book_state(book: dict, exp: dict, n_decisions: int = 400, quotes: dict | None = None) -> dict:
    path = ROOT / book["ledger"]
    out = {"id": book["id"], "name": book["name"], "subtitle": book["subtitle"], "strategy_file": book["strategy"]}
    if not path.exists():
        out["frozen"] = False
        return out
    L = Ledger(path)
    try:
        e = L.experiment()
        out["frozen"] = e is not None
        out["experiment"] = e
        cash0 = exp["starting_cash"]
        snaps = L.snapshots()
        for s in snaps:
            s["holdings"] = json.loads(s["holdings"] or "{}")
            s["marks"] = json.loads(s["marks"] or "{}")
            s.pop("risk_state", None)
        out["snapshots"] = snaps
        out["perf"] = perf(snaps, cash0)
        pos = [dict(r) for r in L.db.execute("SELECT * FROM positions ORDER BY ticker")]
        live = L.get_state("live_marks", {}) or {}
        last_marks = (snaps[-1]["marks"].get("marks", {}) if snaps else {})
        cash = L.get_state("cash", cash0)
        total = cash
        for p in pos:
            p["meta"] = json.loads(p["meta"] or "{}")
            lm = (quotes or {}).get(p["ticker"]) or (live.get("marks") or {}).get(p["ticker"])
            p["mark"], p["mark_time"] = (lm[0], lm[1]) if lm else (last_marks.get(p["ticker"], p["entry_price"]), "last close")
            p["value"] = p["qty"] * p["mark"]
            p["unrealized"] = (p["mark"] - p["avg_cost"]) * p["qty"]
            stop = p["initial_stop"] or 0
            if p["trail_pct"]:
                stop = max(stop, p["high_water"] * (1 - p["trail_pct"]))
            p["stop"] = stop or None
            total += p["value"]
        for p in pos:
            p["weight"] = p["value"] / total if total else 0
        out["positions"] = pos
        out["cash"] = cash
        out["live_equity"] = total
        out["live_as_of"] = live.get("as_of")
        out["risk"] = L.get_state("risk", {})
        out["regime"] = L.get_state("last_regime")
        out["benchmark"] = L.get_state("benchmark")
        day = L.db.execute("SELECT key, value FROM state WHERE key LIKE 'dt:%' ORDER BY key DESC LIMIT 1").fetchone()
        if day:
            ds = json.loads(day["value"])
            out["day_state"] = {k: ds.get(k) for k in ("session", "cash_at_open", "buys_used", "closed", "processed_through")}
            out["day_state"]["n_candidates"] = len(ds.get("candidates") or [])
        bq = (quotes or {}).get("SPY")
        bm = out["benchmark"]
        if bm and bq:
            out["live_spy_equity"] = bm["qty"] * bq[0] + bm.get("div_cash", 0.0)
        if quotes and pos:
            out["live_as_of"] = max(p["mark_time"] for p in pos if p["mark_time"] != "last close") if any(p["mark_time"] != "last close" for p in pos) else out.get("live_as_of")
        out["orders"] = [dict(r) for r in L.db.execute("SELECT order_key, created_at, ticker, side, order_type, session, sleeve, notional, qty, "
                                                       "reason_code, reason, status, status_reason, updated_at FROM orders ORDER BY created_at DESC LIMIT 300")]
        out["fills"] = [dict(r) for r in L.db.execute("SELECT * FROM fills ORDER BY fill_id DESC")]
        decs = [dict(r) for r in L.db.execute("SELECT * FROM decisions ORDER BY decision_id DESC LIMIT ?", (n_decisions,))]
        ids = set()
        for d in decs:
            d["metrics"] = json.loads(d["metrics"] or "{}")
            d["news_ids"] = json.loads(d["news_ids"] or "[]")
            ids.update(d["news_ids"])
        out["decisions"] = decs
        news = {}
        if ids:
            q = ",".join("?" for _ in ids)
            for r in L.db.execute(f"SELECT * FROM news WHERE news_id IN ({q})", tuple(ids)):
                news[r["news_id"]] = dict(r)
        out["news"] = news
        out["issues"] = [dict(r) for r in L.db.execute("SELECT * FROM data_issues ORDER BY id DESC LIMIT 200")]
        out["runs"] = [dict(r) for r in L.db.execute("SELECT * FROM runs ORDER BY started_at DESC LIMIT 150")]
        out["dividends"] = [dict(r) for r in L.db.execute("SELECT * FROM dividends ORDER BY ex_date")]
        out["changes"] = [dict(r) for r in L.db.execute("SELECT * FROM strategy_changes ORDER BY id")]
        ok, msg = L.verify_chain()
        out["audit"] = {"chain_ok": ok, "detail": msg}
        if e:
            cur_sha = sha256_file(ROOT / book["strategy"])
            approved = e["strategy_sha256"]
            ch = L.db.execute("SELECT to_sha256 FROM strategy_changes ORDER BY id DESC LIMIT 1").fetchone()
            if ch:
                approved = ch["to_sha256"]
            out["audit"]["strategy_file_matches_frozen"] = cur_sha == approved
        out["costs_total"] = sum(f["cost_usd"] for f in out["fills"])
        out["realized_pnl"] = sum(f["realized_pnl"] or 0 for f in out["fills"] if f["side"] == "SELL")
    finally:
        L.close()
    return out


def experiment_calendar(exp: dict, now: dt.datetime) -> dict:
    start, end = dt.date.fromisoformat(exp["start_date"]), dt.date.fromisoformat(exp["end_date"])
    today = now.astimezone(ET).date()
    day = (today - start).days + 1
    return {
        "start": exp["start_date"], "end": exp["end_date"], "today_et": today.isoformat(), "day": day,
        "total_days": (end - start).days + 1, "status": "not started" if day < 1 else ("finished" if today > end else "running"),
        "sessions_total": len(sessions_between(start, end)),
        "sessions_done": len([s for s in sessions_between(start, min(end, last_completed_session(now)))]),
        "market_open_now": current_session(now) is not None,
        "report_schedule": [{"day": n, "date": (start + dt.timedelta(days=n - 1)).isoformat()} for n in exp["report_days"]],
    }


def reports_list() -> list[dict]:
    out = []
    for p in sorted(REPORTS_DIR.glob("*.html")):
        meta = p.with_suffix(".json")
        m = json.loads(meta.read_text()) if meta.exists() else {}
        out.append({"file": p.name, "md": p.with_suffix(".md").name, **m})
    return out


def backtest_summary() -> dict | None:
    try:
        r = load_json(RESEARCH_DIR / "backtest_results.json")
        curves = load_json(RESEARCH_DIR / "backtest_curves.json")
    except OSError:
        return None
    keep = ("spy_buy_hold", "regime_gated_spy_only", "without_catalyst", "without_momentum", "full_strategy")
    out = {"periods": {}}
    for p, d in r["periods"].items():
        out["periods"][p] = {"start": d["start"], "end": d["end"],
                             "rows": {k: {x: d[k].get(x) for x in ("total_return", "cagr", "max_drawdown", "sharpe_rf0", "ann_vol",
                                                                   "n_stock_round_trips", "win_rate", "costs_usd")} for k in keep},
                             "rolling": d["rolling_30d_full_vs_spy"],
                             "event_study": {k: {x: v.get(x) for x in ("n", "excess_5d_mean", "excess_5d_tstat", "excess_20d_mean",
                                                                         "excess_20d_tstat", "hit_rate_20d")} for k, v in d["catalyst_event_study"].items()}}
        c = curves[p]
        step = max(1, len(c["dates"]) // 400)  # downsample for the UI
        out["periods"][p]["curve"] = {k: v[::step] for k, v in c.items()}
    return out


def full_state(quotes: dict | None = None) -> dict:
    exp = load_experiment()
    now = now_utc()
    return {
        "generated_at": iso(now),
        "experiment": {k: v for k, v in exp.items() if k != "books"},
        "calendar": experiment_calendar(exp, now),
        "scheduler": scheduler_status(),
        "books": [book_state(b, exp, quotes=quotes) for b in exp["books"]],
        "reports": reports_list(),
        "backtest": backtest_summary(),
        "backtest_daytrade": _dt_backtests(),
        "pm_calibration": _pm_calibration(),
        "strategies": {b["id"]: load_json(ROOT / b["strategy"]) for b in exp["books"]},
        "deployment": _deployment(),
        "names": {**{m["ticker"]: m["name"] for m in load_json(ROOT / "config" / "universe.json")["members"]},
                  "SPY": "S&P 500 index fund"},
    }


def _deployment() -> dict:
    from .cloud import deployment
    return deployment()


def _dt_backtests() -> dict:
    out = {}
    for m in (5, 1):
        p = RESEARCH_DIR / f"backtest_daytrade_{m}m.json"
        if p.exists():
            r = load_json(p)
            out[f"{m}m"] = {k: r[k] for k in ("note", "full", "first_half", "second_half", "spy_same_period", "trades", "curve") if k in r}
    return out


def _pm_calibration() -> dict | None:
    p = RESEARCH_DIR / "pm_calibration.json"
    if not p.exists():
        return None
    r = load_json(p)
    return {k: r.get(k) for k in ("period_utc", "samples", "brier_model", "brier_market", "bets_by_window")} | {"one_bet_per_window": r.get("one_bet_per_window")}
