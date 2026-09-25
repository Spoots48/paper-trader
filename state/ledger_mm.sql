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
INSERT INTO "decisions" VALUES(1,'mm:quote:2026-09-25T20:26:49Z','20260925T202649Z-mm','2026-09-25T20:26:49Z','2026-09-25T20:26:49Z','2026-09-25','*','predmarket','INFO','MM_QUOTES','quoted 0 market(s): btc-updown-15m-1790367300: 79% elapsed, not quoting; bitcoin-up-or-down-september-25-2026-4pm-et: best bids 0.66+0.33 leave no room under $1; eth-updown-15m-1790367300: 79% elapsed, not quoting; ethereum-up-or-down-september-25-2026-4pm-et: best bids 0.59+0.4 leave no room under $1','{"notes": ["btc-updown-15m-1790367300: 79% elapsed, not quoting", "bitcoin-up-or-down-september-25-2026-4pm-et: best bids 0.66+0.33 leave no room under $1", "eth-updown-15m-1790367300: 79% elapsed, not quoting", "ethereum-up-or-down-september-25-2026-4pm-et: best bids 0.59+0.4 leave no room under $1"]}','[]');
INSERT INTO "decisions" VALUES(2,'mm:quote:2026-09-25T20:36:11Z','20260925T203611Z-mm','2026-09-25T20:36:11Z','2026-09-25T20:36:11Z','2026-09-25','*','predmarket','INFO','MM_QUOTES','quoted 0 market(s): btc-updown-15m-1790368200: best bids 0.56+0.43 leave no room under $1; bitcoin-up-or-down-september-25-2026-4pm-et: 60% elapsed, not quoting; eth-updown-15m-1790368200: best bids 0.4+0.59 leave no room under $1; ethereum-up-or-down-september-25-2026-4pm-et: 60% elapsed, not quoting','{"notes": ["btc-updown-15m-1790368200: best bids 0.56+0.43 leave no room under $1", "bitcoin-up-or-down-september-25-2026-4pm-et: 60% elapsed, not quoting", "eth-updown-15m-1790368200: best bids 0.4+0.59 leave no room under $1", "ethereum-up-or-down-september-25-2026-4pm-et: 60% elapsed, not quoting"]}','[]');
INSERT INTO "decisions" VALUES(3,'mm:quote:2026-09-25T20:43:59Z','20260925T204359Z-mm','2026-09-25T20:43:59Z','2026-09-25T20:43:59Z','2026-09-25','*','predmarket','INFO','MM_QUOTES','quoted 0 market(s): btc-updown-15m-1790368200: 93% elapsed, not quoting; bitcoin-up-or-down-september-25-2026-4pm-et: 73% elapsed, not quoting; eth-updown-15m-1790368200: 93% elapsed, not quoting; ethereum-up-or-down-september-25-2026-4pm-et: 73% elapsed, not quoting','{"notes": ["btc-updown-15m-1790368200: 93% elapsed, not quoting", "bitcoin-up-or-down-september-25-2026-4pm-et: 73% elapsed, not quoting", "eth-updown-15m-1790368200: 93% elapsed, not quoting", "ethereum-up-or-down-september-25-2026-4pm-et: 73% elapsed, not quoting"]}','[]');
INSERT INTO "decisions" VALUES(4,'mm:quote:2026-09-25T23:13:53Z','20260925T231353Z-mm','2026-09-25T23:13:53Z','2026-09-25T23:13:53Z','2026-09-25','*','predmarket','INFO','MM_QUOTES','quoted 0 market(s): btc-updown-15m-1790377200: 93% elapsed, not quoting; bitcoin-up-or-down-september-25-2026-7pm-et: best bids 0.4+0.59 leave no room under $1; eth-updown-15m-1790377200: 93% elapsed, not quoting; ethereum-up-or-down-september-25-2026-7pm-et: best bids 0.64+0.35 leave no room under $1','{"notes": ["btc-updown-15m-1790377200: 93% elapsed, not quoting", "bitcoin-up-or-down-september-25-2026-7pm-et: best bids 0.4+0.59 leave no room under $1", "eth-updown-15m-1790377200: 93% elapsed, not quoting", "ethereum-up-or-down-september-25-2026-7pm-et: best bids 0.64+0.35 leave no room under $1"]}','[]');
INSERT INTO "decisions" VALUES(5,'mm:quote:2026-09-25T23:28:53Z','20260925T232853Z-mm','2026-09-25T23:28:53Z','2026-09-25T23:28:53Z','2026-09-25','*','predmarket','INFO','MM_QUOTES','quoted 0 market(s): btc-updown-15m-1790378100: 93% elapsed, not quoting; bitcoin-up-or-down-september-25-2026-7pm-et: best bids 0.47+0.52 leave no room under $1; eth-updown-15m-1790378100: 93% elapsed, not quoting; ethereum-up-or-down-september-25-2026-7pm-et: best bids 0.6+0.39 leave no room under $1','{"notes": ["btc-updown-15m-1790378100: 93% elapsed, not quoting", "bitcoin-up-or-down-september-25-2026-7pm-et: best bids 0.47+0.52 leave no room under $1", "eth-updown-15m-1790378100: 93% elapsed, not quoting", "ethereum-up-or-down-september-25-2026-7pm-et: best bids 0.6+0.39 leave no room under $1"]}','[]');
CREATE TABLE dividends (
  ticker TEXT NOT NULL, ex_date TEXT NOT NULL, per_share REAL NOT NULL, qty REAL NOT NULL,
  amount REAL NOT NULL, recorded_at TEXT NOT NULL, PRIMARY KEY (ticker, ex_date)
);
CREATE TABLE events (
  seq INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT NOT NULL, run_id TEXT, kind TEXT NOT NULL,
  payload TEXT NOT NULL, prev_hash TEXT NOT NULL, hash TEXT NOT NULL
);
INSERT INTO "events" VALUES(1,'2026-09-25T20:26:19Z',NULL,'freeze','{"book": "mm", "end": "2026-10-22", "start": "2026-09-25", "strategy_sha256": "389313b22ae633d70f0881a8b34067458eb84ec5fac14d02d970b801dc3bc6de", "universe_sha256": "172ba39de91f49af21ee2539df0b42cd5d6aa9c7afbd426114cb33bba2c27afa", "version": "mm-1.0.0"}','GENESIS','dddec3dfe86b1d0ece911c2525c605b6a2c0bdfdb4144e2315eb8aa2bd610176');
INSERT INTO "events" VALUES(2,'2026-09-25T20:26:55Z','20260925T202649Z-mm','decision','{"action": "INFO", "code": "MM_QUOTES", "key": "mm:quote:2026-09-25T20:26:49Z", "reason": "quoted 0 market(s): btc-updown-15m-1790367300: 79% elapsed, not quoting; bitcoin-up-or-down-september-25-2026-4pm-et: best bids 0.66+0.33 leave no room under $1; eth-updown-15m-1790367300: 79% elapsed, not quoting; ethereum-up-or-down-september-25-2026-4pm-et: best bids 0.59+0.4 leave no room under $1", "ticker": "*"}','dddec3dfe86b1d0ece911c2525c605b6a2c0bdfdb4144e2315eb8aa2bd610176','4b9d3f69d6ec5fbadb486a0c81deec6bc8b289b9fb01752ee4ad24baeea7c990');
INSERT INTO "events" VALUES(3,'2026-09-25T20:36:17Z','20260925T203611Z-mm','decision','{"action": "INFO", "code": "MM_QUOTES", "key": "mm:quote:2026-09-25T20:36:11Z", "reason": "quoted 0 market(s): btc-updown-15m-1790368200: best bids 0.56+0.43 leave no room under $1; bitcoin-up-or-down-september-25-2026-4pm-et: 60% elapsed, not quoting; eth-updown-15m-1790368200: best bids 0.4+0.59 leave no room under $1; ethereum-up-or-down-september-25-2026-4pm-et: 60% elapsed, not quoting", "ticker": "*"}','4b9d3f69d6ec5fbadb486a0c81deec6bc8b289b9fb01752ee4ad24baeea7c990','20caa06229c23e78efd8f356aba29ea84da2660c13341fdce422dc00db0c461d');
INSERT INTO "events" VALUES(4,'2026-09-25T20:44:05Z','20260925T204359Z-mm','decision','{"action": "INFO", "code": "MM_QUOTES", "key": "mm:quote:2026-09-25T20:43:59Z", "reason": "quoted 0 market(s): btc-updown-15m-1790368200: 93% elapsed, not quoting; bitcoin-up-or-down-september-25-2026-4pm-et: 73% elapsed, not quoting; eth-updown-15m-1790368200: 93% elapsed, not quoting; ethereum-up-or-down-september-25-2026-4pm-et: 73% elapsed, not quoting", "ticker": "*"}','20caa06229c23e78efd8f356aba29ea84da2660c13341fdce422dc00db0c461d','9e4f4e84bd39cd36de621059addb1c3d8299600f315105f57cb5cd267eed7300');
INSERT INTO "events" VALUES(5,'2026-09-25T23:13:58Z','20260925T231353Z-mm','decision','{"action": "INFO", "code": "MM_QUOTES", "key": "mm:quote:2026-09-25T23:13:53Z", "reason": "quoted 0 market(s): btc-updown-15m-1790377200: 93% elapsed, not quoting; bitcoin-up-or-down-september-25-2026-7pm-et: best bids 0.4+0.59 leave no room under $1; eth-updown-15m-1790377200: 93% elapsed, not quoting; ethereum-up-or-down-september-25-2026-7pm-et: best bids 0.64+0.35 leave no room under $1", "ticker": "*"}','9e4f4e84bd39cd36de621059addb1c3d8299600f315105f57cb5cd267eed7300','e4cb9b6b3495f172780574e113b144da6aa4e43b5a323de7433054c9e7a9a67f');
INSERT INTO "events" VALUES(6,'2026-09-25T23:28:58Z','20260925T232853Z-mm','decision','{"action": "INFO", "code": "MM_QUOTES", "key": "mm:quote:2026-09-25T23:28:53Z", "reason": "quoted 0 market(s): btc-updown-15m-1790378100: 93% elapsed, not quoting; bitcoin-up-or-down-september-25-2026-7pm-et: best bids 0.47+0.52 leave no room under $1; eth-updown-15m-1790378100: 93% elapsed, not quoting; ethereum-up-or-down-september-25-2026-7pm-et: best bids 0.6+0.39 leave no room under $1", "ticker": "*"}','e4cb9b6b3495f172780574e113b144da6aa4e43b5a323de7433054c9e7a9a67f','03df190b8a1a54276acf716ee5cbc9ff46084adb3aa4eeeec6c65fa588e19ab5');
CREATE TABLE experiment (
  id INTEGER PRIMARY KEY CHECK (id = 1),
  frozen_at TEXT NOT NULL, start_date TEXT NOT NULL, end_date TEXT NOT NULL,
  starting_cash REAL NOT NULL, strategy_version TEXT NOT NULL,
  strategy_sha256 TEXT NOT NULL, universe_sha256 TEXT NOT NULL, report_days TEXT NOT NULL, notes TEXT
);
INSERT INTO "experiment" VALUES(1,'2026-09-25T20:26:19Z','2026-09-25','2026-10-22',100.0,'mm-1.0.0','389313b22ae633d70f0881a8b34067458eb84ec5fac14d02d970b801dc3bc6de','172ba39de91f49af21ee2539df0b42cd5d6aa9c7afbd426114cb33bba2c27afa','[7, 14, 21, 28, 30]','book=mm; strategy=config/strategy_mm_v1.json');
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
INSERT INTO "runs" VALUES('20260925T202649Z-mm','2026-09-25T20:26:54Z','2026-09-25T20:26:55Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260925T203611Z-mm','2026-09-25T20:36:16Z','2026-09-25T20:36:17Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260925T204359Z-mm','2026-09-25T20:44:04Z','2026-09-25T20:44:05Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260925T231353Z-mm','2026-09-25T23:13:57Z','2026-09-25T23:13:58Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260925T232853Z-mm','2026-09-25T23:28:57Z','2026-09-25T23:28:58Z','OK','github-actions','no action needed',NULL);
CREATE TABLE snapshots (
  session TEXT PRIMARY KEY, created_at TEXT NOT NULL, run_id TEXT, equity REAL NOT NULL,
  cash REAL NOT NULL, positions_value REAL NOT NULL, spy_bh_equity REAL, cash_bh_equity REAL,
  peak REAL NOT NULL, drawdown REAL NOT NULL, regime TEXT, risk_state TEXT, marks TEXT, holdings TEXT
);
CREATE TABLE state (key TEXT PRIMARY KEY, value TEXT NOT NULL, updated_at TEXT NOT NULL);
INSERT INTO "state" VALUES('cash','100.0','2026-09-25T20:26:19Z');
INSERT INTO "state" VALUES('strategy_integrity_ok','true','2026-09-25T23:28:57Z');
INSERT INTO "state" VALUES('mm_orders','[]','2026-09-25T23:28:57Z');
INSERT INTO "state" VALUES('risk','{"peak": 100.0, "drawdown": 0.0}','2026-09-25T23:28:57Z');
INSERT INTO "state" VALUES('pm_day','{"date": "2026-09-25", "start_equity": 100.0}','2026-09-25T23:28:57Z');
INSERT INTO "state" VALUES('pm_positions','{}','2026-09-25T23:28:58Z');
INSERT INTO "state" VALUES('live_marks','{"as_of": "2026-09-25T23:28:53Z", "marks": {}}','2026-09-25T23:28:58Z');
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
INSERT INTO "sqlite_sequence" VALUES('events',6);
INSERT INTO "sqlite_sequence" VALUES('decisions',5);
COMMIT;
