BEGIN TRANSACTION;
CREATE TABLE data_issues (
  id INTEGER PRIMARY KEY AUTOINCREMENT, occurred_at TEXT NOT NULL, run_id TEXT, severity TEXT NOT NULL,
  component TEXT NOT NULL, ticker TEXT, message TEXT NOT NULL
);
INSERT INTO "data_issues" VALUES(1,'2026-10-07T15:27:54Z','20261007T152744Z-ctrend','INFO','marketdata',NULL,'official close missing for 2026-10-06; derived daily bars from 5m data for 2 tickers');
INSERT INTO "data_issues" VALUES(2,'2026-10-07T15:27:54Z','20261007T152744Z-ctrend','ERROR','engine',NULL,'ValueError: IBIT: 1 closes, need 200');
CREATE TABLE decisions (
  decision_id INTEGER PRIMARY KEY AUTOINCREMENT, decision_key TEXT NOT NULL UNIQUE, run_id TEXT,
  created_at TEXT NOT NULL, data_through TEXT NOT NULL, session TEXT NOT NULL, ticker TEXT NOT NULL,
  sleeve TEXT, action TEXT NOT NULL, reason_code TEXT, reason TEXT, metrics TEXT, news_ids TEXT
);
INSERT INTO "decisions" VALUES(1,'2026-10-07:000:trend:ETHA:TREND_BUY','20261007T153112Z-ctrend','2026-10-07T15:31:12Z','2026-10-06','2026-10-07','ETHA','trend','BUY','TREND_BUY','week-end trend rebalance; ETHA: above [50, 100, 200]-session averages','{"value": 49.5, "close": 60.88999938964844, "above_sma_sessions": [50, 100, 200], "weight_fraction": 1.0}','[]');
INSERT INTO "decisions" VALUES(2,'2026-10-07:001:trend:IBIT:TREND_BUY','20261007T153112Z-ctrend','2026-10-07T15:31:12Z','2026-10-06','2026-10-07','IBIT','trend','BUY','TREND_BUY','week-end trend rebalance; IBIT: above [50, 100, 200]-session averages','{"value": 49.5, "close": 48.4900016784668, "above_sma_sessions": [50, 100, 200], "weight_fraction": 1.0}','[]');
INSERT INTO "decisions" VALUES(3,'decide:2026-10-07','20261007T153112Z-ctrend','2026-10-07T15:31:12Z','2026-10-06','2026-10-07','*','system','INFO','DECIDED','2 orders (MKT) for 2026-10-07; rebalance=True; trend weights IBIT 50%, ETHA 50%','{"rebalance": true, "order_type": "MKT", "data_through": "2026-10-06", "detail": {"IBIT": {"close": 48.4900016784668, "above_sma_sessions": [50, 100, 200], "weight_fraction": 1.0}, "ETHA": {"close": 60.88999938964844, "above_sma_sessions": [50, 100, 200], "weight_fraction": 1.0}}, "halted": false}','[]');
INSERT INTO "decisions" VALUES(4,'decide:2026-10-08','20261007T204612Z-ctrend','2026-10-07T20:46:12Z','2026-10-07','2026-10-08','*','system','INFO','DECIDED','0 orders (MOO) for 2026-10-08; rebalance=False (weekly)','{"rebalance": false, "order_type": "MOO", "data_through": "2026-10-07", "detail": {}, "halted": false}','[]');
CREATE TABLE dividends (
  ticker TEXT NOT NULL, ex_date TEXT NOT NULL, per_share REAL NOT NULL, qty REAL NOT NULL,
  amount REAL NOT NULL, recorded_at TEXT NOT NULL, PRIMARY KEY (ticker, ex_date)
);
CREATE TABLE events (
  seq INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT NOT NULL, run_id TEXT, kind TEXT NOT NULL,
  payload TEXT NOT NULL, prev_hash TEXT NOT NULL, hash TEXT NOT NULL
);
INSERT INTO "events" VALUES(1,'2026-10-07T15:25:55Z',NULL,'freeze','{"book": "ctrend", "end": "2026-10-22", "start": "2026-10-07", "strategy_sha256": "77c7659af254c4ab2c15f7087c0e0d7d2b3a5b80057cfcb6d2ff691c25b6a5a8", "universe_sha256": "172ba39de91f49af21ee2539df0b42cd5d6aa9c7afbd426114cb33bba2c27afa", "version": "crypto-trend-1.0.0"}','GENESIS','98a6033c3e6bfc6a83aab86ca91e02502ca5d3599d1880e9eb14a0a262c44ed1');
INSERT INTO "events" VALUES(2,'2026-10-07T15:27:53Z','20261007T152744Z-ctrend','benchmark_init','{"entry_price": 776.3130585449218, "qty": 0.12881401246480959}','98a6033c3e6bfc6a83aab86ca91e02502ca5d3599d1880e9eb14a0a262c44ed1','17b0d4205f691d11cb561fc33a86e99b04c72a8d18d07330bca290fae2019970');
INSERT INTO "events" VALUES(3,'2026-10-07T15:31:23Z','20261007T153112Z-ctrend','decision','{"action": "BUY", "code": "TREND_BUY", "key": "2026-10-07:000:trend:ETHA:TREND_BUY", "reason": "week-end trend rebalance; ETHA: above [50, 100, 200]-session averages", "ticker": "ETHA"}','17b0d4205f691d11cb561fc33a86e99b04c72a8d18d07330bca290fae2019970','6ceae2d8d6bb6a0bdc1daf9a773c8f27d8c357bbc4604d22c8595a767ecab956');
INSERT INTO "events" VALUES(4,'2026-10-07T15:31:23Z','20261007T153112Z-ctrend','decision','{"action": "BUY", "code": "TREND_BUY", "key": "2026-10-07:001:trend:IBIT:TREND_BUY", "reason": "week-end trend rebalance; IBIT: above [50, 100, 200]-session averages", "ticker": "IBIT"}','6ceae2d8d6bb6a0bdc1daf9a773c8f27d8c357bbc4604d22c8595a767ecab956','f5e352f08578d43f46099bd57ebb588002f98f4285e62eff4f163a3d488567e0');
INSERT INTO "events" VALUES(5,'2026-10-07T15:31:23Z','20261007T153112Z-ctrend','order','{"key": "2026-10-07:trend:ETHA:BUY:TREND_BUY", "notional": 49.2525, "qty": null, "reason": "week-end trend rebalance; ETHA: above [50, 100, 200]-session averages", "session": "2026-10-07", "side": "BUY", "ticker": "ETHA", "type": "MKT"}','f5e352f08578d43f46099bd57ebb588002f98f4285e62eff4f163a3d488567e0','650038e2f95b478eb6cbfc7058a008cf5f752fb41c5a1689ea2946858cebc783');
INSERT INTO "events" VALUES(6,'2026-10-07T15:31:23Z','20261007T153112Z-ctrend','order','{"key": "2026-10-07:trend:IBIT:BUY:TREND_BUY", "notional": 49.2525, "qty": null, "reason": "week-end trend rebalance; IBIT: above [50, 100, 200]-session averages", "session": "2026-10-07", "side": "BUY", "ticker": "IBIT", "type": "MKT"}','650038e2f95b478eb6cbfc7058a008cf5f752fb41c5a1689ea2946858cebc783','9b8ea4883163c82693db6673ede106a9596bf3627d1c8f399169ad3f2ca09e5c');
INSERT INTO "events" VALUES(7,'2026-10-07T15:31:23Z','20261007T153112Z-ctrend','decision','{"action": "INFO", "code": "DECIDED", "key": "decide:2026-10-07", "reason": "2 orders (MKT) for 2026-10-07; rebalance=True; trend weights IBIT 50%, ETHA 50%", "ticker": "*"}','9b8ea4883163c82693db6673ede106a9596bf3627d1c8f399169ad3f2ca09e5c','8ffe4d396dd0e5ad6cef404767ba7f609743fdcdc2b6db52bed2c6f26019ab4d');
INSERT INTO "events" VALUES(8,'2026-10-07T15:41:19Z','20261007T154112Z-ctrend','fill','{"fill_price": 57.992595192718504, "key": "2026-10-07:trend:ETHA:BUY:TREND_BUY", "price_time": "2026-10-07T11:35:00-04:00", "qty": 0.849289, "ref_price": 57.98099899291992, "side": "BUY", "source": "yahoo_5m_bar_open", "ticker": "ETHA"}','8ffe4d396dd0e5ad6cef404767ba7f609743fdcdc2b6db52bed2c6f26019ab4d','b56fc9ebffda38e5e7957957f6a1252403ed00364a0c1b2ebe5672e584ec0118');
INSERT INTO "events" VALUES(9,'2026-10-07T15:41:19Z','20261007T154112Z-ctrend','order_status','{"key": "2026-10-07:trend:ETHA:BUY:TREND_BUY", "reason": "BUY 0.849289 ETHA @ 57.9926", "status": "FILLED"}','b56fc9ebffda38e5e7957957f6a1252403ed00364a0c1b2ebe5672e584ec0118','54813a3cc36b5437c83e57ee44559b61402ac2e7c9fbad5f884ef91592e07224');
INSERT INTO "events" VALUES(10,'2026-10-07T15:41:19Z','20261007T154112Z-ctrend','fill','{"fill_price": 47.10442022094726, "key": "2026-10-07:trend:IBIT:BUY:TREND_BUY", "price_time": "2026-10-07T11:35:00-04:00", "qty": 1.045602, "ref_price": 47.095001220703125, "side": "BUY", "source": "yahoo_5m_bar_open", "ticker": "IBIT"}','54813a3cc36b5437c83e57ee44559b61402ac2e7c9fbad5f884ef91592e07224','126048ce6a4b9e646e7f2702794021dc213acfbb85e29296e3c4c828ecdee5cb');
INSERT INTO "events" VALUES(11,'2026-10-07T15:41:19Z','20261007T154112Z-ctrend','order_status','{"key": "2026-10-07:trend:IBIT:BUY:TREND_BUY", "reason": "BUY 1.045602 IBIT @ 47.1044", "status": "FILLED"}','126048ce6a4b9e646e7f2702794021dc213acfbb85e29296e3c4c828ecdee5cb','35f3d8de4c70a8632bad891c59d7b4216bbe373e6a5bf47e78129fcd67fbf729');
INSERT INTO "events" VALUES(12,'2026-10-07T20:47:31Z','20261007T204612Z-ctrend','snapshot','{"cash": 1.4950508295084006, "drawdown": 0.0, "equity": 100.201609896319, "session": "2026-10-07", "spy_bh_equity": 100.11682299405129}','35f3d8de4c70a8632bad891c59d7b4216bbe373e6a5bf47e78129fcd67fbf729','c6814cec08d43299cd16bc083c9fd891e3f6d3d05b2511feda0a47a583bb1e50');
INSERT INTO "events" VALUES(13,'2026-10-07T20:47:33Z','20261007T204612Z-ctrend','decision','{"action": "INFO", "code": "DECIDED", "key": "decide:2026-10-08", "reason": "0 orders (MOO) for 2026-10-08; rebalance=False (weekly)", "ticker": "*"}','c6814cec08d43299cd16bc083c9fd891e3f6d3d05b2511feda0a47a583bb1e50','23ccbf78917bd2aea97e3f6ebfc76bd4d768f5cc357134471fa9b90af62071fa');
CREATE TABLE experiment (
  id INTEGER PRIMARY KEY CHECK (id = 1),
  frozen_at TEXT NOT NULL, start_date TEXT NOT NULL, end_date TEXT NOT NULL,
  starting_cash REAL NOT NULL, strategy_version TEXT NOT NULL,
  strategy_sha256 TEXT NOT NULL, universe_sha256 TEXT NOT NULL, report_days TEXT NOT NULL, notes TEXT
);
INSERT INTO "experiment" VALUES(1,'2026-10-07T15:25:55Z','2026-10-07','2026-10-22',100.0,'crypto-trend-1.0.0','77c7659af254c4ab2c15f7087c0e0d7d2b3a5b80057cfcb6d2ff691c25b6a5a8','172ba39de91f49af21ee2539df0b42cd5d6aa9c7afbd426114cb33bba2c27afa','[7, 14, 21, 28, 30]','book=ctrend; strategy=config/strategy_crypto_trend_v1.json');
CREATE TABLE fills (
  fill_id INTEGER PRIMARY KEY AUTOINCREMENT, order_key TEXT NOT NULL UNIQUE, run_id TEXT,
  recorded_at TEXT NOT NULL, session TEXT NOT NULL, ticker TEXT NOT NULL, side TEXT NOT NULL,
  qty REAL NOT NULL, ref_price REAL NOT NULL, fill_price REAL NOT NULL, cost_bps REAL NOT NULL,
  cost_usd REAL NOT NULL, price_time TEXT NOT NULL, price_source TEXT NOT NULL, sleeve TEXT,
  reason_code TEXT, reason TEXT, realized_pnl REAL
);
INSERT INTO "fills" VALUES(1,'2026-10-07:trend:ETHA:BUY:TREND_BUY','20261007T154112Z-ctrend','2026-10-07T15:41:19Z','2026-10-07','ETHA','BUY',0.849289,5.79809989929199218e+01,5.79925951927185039e+01,2.0,9.84852493073796152e-03,'2026-10-07T11:35:00-04:00','yahoo_5m_bar_open','residual','TREND_BUY','week-end trend rebalance; ETHA: above [50, 100, 200]-session averages',NULL);
INSERT INTO "fills" VALUES(2,'2026-10-07:trend:IBIT:BUY:TREND_BUY','20261007T154112Z-ctrend','2026-10-07T15:41:19Z','2026-10-07','IBIT','BUY',1.045602,4.7095001220703125e+01,4.71044202209472615e+01,2.0,0.00984852549326967,'2026-10-07T11:35:00-04:00','yahoo_5m_bar_open','residual','TREND_BUY','week-end trend rebalance; IBIT: above [50, 100, 200]-session averages',NULL);
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
INSERT INTO "orders" VALUES('2026-10-07:trend:ETHA:BUY:TREND_BUY','2026-10-07T15:31:12Z','20261007T153112Z-ctrend','ETHA','BUY','MKT','2026-10-07','residual',49.2525,NULL,50,'TREND_BUY','week-end trend rebalance; ETHA: above [50, 100, 200]-session averages','{}','{}','FILLED','BUY 0.849289 ETHA @ 57.9926','2026-10-07T15:41:19Z');
INSERT INTO "orders" VALUES('2026-10-07:trend:IBIT:BUY:TREND_BUY','2026-10-07T15:31:12Z','20261007T153112Z-ctrend','IBIT','BUY','MKT','2026-10-07','residual',49.2525,NULL,50,'TREND_BUY','week-end trend rebalance; IBIT: above [50, 100, 200]-session averages','{}','{}','FILLED','BUY 1.045602 IBIT @ 47.1044','2026-10-07T15:41:19Z');
CREATE TABLE positions (
  ticker TEXT PRIMARY KEY, qty REAL NOT NULL, avg_cost REAL NOT NULL, sleeve TEXT NOT NULL,
  entry_session TEXT NOT NULL, entry_price REAL NOT NULL, initial_stop REAL, trail_pct REAL,
  high_water REAL NOT NULL, max_hold_until TEXT, stop_checked_through TEXT, meta TEXT
);
INSERT INTO "positions" VALUES('ETHA',0.849289,5.79925951927185039e+01,'residual','2026-10-07',5.79925951927185039e+01,NULL,NULL,5.83050003051757812e+01,NULL,'2026-10-07T16:00:00-04:00','{"entry_time": "2026-10-07T11:35:00-04:00"}');
INSERT INTO "positions" VALUES('IBIT',1.045602,4.71044202209472615e+01,'residual','2026-10-07',4.71044202209472615e+01,NULL,NULL,47.3484992980957,NULL,'2026-10-07T16:00:00-04:00','{"entry_time": "2026-10-07T11:35:00-04:00"}');
CREATE TABLE reports (
  report_key TEXT PRIMARY KEY, day_number INTEGER NOT NULL, report_date TEXT NOT NULL,
  as_of_session TEXT NOT NULL, generated_at TEXT NOT NULL, path_md TEXT NOT NULL, path_html TEXT NOT NULL,
  late_by_hours REAL, notified INTEGER DEFAULT 0
);
CREATE TABLE runs (
  run_id TEXT PRIMARY KEY, started_at TEXT NOT NULL, finished_at TEXT, status TEXT NOT NULL,
  trigger TEXT, summary TEXT, error TEXT
);
INSERT INTO "runs" VALUES('20261007T152744Z-ctrend','2026-10-07T15:27:53Z','2026-10-07T15:27:54Z','ERROR','github-actions','','Traceback (most recent call last):
  File "/home/runner/work/paper-trader/paper-trader/papertrader/cycle.py", line 111, in run_cycle
    summary = TrendEngine(L, md, cfg, {**exp, "book": book["id"]}, now).step()
  File "/home/runner/work/paper-trader/paper-trader/papertrader/engine.py", line 101, in step
    self.maybe_decide(last_done, lcs)
    ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^
  File "/home/runner/work/paper-trader/paper-trader/papertrader/trend.py", line 171, in maybe_decide
    weights, detail = trend_weights(closes, self.assets, self.months, self.sessions)
                      ~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/runner/work/paper-trader/paper-trader/papertrader/trend.py", line 33, in trend_weights
    raise ValueError(f"{a}: {len(s)} closes, need {need}")
ValueError: IBIT: 1 closes, need 200
');
INSERT INTO "runs" VALUES('20261007T153112Z-ctrend','2026-10-07T15:31:21Z','2026-10-07T15:31:23Z','OK','github-actions','decided for 2026-10-07: 2 orders (MKT), rebalance=True',NULL);
INSERT INTO "runs" VALUES('20261007T153612Z-ctrend','2026-10-07T15:36:20Z','2026-10-07T15:36:20Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261007T154112Z-ctrend','2026-10-07T15:41:19Z','2026-10-07T15:41:19Z','OK','github-actions','FILL BUY ETHA 0.8493 @ 57.99 (TREND_BUY); FILL BUY IBIT 1.0456 @ 47.10 (TREND_BUY)',NULL);
INSERT INTO "runs" VALUES('20261007T154612Z-ctrend','2026-10-07T15:46:19Z','2026-10-07T15:46:20Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261007T155112Z-ctrend','2026-10-07T15:51:20Z','2026-10-07T15:51:20Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261007T155308Z-ctrend','2026-10-07T15:53:15Z','2026-10-07T15:53:15Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261007T155808Z-ctrend','2026-10-07T15:58:13Z','2026-10-07T15:58:13Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261007T160308Z-ctrend','2026-10-07T16:03:16Z','2026-10-07T16:03:16Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261007T160808Z-ctrend','2026-10-07T16:08:15Z','2026-10-07T16:08:15Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261007T161308Z-ctrend','2026-10-07T16:13:15Z','2026-10-07T16:13:15Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261007T161442Z-ctrend','2026-10-07T16:14:49Z','2026-10-07T16:14:49Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261007T161942Z-ctrend','2026-10-07T16:19:52Z','2026-10-07T16:19:52Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261007T162442Z-ctrend','2026-10-07T16:24:50Z','2026-10-07T16:24:50Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261007T162942Z-ctrend','2026-10-07T16:29:48Z','2026-10-07T16:29:49Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261007T163442Z-ctrend','2026-10-07T16:34:50Z','2026-10-07T16:34:50Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261007T204612Z-ctrend','2026-10-07T20:47:29Z','2026-10-07T20:47:33Z','OK','github-actions','closed 2026-10-07; decided for 2026-10-08: 0 orders (MOO), rebalance=False',NULL);
INSERT INTO "runs" VALUES('20261007T214343Z-ctrend','2026-10-07T21:43:49Z','2026-10-07T21:43:49Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261008T001042Z-ctrend','2026-10-08T00:10:48Z','2026-10-08T00:10:48Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261008T002423Z-ctrend','2026-10-08T00:24:29Z','2026-10-08T00:24:29Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261008T010021Z-ctrend','2026-10-08T01:00:27Z','2026-10-08T01:00:27Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261008T011955Z-ctrend','2026-10-08T01:20:01Z','2026-10-08T01:20:01Z','OK','github-actions','no action needed',NULL);
CREATE TABLE snapshots (
  session TEXT PRIMARY KEY, created_at TEXT NOT NULL, run_id TEXT, equity REAL NOT NULL,
  cash REAL NOT NULL, positions_value REAL NOT NULL, spy_bh_equity REAL, cash_bh_equity REAL,
  peak REAL NOT NULL, drawdown REAL NOT NULL, regime TEXT, risk_state TEXT, marks TEXT, holdings TEXT
);
INSERT INTO "snapshots" VALUES('2026-10-07','2026-10-07T20:46:12Z','20261007T204612Z-ctrend',100.201609896319,1.49505082950840062e+00,98.7065590668106,1.0011682299405129e+02,100.0,100.201609896319,0.0,'TREND','{"peak": 100.201609896319, "pause_until": null, "halt_until": null, "drawdown": 0.0}','{"marks": {"ETHA": 58.099998474121094, "IBIT": 47.209999084472656}, "flags": {}}','{"ETHA": {"qty": 0.849289, "avg_cost": 57.992595192718504, "sleeve": "residual", "stop": null, "entry_session": "2026-10-07", "max_hold_until": null}, "IBIT": {"qty": 1.045602, "avg_cost": 47.10442022094726, "sleeve": "residual", "stop": null, "entry_session": "2026-10-07", "max_hold_until": null}}');
CREATE TABLE state (key TEXT PRIMARY KEY, value TEXT NOT NULL, updated_at TEXT NOT NULL);
INSERT INTO "state" VALUES('cash','1.4950508295084006','2026-10-07T20:47:31Z');
INSERT INTO "state" VALUES('strategy_integrity_ok','true','2026-10-08T01:20:01Z');
INSERT INTO "state" VALUES('benchmark','{"ticker": "SPY", "qty": 0.12881401246480959, "entry_price": 776.3130585449218, "entry_session": "2026-10-07", "div_cash": 0.0, "note": "SPY bought at the first session''s official open with the same cost model"}','2026-10-07T15:27:53Z');
INSERT INTO "state" VALUES('open_done:2026-10-07','true','2026-10-07T15:27:53Z');
INSERT INTO "state" VALUES('live_marks','{"as_of": "2026-10-07T16:34:42Z", "marks": {"ETHA": [58.10499954223633, "2026-10-07T12:25:00-04:00"], "IBIT": [47.26499938964844, "2026-10-07T12:25:00-04:00"]}}','2026-10-07T16:34:50Z');
INSERT INTO "state" VALUES('last_regime','"TREND"','2026-10-07T20:47:33Z');
INSERT INTO "state" VALUES('risk','{"peak": 100.201609896319, "pause_until": null, "halt_until": null, "drawdown": 0.0}','2026-10-07T20:47:31Z');
INSERT INTO "state" VALUES('last_closed_session','"2026-10-07"','2026-10-07T20:47:31Z');
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
INSERT INTO "sqlite_sequence" VALUES('events',13);
INSERT INTO "sqlite_sequence" VALUES('data_issues',2);
INSERT INTO "sqlite_sequence" VALUES('decisions',4);
INSERT INTO "sqlite_sequence" VALUES('fills',2);
COMMIT;
