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
INSERT INTO "decisions" VALUES(1,'2026-10-05:000:trend:EFA:TREND_BUY','20261005T082513Z-trend','2026-10-05T08:25:13Z','2026-10-02','2026-10-05','EFA','trend','BUY','TREND_BUY','month-end trend rebalance; EFA: above [8, 10, 12]-month averages','{"value": 19.8, "close": 103.95999908447266, "above_sma_months": [8, 10, 12], "weight_fraction": 1.0}','[]');
INSERT INTO "decisions" VALUES(2,'2026-10-05:001:trend:SHY:TREND_BUY','20261005T082513Z-trend','2026-10-05T08:25:13Z','2026-10-02','2026-10-05','SHY','trend','BUY','TREND_BUY','month-end trend rebalance; SHY: unallocated capital held in short-term Treasuries','{"value": 59.4}','[]');
INSERT INTO "decisions" VALUES(3,'2026-10-05:002:trend:SPY:TREND_BUY','20261005T082513Z-trend','2026-10-05T08:25:13Z','2026-10-02','2026-10-05','SPY','trend','BUY','TREND_BUY','month-end trend rebalance; SPY: above [8, 10, 12]-month averages','{"value": 19.8, "close": 769.6400146484375, "above_sma_months": [8, 10, 12], "weight_fraction": 1.0}','[]');
INSERT INTO "decisions" VALUES(4,'decide:2026-10-05','20261005T082513Z-trend','2026-10-05T08:25:13Z','2026-10-02','2026-10-05','*','system','INFO','DECIDED','3 orders (MOO) for 2026-10-05; rebalance=True; trend weights SPY 20%, EFA 20%','{"rebalance": true, "order_type": "MOO", "data_through": "2026-10-02", "detail": {"SPY": {"close": 769.6400146484375, "above_sma_months": [8, 10, 12], "weight_fraction": 1.0}, "EFA": {"close": 103.95999908447266, "above_sma_months": [8, 10, 12], "weight_fraction": 1.0}, "IEF": {"close": 89.05000305175781, "above_sma_months": [], "weight_fraction": 0.0}, "GLD": {"close": 380.1400146484375, "above_sma_months": [], "weight_fraction": 0.0}, "VNQ": {"close": 89.5, "above_sma_months": [], "weight_fraction": 0.0}}, "halted": false}','[]');
CREATE TABLE dividends (
  ticker TEXT NOT NULL, ex_date TEXT NOT NULL, per_share REAL NOT NULL, qty REAL NOT NULL,
  amount REAL NOT NULL, recorded_at TEXT NOT NULL, PRIMARY KEY (ticker, ex_date)
);
CREATE TABLE events (
  seq INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT NOT NULL, run_id TEXT, kind TEXT NOT NULL,
  payload TEXT NOT NULL, prev_hash TEXT NOT NULL, hash TEXT NOT NULL
);
INSERT INTO "events" VALUES(1,'2026-10-05T08:23:55Z',NULL,'freeze','{"book": "trend", "end": "2026-10-22", "start": "2026-10-05", "strategy_sha256": "7ca9ab6e33f01b928a7edd3f963091f363563fc20b6c2aba8617cc23587f4d8e", "universe_sha256": "172ba39de91f49af21ee2539df0b42cd5d6aa9c7afbd426114cb33bba2c27afa", "version": "trend-1.0.0"}','GENESIS','64144c54c34c3d5e045d4a445799bc88a55cbd88332daa414e676bce337f8e5d');
INSERT INTO "events" VALUES(2,'2026-10-05T08:25:21Z','20261005T082513Z-trend','decision','{"action": "BUY", "code": "TREND_BUY", "key": "2026-10-05:000:trend:EFA:TREND_BUY", "reason": "month-end trend rebalance; EFA: above [8, 10, 12]-month averages", "ticker": "EFA"}','64144c54c34c3d5e045d4a445799bc88a55cbd88332daa414e676bce337f8e5d','527a0772dcf39531e0fbd18e782e9448677a0b55055830caf28c7bbfe732317b');
INSERT INTO "events" VALUES(3,'2026-10-05T08:25:21Z','20261005T082513Z-trend','decision','{"action": "BUY", "code": "TREND_BUY", "key": "2026-10-05:001:trend:SHY:TREND_BUY", "reason": "month-end trend rebalance; SHY: unallocated capital held in short-term Treasuries", "ticker": "SHY"}','527a0772dcf39531e0fbd18e782e9448677a0b55055830caf28c7bbfe732317b','eb2a8c465479c55e101bbc00e4a227574bfd9b403124c7fa5664c74b252ba600');
INSERT INTO "events" VALUES(4,'2026-10-05T08:25:21Z','20261005T082513Z-trend','decision','{"action": "BUY", "code": "TREND_BUY", "key": "2026-10-05:002:trend:SPY:TREND_BUY", "reason": "month-end trend rebalance; SPY: above [8, 10, 12]-month averages", "ticker": "SPY"}','eb2a8c465479c55e101bbc00e4a227574bfd9b403124c7fa5664c74b252ba600','2b1ebf9da66596d07266613d79d988de01ca80391138368dfce941f7d38af333');
INSERT INTO "events" VALUES(5,'2026-10-05T08:25:21Z','20261005T082513Z-trend','order','{"key": "2026-10-05:trend:EFA:BUY:TREND_BUY", "notional": 19.701, "qty": null, "reason": "month-end trend rebalance; EFA: above [8, 10, 12]-month averages", "session": "2026-10-05", "side": "BUY", "ticker": "EFA", "type": "MOO"}','2b1ebf9da66596d07266613d79d988de01ca80391138368dfce941f7d38af333','460700a4a12066bae6e5d98f4e2f44561af17c2a396fba97d75a366e09119f26');
INSERT INTO "events" VALUES(6,'2026-10-05T08:25:21Z','20261005T082513Z-trend','order','{"key": "2026-10-05:trend:SHY:BUY:TREND_BUY", "notional": 59.103, "qty": null, "reason": "month-end trend rebalance; SHY: unallocated capital held in short-term Treasuries", "session": "2026-10-05", "side": "BUY", "ticker": "SHY", "type": "MOO"}','460700a4a12066bae6e5d98f4e2f44561af17c2a396fba97d75a366e09119f26','e220ef2ac2148e4cb3325efc970adea4ee399200338e29b1f45fe666f5173e91');
INSERT INTO "events" VALUES(7,'2026-10-05T08:25:21Z','20261005T082513Z-trend','order','{"key": "2026-10-05:trend:SPY:BUY:TREND_BUY", "notional": 19.701, "qty": null, "reason": "month-end trend rebalance; SPY: above [8, 10, 12]-month averages", "session": "2026-10-05", "side": "BUY", "ticker": "SPY", "type": "MOO"}','e220ef2ac2148e4cb3325efc970adea4ee399200338e29b1f45fe666f5173e91','3d9f5715c53d9a7b4bff098b27cf32dc8961040ef9960e1e950d2fbb27c59699');
INSERT INTO "events" VALUES(8,'2026-10-05T08:25:21Z','20261005T082513Z-trend','decision','{"action": "INFO", "code": "DECIDED", "key": "decide:2026-10-05", "reason": "3 orders (MOO) for 2026-10-05; rebalance=True; trend weights SPY 20%, EFA 20%", "ticker": "*"}','3d9f5715c53d9a7b4bff098b27cf32dc8961040ef9960e1e950d2fbb27c59699','7c65e58093367a29c2466e35b2f9d5dde1a4cede4ba4dbe86080908ae64189b8');
CREATE TABLE experiment (
  id INTEGER PRIMARY KEY CHECK (id = 1),
  frozen_at TEXT NOT NULL, start_date TEXT NOT NULL, end_date TEXT NOT NULL,
  starting_cash REAL NOT NULL, strategy_version TEXT NOT NULL,
  strategy_sha256 TEXT NOT NULL, universe_sha256 TEXT NOT NULL, report_days TEXT NOT NULL, notes TEXT
);
INSERT INTO "experiment" VALUES(1,'2026-10-05T08:23:55Z','2026-10-05','2026-10-22',100.0,'trend-1.0.0','7ca9ab6e33f01b928a7edd3f963091f363563fc20b6c2aba8617cc23587f4d8e','172ba39de91f49af21ee2539df0b42cd5d6aa9c7afbd426114cb33bba2c27afa','[7, 14, 21, 28, 30]','book=trend; strategy=config/strategy_trend_v1.json');
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
INSERT INTO "orders" VALUES('2026-10-05:trend:EFA:BUY:TREND_BUY','2026-10-05T08:25:13Z','20261005T082513Z-trend','EFA','BUY','MOO','2026-10-05','residual',19.701,NULL,50,'TREND_BUY','month-end trend rebalance; EFA: above [8, 10, 12]-month averages','{}','{}','OPEN',NULL,'2026-10-05T08:25:21Z');
INSERT INTO "orders" VALUES('2026-10-05:trend:SHY:BUY:TREND_BUY','2026-10-05T08:25:13Z','20261005T082513Z-trend','SHY','BUY','MOO','2026-10-05','residual',59.103,NULL,50,'TREND_BUY','month-end trend rebalance; SHY: unallocated capital held in short-term Treasuries','{}','{}','OPEN',NULL,'2026-10-05T08:25:21Z');
INSERT INTO "orders" VALUES('2026-10-05:trend:SPY:BUY:TREND_BUY','2026-10-05T08:25:13Z','20261005T082513Z-trend','SPY','BUY','MOO','2026-10-05','residual',19.701,NULL,50,'TREND_BUY','month-end trend rebalance; SPY: above [8, 10, 12]-month averages','{}','{}','OPEN',NULL,'2026-10-05T08:25:21Z');
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
INSERT INTO "runs" VALUES('20261005T082513Z-trend','2026-10-05T08:25:20Z','2026-10-05T08:25:21Z','OK','github-actions','decided for 2026-10-05: 3 orders (MOO), rebalance=True',NULL);
INSERT INTO "runs" VALUES('20261005T084604Z-trend','2026-10-05T08:46:10Z','2026-10-05T08:46:10Z','OK','github-actions','no action needed',NULL);
CREATE TABLE snapshots (
  session TEXT PRIMARY KEY, created_at TEXT NOT NULL, run_id TEXT, equity REAL NOT NULL,
  cash REAL NOT NULL, positions_value REAL NOT NULL, spy_bh_equity REAL, cash_bh_equity REAL,
  peak REAL NOT NULL, drawdown REAL NOT NULL, regime TEXT, risk_state TEXT, marks TEXT, holdings TEXT
);
CREATE TABLE state (key TEXT PRIMARY KEY, value TEXT NOT NULL, updated_at TEXT NOT NULL);
INSERT INTO "state" VALUES('cash','100.0','2026-10-05T08:23:55Z');
INSERT INTO "state" VALUES('strategy_integrity_ok','true','2026-10-05T08:46:10Z');
INSERT INTO "state" VALUES('last_regime','"TREND"','2026-10-05T08:25:21Z');
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
INSERT INTO "sqlite_sequence" VALUES('events',8);
INSERT INTO "sqlite_sequence" VALUES('decisions',4);
COMMIT;
