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
INSERT INTO "decisions" VALUES(1,'2026-09-23:000:residual:SPY:RESIDUAL','20260923T014323Z-primary','2026-09-23T01:43:23Z','2026-09-22','2026-09-23','SPY','residual','BUY','RESIDUAL','invest idle cash (~$98.00) in SPY','{}','[]');
INSERT INTO "decisions" VALUES(2,'decide:2026-09-23','20260923T014323Z-primary','2026-09-23T01:43:23Z','2026-09-22','2026-09-23','*','system','INFO','DECIDED','1 orders (MOO) for 2026-09-23; regime ON; SPY 773.44 vs 200d 717.19; VIX 14.210000038146973; 0 earnings reactions on 2026-09-22; rebalance=True','{"regime": "ON", "spy_close": 773.4400024414062, "spy_sma200": 717.1891497802734, "vix": 14.210000038146973, "order_type": "MOO", "data_through": "2026-09-22", "stock_bars_missing": 0, "risk": {"drawdown": 0.0, "halted": false, "paused": false}, "earnings_events_loaded": 0, "earnings_dates_failed": []}','[]');
INSERT INTO "decisions" VALUES(3,'decide:2026-09-24','20260923T215408Z-primary','2026-09-23T21:54:08Z','2026-09-23','2026-09-24','*','system','INFO','DECIDED','0 orders (MOO) for 2026-09-24; regime ON; SPY 767.81 vs 200d 717.61; VIX 15.180000305175781; 0 earnings reactions on 2026-09-23; rebalance=False','{"regime": "ON", "spy_close": 767.8099975585938, "spy_sma200": 717.6059497070313, "vix": 15.180000305175781, "order_type": "MOO", "data_through": "2026-09-23", "stock_bars_missing": 0, "risk": {"drawdown": 0.006996347709447459, "halted": false, "paused": false}, "earnings_events_loaded": 0, "earnings_dates_failed": []}','[]');
INSERT INTO "decisions" VALUES(4,'decide:2026-09-25','20260924T203813Z-primary','2026-09-24T20:38:13Z','2026-09-24','2026-09-25','*','system','INFO','DECIDED','0 orders (MOO) for 2026-09-25; regime ON; SPY 767.18 vs 200d 718.01; VIX 15.670000076293945; 0 earnings reactions on 2026-09-24; rebalance=False','{"regime": "ON", "spy_close": 767.1799926757812, "spy_sma200": 718.0133996582031, "vix": 15.670000076293945, "order_type": "MOO", "data_through": "2026-09-24", "stock_bars_missing": 0, "risk": {"drawdown": 0.00779471509714269, "halted": false, "paused": false}, "earnings_events_loaded": 0, "earnings_dates_failed": []}','[]');
CREATE TABLE dividends (
  ticker TEXT NOT NULL, ex_date TEXT NOT NULL, per_share REAL NOT NULL, qty REAL NOT NULL,
  amount REAL NOT NULL, recorded_at TEXT NOT NULL, PRIMARY KEY (ticker, ex_date)
);
CREATE TABLE events (
  seq INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT NOT NULL, run_id TEXT, kind TEXT NOT NULL,
  payload TEXT NOT NULL, prev_hash TEXT NOT NULL, hash TEXT NOT NULL
);
INSERT INTO "events" VALUES(1,'2026-09-23T01:43:16Z',NULL,'freeze','{"book": "primary", "end": "2026-10-22", "start": "2026-09-23", "strategy_sha256": "08c6983d1764dc56665bb3914d4da2935023792e0222e96f4ca159c28d602da5", "universe_sha256": "172ba39de91f49af21ee2539df0b42cd5d6aa9c7afbd426114cb33bba2c27afa", "version": "1.0.0-primary"}','GENESIS','bc04d586f0ec3974281c5eb04007285c2cbc45869897f570927f4450d6916440');
INSERT INTO "events" VALUES(2,'2026-09-23T01:43:24Z','20260923T014323Z-primary','decision','{"action": "BUY", "code": "RESIDUAL", "key": "2026-09-23:000:residual:SPY:RESIDUAL", "reason": "invest idle cash (~$98.00) in SPY", "ticker": "SPY"}','bc04d586f0ec3974281c5eb04007285c2cbc45869897f570927f4450d6916440','e3711223c18a795532bbfe17699ded372279267deedbdc68bec2d049901aa4a9');
INSERT INTO "events" VALUES(3,'2026-09-23T01:43:24Z','20260923T014323Z-primary','order','{"key": "2026-09-23:residual:SPY:BUY:RESIDUAL", "notional": null, "qty": null, "reason": "park idle cash in SPY (regime risk-on)", "session": "2026-09-23", "side": "BUY", "ticker": "SPY", "type": "MOO"}','e3711223c18a795532bbfe17699ded372279267deedbdc68bec2d049901aa4a9','6c5225616c10523bc8a996ca6effce06968a5e9c299afc8ca0177471339c7042');
INSERT INTO "events" VALUES(4,'2026-09-23T01:43:24Z','20260923T014323Z-primary','decision','{"action": "INFO", "code": "DECIDED", "key": "decide:2026-09-23", "reason": "1 orders (MOO) for 2026-09-23; regime ON; SPY 773.44 vs 200d 717.19; VIX 14.210000038146973; 0 earnings reactions on 2026-09-22; rebalance=True", "ticker": "*"}','6c5225616c10523bc8a996ca6effce06968a5e9c299afc8ca0177471339c7042','ead499d159a19ae771d8cf431a4b6ef2f395f255c002136ff461303a3738ca18');
INSERT INTO "events" VALUES(5,'2026-09-23T17:50:09Z','20260923T175009Z-primary','benchmark_init','{"entry_price": 773.3309310119628, "qty": 0.12931074652496097}','ead499d159a19ae771d8cf431a4b6ef2f395f255c002136ff461303a3738ca18','a4660b2490d4997d278e0c4aa3e3082318e183c772fc722573d4b2dc4c455f34');
INSERT INTO "events" VALUES(6,'2026-09-23T17:50:09Z','20260923T175009Z-primary','fill','{"fill_price": 773.3309310119628, "key": "2026-09-23:residual:SPY:BUY:RESIDUAL", "price_time": "2026-09-23T09:30:00-04:00 (official open)", "qty": 0.126724, "ref_price": 772.7899780273438, "side": "BUY", "source": "yahoo_daily_open", "ticker": "SPY"}','a4660b2490d4997d278e0c4aa3e3082318e183c772fc722573d4b2dc4c455f34','aac8616dca3bc6eae4001e8660da519b64902ee6a7d28ef238c815beae441d85');
INSERT INTO "events" VALUES(7,'2026-09-23T17:50:09Z','20260923T175009Z-primary','order_status','{"key": "2026-09-23:residual:SPY:BUY:RESIDUAL", "reason": "BUY 0.126724 SPY @ 773.3309", "status": "FILLED"}','aac8616dca3bc6eae4001e8660da519b64902ee6a7d28ef238c815beae441d85','e50c480ba8d125a4545ddf42bd1cc0502b62a881514857ff0bdedc2e08b2a291');
INSERT INTO "events" VALUES(8,'2026-09-23T21:54:11Z','20260923T215408Z-primary','snapshot','{"cash": 2.0004110984400256, "drawdown": 0.006996347709447459, "equity": 99.30036522905526, "session": "2026-09-23", "spy_bh_equity": 99.28608397363021}','e50c480ba8d125a4545ddf42bd1cc0502b62a881514857ff0bdedc2e08b2a291','08afcbab57e5b7ad0c3287ad38325abf9d5e957107fddb91cc9499548e388a17');
INSERT INTO "events" VALUES(9,'2026-09-23T21:54:14Z','20260923T215408Z-primary','decision','{"action": "INFO", "code": "DECIDED", "key": "decide:2026-09-24", "reason": "0 orders (MOO) for 2026-09-24; regime ON; SPY 767.81 vs 200d 717.61; VIX 15.180000305175781; 0 earnings reactions on 2026-09-23; rebalance=False", "ticker": "*"}','08afcbab57e5b7ad0c3287ad38325abf9d5e957107fddb91cc9499548e388a17','fb5195fb5b8edb7edc3de3792c38d80dcea9828c81acf2f0f27f4e359b83cdda');
INSERT INTO "events" VALUES(10,'2026-09-24T20:38:17Z','20260924T203813Z-primary','snapshot','{"cash": 2.0004110984400256, "drawdown": 0.00779471509714269, "equity": 99.22052849028573, "session": "2026-09-24", "spy_bh_equity": 99.20461757191936}','fb5195fb5b8edb7edc3de3792c38d80dcea9828c81acf2f0f27f4e359b83cdda','fb0960851714e0e7a7d68678dc0e987d1740dd80a840f661f05f2b170728f6e3');
INSERT INTO "events" VALUES(11,'2026-09-24T20:38:18Z','20260924T203813Z-primary','decision','{"action": "INFO", "code": "DECIDED", "key": "decide:2026-09-25", "reason": "0 orders (MOO) for 2026-09-25; regime ON; SPY 767.18 vs 200d 718.01; VIX 15.670000076293945; 0 earnings reactions on 2026-09-24; rebalance=False", "ticker": "*"}','fb0960851714e0e7a7d68678dc0e987d1740dd80a840f661f05f2b170728f6e3','b8a1d66739af6b27add2f62eb8263be493574317c1dae98f694148e53afcced5');
CREATE TABLE experiment (
  id INTEGER PRIMARY KEY CHECK (id = 1),
  frozen_at TEXT NOT NULL, start_date TEXT NOT NULL, end_date TEXT NOT NULL,
  starting_cash REAL NOT NULL, strategy_version TEXT NOT NULL,
  strategy_sha256 TEXT NOT NULL, universe_sha256 TEXT NOT NULL, report_days TEXT NOT NULL, notes TEXT
);
INSERT INTO "experiment" VALUES(1,'2026-09-23T01:43:16Z','2026-09-23','2026-10-22',100.0,'1.0.0-primary','08c6983d1764dc56665bb3914d4da2935023792e0222e96f4ca159c28d602da5','172ba39de91f49af21ee2539df0b42cd5d6aa9c7afbd426114cb33bba2c27afa','[7, 14, 21, 28, 30]','book=primary; strategy=config/strategy_v1_primary.json');
CREATE TABLE fills (
  fill_id INTEGER PRIMARY KEY AUTOINCREMENT, order_key TEXT NOT NULL UNIQUE, run_id TEXT,
  recorded_at TEXT NOT NULL, session TEXT NOT NULL, ticker TEXT NOT NULL, side TEXT NOT NULL,
  qty REAL NOT NULL, ref_price REAL NOT NULL, fill_price REAL NOT NULL, cost_bps REAL NOT NULL,
  cost_usd REAL NOT NULL, price_time TEXT NOT NULL, price_source TEXT NOT NULL, sleeve TEXT,
  reason_code TEXT, reason TEXT, realized_pnl REAL
);
INSERT INTO "fills" VALUES(1,'2026-09-23:residual:SPY:BUY:RESIDUAL','20260923T175009Z-primary','2026-09-23T17:50:09Z','2026-09-23','SPY','BUY',0.126724,7.7278997802734375e+02,7.73330931011962775e+02,7.0,6.85517260228613589e-02,'2026-09-23T09:30:00-04:00 (official open)','yahoo_daily_open','residual','RESIDUAL','park idle cash in SPY (regime risk-on)',NULL);
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
INSERT INTO "orders" VALUES('2026-09-23:residual:SPY:BUY:RESIDUAL','2026-09-23T01:43:23Z','20260923T014323Z-primary','SPY','BUY','MOO','2026-09-23','residual',NULL,NULL,90,'RESIDUAL','park idle cash in SPY (regime risk-on)','{}','{}','FILLED','BUY 0.126724 SPY @ 773.3309','2026-09-23T17:50:09Z');
CREATE TABLE positions (
  ticker TEXT PRIMARY KEY, qty REAL NOT NULL, avg_cost REAL NOT NULL, sleeve TEXT NOT NULL,
  entry_session TEXT NOT NULL, entry_price REAL NOT NULL, initial_stop REAL, trail_pct REAL,
  high_water REAL NOT NULL, max_hold_until TEXT, stop_checked_through TEXT, meta TEXT
);
INSERT INTO "positions" VALUES('SPY',0.126724,7.73330931011962775e+02,'residual','2026-09-23',7.73330931011962775e+02,NULL,NULL,7.73330931011962775e+02,NULL,'2026-09-25T09:45:00-04:00','{}');
CREATE TABLE reports (
  report_key TEXT PRIMARY KEY, day_number INTEGER NOT NULL, report_date TEXT NOT NULL,
  as_of_session TEXT NOT NULL, generated_at TEXT NOT NULL, path_md TEXT NOT NULL, path_html TEXT NOT NULL,
  late_by_hours REAL, notified INTEGER DEFAULT 0
);
CREATE TABLE runs (
  run_id TEXT PRIMARY KEY, started_at TEXT NOT NULL, finished_at TEXT, status TEXT NOT NULL,
  trigger TEXT, summary TEXT, error TEXT
);
INSERT INTO "runs" VALUES('20260923T014323Z-primary','2026-09-23T01:43:23Z','2026-09-23T01:43:24Z','OK','manual-first-run','decided for 2026-09-23: 1 orders (MOO), regime ON',NULL);
INSERT INTO "runs" VALUES('20260923T014524Z-primary','2026-09-23T01:45:24Z','2026-09-23T01:45:24Z','OK','launchd','no action needed',NULL);
INSERT INTO "runs" VALUES('20260923T015119Z-primary','2026-09-23T01:51:19Z','2026-09-23T01:51:20Z','OK','launchd','no action needed',NULL);
INSERT INTO "runs" VALUES('20260923T020657Z-primary','2026-09-23T02:06:57Z','2026-09-23T02:06:57Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260923T175009Z-primary','2026-09-23T17:50:09Z','2026-09-23T17:50:09Z','OK','github-actions','FILL BUY SPY 0.1267 @ 773.33 (RESIDUAL)',NULL);
INSERT INTO "runs" VALUES('20260923T175810Z-primary','2026-09-23T17:58:10Z','2026-09-23T17:58:11Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260923T194251Z-primary','2026-09-23T19:42:51Z','2026-09-23T19:42:51Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260923T215408Z-primary','2026-09-23T21:54:08Z','2026-09-23T21:54:14Z','OK','github-actions','closed 2026-09-23; decided for 2026-09-24: 0 orders (MOO), regime ON',NULL);
INSERT INTO "runs" VALUES('20260923T222126Z-primary','2026-09-23T22:21:26Z','2026-09-23T22:21:26Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260923T230604Z-primary','2026-09-23T23:06:04Z','2026-09-23T23:06:04Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260923T233747Z-primary','2026-09-23T23:37:47Z','2026-09-23T23:37:47Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260924T012001Z-primary','2026-09-24T01:20:01Z','2026-09-24T01:20:01Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260924T031040Z-primary','2026-09-24T03:10:40Z','2026-09-24T03:10:40Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260924T133958Z-primary','2026-09-24T13:42:01Z','2026-09-24T13:42:01Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260924T135503Z-primary','2026-09-24T13:55:07Z','2026-09-24T13:55:07Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260924T144029Z-primary','2026-09-24T14:40:37Z','2026-09-24T14:40:38Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260924T155544Z-primary','2026-09-24T15:55:45Z','2026-09-24T15:55:46Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260924T163052Z-primary','2026-09-24T16:30:54Z','2026-09-24T16:30:54Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260924T173715Z-primary','2026-09-24T17:37:16Z','2026-09-24T17:37:16Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260924T192233Z-primary','2026-09-24T19:22:35Z','2026-09-24T19:22:36Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260924T195254Z-primary','2026-09-24T19:52:57Z','2026-09-24T19:52:57Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260924T203813Z-primary','2026-09-24T20:38:15Z','2026-09-24T20:38:18Z','OK','github-actions','closed 2026-09-24; decided for 2026-09-25: 0 orders (MOO), regime ON',NULL);
INSERT INTO "runs" VALUES('20260924T204507Z-primary','2026-09-24T20:45:07Z','2026-09-24T20:45:07Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260924T230943Z-primary','2026-09-24T23:09:43Z','2026-09-24T23:09:43Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260924T232303Z-primary','2026-09-24T23:23:03Z','2026-09-24T23:23:03Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260924T235131Z-primary','2026-09-24T23:51:31Z','2026-09-24T23:51:31Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260925T012607Z-primary','2026-09-25T01:26:07Z','2026-09-25T01:26:07Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260925T131445Z-primary','2026-09-25T13:14:50Z','2026-09-25T13:14:50Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260925T133706Z-primary','2026-09-25T13:38:34Z','2026-09-25T13:38:34Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260925T135248Z-primary','2026-09-25T13:53:06Z','2026-09-25T13:53:06Z','OK','github-actions','no action needed',NULL);
CREATE TABLE snapshots (
  session TEXT PRIMARY KEY, created_at TEXT NOT NULL, run_id TEXT, equity REAL NOT NULL,
  cash REAL NOT NULL, positions_value REAL NOT NULL, spy_bh_equity REAL, cash_bh_equity REAL,
  peak REAL NOT NULL, drawdown REAL NOT NULL, regime TEXT, risk_state TEXT, marks TEXT, holdings TEXT
);
INSERT INTO "snapshots" VALUES('2026-09-23','2026-09-23T21:54:08Z','20260923T215408Z-primary',9.93003652290552594e+01,2.00041109844002562e+00,9.72999541306152338e+01,9.92860839736302125e+01,100.0,100.0,6.99634770944745909e-03,'ON','{"peak": 100.0, "pause_until": null, "halt_until": null, "drawdown": 0.006996347709447459}','{"marks": {"SPY": 767.8099975585938}, "flags": {}}','{"SPY": {"qty": 0.126724, "avg_cost": 773.3309310119628, "sleeve": "residual", "stop": null, "entry_session": "2026-09-23", "max_hold_until": null}}');
INSERT INTO "snapshots" VALUES('2026-09-24','2026-09-24T20:38:13Z','20260924T203813Z-primary',9.922052849028573e+01,2.00041109844002562e+00,97.2201173918457,9.9204617571919357e+01,100.0,100.0,0.00779471509714269,'ON','{"peak": 100.0, "pause_until": null, "halt_until": null, "drawdown": 0.00779471509714269}','{"marks": {"SPY": 767.1799926757812}, "flags": {}}','{"SPY": {"qty": 0.126724, "avg_cost": 773.3309310119628, "sleeve": "residual", "stop": null, "entry_session": "2026-09-23", "max_hold_until": null}}');
CREATE TABLE state (key TEXT PRIMARY KEY, value TEXT NOT NULL, updated_at TEXT NOT NULL);
INSERT INTO "state" VALUES('cash','2.0004110984400256','2026-09-25T13:53:06Z');
INSERT INTO "state" VALUES('strategy_integrity_ok','true','2026-09-25T13:53:06Z');
INSERT INTO "state" VALUES('last_regime','"ON"','2026-09-24T20:38:18Z');
INSERT INTO "state" VALUES('benchmark','{"ticker": "SPY", "qty": 0.12931074652496097, "entry_price": 773.3309310119628, "entry_session": "2026-09-23", "div_cash": 0.0, "note": "SPY bought at the first session''s official open with the same cost model"}','2026-09-23T17:50:09Z');
INSERT INTO "state" VALUES('open_done:2026-09-23','true','2026-09-23T17:50:09Z');
INSERT INTO "state" VALUES('live_marks','{"as_of": "2026-09-25T13:52:48Z", "marks": {"SPY": [769.52001953125, "2026-09-25T09:45:00-04:00"]}}','2026-09-25T13:53:06Z');
INSERT INTO "state" VALUES('risk','{"peak": 100.0, "pause_until": null, "halt_until": null, "drawdown": 0.00779471509714269}','2026-09-24T20:38:17Z');
INSERT INTO "state" VALUES('last_closed_session','"2026-09-24"','2026-09-24T20:38:17Z');
INSERT INTO "state" VALUES('open_done:2026-09-24','true','2026-09-24T13:42:01Z');
INSERT INTO "state" VALUES('open_done:2026-09-25','true','2026-09-25T13:38:34Z');
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
INSERT INTO "sqlite_sequence" VALUES('events',11);
INSERT INTO "sqlite_sequence" VALUES('decisions',4);
INSERT INTO "sqlite_sequence" VALUES('fills',1);
COMMIT;
