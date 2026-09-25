BEGIN TRANSACTION;
CREATE TABLE data_issues (
  id INTEGER PRIMARY KEY AUTOINCREMENT, occurred_at TEXT NOT NULL, run_id TEXT, severity TEXT NOT NULL,
  component TEXT NOT NULL, ticker TEXT, message TEXT NOT NULL
);
CREATE TABLE decisions (
  decision_id INTEGER PRIMARY KEY AUTOINCREMENT, decision_key TEXT NOT NULL UNIQUE, run_id TEXT,
  created_at TEXT NOT NULL, data_through TEXT NOT NULL, session TEXT NOT NULL, ticker TEXT NOT NULL,
  sleeve TEXT, action TEXT NOT NULL, reason_code TEXT, reason TEXT, metrics TEXT, news_ids TEXT
);
INSERT INTO "decisions" VALUES(1,'pm:scan:2026-09-25T13:14:45Z','20260925T131445Z-crypto','2026-09-25T13:14:45Z','2026-09-25T13:14:45Z','2026-09-25','*','predmarket','INFO','PM_SCAN','scanned 10 live markets; 0 bet(s). Best gaps: btc-updown-4h-1790337600 Down +0.03, xrp-up-or-down-september-25-2026-9am-et Down +0.03, xrp-updown-4h-1790337600 Up +0.02, sol-updown-4h-1790337600 Down +0.01, dogecoin-up-or-down-september-25-2026-9am-et Down +0.00','{"scanned": [{"market": "bitcoin-up-or-down-september-25-2026-9am-et", "p_up": 0.44, "best_side": "Down", "edge": -0.06}, {"market": "btc-updown-4h-1790337600", "p_up": 0.316, "best_side": "Down", "edge": 0.029}, {"market": "ethereum-up-or-down-september-25-2026-9am-et", "p_up": 0.368, "best_side": "Down", "edge": -0.046}, {"market": "eth-updown-4h-1790337600", "p_up": 0.409, "best_side": "Down", "edge": -0.011}, {"market": "solana-up-or-down-september-25-2026-9am-et", "p_up": 0.479, "best_side": "Up", "edge": -0.096}, {"market": "sol-updown-4h-1790337600", "p_up": 0.41, "best_side": "Down", "edge": 0.006}, {"market": "xrp-up-or-down-september-25-2026-9am-et", "p_up": 0.281, "best_side": "Down", "edge": 0.026}, {"market": "xrp-updown-4h-1790337600", "p_up": 0.598, "best_side": "Up", "edge": 0.023}, {"market": "dogecoin-up-or-down-september-25-2026-9am-et", "p_up": 0.272, "best_side": "Down", "edge": 0.001}, {"market": "doge-updown-4h-1790337600", "p_up": 0.621, "best_side": "Up", "edge": -0.006}]}','[]');
CREATE TABLE dividends (
  ticker TEXT NOT NULL, ex_date TEXT NOT NULL, per_share REAL NOT NULL, qty REAL NOT NULL,
  amount REAL NOT NULL, recorded_at TEXT NOT NULL, PRIMARY KEY (ticker, ex_date)
);
CREATE TABLE events (
  seq INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT NOT NULL, run_id TEXT, kind TEXT NOT NULL,
  payload TEXT NOT NULL, prev_hash TEXT NOT NULL, hash TEXT NOT NULL
);
INSERT INTO "events" VALUES(1,'2026-09-25T13:13:46Z',NULL,'freeze','{"book": "crypto", "end": "2026-10-22", "start": "2026-09-25", "strategy_sha256": "25a8a20803d222eeee466b548b1db6c923293e26df5e94960c6f226c70b81217", "universe_sha256": "172ba39de91f49af21ee2539df0b42cd5d6aa9c7afbd426114cb33bba2c27afa", "version": "pm-1.0.0"}','GENESIS','dd6067cbd17c0ed13ee27f3c52db532716941d05ac3d91dbea535b0fc73aae39');
INSERT INTO "events" VALUES(2,'2026-09-25T13:14:50Z','20260925T131445Z-crypto','decision','{"action": "INFO", "code": "PM_SCAN", "key": "pm:scan:2026-09-25T13:14:45Z", "reason": "scanned 10 live markets; 0 bet(s). Best gaps: btc-updown-4h-1790337600 Down +0.03, xrp-up-or-down-september-25-2026-9am-et Down +0.03, xrp-updown-4h-1790337600 Up +0.02, sol-updown-4h-1790337600 Down +0.01, dogecoin-up-or-down-september-25-2026-9am-et Down +0.00", "ticker": "*"}','dd6067cbd17c0ed13ee27f3c52db532716941d05ac3d91dbea535b0fc73aae39','d07731ab1dffe7b3a79ce477737c2929e4c392b1ed672d93c8931c404198c021');
CREATE TABLE experiment (
  id INTEGER PRIMARY KEY CHECK (id = 1),
  frozen_at TEXT NOT NULL, start_date TEXT NOT NULL, end_date TEXT NOT NULL,
  starting_cash REAL NOT NULL, strategy_version TEXT NOT NULL,
  strategy_sha256 TEXT NOT NULL, universe_sha256 TEXT NOT NULL, report_days TEXT NOT NULL, notes TEXT
);
INSERT INTO "experiment" VALUES(1,'2026-09-25T13:13:46Z','2026-09-25','2026-10-22',100.0,'pm-1.0.0','25a8a20803d222eeee466b548b1db6c923293e26df5e94960c6f226c70b81217','172ba39de91f49af21ee2539df0b42cd5d6aa9c7afbd426114cb33bba2c27afa','[7, 14, 21, 28, 30]','book=crypto; strategy=config/strategy_pm_v1.json');
CREATE TABLE fills (
  fill_id INTEGER PRIMARY KEY AUTOINCREMENT, order_key TEXT NOT NULL UNIQUE, run_id TEXT,
  recorded_at TEXT NOT NULL, session TEXT NOT NULL, ticker TEXT NOT NULL, side TEXT NOT NULL,
  qty REAL NOT NULL, ref_price REAL NOT NULL, fill_price REAL NOT NULL, cost_bps REAL NOT NULL,
  cost_usd REAL NOT NULL, price_time TEXT NOT NULL, price_source TEXT NOT NULL, sleeve TEXT,
  reason_code TEXT, reason TEXT, realized_pnl REAL
);
CREATE TABLE news (
  news_id INTEGER PRIMARY KEY AUTOINCREMENT, uid TEXT NOT NULL UNIQUE, ticker TEXT NOT NULL,
  source TEXT NOT NULL, provider TEXT, title TEXT NOT NULL, url TEXT, published_at TEXT,
  retrieved_at TEXT NOT NULL, categories TEXT, matched TEXT
);
CREATE TABLE orders (
  order_key TEXT PRIMARY KEY, created_at TEXT NOT NULL, run_id TEXT, ticker TEXT NOT NULL,
  side TEXT NOT NULL, order_type TEXT NOT NULL, session TEXT NOT NULL, sleeve TEXT NOT NULL,
  notional REAL, qty REAL, priority INTEGER, reason_code TEXT, reason TEXT,
  entry_params TEXT, meta TEXT,
  status TEXT NOT NULL DEFAULT 'OPEN', status_reason TEXT, updated_at TEXT
);
CREATE TABLE positions (
  ticker TEXT PRIMARY KEY, qty REAL NOT NULL, avg_cost REAL NOT NULL, sleeve TEXT NOT NULL,
  entry_session TEXT NOT NULL, entry_price REAL NOT NULL, initial_stop REAL, trail_pct REAL,
  high_water REAL NOT NULL, max_hold_until TEXT, stop_checked_through TEXT, meta TEXT
);
CREATE TABLE reports (
  report_key TEXT PRIMARY KEY, day_number INTEGER NOT NULL, report_date TEXT NOT NULL,
  as_of_session TEXT NOT NULL, generated_at TEXT NOT NULL, path_md TEXT NOT NULL, path_html TEXT NOT NULL,
  late_by_hours REAL, notified INTEGER DEFAULT 0
);
CREATE TABLE runs (
  run_id TEXT PRIMARY KEY, started_at TEXT NOT NULL, finished_at TEXT, status TEXT NOT NULL,
  trigger TEXT, summary TEXT, error TEXT
);
INSERT INTO "runs" VALUES('20260925T131445Z-crypto','2026-09-25T13:14:45Z','2026-09-25T13:14:50Z','OK','github-actions','no action needed',NULL);
CREATE TABLE snapshots (
  session TEXT PRIMARY KEY, created_at TEXT NOT NULL, run_id TEXT, equity REAL NOT NULL,
  cash REAL NOT NULL, positions_value REAL NOT NULL, spy_bh_equity REAL, cash_bh_equity REAL,
  peak REAL NOT NULL, drawdown REAL NOT NULL, regime TEXT, risk_state TEXT, marks TEXT, holdings TEXT
);
CREATE TABLE state (key TEXT PRIMARY KEY, value TEXT NOT NULL, updated_at TEXT NOT NULL);
INSERT INTO "state" VALUES('cash','100.0','2026-09-25T13:13:46Z');
INSERT INTO "state" VALUES('strategy_integrity_ok','true','2026-09-25T13:14:45Z');
INSERT INTO "state" VALUES('pm_positions','{}','2026-09-25T13:14:50Z');
INSERT INTO "state" VALUES('live_marks','{"as_of": "2026-09-25T13:14:45Z", "marks": {}}','2026-09-25T13:14:50Z');
CREATE TABLE strategy_changes (
  id INTEGER PRIMARY KEY AUTOINCREMENT, logged_at TEXT NOT NULL, from_version TEXT, to_version TEXT,
  from_sha256 TEXT, to_sha256 TEXT, effective_session TEXT, description TEXT NOT NULL, evidence TEXT
);
CREATE TRIGGER fills_no_update BEFORE UPDATE ON fills BEGIN SELECT RAISE(ABORT, 'fills is append-only'); END;
CREATE TRIGGER fills_no_delete BEFORE DELETE ON fills BEGIN SELECT RAISE(ABORT, 'fills is append-only'); END;
CREATE TRIGGER snapshots_no_update BEFORE UPDATE ON snapshots BEGIN SELECT RAISE(ABORT, 'snapshots is append-only'); END;
CREATE TRIGGER snapshots_no_delete BEFORE DELETE ON snapshots BEGIN SELECT RAISE(ABORT, 'snapshots is append-only'); END;
CREATE TRIGGER decisions_no_update BEFORE UPDATE ON decisions BEGIN SELECT RAISE(ABORT, 'decisions is append-only'); END;
CREATE TRIGGER decisions_no_delete BEFORE DELETE ON decisions BEGIN SELECT RAISE(ABORT, 'decisions is append-only'); END;
CREATE TRIGGER news_no_update BEFORE UPDATE ON news BEGIN SELECT RAISE(ABORT, 'news is append-only'); END;
CREATE TRIGGER news_no_delete BEFORE DELETE ON news BEGIN SELECT RAISE(ABORT, 'news is append-only'); END;
CREATE TRIGGER events_no_update BEFORE UPDATE ON events BEGIN SELECT RAISE(ABORT, 'events is append-only'); END;
CREATE TRIGGER events_no_delete BEFORE DELETE ON events BEGIN SELECT RAISE(ABORT, 'events is append-only'); END;
CREATE TRIGGER dividends_no_update BEFORE UPDATE ON dividends BEGIN SELECT RAISE(ABORT, 'dividends is append-only'); END;
CREATE TRIGGER dividends_no_delete BEFORE DELETE ON dividends BEGIN SELECT RAISE(ABORT, 'dividends is append-only'); END;
CREATE TRIGGER strategy_changes_no_update BEFORE UPDATE ON strategy_changes BEGIN SELECT RAISE(ABORT, 'strategy_changes is append-only'); END;
CREATE TRIGGER strategy_changes_no_delete BEFORE DELETE ON strategy_changes BEGIN SELECT RAISE(ABORT, 'strategy_changes is append-only'); END;
CREATE TRIGGER experiment_no_update BEFORE UPDATE ON experiment BEGIN SELECT RAISE(ABORT, 'experiment is append-only'); END;
CREATE TRIGGER experiment_no_delete BEFORE DELETE ON experiment BEGIN SELECT RAISE(ABORT, 'experiment is append-only'); END;
CREATE TRIGGER orders_economics_immutable BEFORE UPDATE OF order_key, created_at, ticker, side, order_type, session, notional, qty, sleeve ON orders BEGIN SELECT RAISE(ABORT, 'order economics are immutable'); END;
CREATE TRIGGER orders_no_delete BEFORE DELETE ON orders BEGIN SELECT RAISE(ABORT, 'orders cannot be deleted'); END;
DELETE FROM "sqlite_sequence";
INSERT INTO "sqlite_sequence" VALUES('events',2);
INSERT INTO "sqlite_sequence" VALUES('decisions',1);
COMMIT;
