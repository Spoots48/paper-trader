#!/usr/bin/env python3
"""Paper Trader command line.

  python run.py freeze            freeze strategies + start the ledgers (once, before the start date)
  python run.py cycle             run one scheduled cycle now (what launchd runs every 15 min)
  python run.py status            print a summary
  python run.py serve             start the local control panel (the Mac app does this for you)
  python run.py export            write dashboard/index.html (static snapshot)
  python run.py verify            verify audit hash chains, strategy hashes and cash reconciliation
  python run.py report --day 7 --preview   render a report now without registering it
  python run.py backtest          re-run the historical test (research only)
  python run.py log-change --book research --new-config path.json --description "..." --evidence "..."
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from papertrader.config import CONFIG_DIR, ensure_dirs, load_experiment, load_json, sha256_file, UNIVERSE_PATH  # noqa: E402
from papertrader.nyse_calendar import iso, now_utc  # noqa: E402


def cmd_freeze(a) -> None:
    from papertrader.ledger import Ledger
    exp = load_experiment()
    frozen_dir = CONFIG_DIR / "frozen"
    frozen_dir.mkdir(exist_ok=True)
    for b in exp["books"]:
        L = Ledger(ROOT / b["ledger"])
        if L.experiment():
            print(f"[{b['id']}] already frozen at {L.experiment()['frozen_at']} — refusing to re-freeze")
            L.close()
            continue
        cfg_path = ROOT / b["strategy"]
        cfg = load_json(cfg_path)
        sha = sha256_file(cfg_path)
        usha = sha256_file(UNIVERSE_PATH)
        shutil.copy2(cfg_path, frozen_dir / f"{b['id']}_{sha[:12]}.json")
        L.freeze({**exp, "start_date": b.get("start_date", exp["start_date"])}, b, cfg["version"], sha, usha)
        print(f"[{b['id']}] frozen: {cfg['version']} sha256={sha[:16]}… start {b.get('start_date', exp['start_date'])} end {exp['end_date']}")
        L.close()


def cmd_cycle(a) -> None:
    from papertrader.cloud import cloud_viewer, sync
    if cloud_viewer():  # the experiment trades on GitHub Actions; this Mac only syncs
        from papertrader.cycle import online, setup_logging
        setup_logging()
        if not online():
            print(json.dumps({"status": "offline"}))
            return
        out = sync()
        from papertrader import cloud
        from papertrader.live import watchdog_check
        from papertrader.nyse_calendar import now_utc
        why = watchdog_check(cloud.status(max_age=0), now_utc())
        if why:  # GitHub skipped a key scheduled run: start it now (manual starts run immediately)
            out["watchdog"] = {"reason": why, "started": cloud.trigger()}
        print(json.dumps(out, indent=1, default=str))
        return
    from papertrader.cycle import run_cycle
    r = run_cycle(trigger=a.trigger)
    print(json.dumps(r, indent=1, default=str))


def cmd_status(a) -> None:
    from papertrader.state import full_state
    st = full_state()
    cal = st["calendar"]
    sc = st["scheduler"]
    print(f"Experiment {cal['start']} → {cal['end']} | day {cal['day']}/{cal['total_days']} ({cal['status']}) | "
          f"sessions {cal['sessions_done']}/{cal['sessions_total']}")
    print(f"Scheduler: installed={sc['installed']} loaded={sc['loaded']} paused={sc['paused']} last_exit={sc['last_exit']} "
          f"heartbeat={(sc.get('heartbeat') or {}).get('at')} {(sc.get('heartbeat') or {}).get('status')}")
    for b in st["books"]:
        if not b.get("frozen"):
            print(f"  {b['name']}: not frozen")
            continue
        p = b["perf"]
        print(f"  {b['name']:9s} equity ${p['equity']:.2f} ({p['ret']:+.2%}) | SPY B&H {('$%.2f' % p['spy_equity']) if p['spy_equity'] else 'n/a'} | "
              f"max DD {p['max_dd']:.2%} | cash ${b['cash']:.2f} | positions {', '.join(x['ticker'] for x in b['positions']) or 'none'} | "
              f"open orders {sum(1 for o in b['orders'] if o['status'] == 'OPEN')} | audit {b['audit']['detail']}")
    print(f"Reports: {[r['file'] for r in st['reports']] or 'none yet'}")


def cmd_serve(a) -> None:
    from papertrader.webapp import serve
    serve(a.port)


def cmd_export(a) -> None:
    from papertrader.webapp import export_static
    print(export_static())


def cmd_verify(a) -> None:
    from papertrader.ledger import Ledger
    exp = load_experiment()
    ok_all = True
    for b in exp["books"]:
        L = Ledger(ROOT / b["ledger"])
        e = L.experiment()
        if not e:
            print(f"[{b['id']}] not frozen")
            continue
        ok, msg = L.verify_chain()
        approved = e["strategy_sha256"]
        ch = L.db.execute("SELECT to_sha256 FROM strategy_changes ORDER BY id DESC LIMIT 1").fetchone()
        if ch:
            approved = ch["to_sha256"]
        sha_ok = sha256_file(ROOT / b["strategy"]) == approved
        # cash reconciliation: starting cash - buys + sells + dividends == stored cash
        buys = L.db.execute("SELECT COALESCE(SUM(qty*fill_price),0) s FROM fills WHERE side='BUY'").fetchone()["s"]
        sells = L.db.execute("SELECT COALESCE(SUM(qty*fill_price),0) s FROM fills WHERE side='SELL'").fetchone()["s"]
        divs = L.db.execute("SELECT COALESCE(SUM(amount),0) s FROM dividends").fetchone()["s"]
        derived = e["starting_cash"] - buys + sells + divs
        stored = L.get_state("cash", e["starting_cash"])
        cash_ok = abs(derived - stored) < 1e-6
        print(f"[{b['id']}] audit chain: {msg} ({'OK' if ok else 'BROKEN'}) | strategy file matches frozen: {sha_ok} | "
              f"cash reconciles: {cash_ok} (derived {derived:.6f} vs stored {stored:.6f})")
        ok_all &= ok and sha_ok and cash_ok
        L.close()
    sys.exit(0 if ok_all else 1)


def cmd_report(a) -> None:
    from papertrader.marketdata import MarketData
    from papertrader.reporting import generate
    exp = load_experiment()
    out = generate(exp, a.day, MarketData(), now_utc(), registry=None, suffix="_preview" if a.preview else "_manual")
    print(out["html"])


def cmd_backtest(a) -> None:
    from papertrader import backtest
    r = backtest.main()
    for p, d in r["periods"].items():
        print(p, {k: round(d[k]["cagr"], 4) for k in ("spy_buy_hold", "regime_gated_spy_only", "full_strategy")})


def cmd_log_change(a) -> None:
    """Record a strategy change. Past results are never rewritten; the change applies from the next decision."""
    from papertrader.ledger import Ledger
    exp = load_experiment()
    b = next(x for x in exp["books"] if x["id"] == a.book)
    L = Ledger(ROOT / b["ledger"])
    e = L.experiment()
    old_path = ROOT / b["strategy"]
    new = Path(a.new_config)
    old_cfg, new_cfg = load_json(old_path), load_json(new)
    prev_sha = sha256_file(old_path)
    last = L.db.execute("SELECT to_sha256 FROM strategy_changes ORDER BY id DESC LIMIT 1").fetchone()
    shutil.copy2(old_path, CONFIG_DIR / "frozen" / f"{b['id']}_{prev_sha[:12]}.json")
    shutil.copy2(new, old_path)
    new_sha = sha256_file(old_path)
    with L.tx():
        L.db.execute("INSERT INTO strategy_changes (logged_at, from_version, to_version, from_sha256, to_sha256, effective_session, description, evidence) "
                     "VALUES (?,?,?,?,?,?,?,?)", (iso(now_utc()), old_cfg.get("version"), new_cfg.get("version"),
                                                  last["to_sha256"] if last else e["strategy_sha256"], new_sha, a.effective or "next decision",
                                                  a.description, a.evidence))
        L.event("strategy_change", {"book": a.book, "to_sha256": new_sha, "description": a.description})
        L.set_state("strategy_integrity_ok", True)
    with open(ROOT / "CHANGELOG.md", "a") as f:
        f.write(f"\n## {iso(now_utc())} — {a.book}: {old_cfg.get('version')} → {new_cfg.get('version')}\n\n{a.description}\n\nEvidence: {a.evidence}\n")
    print(f"logged change for {a.book}: {prev_sha[:12]} → {new_sha[:12]}")


def main() -> None:
    ensure_dirs()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("freeze").set_defaults(fn=cmd_freeze)
    c = sub.add_parser("cycle")
    c.add_argument("--trigger", default="manual")
    c.set_defaults(fn=cmd_cycle)
    sub.add_parser("status").set_defaults(fn=cmd_status)
    s = sub.add_parser("serve")
    s.add_argument("--port", type=int, default=8765)
    s.set_defaults(fn=cmd_serve)
    sub.add_parser("export").set_defaults(fn=cmd_export)
    sub.add_parser("verify").set_defaults(fn=cmd_verify)
    r = sub.add_parser("report")
    r.add_argument("--day", type=int, required=True)
    r.add_argument("--preview", action="store_true")
    r.set_defaults(fn=cmd_report)
    sub.add_parser("backtest").set_defaults(fn=cmd_backtest)
    lc = sub.add_parser("log-change")
    lc.add_argument("--book", required=True)
    lc.add_argument("--new-config", required=True)
    lc.add_argument("--description", required=True)
    lc.add_argument("--evidence", required=True)
    lc.add_argument("--effective")
    lc.set_defaults(fn=cmd_log_change)
    a = ap.parse_args()
    from papertrader.config import LIVE_RUNTIME, is_live_copy
    if a.cmd in ("freeze", "cycle", "serve", "log-change") and not is_live_copy():
        sys.exit(f"This is the development copy. The live experiment runs from:\n  {LIVE_RUNTIME}\n"
                 "Use the Paper Trader app, or run that copy's run.py.")
    a.fn(a)


if __name__ == "__main__":
    main()
