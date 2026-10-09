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
INSERT INTO "decisions" VALUES(5,'decide:2026-10-06','20261005T220617Z-trend','2026-10-05T22:06:17Z','2026-10-05','2026-10-06','*','system','INFO','DECIDED','0 orders (MOO) for 2026-10-06; rebalance=False (monthly)','{"rebalance": false, "order_type": "MOO", "data_through": "2026-10-05", "detail": {}, "halted": false}','[]');
INSERT INTO "decisions" VALUES(6,'decide:2026-10-07','20261006T225728Z-trend','2026-10-06T22:57:28Z','2026-10-06','2026-10-07','*','system','INFO','DECIDED','0 orders (MOO) for 2026-10-07; rebalance=False (monthly)','{"rebalance": false, "order_type": "MOO", "data_through": "2026-10-06", "detail": {}, "halted": false}','[]');
INSERT INTO "decisions" VALUES(7,'decide:2026-10-08','20261007T204612Z-trend','2026-10-07T20:46:12Z','2026-10-07','2026-10-08','*','system','INFO','DECIDED','0 orders (MOO) for 2026-10-08; rebalance=False (monthly)','{"rebalance": false, "order_type": "MOO", "data_through": "2026-10-07", "detail": {}, "halted": false}','[]');
INSERT INTO "decisions" VALUES(8,'decide:2026-10-09','20261008T234842Z-trend','2026-10-08T23:48:42Z','2026-10-08','2026-10-09','*','system','INFO','DECIDED','0 orders (MOO) for 2026-10-09; rebalance=False (monthly)','{"rebalance": false, "order_type": "MOO", "data_through": "2026-10-08", "detail": {}, "halted": false}','[]');
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
INSERT INTO "events" VALUES(9,'2026-10-05T13:35:26Z','20261005T133519Z-trend','benchmark_init','{"entry_price": 771.1194231018065, "qty": 0.12968159924924827}','7c65e58093367a29c2466e35b2f9d5dde1a4cede4ba4dbe86080908ae64189b8','a47fa2eb584a91af4aee8f46a8e547c97b3ae33c8b882735fe2ea723a68cb865');
INSERT INTO "events" VALUES(10,'2026-10-05T13:35:26Z','20261005T133519Z-trend','fill','{"fill_price": 103.78259608383178, "key": "2026-10-05:trend:EFA:BUY:TREND_BUY", "price_time": "2026-10-05T09:30:00-04:00 (official open)", "qty": 0.189829, "ref_price": 103.70999908447266, "side": "BUY", "source": "yahoo_daily_open", "ticker": "EFA"}','a47fa2eb584a91af4aee8f46a8e547c97b3ae33c8b882735fe2ea723a68cb865','5951890e18c1535558722066abf12df8291870d5e4d3ef370138493d28c51a93');
INSERT INTO "events" VALUES(11,'2026-10-05T13:35:26Z','20261005T133519Z-trend','order_status','{"key": "2026-10-05:trend:EFA:BUY:TREND_BUY", "reason": "BUY 0.189829 EFA @ 103.7826", "status": "FILLED"}','5951890e18c1535558722066abf12df8291870d5e4d3ef370138493d28c51a93','5195782286a27804ba292f7f24bae00a109a18f4ba4f16a45c0525f3e7c8401c');
INSERT INTO "events" VALUES(12,'2026-10-05T13:35:26Z','20261005T133519Z-trend','fill','{"fill_price": 81.11673955688475, "key": "2026-10-05:trend:SHY:BUY:TREND_BUY", "price_time": "2026-10-05T09:30:00-04:00 (official open)", "qty": 0.728616, "ref_price": 81.05999755859375, "side": "BUY", "source": "yahoo_daily_open", "ticker": "SHY"}','5195782286a27804ba292f7f24bae00a109a18f4ba4f16a45c0525f3e7c8401c','6a3801be1d89495c100848f8d9fbbd44bf8531f8e39743befff3ac2dc62ad814');
INSERT INTO "events" VALUES(13,'2026-10-05T13:35:26Z','20261005T133519Z-trend','order_status','{"key": "2026-10-05:trend:SHY:BUY:TREND_BUY", "reason": "BUY 0.728616 SHY @ 81.1167", "status": "FILLED"}','6a3801be1d89495c100848f8d9fbbd44bf8531f8e39743befff3ac2dc62ad814','98b954bb1520186be9600f1819ac2179abcfba8e2fb4056a2b1820522d982a39');
INSERT INTO "events" VALUES(14,'2026-10-05T13:35:26Z','20261005T133519Z-trend','fill','{"fill_price": 771.1194231018065, "key": "2026-10-05:trend:SPY:BUY:TREND_BUY", "price_time": "2026-10-05T09:30:00-04:00 (official open)", "qty": 0.025548, "ref_price": 770.5800170898438, "side": "BUY", "source": "yahoo_daily_open", "ticker": "SPY"}','98b954bb1520186be9600f1819ac2179abcfba8e2fb4056a2b1820522d982a39','7135bdd08da359375567d222b3f220887439aacad3dfc7c6eec464403e4cccdd');
INSERT INTO "events" VALUES(15,'2026-10-05T13:35:26Z','20261005T133519Z-trend','order_status','{"key": "2026-10-05:trend:SPY:BUY:TREND_BUY", "reason": "BUY 0.025548 SPY @ 771.1194", "status": "FILLED"}','7135bdd08da359375567d222b3f220887439aacad3dfc7c6eec464403e4cccdd','1c7c824a703794bf129948c0ba059bc0e062053f5337dcacff8ab0a597fa47e1');
INSERT INTO "events" VALUES(16,'2026-10-05T22:07:44Z','20261005T220617Z-trend','snapshot','{"cash": 1.4955402376181937, "drawdown": 0.0, "equity": 100.11499476664042, "session": "2026-10-05", "spy_bh_equity": 100.4811957625333}','1c7c824a703794bf129948c0ba059bc0e062053f5337dcacff8ab0a597fa47e1','00352aec5e13627e67bd0eeea64c5e6ab75c24a27915b519bcfeae487b7ed342');
INSERT INTO "events" VALUES(17,'2026-10-05T22:07:46Z','20261005T220617Z-trend','decision','{"action": "INFO", "code": "DECIDED", "key": "decide:2026-10-06", "reason": "0 orders (MOO) for 2026-10-06; rebalance=False (monthly)", "ticker": "*"}','00352aec5e13627e67bd0eeea64c5e6ab75c24a27915b519bcfeae487b7ed342','fc74031c416a26259fb99ef533451a2c410cb31ee20a6750fd5b5502c4467807');
INSERT INTO "events" VALUES(18,'2026-10-06T22:58:54Z','20261006T225728Z-trend','snapshot','{"cash": 1.4955402376181937, "drawdown": 0.0, "equity": 100.29632493424296, "session": "2026-10-06", "spy_bh_equity": 101.03364064175697}','fc74031c416a26259fb99ef533451a2c410cb31ee20a6750fd5b5502c4467807','1063eaa7c9ed774ac447cd6856fcb1e1fbb194e89e0151a7240e2bd905369a07');
INSERT INTO "events" VALUES(19,'2026-10-06T22:58:56Z','20261006T225728Z-trend','decision','{"action": "INFO", "code": "DECIDED", "key": "decide:2026-10-07", "reason": "0 orders (MOO) for 2026-10-07; rebalance=False (monthly)", "ticker": "*"}','1063eaa7c9ed774ac447cd6856fcb1e1fbb194e89e0151a7240e2bd905369a07','70ed1ec71c1cd06260a3e6ad33c4fc6aa7141227aac9025812d908fe557faab3');
INSERT INTO "events" VALUES(20,'2026-10-07T20:47:28Z','20261007T204612Z-trend','snapshot','{"cash": 1.4955402376181937, "drawdown": 0.0023781733442606035, "equity": 100.05780288775705, "session": "2026-10-07", "spy_bh_equity": 100.79112876923514}','70ed1ec71c1cd06260a3e6ad33c4fc6aa7141227aac9025812d908fe557faab3','d63bfae08cf1f1d7175dd2db5db4cfda959dd1f4c82cce190281d8a1dcdcb81e');
INSERT INTO "events" VALUES(21,'2026-10-07T20:47:29Z','20261007T204612Z-trend','decision','{"action": "INFO", "code": "DECIDED", "key": "decide:2026-10-08", "reason": "0 orders (MOO) for 2026-10-08; rebalance=False (monthly)", "ticker": "*"}','d63bfae08cf1f1d7175dd2db5db4cfda959dd1f4c82cce190281d8a1dcdcb81e','e5731d77c55edfdf516aa6ef57016b184433768ed1f946a4f56df41e6a5f8d17');
INSERT INTO "events" VALUES(22,'2026-10-08T23:50:32Z','20261008T234842Z-trend','snapshot','{"cash": 1.4955402376181937, "drawdown": 0.0036827525520777282, "equity": 99.92695838762737, "session": "2026-10-08", "spy_bh_equity": 100.3644791571543}','e5731d77c55edfdf516aa6ef57016b184433768ed1f946a4f56df41e6a5f8d17','085b13b3b796737f42edfa686f3c2986eaef8a469292e5f63e0d667ab0c163aa');
INSERT INTO "events" VALUES(23,'2026-10-08T23:50:34Z','20261008T234842Z-trend','decision','{"action": "INFO", "code": "DECIDED", "key": "decide:2026-10-09", "reason": "0 orders (MOO) for 2026-10-09; rebalance=False (monthly)", "ticker": "*"}','085b13b3b796737f42edfa686f3c2986eaef8a469292e5f63e0d667ab0c163aa','23ab0cca785331eb45c0cb61315d0184808d41d8d3556a2e3870251718898bca');
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
INSERT INTO "fills" VALUES(1,'2026-10-05:trend:EFA:BUY:TREND_BUY','20261005T133519Z-trend','2026-10-05T13:35:26Z','2026-10-05','EFA','BUY',0.189829,1.03709999084472656e+02,1.03782596083831776e+02,7.0,1.37810157913425181e-02,'2026-10-05T09:30:00-04:00 (official open)','yahoo_daily_open','residual','TREND_BUY','month-end trend rebalance; EFA: above [8, 10, 12]-month averages',NULL);
INSERT INTO "fills" VALUES(2,'2026-10-05:trend:SHY:BUY:TREND_BUY','20261005T133519Z-trend','2026-10-05T13:35:26Z','2026-10-05','SHY','BUY',0.728616,8.105999755859375e+01,8.11167395568847524e+01,7.0,4.13431278267970478e-02,'2026-10-05T09:30:00-04:00 (official open)','yahoo_daily_open','residual','TREND_BUY','month-end trend rebalance; SHY: unallocated capital held in short-term Treasuries',NULL);
INSERT INTO "fills" VALUES(3,'2026-10-05:trend:SPY:BUY:TREND_BUY','20261005T133519Z-trend','2026-10-05T13:35:26Z','2026-10-05','SPY','BUY',0.025548,7.7058001708984375e+02,7.71119423101806546e+02,7.0,1.37807447936255274e-02,'2026-10-05T09:30:00-04:00 (official open)','yahoo_daily_open','residual','TREND_BUY','month-end trend rebalance; SPY: above [8, 10, 12]-month averages',NULL);
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
INSERT INTO "orders" VALUES('2026-10-05:trend:EFA:BUY:TREND_BUY','2026-10-05T08:25:13Z','20261005T082513Z-trend','EFA','BUY','MOO','2026-10-05','residual',19.701,NULL,50,'TREND_BUY','month-end trend rebalance; EFA: above [8, 10, 12]-month averages','{}','{}','FILLED','BUY 0.189829 EFA @ 103.7826','2026-10-05T13:35:26Z');
INSERT INTO "orders" VALUES('2026-10-05:trend:SHY:BUY:TREND_BUY','2026-10-05T08:25:13Z','20261005T082513Z-trend','SHY','BUY','MOO','2026-10-05','residual',59.103,NULL,50,'TREND_BUY','month-end trend rebalance; SHY: unallocated capital held in short-term Treasuries','{}','{}','FILLED','BUY 0.728616 SHY @ 81.1167','2026-10-05T13:35:26Z');
INSERT INTO "orders" VALUES('2026-10-05:trend:SPY:BUY:TREND_BUY','2026-10-05T08:25:13Z','20261005T082513Z-trend','SPY','BUY','MOO','2026-10-05','residual',19.701,NULL,50,'TREND_BUY','month-end trend rebalance; SPY: above [8, 10, 12]-month averages','{}','{}','FILLED','BUY 0.025548 SPY @ 771.1194','2026-10-05T13:35:26Z');
CREATE TABLE positions (
  ticker TEXT PRIMARY KEY, qty REAL NOT NULL, avg_cost REAL NOT NULL, sleeve TEXT NOT NULL,
  entry_session TEXT NOT NULL, entry_price REAL NOT NULL, initial_stop REAL, trail_pct REAL,
  high_water REAL NOT NULL, max_hold_until TEXT, stop_checked_through TEXT, meta TEXT
);
INSERT INTO "positions" VALUES('EFA',0.189829,1.03782596083831776e+02,'residual','2026-10-05',1.03782596083831776e+02,NULL,NULL,1.04699996948242187e+02,NULL,'2026-10-09T11:45:00-04:00','{}');
INSERT INTO "positions" VALUES('SHY',0.728616,8.11167395568847524e+01,'residual','2026-10-05',8.11167395568847524e+01,NULL,NULL,81.2300033569336,NULL,'2026-10-09T11:45:00-04:00','{}');
INSERT INTO "positions" VALUES('SPY',0.025548,7.71119423101806546e+02,'residual','2026-10-05',7.71119423101806546e+02,NULL,NULL,7.816199951171875e+02,NULL,'2026-10-09T11:45:00-04:00','{}');
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
INSERT INTO "runs" VALUES('20261005T090639Z-trend','2026-10-05T09:06:46Z','2026-10-05T09:06:46Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T092733Z-trend','2026-10-05T09:27:39Z','2026-10-05T09:27:39Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T094822Z-trend','2026-10-05T09:48:29Z','2026-10-05T09:48:29Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T100902Z-trend','2026-10-05T10:09:09Z','2026-10-05T10:09:09Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T102935Z-trend','2026-10-05T10:29:41Z','2026-10-05T10:29:41Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T105106Z-trend','2026-10-05T10:51:13Z','2026-10-05T10:51:13Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T111119Z-trend','2026-10-05T11:11:25Z','2026-10-05T11:11:25Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T113214Z-trend','2026-10-05T11:32:20Z','2026-10-05T11:32:20Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T115303Z-trend','2026-10-05T11:53:09Z','2026-10-05T11:53:09Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T121343Z-trend','2026-10-05T12:13:48Z','2026-10-05T12:13:48Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T133519Z-trend','2026-10-05T13:35:26Z','2026-10-05T13:35:26Z','OK','github-actions','FILL BUY EFA 0.1898 @ 103.78 (TREND_BUY); FILL BUY SHY 0.7286 @ 81.12 (TREND_BUY); FILL BUY SPY 0.0255 @ 771.12 (TREND_BUY)',NULL);
INSERT INTO "runs" VALUES('20261005T134019Z-trend','2026-10-05T13:41:16Z','2026-10-05T13:41:16Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T134519Z-trend','2026-10-05T13:45:25Z','2026-10-05T13:45:25Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T135019Z-trend','2026-10-05T13:50:25Z','2026-10-05T13:50:25Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T135519Z-trend','2026-10-05T13:55:25Z','2026-10-05T13:55:25Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T135642Z-trend','2026-10-05T13:56:48Z','2026-10-05T13:56:49Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T140142Z-trend','2026-10-05T14:01:49Z','2026-10-05T14:01:49Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T140642Z-trend','2026-10-05T14:06:49Z','2026-10-05T14:06:49Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T141142Z-trend','2026-10-05T14:11:48Z','2026-10-05T14:11:48Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T141642Z-trend','2026-10-05T14:16:50Z','2026-10-05T14:16:50Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T141811Z-trend','2026-10-05T14:18:20Z','2026-10-05T14:18:21Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T142311Z-trend','2026-10-05T14:23:19Z','2026-10-05T14:23:19Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T142811Z-trend','2026-10-05T14:28:19Z','2026-10-05T14:28:19Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T143311Z-trend','2026-10-05T14:33:19Z','2026-10-05T14:33:19Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T143811Z-trend','2026-10-05T14:38:18Z','2026-10-05T14:38:19Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T143934Z-trend','2026-10-05T14:39:41Z','2026-10-05T14:39:41Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T144434Z-trend','2026-10-05T14:44:40Z','2026-10-05T14:44:40Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T144934Z-trend','2026-10-05T14:49:46Z','2026-10-05T14:49:47Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T145434Z-trend','2026-10-05T14:54:41Z','2026-10-05T14:54:41Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T145934Z-trend','2026-10-05T14:59:39Z','2026-10-05T14:59:39Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T150055Z-trend','2026-10-05T15:01:02Z','2026-10-05T15:01:02Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T150555Z-trend','2026-10-05T15:06:03Z','2026-10-05T15:06:03Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T151055Z-trend','2026-10-05T15:11:02Z','2026-10-05T15:11:03Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T151555Z-trend','2026-10-05T15:16:03Z','2026-10-05T15:16:03Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T152055Z-trend','2026-10-05T15:21:04Z','2026-10-05T15:21:04Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T152221Z-trend','2026-10-05T15:22:29Z','2026-10-05T15:22:29Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T152721Z-trend','2026-10-05T15:27:29Z','2026-10-05T15:27:29Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T153221Z-trend','2026-10-05T15:32:28Z','2026-10-05T15:32:28Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T153721Z-trend','2026-10-05T15:37:28Z','2026-10-05T15:37:28Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T154221Z-trend','2026-10-05T15:42:27Z','2026-10-05T15:42:27Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T154344Z-trend','2026-10-05T15:43:50Z','2026-10-05T15:43:51Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T154844Z-trend','2026-10-05T15:48:51Z','2026-10-05T15:48:51Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T155344Z-trend','2026-10-05T15:53:51Z','2026-10-05T15:53:51Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T155844Z-trend','2026-10-05T15:58:49Z','2026-10-05T15:58:49Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T160344Z-trend','2026-10-05T16:03:53Z','2026-10-05T16:03:53Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T160516Z-trend','2026-10-05T16:05:25Z','2026-10-05T16:05:26Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T161016Z-trend','2026-10-05T16:10:24Z','2026-10-05T16:10:24Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T161516Z-trend','2026-10-05T16:15:24Z','2026-10-05T16:15:24Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T162016Z-trend','2026-10-05T16:20:24Z','2026-10-05T16:20:24Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T162516Z-trend','2026-10-05T16:25:23Z','2026-10-05T16:25:24Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T162642Z-trend','2026-10-05T16:26:49Z','2026-10-05T16:26:50Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T163142Z-trend','2026-10-05T16:31:49Z','2026-10-05T16:31:49Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T163642Z-trend','2026-10-05T16:36:49Z','2026-10-05T16:36:49Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T164142Z-trend','2026-10-05T16:41:49Z','2026-10-05T16:41:50Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T164642Z-trend','2026-10-05T16:46:49Z','2026-10-05T16:46:49Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T164806Z-trend','2026-10-05T16:48:13Z','2026-10-05T16:48:14Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T165306Z-trend','2026-10-05T16:53:12Z','2026-10-05T16:53:12Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T165806Z-trend','2026-10-05T16:58:11Z','2026-10-05T16:58:11Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T172537Z-trend','2026-10-05T17:25:44Z','2026-10-05T17:25:44Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T220617Z-trend','2026-10-05T22:07:42Z','2026-10-05T22:07:46Z','OK','github-actions','closed 2026-10-05; decided for 2026-10-06: 0 orders (MOO), rebalance=False',NULL);
INSERT INTO "runs" VALUES('20261005T222657Z-trend','2026-10-05T22:27:12Z','2026-10-05T22:27:12Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T224741Z-trend','2026-10-05T22:47:48Z','2026-10-05T22:47:48Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261006T011528Z-trend','2026-10-06T01:15:35Z','2026-10-06T01:15:35Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261006T012613Z-trend','2026-10-06T01:26:20Z','2026-10-06T01:26:20Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261006T014518Z-trend','2026-10-06T01:45:25Z','2026-10-06T01:45:25Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261006T015548Z-trend','2026-10-06T01:55:53Z','2026-10-06T01:55:53Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261006T025726Z-trend','2026-10-06T02:57:32Z','2026-10-06T02:57:32Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261006T092627Z-trend','2026-10-06T09:26:33Z','2026-10-06T09:26:33Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261006T161726Z-trend','2026-10-06T16:18:16Z','2026-10-06T16:18:17Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261006T162226Z-trend','2026-10-06T16:22:33Z','2026-10-06T16:22:33Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261006T162726Z-trend','2026-10-06T16:27:33Z','2026-10-06T16:27:33Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261006T163226Z-trend','2026-10-06T16:32:33Z','2026-10-06T16:32:33Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261006T163726Z-trend','2026-10-06T16:37:32Z','2026-10-06T16:37:32Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261006T163850Z-trend','2026-10-06T16:38:56Z','2026-10-06T16:38:56Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261006T164350Z-trend','2026-10-06T16:43:56Z','2026-10-06T16:43:56Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261006T164850Z-trend','2026-10-06T16:48:57Z','2026-10-06T16:48:57Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261006T165350Z-trend','2026-10-06T16:53:55Z','2026-10-06T16:53:56Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261006T165850Z-trend','2026-10-06T16:58:54Z','2026-10-06T16:58:54Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261006T185128Z-trend','2026-10-06T18:51:35Z','2026-10-06T18:51:35Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261006T225728Z-trend','2026-10-06T22:58:53Z','2026-10-06T22:58:56Z','OK','github-actions','closed 2026-10-06; decided for 2026-10-07: 0 orders (MOO), rebalance=False',NULL);
INSERT INTO "runs" VALUES('20261006T234249Z-trend','2026-10-06T23:42:54Z','2026-10-06T23:42:54Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261007T000539Z-trend','2026-10-07T00:05:46Z','2026-10-07T00:05:46Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261007T003908Z-trend','2026-10-07T00:39:13Z','2026-10-07T00:39:13Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261007T010211Z-trend','2026-10-07T01:02:17Z','2026-10-07T01:02:17Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261007T022147Z-trend','2026-10-07T02:21:55Z','2026-10-07T02:21:55Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261007T074356Z-trend','2026-10-07T07:44:01Z','2026-10-07T07:44:01Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261007T142234Z-trend','2026-10-07T14:23:28Z','2026-10-07T14:23:28Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261007T142734Z-trend','2026-10-07T14:27:41Z','2026-10-07T14:27:42Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261007T143234Z-trend','2026-10-07T14:32:41Z','2026-10-07T14:32:41Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261007T143734Z-trend','2026-10-07T14:37:40Z','2026-10-07T14:37:40Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261007T144234Z-trend','2026-10-07T14:42:40Z','2026-10-07T14:42:41Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261007T144358Z-trend','2026-10-07T14:44:03Z','2026-10-07T14:44:04Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261007T144857Z-trend','2026-10-07T14:49:04Z','2026-10-07T14:49:04Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261007T145357Z-trend','2026-10-07T14:54:06Z','2026-10-07T14:54:06Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261007T145857Z-trend','2026-10-07T14:59:02Z','2026-10-07T14:59:02Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261007T150357Z-trend','2026-10-07T15:04:04Z','2026-10-07T15:04:04Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261007T150526Z-trend','2026-10-07T15:05:35Z','2026-10-07T15:05:35Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261007T151026Z-trend','2026-10-07T15:10:34Z','2026-10-07T15:10:34Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261007T151526Z-trend','2026-10-07T15:15:33Z','2026-10-07T15:15:33Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261007T152026Z-trend','2026-10-07T15:20:35Z','2026-10-07T15:20:35Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261007T152526Z-trend','2026-10-07T15:25:34Z','2026-10-07T15:25:34Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261007T152744Z-trend','2026-10-07T15:27:53Z','2026-10-07T15:27:53Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261007T153112Z-trend','2026-10-07T15:31:20Z','2026-10-07T15:31:21Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261007T153612Z-trend','2026-10-07T15:36:20Z','2026-10-07T15:36:20Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261007T154112Z-trend','2026-10-07T15:41:19Z','2026-10-07T15:41:19Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261007T154612Z-trend','2026-10-07T15:46:19Z','2026-10-07T15:46:19Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261007T155112Z-trend','2026-10-07T15:51:19Z','2026-10-07T15:51:20Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261007T155308Z-trend','2026-10-07T15:53:14Z','2026-10-07T15:53:15Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261007T155808Z-trend','2026-10-07T15:58:12Z','2026-10-07T15:58:13Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261007T160308Z-trend','2026-10-07T16:03:15Z','2026-10-07T16:03:15Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261007T160808Z-trend','2026-10-07T16:08:15Z','2026-10-07T16:08:15Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261007T161308Z-trend','2026-10-07T16:13:14Z','2026-10-07T16:13:15Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261007T161442Z-trend','2026-10-07T16:14:49Z','2026-10-07T16:14:49Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261007T161942Z-trend','2026-10-07T16:19:52Z','2026-10-07T16:19:52Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261007T162442Z-trend','2026-10-07T16:24:49Z','2026-10-07T16:24:50Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261007T162942Z-trend','2026-10-07T16:29:48Z','2026-10-07T16:29:48Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261007T163442Z-trend','2026-10-07T16:34:49Z','2026-10-07T16:34:50Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261007T204612Z-trend','2026-10-07T20:47:26Z','2026-10-07T20:47:29Z','OK','github-actions','closed 2026-10-07; decided for 2026-10-08: 0 orders (MOO), rebalance=False',NULL);
INSERT INTO "runs" VALUES('20261007T214343Z-trend','2026-10-07T21:43:49Z','2026-10-07T21:43:49Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261008T001042Z-trend','2026-10-08T00:10:48Z','2026-10-08T00:10:48Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261008T002423Z-trend','2026-10-08T00:24:29Z','2026-10-08T00:24:29Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261008T010021Z-trend','2026-10-08T01:00:27Z','2026-10-08T01:00:27Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261008T011955Z-trend','2026-10-08T01:20:01Z','2026-10-08T01:20:01Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261008T024148Z-trend','2026-10-08T02:41:53Z','2026-10-08T02:41:53Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261008T075925Z-trend','2026-10-08T07:59:28Z','2026-10-08T07:59:28Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261008T155221Z-trend','2026-10-08T15:53:15Z','2026-10-08T15:53:15Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261008T155721Z-trend','2026-10-08T15:57:27Z','2026-10-08T15:57:27Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261008T160221Z-trend','2026-10-08T16:02:29Z','2026-10-08T16:02:29Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261008T160721Z-trend','2026-10-08T16:07:29Z','2026-10-08T16:07:30Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261008T161221Z-trend','2026-10-08T16:12:28Z','2026-10-08T16:12:28Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261008T161349Z-trend','2026-10-08T16:13:55Z','2026-10-08T16:13:55Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261008T161849Z-trend','2026-10-08T16:18:57Z','2026-10-08T16:18:57Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261008T162349Z-trend','2026-10-08T16:23:55Z','2026-10-08T16:23:55Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261008T162849Z-trend','2026-10-08T16:28:54Z','2026-10-08T16:28:55Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261008T163349Z-trend','2026-10-08T16:33:56Z','2026-10-08T16:33:56Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261008T163521Z-trend','2026-10-08T16:35:35Z','2026-10-08T16:35:36Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261008T164022Z-trend','2026-10-08T16:40:33Z','2026-10-08T16:40:34Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261008T164522Z-trend','2026-10-08T16:45:35Z','2026-10-08T16:45:35Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261008T165022Z-trend','2026-10-08T16:50:34Z','2026-10-08T16:50:35Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261008T165521Z-trend','2026-10-08T16:55:33Z','2026-10-08T16:55:34Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261008T191442Z-trend','2026-10-08T19:14:50Z','2026-10-08T19:14:50Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261008T234842Z-trend','2026-10-08T23:50:30Z','2026-10-08T23:50:34Z','OK','github-actions','closed 2026-10-08; decided for 2026-10-09: 0 orders (MOO), rebalance=False',NULL);
INSERT INTO "runs" VALUES('20261009T001928Z-trend','2026-10-09T00:19:35Z','2026-10-09T00:19:35Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261009T003813Z-trend','2026-10-09T00:38:19Z','2026-10-09T00:38:19Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261009T011421Z-trend','2026-10-09T01:14:27Z','2026-10-09T01:14:27Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261009T012731Z-trend','2026-10-09T01:27:37Z','2026-10-09T01:27:37Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261009T025621Z-trend','2026-10-09T02:56:27Z','2026-10-09T02:56:27Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261009T080112Z-trend','2026-10-09T08:01:20Z','2026-10-09T08:01:20Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261009T153448Z-trend','2026-10-09T15:35:58Z','2026-10-09T15:35:58Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261009T153948Z-trend','2026-10-09T15:39:54Z','2026-10-09T15:39:55Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261009T154448Z-trend','2026-10-09T15:44:53Z','2026-10-09T15:44:55Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261009T154948Z-trend','2026-10-09T15:49:55Z','2026-10-09T15:49:56Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261009T155448Z-trend','2026-10-09T15:54:55Z','2026-10-09T15:54:55Z','OK','github-actions','no action needed',NULL);
CREATE TABLE snapshots (
  session TEXT PRIMARY KEY, created_at TEXT NOT NULL, run_id TEXT, equity REAL NOT NULL,
  cash REAL NOT NULL, positions_value REAL NOT NULL, spy_bh_equity REAL, cash_bh_equity REAL,
  peak REAL NOT NULL, drawdown REAL NOT NULL, regime TEXT, risk_state TEXT, marks TEXT, holdings TEXT
);
INSERT INTO "snapshots" VALUES('2026-10-05','2026-10-05T22:06:17Z','20261005T220617Z-trend',1.00114994766640421e+02,1.49554023761819365e+00,9.86194545290222208e+01,1.00481195762533303e+02,100.0,1.00114994766640421e+02,0.0,'TREND','{"peak": 100.11499476664042, "pause_until": null, "halt_until": null, "drawdown": 0.0}','{"marks": {"EFA": 104.02999877929688, "SHY": 81.08000183105469, "SPY": 774.8300170898438}, "flags": {}}','{"EFA": {"qty": 0.189829, "avg_cost": 103.78259608383178, "sleeve": "residual", "stop": null, "entry_session": "2026-10-05", "max_hold_until": null}, "SHY": {"qty": 0.728616, "avg_cost": 81.11673955688475, "sleeve": "residual", "stop": null, "entry_session": "2026-10-05", "max_hold_until": null}, "SPY": {"qty": 0.025548, "avg_cost": 771.1194231018065, "sleeve": "residual", "stop": null, "entry_session": "2026-10-05", "max_hold_until": null}}');
INSERT INTO "snapshots" VALUES('2026-10-06','2026-10-06T22:57:28Z','20261006T225728Z-trend',1.0029632493424296e+02,1.49554023761819365e+00,9.88007846966247598e+01,1.01033640641756974e+02,100.0,1.0029632493424296e+02,0.0,'TREND','{"peak": 100.29632493424296, "pause_until": null, "halt_until": null, "drawdown": 0.0}','{"marks": {"EFA": 104.22000122070312, "SHY": 81.12999725341797, "SPY": 779.0900268554688}, "flags": {}}','{"EFA": {"qty": 0.189829, "avg_cost": 103.78259608383178, "sleeve": "residual", "stop": null, "entry_session": "2026-10-05", "max_hold_until": null}, "SHY": {"qty": 0.728616, "avg_cost": 81.11673955688475, "sleeve": "residual", "stop": null, "entry_session": "2026-10-05", "max_hold_until": null}, "SPY": {"qty": 0.025548, "avg_cost": 771.1194231018065, "sleeve": "residual", "stop": null, "entry_session": "2026-10-05", "max_hold_until": null}}');
INSERT INTO "snapshots" VALUES('2026-10-07','2026-10-07T20:46:12Z','20261007T204612Z-trend',1.00057802887757048e+02,1.49554023761819365e+00,9.85622626501388481e+01,1.00791128769235143e+02,100.0,1.0029632493424296e+02,2.37817334426060345e-03,'TREND','{"peak": 100.29632493424296, "pause_until": null, "halt_until": null, "drawdown": 0.0023781733442606035}','{"marks": {"EFA": 103.0999984741211, "SHY": 81.16000366210938, "SPY": 777.219970703125}, "flags": {}}','{"EFA": {"qty": 0.189829, "avg_cost": 103.78259608383178, "sleeve": "residual", "stop": null, "entry_session": "2026-10-05", "max_hold_until": null}, "SHY": {"qty": 0.728616, "avg_cost": 81.11673955688475, "sleeve": "residual", "stop": null, "entry_session": "2026-10-05", "max_hold_until": null}, "SPY": {"qty": 0.025548, "avg_cost": 771.1194231018065, "sleeve": "residual", "stop": null, "entry_session": "2026-10-05", "max_hold_until": null}}');
INSERT INTO "snapshots" VALUES('2026-10-08','2026-10-08T23:48:42Z','20261008T234842Z-trend',9.99269583876273657e+01,1.49554023761819365e+00,9.84314181500091649e+01,1.00364479157154306e+02,100.0,1.0029632493424296e+02,3.68275255207772822e-03,'TREND','{"peak": 100.29632493424296, "pause_until": null, "halt_until": null, "drawdown": 0.0036827525520777282}','{"marks": {"EFA": 102.69999694824219, "SHY": 81.19999694824219, "SPY": 773.9299926757812}, "flags": {}}','{"EFA": {"qty": 0.189829, "avg_cost": 103.78259608383178, "sleeve": "residual", "stop": null, "entry_session": "2026-10-05", "max_hold_until": null}, "SHY": {"qty": 0.728616, "avg_cost": 81.11673955688475, "sleeve": "residual", "stop": null, "entry_session": "2026-10-05", "max_hold_until": null}, "SPY": {"qty": 0.025548, "avg_cost": 771.1194231018065, "sleeve": "residual", "stop": null, "entry_session": "2026-10-05", "max_hold_until": null}}');
CREATE TABLE state (key TEXT PRIMARY KEY, value TEXT NOT NULL, updated_at TEXT NOT NULL);
INSERT INTO "state" VALUES('cash','1.4955402376181937','2026-10-09T15:54:55Z');
INSERT INTO "state" VALUES('strategy_integrity_ok','true','2026-10-09T15:54:55Z');
INSERT INTO "state" VALUES('last_regime','"TREND"','2026-10-08T23:50:34Z');
INSERT INTO "state" VALUES('benchmark','{"ticker": "SPY", "qty": 0.12968159924924827, "entry_price": 771.1194231018065, "entry_session": "2026-10-05", "div_cash": 0.0, "note": "SPY bought at the first session''s official open with the same cost model"}','2026-10-05T13:35:26Z');
INSERT INTO "state" VALUES('open_done:2026-10-05','true','2026-10-05T13:35:26Z');
INSERT INTO "state" VALUES('live_marks','{"as_of": "2026-10-09T15:54:48Z", "marks": {"EFA": [103.08000183105469, "2026-10-09T11:45:00-04:00"], "SHY": [81.17500305175781, "2026-10-09T11:45:00-04:00"], "SPY": [777.1900024414062, "2026-10-09T11:45:00-04:00"]}}','2026-10-09T15:54:55Z');
INSERT INTO "state" VALUES('risk','{"peak": 100.29632493424296, "pause_until": null, "halt_until": null, "drawdown": 0.0036827525520777282}','2026-10-08T23:50:32Z');
INSERT INTO "state" VALUES('last_closed_session','"2026-10-08"','2026-10-08T23:50:32Z');
INSERT INTO "state" VALUES('open_done:2026-10-06','true','2026-10-06T16:18:17Z');
INSERT INTO "state" VALUES('open_done:2026-10-07','true','2026-10-07T14:23:28Z');
INSERT INTO "state" VALUES('open_done:2026-10-08','true','2026-10-08T15:53:15Z');
INSERT INTO "state" VALUES('open_done:2026-10-09','true','2026-10-09T15:35:58Z');
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
INSERT INTO "sqlite_sequence" VALUES('events',23);
INSERT INTO "sqlite_sequence" VALUES('decisions',8);
INSERT INTO "sqlite_sequence" VALUES('fills',3);
COMMIT;
