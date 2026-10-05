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
INSERT INTO "decisions" VALUES(1,'missed:2026-09-23','20261005T082237Z-trend','2026-10-05T08:22:37Z','-','2026-09-23','*','system','INFO','MISSED_WINDOW','no decision was made for this session (data unavailable or the cycle did not run in the window)','{}','[]');
INSERT INTO "decisions" VALUES(2,'missed:2026-09-24','20261005T082237Z-trend','2026-10-05T08:22:37Z','-','2026-09-24','*','system','INFO','MISSED_WINDOW','no decision was made for this session (data unavailable or the cycle did not run in the window)','{}','[]');
INSERT INTO "decisions" VALUES(3,'missed:2026-09-25','20261005T082237Z-trend','2026-10-05T08:22:37Z','-','2026-09-25','*','system','INFO','MISSED_WINDOW','no decision was made for this session (data unavailable or the cycle did not run in the window)','{}','[]');
INSERT INTO "decisions" VALUES(4,'missed:2026-09-28','20261005T082237Z-trend','2026-10-05T08:22:37Z','-','2026-09-28','*','system','INFO','MISSED_WINDOW','no decision was made for this session (data unavailable or the cycle did not run in the window)','{}','[]');
INSERT INTO "decisions" VALUES(5,'missed:2026-09-29','20261005T082237Z-trend','2026-10-05T08:22:37Z','-','2026-09-29','*','system','INFO','MISSED_WINDOW','no decision was made for this session (data unavailable or the cycle did not run in the window)','{}','[]');
INSERT INTO "decisions" VALUES(6,'missed:2026-09-30','20261005T082237Z-trend','2026-10-05T08:22:37Z','-','2026-09-30','*','system','INFO','MISSED_WINDOW','no decision was made for this session (data unavailable or the cycle did not run in the window)','{}','[]');
INSERT INTO "decisions" VALUES(7,'missed:2026-10-01','20261005T082237Z-trend','2026-10-05T08:22:37Z','-','2026-10-01','*','system','INFO','MISSED_WINDOW','no decision was made for this session (data unavailable or the cycle did not run in the window)','{}','[]');
INSERT INTO "decisions" VALUES(8,'missed:2026-10-02','20261005T082237Z-trend','2026-10-05T08:22:37Z','-','2026-10-02','*','system','INFO','MISSED_WINDOW','no decision was made for this session (data unavailable or the cycle did not run in the window)','{}','[]');
INSERT INTO "decisions" VALUES(9,'2026-10-05:000:trend:EFA:TREND_BUY','20261005T082237Z-trend','2026-10-05T08:22:37Z','2026-10-02','2026-10-05','EFA','trend','BUY','TREND_BUY','month-end trend rebalance; EFA: above [8, 10, 12]-month averages','{"value": 19.8, "close": 103.95999908447266, "above_sma_months": [8, 10, 12], "weight_fraction": 1.0}','[]');
INSERT INTO "decisions" VALUES(10,'2026-10-05:001:trend:SHY:TREND_BUY','20261005T082237Z-trend','2026-10-05T08:22:37Z','2026-10-02','2026-10-05','SHY','trend','BUY','TREND_BUY','month-end trend rebalance; SHY: unallocated capital held in short-term Treasuries','{"value": 59.4}','[]');
INSERT INTO "decisions" VALUES(11,'2026-10-05:002:trend:SPY:TREND_BUY','20261005T082237Z-trend','2026-10-05T08:22:37Z','2026-10-02','2026-10-05','SPY','trend','BUY','TREND_BUY','month-end trend rebalance; SPY: above [8, 10, 12]-month averages','{"value": 19.8, "close": 769.6400146484375, "above_sma_months": [8, 10, 12], "weight_fraction": 1.0}','[]');
INSERT INTO "decisions" VALUES(12,'decide:2026-10-05','20261005T082237Z-trend','2026-10-05T08:22:37Z','2026-10-02','2026-10-05','*','system','INFO','DECIDED','3 orders (MOO) for 2026-10-05; rebalance=True; trend weights SPY 20%, EFA 20%','{"rebalance": true, "order_type": "MOO", "data_through": "2026-10-02", "detail": {"SPY": {"close": 769.6400146484375, "above_sma_months": [8, 10, 12], "weight_fraction": 1.0}, "EFA": {"close": 103.95999908447266, "above_sma_months": [8, 10, 12], "weight_fraction": 1.0}, "IEF": {"close": 89.05000305175781, "above_sma_months": [], "weight_fraction": 0.0}, "GLD": {"close": 380.1400146484375, "above_sma_months": [], "weight_fraction": 0.0}, "VNQ": {"close": 89.5, "above_sma_months": [], "weight_fraction": 0.0}}, "halted": false}','[]');
CREATE TABLE dividends (
  ticker TEXT NOT NULL, ex_date TEXT NOT NULL, per_share REAL NOT NULL, qty REAL NOT NULL,
  amount REAL NOT NULL, recorded_at TEXT NOT NULL, PRIMARY KEY (ticker, ex_date)
);
CREATE TABLE events (
  seq INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT NOT NULL, run_id TEXT, kind TEXT NOT NULL,
  payload TEXT NOT NULL, prev_hash TEXT NOT NULL, hash TEXT NOT NULL
);
INSERT INTO "events" VALUES(1,'2026-10-05T08:21:09Z',NULL,'freeze','{"book": "trend", "end": "2026-10-22", "start": "2026-10-05", "strategy_sha256": "7ca9ab6e33f01b928a7edd3f963091f363563fc20b6c2aba8617cc23587f4d8e", "universe_sha256": "172ba39de91f49af21ee2539df0b42cd5d6aa9c7afbd426114cb33bba2c27afa", "version": "trend-1.0.0"}','GENESIS','8a19298a904637428028ba47fcf72d84ae3a76b3236587430082f6de89e79cce');
INSERT INTO "events" VALUES(2,'2026-10-05T08:22:45Z','20261005T082237Z-trend','benchmark_init','{"entry_price": 773.3309310119628, "qty": 0.12931074652496097}','8a19298a904637428028ba47fcf72d84ae3a76b3236587430082f6de89e79cce','c5ec76035382acc99924e1fc976887f7fac85790dac2f66c51377022ecbebd8d');
INSERT INTO "events" VALUES(3,'2026-10-05T08:22:45Z','20261005T082237Z-trend','snapshot','{"cash": 100.0, "drawdown": 0.0, "equity": 100.0, "session": "2026-09-23", "spy_bh_equity": 99.28608397363021}','c5ec76035382acc99924e1fc976887f7fac85790dac2f66c51377022ecbebd8d','195d6ddf03d48c22654a8faee84a4bb0ac615d4a0229d826a474346f7616a9e7');
INSERT INTO "events" VALUES(4,'2026-10-05T08:22:45Z','20261005T082237Z-trend','snapshot','{"cash": 100.0, "drawdown": 0.0, "equity": 100.0, "session": "2026-09-24", "spy_bh_equity": 99.20461757191936}','195d6ddf03d48c22654a8faee84a4bb0ac615d4a0229d826a474346f7616a9e7','209c12964da9d927d3811f011eefa29a87449e6aafc5c2b4550f6ad4855d6cf2');
INSERT INTO "events" VALUES(5,'2026-10-05T08:22:45Z','20261005T082237Z-trend','snapshot','{"cash": 100.0, "drawdown": 0.0, "equity": 100.0, "session": "2026-09-25", "spy_bh_equity": 99.743841175028}','209c12964da9d927d3811f011eefa29a87449e6aafc5c2b4550f6ad4855d6cf2','f6631c2f9124ee5659007b07ff3dd492bde76a620bf7175c2b1d069289df01b8');
INSERT INTO "events" VALUES(6,'2026-10-05T08:22:45Z','20261005T082237Z-trend','snapshot','{"cash": 100.0, "drawdown": 0.0, "equity": 100.0, "session": "2026-09-28", "spy_bh_equity": 99.00159875277498}','f6631c2f9124ee5659007b07ff3dd492bde76a620bf7175c2b1d069289df01b8','27bffa9d6609747c792dac750c7dfae8b3c3035f97390ae3558cc3edc603d5b8');
INSERT INTO "events" VALUES(7,'2026-10-05T08:22:45Z','20261005T082237Z-trend','snapshot','{"cash": 100.0, "drawdown": 0.0, "equity": 100.0, "session": "2026-09-29", "spy_bh_equity": 98.8192740728755}','27bffa9d6609747c792dac750c7dfae8b3c3035f97390ae3558cc3edc603d5b8','d01ce4d58e0c71aac5cd8d35449545307a2198af2d0f2b368021f7584f31c61d');
INSERT INTO "events" VALUES(8,'2026-10-05T08:22:45Z','20261005T082237Z-trend','snapshot','{"cash": 100.0, "drawdown": 0.0, "equity": 100.0, "session": "2026-09-30", "spy_bh_equity": 98.61625525373111}','d01ce4d58e0c71aac5cd8d35449545307a2198af2d0f2b368021f7584f31c61d','b23826adf3016634d1a3e1ae17e18fb9a0689291cf57d148b4038434c59ee805');
INSERT INTO "events" VALUES(9,'2026-10-05T08:22:45Z','20261005T082237Z-trend','snapshot','{"cash": 100.0, "drawdown": 0.0, "equity": 100.0, "session": "2026-10-01", "spy_bh_equity": 98.79211597480467}','b23826adf3016634d1a3e1ae17e18fb9a0689291cf57d148b4038434c59ee805','b0eb532fd4b4d4f7e4eca7d6fdce0b4776b1c0dc7bd46a5d6c20d51f2ab1aebc');
INSERT INTO "events" VALUES(10,'2026-10-05T08:22:45Z','20261005T082237Z-trend','snapshot','{"cash": 100.0, "drawdown": 0.0, "equity": 100.0, "session": "2026-10-02", "spy_bh_equity": 99.52272484967135}','b0eb532fd4b4d4f7e4eca7d6fdce0b4776b1c0dc7bd46a5d6c20d51f2ab1aebc','7a6c7e4dc15babe368d685c13a2f581701d9812457cfe2b215fa591f1697a187');
INSERT INTO "events" VALUES(11,'2026-10-05T08:22:45Z','20261005T082237Z-trend','decision','{"action": "INFO", "code": "MISSED_WINDOW", "key": "missed:2026-09-23", "reason": "no decision was made for this session (data unavailable or the cycle did not run in the window)", "ticker": "*"}','7a6c7e4dc15babe368d685c13a2f581701d9812457cfe2b215fa591f1697a187','66ba7c6ea69b0563a7c93604014881e0abb21647aea6b09c02b16966876373e8');
INSERT INTO "events" VALUES(12,'2026-10-05T08:22:45Z','20261005T082237Z-trend','decision','{"action": "INFO", "code": "MISSED_WINDOW", "key": "missed:2026-09-24", "reason": "no decision was made for this session (data unavailable or the cycle did not run in the window)", "ticker": "*"}','66ba7c6ea69b0563a7c93604014881e0abb21647aea6b09c02b16966876373e8','42d6e3e0a74da0b2a2af25683d7e8174466ec2400b572bab9f182053edbe2765');
INSERT INTO "events" VALUES(13,'2026-10-05T08:22:45Z','20261005T082237Z-trend','decision','{"action": "INFO", "code": "MISSED_WINDOW", "key": "missed:2026-09-25", "reason": "no decision was made for this session (data unavailable or the cycle did not run in the window)", "ticker": "*"}','42d6e3e0a74da0b2a2af25683d7e8174466ec2400b572bab9f182053edbe2765','a2b30fb2589f11ff49b20668695b55b71af21be93cdcae748f83173b0c850f2e');
INSERT INTO "events" VALUES(14,'2026-10-05T08:22:45Z','20261005T082237Z-trend','decision','{"action": "INFO", "code": "MISSED_WINDOW", "key": "missed:2026-09-28", "reason": "no decision was made for this session (data unavailable or the cycle did not run in the window)", "ticker": "*"}','a2b30fb2589f11ff49b20668695b55b71af21be93cdcae748f83173b0c850f2e','f9d4dc49637ff8d217ccb927cbd5bf43fa45b8415f2d5e3c13f2711fa3f43866');
INSERT INTO "events" VALUES(15,'2026-10-05T08:22:45Z','20261005T082237Z-trend','decision','{"action": "INFO", "code": "MISSED_WINDOW", "key": "missed:2026-09-29", "reason": "no decision was made for this session (data unavailable or the cycle did not run in the window)", "ticker": "*"}','f9d4dc49637ff8d217ccb927cbd5bf43fa45b8415f2d5e3c13f2711fa3f43866','511879da1d4ed3426a4f7812c12d5e87efc954bbcba970717b9840951f42934e');
INSERT INTO "events" VALUES(16,'2026-10-05T08:22:45Z','20261005T082237Z-trend','decision','{"action": "INFO", "code": "MISSED_WINDOW", "key": "missed:2026-09-30", "reason": "no decision was made for this session (data unavailable or the cycle did not run in the window)", "ticker": "*"}','511879da1d4ed3426a4f7812c12d5e87efc954bbcba970717b9840951f42934e','cb6f1db4cc56f10d67b9de22a530b987c006b28fe5cc6fd71075e7dbc2478cd6');
INSERT INTO "events" VALUES(17,'2026-10-05T08:22:45Z','20261005T082237Z-trend','decision','{"action": "INFO", "code": "MISSED_WINDOW", "key": "missed:2026-10-01", "reason": "no decision was made for this session (data unavailable or the cycle did not run in the window)", "ticker": "*"}','cb6f1db4cc56f10d67b9de22a530b987c006b28fe5cc6fd71075e7dbc2478cd6','64a9c2d72c4f30973eaac93b661032393fe0cf7a497bbf6044e3d6a00ea25d46');
INSERT INTO "events" VALUES(18,'2026-10-05T08:22:45Z','20261005T082237Z-trend','decision','{"action": "INFO", "code": "MISSED_WINDOW", "key": "missed:2026-10-02", "reason": "no decision was made for this session (data unavailable or the cycle did not run in the window)", "ticker": "*"}','64a9c2d72c4f30973eaac93b661032393fe0cf7a497bbf6044e3d6a00ea25d46','78eaf30c8d42e74fd24c97643ac6f2b3881beeabf73f177f8eba1b4459c6c4f7');
INSERT INTO "events" VALUES(19,'2026-10-05T08:22:47Z','20261005T082237Z-trend','decision','{"action": "BUY", "code": "TREND_BUY", "key": "2026-10-05:000:trend:EFA:TREND_BUY", "reason": "month-end trend rebalance; EFA: above [8, 10, 12]-month averages", "ticker": "EFA"}','78eaf30c8d42e74fd24c97643ac6f2b3881beeabf73f177f8eba1b4459c6c4f7','b167d0cd9755817ffa421f9ad16eb2f9eeb6d78dcfdab826115d0719d000e152');
INSERT INTO "events" VALUES(20,'2026-10-05T08:22:47Z','20261005T082237Z-trend','decision','{"action": "BUY", "code": "TREND_BUY", "key": "2026-10-05:001:trend:SHY:TREND_BUY", "reason": "month-end trend rebalance; SHY: unallocated capital held in short-term Treasuries", "ticker": "SHY"}','b167d0cd9755817ffa421f9ad16eb2f9eeb6d78dcfdab826115d0719d000e152','c7a11980fbd6805f82fa09c473c2fe001054b0373a275623fa13403ed9e14a11');
INSERT INTO "events" VALUES(21,'2026-10-05T08:22:47Z','20261005T082237Z-trend','decision','{"action": "BUY", "code": "TREND_BUY", "key": "2026-10-05:002:trend:SPY:TREND_BUY", "reason": "month-end trend rebalance; SPY: above [8, 10, 12]-month averages", "ticker": "SPY"}','c7a11980fbd6805f82fa09c473c2fe001054b0373a275623fa13403ed9e14a11','fd0bcab1d31381e8172927398d57f7cf9bce457e1c1fd41a9d42ebc115f16100');
INSERT INTO "events" VALUES(22,'2026-10-05T08:22:47Z','20261005T082237Z-trend','order','{"key": "2026-10-05:trend:EFA:BUY:TREND_BUY", "notional": 19.701, "qty": null, "reason": "month-end trend rebalance; EFA: above [8, 10, 12]-month averages", "session": "2026-10-05", "side": "BUY", "ticker": "EFA", "type": "MOO"}','fd0bcab1d31381e8172927398d57f7cf9bce457e1c1fd41a9d42ebc115f16100','bfa13fd4cf6d7b836d9c9cf628f7d7e616147f65cfdc599806ea9bd2b4e0297f');
INSERT INTO "events" VALUES(23,'2026-10-05T08:22:47Z','20261005T082237Z-trend','order','{"key": "2026-10-05:trend:SHY:BUY:TREND_BUY", "notional": 59.103, "qty": null, "reason": "month-end trend rebalance; SHY: unallocated capital held in short-term Treasuries", "session": "2026-10-05", "side": "BUY", "ticker": "SHY", "type": "MOO"}','bfa13fd4cf6d7b836d9c9cf628f7d7e616147f65cfdc599806ea9bd2b4e0297f','86bb2ff9c7d780e64d92a177725fbb8815666d647a8ae7167f1f7bda33cdf258');
INSERT INTO "events" VALUES(24,'2026-10-05T08:22:47Z','20261005T082237Z-trend','order','{"key": "2026-10-05:trend:SPY:BUY:TREND_BUY", "notional": 19.701, "qty": null, "reason": "month-end trend rebalance; SPY: above [8, 10, 12]-month averages", "session": "2026-10-05", "side": "BUY", "ticker": "SPY", "type": "MOO"}','86bb2ff9c7d780e64d92a177725fbb8815666d647a8ae7167f1f7bda33cdf258','881b376396214e4de5f157fa13595d2268a57582c4e3e045da4ffe2d705b732b');
INSERT INTO "events" VALUES(25,'2026-10-05T08:22:47Z','20261005T082237Z-trend','decision','{"action": "INFO", "code": "DECIDED", "key": "decide:2026-10-05", "reason": "3 orders (MOO) for 2026-10-05; rebalance=True; trend weights SPY 20%, EFA 20%", "ticker": "*"}','881b376396214e4de5f157fa13595d2268a57582c4e3e045da4ffe2d705b732b','486ef72d09b58ab974d26669a28d2f9eb2104f4d79cec08e2514f22c29b11fa6');
CREATE TABLE experiment (
  id INTEGER PRIMARY KEY CHECK (id = 1),
  frozen_at TEXT NOT NULL, start_date TEXT NOT NULL, end_date TEXT NOT NULL,
  starting_cash REAL NOT NULL, strategy_version TEXT NOT NULL,
  strategy_sha256 TEXT NOT NULL, universe_sha256 TEXT NOT NULL, report_days TEXT NOT NULL, notes TEXT
);
INSERT INTO "experiment" VALUES(1,'2026-10-05T08:21:09Z','2026-10-05','2026-10-22',100.0,'trend-1.0.0','7ca9ab6e33f01b928a7edd3f963091f363563fc20b6c2aba8617cc23587f4d8e','172ba39de91f49af21ee2539df0b42cd5d6aa9c7afbd426114cb33bba2c27afa','[7, 14, 21, 28, 30]','book=trend; strategy=config/strategy_trend_v1.json');
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
INSERT INTO "orders" VALUES('2026-10-05:trend:EFA:BUY:TREND_BUY','2026-10-05T08:22:37Z','20261005T082237Z-trend','EFA','BUY','MOO','2026-10-05','residual',19.701,NULL,50,'TREND_BUY','month-end trend rebalance; EFA: above [8, 10, 12]-month averages','{}','{}','OPEN',NULL,'2026-10-05T08:22:47Z');
INSERT INTO "orders" VALUES('2026-10-05:trend:SHY:BUY:TREND_BUY','2026-10-05T08:22:37Z','20261005T082237Z-trend','SHY','BUY','MOO','2026-10-05','residual',59.103,NULL,50,'TREND_BUY','month-end trend rebalance; SHY: unallocated capital held in short-term Treasuries','{}','{}','OPEN',NULL,'2026-10-05T08:22:47Z');
INSERT INTO "orders" VALUES('2026-10-05:trend:SPY:BUY:TREND_BUY','2026-10-05T08:22:37Z','20261005T082237Z-trend','SPY','BUY','MOO','2026-10-05','residual',19.701,NULL,50,'TREND_BUY','month-end trend rebalance; SPY: above [8, 10, 12]-month averages','{}','{}','OPEN',NULL,'2026-10-05T08:22:47Z');
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
INSERT INTO "runs" VALUES('20261005T082237Z-trend','2026-10-05T08:22:43Z','2026-10-05T08:22:47Z','OK','github-actions','closed 2026-09-23; closed 2026-09-24; closed 2026-09-25; closed 2026-09-28; closed 2026-09-29; closed 2026-09-30; closed 2026-10-01; closed 2026-10-02; missed decision window for 2026-09-23; missed decision window for 2026-09-24; missed decision window for 2026-09-25; missed decision window for 2026-09-28; missed decision window for 2026-09-29; missed decision window for 2026-09-30; missed decision window for 2026-10-01; missed decision window for 2026-10-02; decided for 2026-10-05: 3 orders (MOO), rebalance=True',NULL);
CREATE TABLE snapshots (
  session TEXT PRIMARY KEY, created_at TEXT NOT NULL, run_id TEXT, equity REAL NOT NULL,
  cash REAL NOT NULL, positions_value REAL NOT NULL, spy_bh_equity REAL, cash_bh_equity REAL,
  peak REAL NOT NULL, drawdown REAL NOT NULL, regime TEXT, risk_state TEXT, marks TEXT, holdings TEXT
);
INSERT INTO "snapshots" VALUES('2026-09-23','2026-10-05T08:22:37Z','20261005T082237Z-trend',100.0,100.0,0.0,9.92860839736302125e+01,100.0,100.0,0.0,NULL,'{"peak": 100.0, "pause_until": null, "halt_until": null, "drawdown": 0.0}','{"marks": {}, "flags": {}}','{}');
INSERT INTO "snapshots" VALUES('2026-09-24','2026-10-05T08:22:37Z','20261005T082237Z-trend',100.0,100.0,0.0,9.9204617571919357e+01,100.0,100.0,0.0,NULL,'{"peak": 100.0, "pause_until": null, "halt_until": null, "drawdown": 0.0}','{"marks": {}, "flags": {}}','{}');
INSERT INTO "snapshots" VALUES('2026-09-25','2026-10-05T08:22:37Z','20261005T082237Z-trend',100.0,100.0,0.0,99.743841175028,100.0,100.0,0.0,NULL,'{"peak": 100.0, "pause_until": null, "halt_until": null, "drawdown": 0.0}','{"marks": {}, "flags": {}}','{}');
INSERT INTO "snapshots" VALUES('2026-09-28','2026-10-05T08:22:37Z','20261005T082237Z-trend',100.0,100.0,0.0,9.90015987527749814e+01,100.0,100.0,0.0,NULL,'{"peak": 100.0, "pause_until": null, "halt_until": null, "drawdown": 0.0}','{"marks": {}, "flags": {}}','{}');
INSERT INTO "snapshots" VALUES('2026-09-29','2026-10-05T08:22:37Z','20261005T082237Z-trend',100.0,100.0,0.0,98.8192740728755,100.0,100.0,0.0,NULL,'{"peak": 100.0, "pause_until": null, "halt_until": null, "drawdown": 0.0}','{"marks": {}, "flags": {}}','{}');
INSERT INTO "snapshots" VALUES('2026-09-30','2026-10-05T08:22:37Z','20261005T082237Z-trend',100.0,100.0,0.0,9.86162552537311114e+01,100.0,100.0,0.0,NULL,'{"peak": 100.0, "pause_until": null, "halt_until": null, "drawdown": 0.0}','{"marks": {}, "flags": {}}','{}');
INSERT INTO "snapshots" VALUES('2026-10-01','2026-10-05T08:22:37Z','20261005T082237Z-trend',100.0,100.0,0.0,9.87921159748046733e+01,100.0,100.0,0.0,NULL,'{"peak": 100.0, "pause_until": null, "halt_until": null, "drawdown": 0.0}','{"marks": {}, "flags": {}}','{}');
INSERT INTO "snapshots" VALUES('2026-10-02','2026-10-05T08:22:37Z','20261005T082237Z-trend',100.0,100.0,0.0,9.95227248496713485e+01,100.0,100.0,0.0,NULL,'{"peak": 100.0, "pause_until": null, "halt_until": null, "drawdown": 0.0}','{"marks": {}, "flags": {}}','{}');
CREATE TABLE state (key TEXT PRIMARY KEY, value TEXT NOT NULL, updated_at TEXT NOT NULL);
INSERT INTO "state" VALUES('cash','100.0','2026-10-05T08:22:45Z');
INSERT INTO "state" VALUES('strategy_integrity_ok','true','2026-10-05T08:22:43Z');
INSERT INTO "state" VALUES('benchmark','{"ticker": "SPY", "qty": 0.12931074652496097, "entry_price": 773.3309310119628, "entry_session": "2026-09-23", "div_cash": 0.0, "note": "SPY bought at the first session''s official open with the same cost model"}','2026-10-05T08:22:45Z');
INSERT INTO "state" VALUES('open_done:2026-09-23','true','2026-10-05T08:22:45Z');
INSERT INTO "state" VALUES('risk','{"peak": 100.0, "pause_until": null, "halt_until": null, "drawdown": 0.0}','2026-10-05T08:22:45Z');
INSERT INTO "state" VALUES('last_closed_session','"2026-10-02"','2026-10-05T08:22:45Z');
INSERT INTO "state" VALUES('open_done:2026-09-24','true','2026-10-05T08:22:45Z');
INSERT INTO "state" VALUES('open_done:2026-09-25','true','2026-10-05T08:22:45Z');
INSERT INTO "state" VALUES('open_done:2026-09-28','true','2026-10-05T08:22:45Z');
INSERT INTO "state" VALUES('open_done:2026-09-29','true','2026-10-05T08:22:45Z');
INSERT INTO "state" VALUES('open_done:2026-09-30','true','2026-10-05T08:22:45Z');
INSERT INTO "state" VALUES('open_done:2026-10-01','true','2026-10-05T08:22:45Z');
INSERT INTO "state" VALUES('open_done:2026-10-02','true','2026-10-05T08:22:45Z');
INSERT INTO "state" VALUES('last_regime','"TREND"','2026-10-05T08:22:47Z');
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
INSERT INTO "sqlite_sequence" VALUES('events',25);
INSERT INTO "sqlite_sequence" VALUES('decisions',12);
COMMIT;
