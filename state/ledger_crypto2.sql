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
INSERT INTO "decisions" VALUES(1,'pm:scan:2026-09-25T20:10:27Z','20260925T201027Z-crypto2','2026-09-25T20:10:27Z','2026-09-25T20:10:27Z','2026-09-25','*','predmarket','INFO','PM_SCAN','scanned 6 live markets; 0 bet(s).','{"scanned": [{"market": "btc-updown-15m-1790366400", "mid_up": 0.07500000000000001, "model_up": 0.316, "result": "model 32% vs market 8%: too far apart, treated as model error"}, {"market": "bitcoin-up-or-down-september-25-2026-4pm-et", "mid_up": 0.395, "model_up": 0.443, "result": "best edge -0.044 below 0.04"}, {"market": "btc-updown-4h-1790366400", "mid_up": 0.415, "model_up": 0, "result": "outside entry timing (4% of window elapsed)"}, {"market": "eth-updown-15m-1790366400", "mid_up": 0.125, "model_up": 0.266, "result": "no side priced between the allowed 30c-75c"}, {"market": "ethereum-up-or-down-september-25-2026-4pm-et", "mid_up": 0.405, "model_up": 0.425, "result": "best edge -0.057 below 0.04"}, {"market": "eth-updown-4h-1790366400", "mid_up": 0.43, "model_up": 0, "result": "outside entry timing (4% of window elapsed)"}]}','[]');
INSERT INTO "decisions" VALUES(2,'pm:scan:2026-09-25T20:26:49Z','20260925T202649Z-crypto2','2026-09-25T20:26:49Z','2026-09-25T20:26:49Z','2026-09-25','*','predmarket','INFO','PM_SCAN','scanned 6 live markets; 0 bet(s).','{"scanned": [{"market": "btc-updown-15m-1790367300", "mid_up": 0.9884999999999999, "model_up": 0, "result": "outside entry timing (79% of window elapsed)"}, {"market": "bitcoin-up-or-down-september-25-2026-4pm-et", "mid_up": 0.665, "model_up": 0.593, "result": "best edge -0.038 below 0.04"}, {"market": "btc-updown-4h-1790366400", "mid_up": 0.595, "model_up": 0.537, "result": "best edge -0.015 below 0.04"}, {"market": "eth-updown-15m-1790367300", "mid_up": 0.9955, "model_up": 0, "result": "outside entry timing (79% of window elapsed)"}, {"market": "ethereum-up-or-down-september-25-2026-4pm-et", "mid_up": 0.595, "model_up": 0.56, "result": "best edge -0.059 below 0.04"}, {"market": "eth-updown-4h-1790366400", "mid_up": 0.525, "model_up": 0.524, "result": "best edge -0.064 below 0.04"}]}','[]');
INSERT INTO "decisions" VALUES(3,'pm:scan:2026-09-25T20:36:11Z','20260925T203611Z-crypto2','2026-09-25T20:36:11Z','2026-09-25T20:36:11Z','2026-09-25','*','predmarket','INFO','PM_SCAN','scanned 6 live markets; 0 bet(s).','{"scanned": [{"market": "btc-updown-15m-1790368200", "mid_up": 0.515, "model_up": 0.508, "result": "best edge -0.115 below 0.04"}, {"market": "bitcoin-up-or-down-september-25-2026-4pm-et", "mid_up": 0.645, "model_up": 0.577, "result": "best edge -0.051 below 0.04"}, {"market": "btc-updown-4h-1790366400", "mid_up": 0.565, "model_up": 0.527, "result": "best edge -0.026 below 0.04"}, {"market": "eth-updown-15m-1790368200", "mid_up": 0.395, "model_up": 0.444, "result": "best edge -0.109 below 0.04"}, {"market": "ethereum-up-or-down-september-25-2026-4pm-et", "mid_up": 0.495, "model_up": 0.49, "result": "best edge -0.087 below 0.04"}, {"market": "eth-updown-4h-1790366400", "mid_up": 0.485, "model_up": 0.497, "result": "best edge -0.060 below 0.04"}]}','[]');
INSERT INTO "decisions" VALUES(4,'pm:scan:2026-09-25T20:43:59Z','20260925T204359Z-crypto2','2026-09-25T20:43:59Z','2026-09-25T20:43:59Z','2026-09-25','*','predmarket','INFO','PM_SCAN','scanned 4 live markets; 0 bet(s).','{"scanned": [{"market": "bitcoin-up-or-down-september-25-2026-4pm-et", "mid_up": 0.835, "model_up": 0, "result": "outside entry timing (73% of window elapsed)"}, {"market": "btc-updown-4h-1790366400", "mid_up": 0.675, "model_up": 0.567, "result": "best edge +0.010 below 0.04"}, {"market": "ethereum-up-or-down-september-25-2026-4pm-et", "mid_up": 0.45499999999999996, "model_up": 0, "result": "outside entry timing (73% of window elapsed)"}, {"market": "eth-updown-4h-1790366400", "mid_up": 0.46499999999999997, "model_up": 0.492, "result": "best edge -0.053 below 0.04"}]}','[]');
INSERT INTO "decisions" VALUES(5,'pm:scan:2026-09-25T23:13:53Z','20260925T231353Z-crypto2','2026-09-25T23:13:53Z','2026-09-25T23:13:53Z','2026-09-25','*','predmarket','INFO','PM_SCAN','scanned 4 live markets; 0 bet(s).','{"scanned": [{"market": "bitcoin-up-or-down-september-25-2026-7pm-et", "mid_up": 0.405, "model_up": 0.485, "result": "best edge -0.030 below 0.04"}, {"market": "btc-updown-4h-1790366400", "mid_up": 0.65, "model_up": 0, "result": "outside entry timing (81% of window elapsed)"}, {"market": "ethereum-up-or-down-september-25-2026-7pm-et", "mid_up": 0.645, "model_up": 0.567, "result": "best edge -0.029 below 0.04"}, {"market": "eth-updown-4h-1790366400", "mid_up": 0.525, "model_up": 0, "result": "outside entry timing (81% of window elapsed)"}]}','[]');
INSERT INTO "decisions" VALUES(6,'pm:scan:2026-09-25T23:28:53Z','20260925T232853Z-crypto2','2026-09-25T23:28:53Z','2026-09-25T23:28:53Z','2026-09-25','*','predmarket','INFO','PM_SCAN','scanned 4 live markets; 0 bet(s).','{"scanned": [{"market": "bitcoin-up-or-down-september-25-2026-7pm-et", "mid_up": 0.475, "model_up": 0.501, "result": "best edge -0.068 below 0.04"}, {"market": "btc-updown-4h-1790366400", "mid_up": 0.775, "model_up": 0, "result": "outside entry timing (87% of window elapsed)"}, {"market": "ethereum-up-or-down-september-25-2026-7pm-et", "mid_up": 0.605, "model_up": 0.546, "result": "best edge -0.049 below 0.04"}, {"market": "eth-updown-4h-1790366400", "mid_up": 0.43, "model_up": 0, "result": "outside entry timing (87% of window elapsed)"}]}','[]');
INSERT INTO "decisions" VALUES(7,'pm:scan:2026-09-25T23:56:18Z','20260925T235618Z-crypto2','2026-09-25T23:56:18Z','2026-09-25T23:56:18Z','2026-09-25','*','predmarket','INFO','PM_SCAN','scanned 6 live markets; 0 bet(s).','{"scanned": [{"market": "btc-updown-15m-1790379900", "mid_up": 0.355, "model_up": 0, "result": "outside entry timing (75% of window elapsed)"}, {"market": "bitcoin-up-or-down-september-25-2026-7pm-et", "mid_up": 0.175, "model_up": 0, "result": "outside entry timing (94% of window elapsed)"}, {"market": "btc-updown-4h-1790366400", "mid_up": 0.9704999999999999, "model_up": 0, "result": "outside entry timing (98% of window elapsed)"}, {"market": "eth-updown-15m-1790379900", "mid_up": 0.075, "model_up": 0, "result": "outside entry timing (75% of window elapsed)"}, {"market": "ethereum-up-or-down-september-25-2026-7pm-et", "mid_up": 0.135, "model_up": 0, "result": "outside entry timing (94% of window elapsed)"}, {"market": "eth-updown-4h-1790366400", "mid_up": 0.045, "model_up": 0, "result": "outside entry timing (98% of window elapsed)"}]}','[]');
INSERT INTO "decisions" VALUES(8,'pm:scan:2026-09-26T00:08:54Z','20260926T000854Z-crypto2','2026-09-26T00:08:54Z','2026-09-26T00:08:54Z','2026-09-25','*','predmarket','INFO','PM_SCAN','scanned 6 live markets; 0 bet(s).','{"scanned": [{"market": "btc-updown-15m-1790380800", "mid_up": 0.655, "model_up": 0.603, "result": "best edge -0.106 below 0.04"}, {"market": "bitcoin-up-or-down-september-25-2026-8pm-et", "mid_up": 0.535, "model_up": 0.536, "result": "best edge -0.068 below 0.04"}, {"market": "btc-updown-4h-1790380800", "mid_up": 0.575, "model_up": 0, "result": "outside entry timing (4% of window elapsed)"}, {"market": "eth-updown-15m-1790380800", "mid_up": 0.865, "model_up": 0.705, "result": "no side priced between the allowed 30c-75c"}, {"market": "ethereum-up-or-down-september-25-2026-8pm-et", "mid_up": 0.66, "model_up": 0.574, "result": "best edge -0.037 below 0.04"}, {"market": "eth-updown-4h-1790380800", "mid_up": 0.5700000000000001, "model_up": 0, "result": "outside entry timing (4% of window elapsed)"}]}','[]');
INSERT INTO "decisions" VALUES(9,'pm:scan:2026-09-26T01:29:31Z','20260926T012931Z-crypto2','2026-09-26T01:29:31Z','2026-09-26T01:29:31Z','2026-09-25','*','predmarket','INFO','PM_SCAN','scanned 4 live markets; 0 bet(s).','{"scanned": [{"market": "bitcoin-up-or-down-september-25-2026-9pm-et", "mid_up": 0.625, "model_up": 0.55, "result": "best edge -0.042 below 0.04"}, {"market": "btc-updown-4h-1790380800", "mid_up": 0.295, "model_up": 0.401, "result": "best edge +0.008 below 0.04"}, {"market": "ethereum-up-or-down-september-25-2026-9pm-et", "mid_up": 0.62, "model_up": 0.562, "result": "best edge -0.055 below 0.04"}, {"market": "eth-updown-4h-1790380800", "mid_up": 0.395, "model_up": 0.442, "result": "best edge -0.045 below 0.04"}]}','[]');
INSERT INTO "decisions" VALUES(10,'pm:scan:2026-09-26T05:25:42Z','20260926T052542Z-crypto2','2026-09-26T05:25:42Z','2026-09-26T05:25:42Z','2026-09-26','*','predmarket','INFO','PM_SCAN','scanned 6 live markets; 0 bet(s).','{"scanned": [{"market": "btc-updown-15m-1790399700", "mid_up": 0.645, "model_up": 0, "result": "outside entry timing (71% of window elapsed)"}, {"market": "bitcoin-up-or-down-september-26-2026-1am-et", "mid_up": 0.505, "model_up": 0.509, "result": "best edge -0.076 below 0.04"}, {"market": "btc-updown-4h-1790395200", "mid_up": 0.5700000000000001, "model_up": 0.528, "result": "best edge -0.033 below 0.04"}, {"market": "eth-updown-15m-1790399700", "mid_up": 0.97, "model_up": 0, "result": "outside entry timing (71% of window elapsed)"}, {"market": "ethereum-up-or-down-september-26-2026-1am-et", "mid_up": 0.535, "model_up": 0.512, "result": "best edge -0.067 below 0.04"}, {"market": "eth-updown-4h-1790395200", "mid_up": 0.6, "model_up": 0.537, "result": "best edge -0.032 below 0.04"}]}','[]');
CREATE TABLE dividends (
  ticker TEXT NOT NULL, ex_date TEXT NOT NULL, per_share REAL NOT NULL, qty REAL NOT NULL,
  amount REAL NOT NULL, recorded_at TEXT NOT NULL, PRIMARY KEY (ticker, ex_date)
);
CREATE TABLE events (
  seq INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT NOT NULL, run_id TEXT, kind TEXT NOT NULL,
  payload TEXT NOT NULL, prev_hash TEXT NOT NULL, hash TEXT NOT NULL
);
INSERT INTO "events" VALUES(1,'2026-09-25T20:09:49Z',NULL,'freeze','{"book": "crypto2", "end": "2026-10-22", "start": "2026-09-25", "strategy_sha256": "bbcc594254a8b6a103f74d7e7247a694e70d059bd59efdd046b8f5257344564c", "universe_sha256": "172ba39de91f49af21ee2539df0b42cd5d6aa9c7afbd426114cb33bba2c27afa", "version": "pm-2.0.0"}','GENESIS','dffbf249e59c70c4477593b8a535d52a176af138683c4d8e76f425e143c51c0a');
INSERT INTO "events" VALUES(2,'2026-09-25T20:10:36Z','20260925T201027Z-crypto2','decision','{"action": "INFO", "code": "PM_SCAN", "key": "pm:scan:2026-09-25T20:10:27Z", "reason": "scanned 6 live markets; 0 bet(s).", "ticker": "*"}','dffbf249e59c70c4477593b8a535d52a176af138683c4d8e76f425e143c51c0a','90619e315a394b087da3d942a7a323bc27ce71e853d9615a33ba3dd26c2037da');
INSERT INTO "events" VALUES(3,'2026-09-25T20:26:54Z','20260925T202649Z-crypto2','decision','{"action": "INFO", "code": "PM_SCAN", "key": "pm:scan:2026-09-25T20:26:49Z", "reason": "scanned 6 live markets; 0 bet(s).", "ticker": "*"}','90619e315a394b087da3d942a7a323bc27ce71e853d9615a33ba3dd26c2037da','9c773aef9394f2b774ad77f4230afc8e945d00f223659b2bb9f8ce0773e4f5a2');
INSERT INTO "events" VALUES(4,'2026-09-25T20:36:16Z','20260925T203611Z-crypto2','decision','{"action": "INFO", "code": "PM_SCAN", "key": "pm:scan:2026-09-25T20:36:11Z", "reason": "scanned 6 live markets; 0 bet(s).", "ticker": "*"}','9c773aef9394f2b774ad77f4230afc8e945d00f223659b2bb9f8ce0773e4f5a2','6f39edd19da573d76d9c31db86c1e8fce275a65a1fb2b25f49342165bf8657a8');
INSERT INTO "events" VALUES(5,'2026-09-25T20:44:04Z','20260925T204359Z-crypto2','decision','{"action": "INFO", "code": "PM_SCAN", "key": "pm:scan:2026-09-25T20:43:59Z", "reason": "scanned 4 live markets; 0 bet(s).", "ticker": "*"}','6f39edd19da573d76d9c31db86c1e8fce275a65a1fb2b25f49342165bf8657a8','b23766a47ac9dd620600761d09ac3e188ac0e5bbd79aad8af9bf6d6e1205bb24');
INSERT INTO "events" VALUES(6,'2026-09-25T23:13:57Z','20260925T231353Z-crypto2','decision','{"action": "INFO", "code": "PM_SCAN", "key": "pm:scan:2026-09-25T23:13:53Z", "reason": "scanned 4 live markets; 0 bet(s).", "ticker": "*"}','b23766a47ac9dd620600761d09ac3e188ac0e5bbd79aad8af9bf6d6e1205bb24','2d284ed5098150b73b0e959f6642fc71263289d340b92e3eb99d4b8c262e5520');
INSERT INTO "events" VALUES(7,'2026-09-25T23:28:57Z','20260925T232853Z-crypto2','decision','{"action": "INFO", "code": "PM_SCAN", "key": "pm:scan:2026-09-25T23:28:53Z", "reason": "scanned 4 live markets; 0 bet(s).", "ticker": "*"}','2d284ed5098150b73b0e959f6642fc71263289d340b92e3eb99d4b8c262e5520','12c8180ec72211ebd370e57fdf371ccd4952a7a45dba21a414caba3a9b599a03');
INSERT INTO "events" VALUES(8,'2026-09-25T23:56:24Z','20260925T235618Z-crypto2','decision','{"action": "INFO", "code": "PM_SCAN", "key": "pm:scan:2026-09-25T23:56:18Z", "reason": "scanned 6 live markets; 0 bet(s).", "ticker": "*"}','12c8180ec72211ebd370e57fdf371ccd4952a7a45dba21a414caba3a9b599a03','c8aa3cc9ef6a9bc56599a11e26a54f5abc6834dc80184cebfd5409c0ac884a63');
INSERT INTO "events" VALUES(9,'2026-09-26T00:08:59Z','20260926T000854Z-crypto2','decision','{"action": "INFO", "code": "PM_SCAN", "key": "pm:scan:2026-09-26T00:08:54Z", "reason": "scanned 6 live markets; 0 bet(s).", "ticker": "*"}','c8aa3cc9ef6a9bc56599a11e26a54f5abc6834dc80184cebfd5409c0ac884a63','123126c6146c4700436fd55456045fa37f2a7969cc8265e982bf45385f466572');
INSERT INTO "events" VALUES(10,'2026-09-26T01:29:35Z','20260926T012931Z-crypto2','decision','{"action": "INFO", "code": "PM_SCAN", "key": "pm:scan:2026-09-26T01:29:31Z", "reason": "scanned 4 live markets; 0 bet(s).", "ticker": "*"}','123126c6146c4700436fd55456045fa37f2a7969cc8265e982bf45385f466572','0003dcabcb19ffda169c059ec8390a6b874f1bdf9da77f92b4c0330253e5793c');
INSERT INTO "events" VALUES(11,'2026-09-26T05:25:47Z','20260926T052542Z-crypto2','decision','{"action": "INFO", "code": "PM_SCAN", "key": "pm:scan:2026-09-26T05:25:42Z", "reason": "scanned 6 live markets; 0 bet(s).", "ticker": "*"}','0003dcabcb19ffda169c059ec8390a6b874f1bdf9da77f92b4c0330253e5793c','2347d4ce55be71135a1eed0af9b34c8a0bed78b025af83c50e3304967231cec9');
INSERT INTO "events" VALUES(12,'2026-09-26T05:25:47Z','20260926T052542Z-crypto2','snapshot','{"cash": 100.0, "drawdown": 0.0, "equity": 100.0, "session": "2026-09-25", "spy_bh_equity": null}','2347d4ce55be71135a1eed0af9b34c8a0bed78b025af83c50e3304967231cec9','77b74ec54f3f66e9efea11eff07d984a9ee88e7990176219ab6f8825f756def2');
CREATE TABLE experiment (
  id INTEGER PRIMARY KEY CHECK (id = 1),
  frozen_at TEXT NOT NULL, start_date TEXT NOT NULL, end_date TEXT NOT NULL,
  starting_cash REAL NOT NULL, strategy_version TEXT NOT NULL,
  strategy_sha256 TEXT NOT NULL, universe_sha256 TEXT NOT NULL, report_days TEXT NOT NULL, notes TEXT
);
INSERT INTO "experiment" VALUES(1,'2026-09-25T20:09:49Z','2026-09-25','2026-10-22',100.0,'pm-2.0.0','bbcc594254a8b6a103f74d7e7247a694e70d059bd59efdd046b8f5257344564c','172ba39de91f49af21ee2539df0b42cd5d6aa9c7afbd426114cb33bba2c27afa','[7, 14, 21, 28, 30]','book=crypto2; strategy=config/strategy_pm_v2.json');
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
INSERT INTO "runs" VALUES('20260925T201027Z-crypto2','2026-09-25T20:10:30Z','2026-09-25T20:10:36Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260925T202649Z-crypto2','2026-09-25T20:26:49Z','2026-09-25T20:26:54Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260925T203611Z-crypto2','2026-09-25T20:36:11Z','2026-09-25T20:36:16Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260925T204359Z-crypto2','2026-09-25T20:43:59Z','2026-09-25T20:44:04Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260925T231353Z-crypto2','2026-09-25T23:13:53Z','2026-09-25T23:13:57Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260925T232853Z-crypto2','2026-09-25T23:28:53Z','2026-09-25T23:28:57Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260925T235618Z-crypto2','2026-09-25T23:56:18Z','2026-09-25T23:56:24Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260926T000854Z-crypto2','2026-09-26T00:08:54Z','2026-09-26T00:08:59Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260926T012931Z-crypto2','2026-09-26T01:29:31Z','2026-09-26T01:29:35Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260926T052542Z-crypto2','2026-09-26T05:25:42Z','2026-09-26T05:25:47Z','OK','github-actions','no action needed',NULL);
CREATE TABLE snapshots (
  session TEXT PRIMARY KEY, created_at TEXT NOT NULL, run_id TEXT, equity REAL NOT NULL,
  cash REAL NOT NULL, positions_value REAL NOT NULL, spy_bh_equity REAL, cash_bh_equity REAL,
  peak REAL NOT NULL, drawdown REAL NOT NULL, regime TEXT, risk_state TEXT, marks TEXT, holdings TEXT
);
INSERT INTO "snapshots" VALUES('2026-09-25','2026-09-26T05:25:42Z','20260926T052542Z-crypto2',100.0,100.0,0.0,NULL,100.0,100.0,0.0,'0 open bets','{"peak": 100.0, "drawdown": 0.0}','{"marks": {}, "flags": {}}','{}');
CREATE TABLE state (key TEXT PRIMARY KEY, value TEXT NOT NULL, updated_at TEXT NOT NULL);
INSERT INTO "state" VALUES('cash','100.0','2026-09-25T20:09:49Z');
INSERT INTO "state" VALUES('strategy_integrity_ok','true','2026-09-26T05:25:42Z');
INSERT INTO "state" VALUES('risk','{"peak": 100.0, "drawdown": 0.0}','2026-09-26T05:25:47Z');
INSERT INTO "state" VALUES('pm_day','{"date": "2026-09-26", "start_equity": 100.0}','2026-09-26T05:25:42Z');
INSERT INTO "state" VALUES('pm_positions','{}','2026-09-26T05:25:47Z');
INSERT INTO "state" VALUES('live_marks','{"as_of": "2026-09-26T05:25:42Z", "marks": {}}','2026-09-26T05:25:47Z');
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
INSERT INTO "sqlite_sequence" VALUES('events',12);
INSERT INTO "sqlite_sequence" VALUES('decisions',10);
COMMIT;
