"""Persistent SQLite ledger for the live paper-trading experiment.

Integrity guarantees:
  * Results tables (fills, snapshots, decisions, news, events, dividends,
    strategy_changes) are append-only: SQLite triggers abort UPDATE/DELETE.
  * Orders can change status, but their economic fields are immutable.
  * Every material write is also appended to `events`, a SHA-256 hash chain,
    so edits to the history are detectable with `run.py verify`.
  * Order keys and fill order-keys are UNIQUE, so a retried job can't
    create duplicate orders or duplicate fills.
"""
from __future__ import annotations

import contextlib
import hashlib
import json
import sqlite3
from pathlib import Path

from .broker import Fill, Order, Portfolio, Position
from .nyse_calendar import iso, now_utc

SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS experiment (
  id INTEGER PRIMARY KEY CHECK (id = 1),
  frozen_at TEXT NOT NULL, start_date TEXT NOT NULL, end_date TEXT NOT NULL,
  starting_cash REAL NOT NULL, strategy_version TEXT NOT NULL,
  strategy_sha256 TEXT NOT NULL, universe_sha256 TEXT NOT NULL, report_days TEXT NOT NULL, notes TEXT
);
CREATE TABLE IF NOT EXISTS state (key TEXT PRIMARY KEY, value TEXT NOT NULL, updated_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS runs (
  run_id TEXT PRIMARY KEY, started_at TEXT NOT NULL, finished_at TEXT, status TEXT NOT NULL,
  trigger TEXT, summary TEXT, error TEXT
);
CREATE TABLE IF NOT EXISTS orders (
  order_key TEXT PRIMARY KEY, created_at TEXT NOT NULL, run_id TEXT, ticker TEXT NOT NULL,
  side TEXT NOT NULL, order_type TEXT NOT NULL, session TEXT NOT NULL, sleeve TEXT NOT NULL,
  notional REAL, qty REAL, priority INTEGER, reason_code TEXT, reason TEXT,
  entry_params TEXT, meta TEXT,
  status TEXT NOT NULL DEFAULT 'OPEN', status_reason TEXT, updated_at TEXT
);
CREATE TABLE IF NOT EXISTS fills (
  fill_id INTEGER PRIMARY KEY AUTOINCREMENT, order_key TEXT NOT NULL UNIQUE, run_id TEXT,
  recorded_at TEXT NOT NULL, session TEXT NOT NULL, ticker TEXT NOT NULL, side TEXT NOT NULL,
  qty REAL NOT NULL, ref_price REAL NOT NULL, fill_price REAL NOT NULL, cost_bps REAL NOT NULL,
  cost_usd REAL NOT NULL, price_time TEXT NOT NULL, price_source TEXT NOT NULL, sleeve TEXT,
  reason_code TEXT, reason TEXT, realized_pnl REAL
);
CREATE TABLE IF NOT EXISTS positions (
  ticker TEXT PRIMARY KEY, qty REAL NOT NULL, avg_cost REAL NOT NULL, sleeve TEXT NOT NULL,
  entry_session TEXT NOT NULL, entry_price REAL NOT NULL, initial_stop REAL, trail_pct REAL,
  high_water REAL NOT NULL, max_hold_until TEXT, stop_checked_through TEXT, meta TEXT
);
CREATE TABLE IF NOT EXISTS decisions (
  decision_id INTEGER PRIMARY KEY AUTOINCREMENT, decision_key TEXT NOT NULL UNIQUE, run_id TEXT,
  created_at TEXT NOT NULL, data_through TEXT NOT NULL, session TEXT NOT NULL, ticker TEXT NOT NULL,
  sleeve TEXT, action TEXT NOT NULL, reason_code TEXT, reason TEXT, metrics TEXT, news_ids TEXT
);
CREATE TABLE IF NOT EXISTS snapshots (
  session TEXT PRIMARY KEY, created_at TEXT NOT NULL, run_id TEXT, equity REAL NOT NULL,
  cash REAL NOT NULL, positions_value REAL NOT NULL, spy_bh_equity REAL, cash_bh_equity REAL,
  peak REAL NOT NULL, drawdown REAL NOT NULL, regime TEXT, risk_state TEXT, marks TEXT, holdings TEXT
);
CREATE TABLE IF NOT EXISTS news (
  news_id INTEGER PRIMARY KEY AUTOINCREMENT, uid TEXT NOT NULL UNIQUE, ticker TEXT NOT NULL,
  source TEXT NOT NULL, provider TEXT, title TEXT NOT NULL, url TEXT, published_at TEXT,
  retrieved_at TEXT NOT NULL, categories TEXT, matched TEXT
);
CREATE TABLE IF NOT EXISTS dividends (
  ticker TEXT NOT NULL, ex_date TEXT NOT NULL, per_share REAL NOT NULL, qty REAL NOT NULL,
  amount REAL NOT NULL, recorded_at TEXT NOT NULL, PRIMARY KEY (ticker, ex_date)
);
CREATE TABLE IF NOT EXISTS data_issues (
  id INTEGER PRIMARY KEY AUTOINCREMENT, occurred_at TEXT NOT NULL, run_id TEXT, severity TEXT NOT NULL,
  component TEXT NOT NULL, ticker TEXT, message TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS reports (
  report_key TEXT PRIMARY KEY, day_number INTEGER NOT NULL, report_date TEXT NOT NULL,
  as_of_session TEXT NOT NULL, generated_at TEXT NOT NULL, path_md TEXT NOT NULL, path_html TEXT NOT NULL,
  late_by_hours REAL, notified INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS strategy_changes (
  id INTEGER PRIMARY KEY AUTOINCREMENT, logged_at TEXT NOT NULL, from_version TEXT, to_version TEXT,
  from_sha256 TEXT, to_sha256 TEXT, effective_session TEXT, description TEXT NOT NULL, evidence TEXT
);
CREATE TABLE IF NOT EXISTS events (
  seq INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT NOT NULL, run_id TEXT, kind TEXT NOT NULL,
  payload TEXT NOT NULL, prev_hash TEXT NOT NULL, hash TEXT NOT NULL
);
"""

APPEND_ONLY = ["fills", "snapshots", "decisions", "news", "events", "dividends", "strategy_changes", "experiment"]


def _triggers() -> str:
    out = []
    for t in APPEND_ONLY:
        out.append(f"CREATE TRIGGER IF NOT EXISTS {t}_no_update BEFORE UPDATE ON {t} "
                   f"BEGIN SELECT RAISE(ABORT, '{t} is append-only'); END;")
        out.append(f"CREATE TRIGGER IF NOT EXISTS {t}_no_delete BEFORE DELETE ON {t} "
                   f"BEGIN SELECT RAISE(ABORT, '{t} is append-only'); END;")
    out.append("CREATE TRIGGER IF NOT EXISTS orders_economics_immutable BEFORE UPDATE OF "
               "order_key, created_at, ticker, side, order_type, session, notional, qty, sleeve ON orders "
               "BEGIN SELECT RAISE(ABORT, 'order economics are immutable'); END;")
    out.append("CREATE TRIGGER IF NOT EXISTS orders_no_delete BEFORE DELETE ON orders "
               "BEGIN SELECT RAISE(ABORT, 'orders cannot be deleted'); END;")
    return "\n".join(out)


def _hash(prev: str, ts: str, kind: str, payload: str) -> str:
    return hashlib.sha256(f"{prev}|{ts}|{kind}|{payload}".encode()).hexdigest()


class Ledger:
    def __init__(self, path: Path):
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(str(path), timeout=30, isolation_level=None)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA journal_mode=DELETE")  # safest on removable drives
        self.db.execute("PRAGMA synchronous=FULL")
        self.db.executescript(SCHEMA)
        self.db.executescript(_triggers())
        self.run_id: str | None = None

    def close(self) -> None:
        self.db.close()

    @contextlib.contextmanager
    def tx(self):
        self.db.execute("BEGIN IMMEDIATE")
        try:
            yield self.db
            self.db.execute("COMMIT")
        except BaseException:
            self.db.execute("ROLLBACK")
            raise

    # ---- audit chain -------------------------------------------------------------
    def event(self, kind: str, payload: dict) -> None:
        row = self.db.execute("SELECT hash FROM events ORDER BY seq DESC LIMIT 1").fetchone()
        prev = row["hash"] if row else "GENESIS"
        ts = iso(now_utc())
        p = json.dumps(payload, sort_keys=True, default=str)
        self.db.execute("INSERT INTO events (ts, run_id, kind, payload, prev_hash, hash) VALUES (?,?,?,?,?,?)",
                        (ts, self.run_id, kind, p, prev, _hash(prev, ts, kind, p)))

    def verify_chain(self) -> tuple[bool, str]:
        prev = "GENESIS"
        n = 0
        for r in self.db.execute("SELECT * FROM events ORDER BY seq"):
            if r["prev_hash"] != prev or _hash(prev, r["ts"], r["kind"], r["payload"]) != r["hash"]:
                return False, f"hash chain broken at seq {r['seq']}"
            prev = r["hash"]
            n += 1
        return True, f"{n} events verified"

    # ---- state -------------------------------------------------------------------
    def get_state(self, key: str, default=None):
        r = self.db.execute("SELECT value FROM state WHERE key=?", (key,)).fetchone()
        return json.loads(r["value"]) if r else default

    def set_state(self, key: str, value) -> None:
        self.db.execute("INSERT INTO state (key, value, updated_at) VALUES (?,?,?) "
                        "ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at",
                        (key, json.dumps(value, default=str), iso(now_utc())))

    def freeze(self, exp: dict, book: dict, version: str, strategy_sha: str, universe_sha: str) -> None:
        now = iso(now_utc())
        with self.tx():
            self.db.execute("INSERT INTO experiment (id, frozen_at, start_date, end_date, starting_cash, strategy_version, strategy_sha256, "
                            "universe_sha256, report_days, notes) VALUES (1,?,?,?,?,?,?,?,?,?)",
                            (now, exp["start_date"], exp["end_date"], exp["starting_cash"], version, strategy_sha, universe_sha,
                             json.dumps(exp["report_days"]), f"book={book['id']}; strategy={book['strategy']}"))
            self.set_state("cash", exp["starting_cash"])
            self.event("freeze", {"book": book["id"], "strategy_sha256": strategy_sha, "universe_sha256": universe_sha,
                                  "start": exp["start_date"], "end": exp["end_date"], "version": version})

    def experiment(self) -> dict | None:
        r = self.db.execute("SELECT * FROM experiment WHERE id=1").fetchone()
        return dict(r) if r else None

    # ---- runs --------------------------------------------------------------------
    def start_run(self, run_id: str, trigger: str) -> None:
        self.run_id = run_id
        self.db.execute("INSERT INTO runs (run_id, started_at, status, trigger) VALUES (?,?,?,?)",
                        (run_id, iso(now_utc()), "RUNNING", trigger))

    def finish_run(self, status: str, summary: str = "", error: str | None = None) -> None:
        self.db.execute("UPDATE runs SET finished_at=?, status=?, summary=?, error=? WHERE run_id=?",
                        (iso(now_utc()), status, summary, error, self.run_id))

    # ---- issues ------------------------------------------------------------------
    def issue(self, severity: str, component: str, message: str, ticker: str | None = None) -> None:
        self.db.execute("INSERT INTO data_issues (occurred_at, run_id, severity, component, ticker, message) "
                        "VALUES (?,?,?,?,?,?)", (iso(now_utc()), self.run_id, severity, component, ticker, message))

    # ---- orders & fills ----------------------------------------------------------
    def insert_order(self, o: Order) -> bool:
        cur = self.db.execute(
            "INSERT OR IGNORE INTO orders (order_key, created_at, run_id, ticker, side, order_type, session, sleeve, "
            "notional, qty, priority, reason_code, reason, entry_params, meta, status, updated_at) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,'OPEN',?)",
            (o.key, o.created_at, self.run_id, o.ticker, o.side, o.order_type, o.session, o.sleeve, o.notional,
             o.qty, o.priority, o.reason_code, o.reason, json.dumps(o.entry_params, default=str),
             json.dumps(o.meta, default=str), iso(now_utc())))
        if cur.rowcount:
            self.event("order", {"key": o.key, "ticker": o.ticker, "side": o.side, "type": o.order_type,
                                 "session": o.session, "notional": o.notional, "qty": o.qty, "reason": o.reason})
        return bool(cur.rowcount)

    def open_orders(self) -> list[Order]:
        out = []
        for r in self.db.execute("SELECT * FROM orders WHERE status='OPEN' ORDER BY session, priority"):
            out.append(Order(key=r["order_key"], ticker=r["ticker"], side=r["side"], order_type=r["order_type"],
                             session=r["session"], created_at=r["created_at"], sleeve=r["sleeve"],
                             reason_code=r["reason_code"], reason=r["reason"], notional=r["notional"],
                             qty=r["qty"], priority=r["priority"], entry_params=json.loads(r["entry_params"] or "{}"),
                             meta=json.loads(r["meta"] or "{}")))
        return out

    def set_order_status(self, key: str, status: str, reason: str = "") -> None:
        self.db.execute("UPDATE orders SET status=?, status_reason=?, updated_at=? WHERE order_key=?",
                        (status, reason, iso(now_utc()), key))
        self.event("order_status", {"key": key, "status": status, "reason": reason})

    def ensure_order_row(self, key: str, f: Fill, created_at: str) -> None:
        """Stop-triggered sells have no pre-existing order row; create one so every fill has an order."""
        self.db.execute(
            "INSERT OR IGNORE INTO orders (order_key, created_at, run_id, ticker, side, order_type, session, sleeve, "
            "reason_code, reason, status, updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,'OPEN',?)",
            (key, created_at, self.run_id, f.ticker, f.side, "STOP", f.session, f.sleeve, f.reason_code, f.reason,
             iso(now_utc())))

    def has_fill(self, order_key: str) -> bool:
        return self.db.execute("SELECT 1 FROM fills WHERE order_key=?", (order_key,)).fetchone() is not None

    def record_fill(self, f: Fill) -> bool:
        cur = self.db.execute(
            "INSERT OR IGNORE INTO fills (order_key, run_id, recorded_at, session, ticker, side, qty, ref_price, "
            "fill_price, cost_bps, cost_usd, price_time, price_source, sleeve, reason_code, reason, realized_pnl) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (f.order_key, self.run_id, iso(now_utc()), f.session, f.ticker, f.side, f.qty, f.ref_price, f.fill_price,
             f.cost_bps, f.cost_usd, f.price_time, f.price_source, f.sleeve, f.reason_code, f.reason, f.realized_pnl))
        if cur.rowcount:
            self.event("fill", {"key": f.order_key, "ticker": f.ticker, "side": f.side, "qty": f.qty,
                                "fill_price": f.fill_price, "ref_price": f.ref_price, "price_time": f.price_time,
                                "source": f.price_source})
        return bool(cur.rowcount)

    # ---- portfolio ---------------------------------------------------------------
    def load_portfolio(self, starting_cash: float) -> tuple[Portfolio, dict[str, str | None]]:
        cash = self.get_state("cash", starting_cash)
        pf = Portfolio(cash=cash)
        checked = {}
        for r in self.db.execute("SELECT * FROM positions"):
            pf.positions[r["ticker"]] = Position(
                ticker=r["ticker"], qty=r["qty"], avg_cost=r["avg_cost"], sleeve=r["sleeve"],
                entry_session=r["entry_session"], entry_price=r["entry_price"], initial_stop=r["initial_stop"],
                trail_pct=r["trail_pct"], high_water=r["high_water"], max_hold_until=r["max_hold_until"],
                meta=json.loads(r["meta"] or "{}"))
            checked[r["ticker"]] = r["stop_checked_through"]
        return pf, checked

    def save_portfolio(self, pf: Portfolio, checked: dict[str, str | None]) -> None:
        self.set_state("cash", pf.cash)
        self.db.execute("DELETE FROM positions")
        for t, p in pf.positions.items():
            self.db.execute(
                "INSERT INTO positions (ticker, qty, avg_cost, sleeve, entry_session, entry_price, initial_stop, "
                "trail_pct, high_water, max_hold_until, stop_checked_through, meta) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                (t, p.qty, p.avg_cost, p.sleeve, p.entry_session, p.entry_price, p.initial_stop, p.trail_pct,
                 p.high_water, p.max_hold_until, checked.get(t), json.dumps(p.meta, default=str)))

    # ---- decisions, snapshots, news ------------------------------------------------
    def insert_decision(self, key: str, data_through: str, session: str, d, created_at: str) -> None:
        cur = self.db.execute(
            "INSERT OR IGNORE INTO decisions (decision_key, run_id, created_at, data_through, session, ticker, sleeve, "
            "action, reason_code, reason, metrics, news_ids) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            (key, self.run_id, created_at, data_through, session, d.ticker, d.sleeve, d.action, d.reason_code,
             d.reason, json.dumps(d.metrics, default=str), json.dumps(d.news_ids)))
        if cur.rowcount:
            self.event("decision", {"key": key, "ticker": d.ticker, "action": d.action, "code": d.reason_code,
                                    "reason": d.reason})

    def insert_snapshot(self, row: dict) -> bool:
        cols = ", ".join(row)
        q = ", ".join("?" for _ in row)
        cur = self.db.execute(f"INSERT OR IGNORE INTO snapshots ({cols}) VALUES ({q})", tuple(row.values()))
        if cur.rowcount:
            self.event("snapshot", {k: row[k] for k in ("session", "equity", "cash", "drawdown", "spy_bh_equity")})
        return bool(cur.rowcount)

    def snapshots(self) -> list[dict]:
        return [dict(r) for r in self.db.execute("SELECT * FROM snapshots ORDER BY session")]

    def insert_news(self, item: dict) -> int:
        self.db.execute(
            "INSERT OR IGNORE INTO news (uid, ticker, source, provider, title, url, published_at, retrieved_at, "
            "categories, matched) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (item["uid"], item["ticker"], item["source"], item.get("provider"), item["title"], item.get("url"),
             item.get("published_at"), item["retrieved_at"], json.dumps(item.get("categories", [])),
             json.dumps(item.get("matched", []))))
        return self.db.execute("SELECT news_id FROM news WHERE uid=?", (item["uid"],)).fetchone()["news_id"]
