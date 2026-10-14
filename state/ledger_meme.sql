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
CREATE TABLE dividends (
  ticker TEXT NOT NULL, ex_date TEXT NOT NULL, per_share REAL NOT NULL, qty REAL NOT NULL,
  amount REAL NOT NULL, recorded_at TEXT NOT NULL, PRIMARY KEY (ticker, ex_date)
);
CREATE TABLE events (
  seq INTEGER PRIMARY KEY AUTOINCREMENT, ts TEXT NOT NULL, run_id TEXT, kind TEXT NOT NULL,
  payload TEXT NOT NULL, prev_hash TEXT NOT NULL, hash TEXT NOT NULL
);
INSERT INTO "events" VALUES(1,'2026-10-12T17:46:32Z',NULL,'freeze','{"book": "meme", "end": "2026-10-22", "start": "2026-10-13", "strategy_sha256": "da1ee09f6aeffcb18875c989cd862d41507960a5504ca625be3266afdd50c76b", "universe_sha256": "172ba39de91f49af21ee2539df0b42cd5d6aa9c7afbd426114cb33bba2c27afa", "version": "meme-1.0.0"}','GENESIS','e9d7b9884f50dc8c1c7abcec478a798fcad6420c86490073a60b75bb336f44c8');
INSERT INTO "events" VALUES(2,'2026-10-13T23:44:10Z','20261013T234404Z-meme','order','{"key": "meme:CQCDTp8rsFV3PhaPeYjcCW5LdGTxi6jFx7eC3UXnpump:2026-10-13T23:44:04Z:BUY", "notional": 5.0, "qty": null, "reason": "momentum with attention: 1h +11%, 5m +1.7%, buys 6696 vs sells 4054, liquidity $448,529, 24h volume $7,450,906, trending #8; modeled friction 4.0%", "session": "2026-10-13", "side": "BUY", "ticker": "CRAWLER CQCD\u2026pump", "type": "PAPER_MARKET"}','e9d7b9884f50dc8c1c7abcec478a798fcad6420c86490073a60b75bb336f44c8','0858603dfac0a6c96af5984c89af51381480efb42f503586ec7547e59ff6107d');
INSERT INTO "events" VALUES(3,'2026-10-13T23:44:10Z','20261013T234404Z-meme','fill','{"fill_price": 0.02368130765987858, "key": "meme:CQCDTp8rsFV3PhaPeYjcCW5LdGTxi6jFx7eC3UXnpump:2026-10-13T23:44:04Z:BUY", "price_time": "2026-10-13T23:44:04Z", "qty": 211.13698921580735, "ref_price": 0.02277, "side": "BUY", "source": "dexscreener_pair_price", "ticker": "CRAWLER CQCD\u2026pump"}','0858603dfac0a6c96af5984c89af51381480efb42f503586ec7547e59ff6107d','0000d321da1422c55701a3a56e49a7f7061cbeb98d8fd783ffbaf96cd3de0f7c');
INSERT INTO "events" VALUES(4,'2026-10-13T23:44:10Z','20261013T234404Z-meme','order_status','{"key": "meme:CQCDTp8rsFV3PhaPeYjcCW5LdGTxi6jFx7eC3UXnpump:2026-10-13T23:44:04Z:BUY", "reason": "bought 211.137", "status": "FILLED"}','0000d321da1422c55701a3a56e49a7f7061cbeb98d8fd783ffbaf96cd3de0f7c','102e6c3634e53b065cd6671b7f24a3d01f5d7b6106640c44403e3c12a6a66a7a');
INSERT INTO "events" VALUES(5,'2026-10-14T01:56:00Z','20261014T015555Z-meme','fill','{"fill_price": 0.012219790671110741, "key": "meme:CQCDTp8rsFV3PhaPeYjcCW5LdGTxi6jFx7eC3UXnpump:2026-10-13T23:44:04Z:SELL", "price_time": "2026-10-14T01:55:55Z", "qty": 211.13698921580735, "ref_price": 0.013, "side": "SELL", "source": "dexscreener_pair_price", "ticker": "CRAWLER CQCD\u2026pump"}','102e6c3634e53b065cd6671b7f24a3d01f5d7b6106640c44403e3c12a6a66a7a','6d1b734177b6439c8ba3e787118477d6ff54b101ae19d160c4af26bda5d5d80b');
INSERT INTO "events" VALUES(6,'2026-10-14T01:56:00Z','20261014T015555Z-meme','order_status','{"key": "meme:CQCDTp8rsFV3PhaPeYjcCW5LdGTxi6jFx7eC3UXnpump:2026-10-13T23:44:04Z:SELL", "reason": "STOP", "status": "FILLED"}','6d1b734177b6439c8ba3e787118477d6ff54b101ae19d160c4af26bda5d5d80b','1f12a84de76d3dbe8adf0b8952832565c8cd88afe4009c9175402ed59dfc0ee5');
INSERT INTO "events" VALUES(7,'2026-10-14T05:22:11Z','20261014T052204Z-meme','snapshot','{"cash": 97.58004981114573, "drawdown": 0.02499081389729818, "equity": 97.58004981114573, "session": "2026-10-13", "spy_bh_equity": null}','1f12a84de76d3dbe8adf0b8952832565c8cd88afe4009c9175402ed59dfc0ee5','96faf7098e6796a93520fa1aeeda73f44581fd4348b201a3b955001b13110687');
INSERT INTO "events" VALUES(8,'2026-10-14T15:50:37Z','20261014T155025Z-meme','order','{"key": "meme:7jNwX4Me9zGEjmWY7zARDG2LYjVs1WXD6DZ1JvSfpump:2026-10-14T15:50:25Z:BUY", "notional": 5.0, "qty": null, "reason": "momentum with attention: 1h +9%, 5m +2.4%, buys 4489 vs sells 1929, liquidity $74,994, 24h volume $2,830,077, X link on profile; modeled friction 4.0%", "session": "2026-10-14", "side": "BUY", "ticker": "HUMPH 7jNw\u2026pump", "type": "PAPER_MARKET"}','96faf7098e6796a93520fa1aeeda73f44581fd4348b201a3b955001b13110687','12170508d480b47421d233b68836379a8562df038deba24a77683a862c3dad27');
INSERT INTO "events" VALUES(9,'2026-10-14T15:50:37Z','20261014T155025Z-meme','fill','{"fill_price": 0.0006314649529486154, "key": "meme:7jNwX4Me9zGEjmWY7zARDG2LYjVs1WXD6DZ1JvSfpump:2026-10-14T15:50:25Z:BUY", "price_time": "2026-10-14T15:50:25Z", "qty": 7918.095813002101, "ref_price": 0.0006071, "side": "BUY", "source": "dexscreener_pair_price", "ticker": "HUMPH 7jNw\u2026pump"}','12170508d480b47421d233b68836379a8562df038deba24a77683a862c3dad27','fde3b0e23379b495b7d3c60eaf718d905387c2d84f3317a42226cdec4bee660f');
INSERT INTO "events" VALUES(10,'2026-10-14T15:50:37Z','20261014T155025Z-meme','order_status','{"key": "meme:7jNwX4Me9zGEjmWY7zARDG2LYjVs1WXD6DZ1JvSfpump:2026-10-14T15:50:25Z:BUY", "reason": "bought 7918.1", "status": "FILLED"}','fde3b0e23379b495b7d3c60eaf718d905387c2d84f3317a42226cdec4bee660f','c82d2091311fa5d9df9a5c3c721bcee8ba11fc13d98083578efd3adef0b531bb');
CREATE TABLE experiment (
  id INTEGER PRIMARY KEY CHECK (id = 1),
  frozen_at TEXT NOT NULL, start_date TEXT NOT NULL, end_date TEXT NOT NULL,
  starting_cash REAL NOT NULL, strategy_version TEXT NOT NULL,
  strategy_sha256 TEXT NOT NULL, universe_sha256 TEXT NOT NULL, report_days TEXT NOT NULL, notes TEXT
);
INSERT INTO "experiment" VALUES(1,'2026-10-12T17:46:32Z','2026-10-13','2026-10-22',100.0,'meme-1.0.0','da1ee09f6aeffcb18875c989cd862d41507960a5504ca625be3266afdd50c76b','172ba39de91f49af21ee2539df0b42cd5d6aa9c7afbd426114cb33bba2c27afa','[7, 14, 21, 28, 30]','book=meme; strategy=config/strategy_meme_v1.json');
CREATE TABLE fills (
  fill_id INTEGER PRIMARY KEY AUTOINCREMENT, order_key TEXT NOT NULL UNIQUE, run_id TEXT,
  recorded_at TEXT NOT NULL, session TEXT NOT NULL, ticker TEXT NOT NULL, side TEXT NOT NULL,
  qty REAL NOT NULL, ref_price REAL NOT NULL, fill_price REAL NOT NULL, cost_bps REAL NOT NULL,
  cost_usd REAL NOT NULL, price_time TEXT NOT NULL, price_source TEXT NOT NULL, sleeve TEXT,
  reason_code TEXT, reason TEXT, realized_pnl REAL
);
INSERT INTO "fills" VALUES(1,'meme:CQCDTp8rsFV3PhaPeYjcCW5LdGTxi6jFx7eC3UXnpump:2026-10-13T23:44:04Z:BUY','20261013T234404Z-meme','2026-10-13T23:44:10Z','2026-10-13','CRAWLER CQCD…pump','BUY',2.11136989215807346e+02,0.02277,2.36813076598785809e-02,400.2,0.192410755556067,'2026-10-13T23:44:04Z','dexscreener_pair_price','meme','MEME_ENTRY','momentum with attention: 1h +11%, 5m +1.7%, buys 6696 vs sells 4054, liquidity $448,529, 24h volume $7,450,906, trending #8; modeled friction 4.0%',NULL);
INSERT INTO "fills" VALUES(2,'meme:CQCDTp8rsFV3PhaPeYjcCW5LdGTxi6jFx7eC3UXnpump:2026-10-13T23:44:04Z:SELL','20261014T015555Z-meme','2026-10-14T01:56:00Z','2026-10-13','CRAWLER CQCD…pump','SELL',2.11136989215807346e+02,0.013,1.22197906711107411e-02,600.2,1.64731048659763679e-01,'2026-10-14T01:55:55Z','dexscreener_pair_price','meme','STOP','STOP: price 0.013 vs entry 0.02277 (-42.9%); liquidity $340,920',-2.41995018885426826e+00);
INSERT INTO "fills" VALUES(3,'meme:7jNwX4Me9zGEjmWY7zARDG2LYjVs1WXD6DZ1JvSfpump:2026-10-14T15:50:25Z:BUY','20261014T155025Z-meme','2026-10-14T15:50:37Z','2026-10-14','HUMPH 7jNw…pump','BUY',7.91809581300210084e+03,0.0006071,6.31464952948615401e-04,401.3,1.92924031926425404e-01,'2026-10-14T15:50:25Z','dexscreener_pair_price','meme','MEME_ENTRY','momentum with attention: 1h +9%, 5m +2.4%, buys 4489 vs sells 1929, liquidity $74,994, 24h volume $2,830,077, X link on profile; modeled friction 4.0%',NULL);
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
INSERT INTO "orders" VALUES('meme:CQCDTp8rsFV3PhaPeYjcCW5LdGTxi6jFx7eC3UXnpump:2026-10-13T23:44:04Z:BUY','2026-10-13T23:44:04Z','20261013T234404Z-meme','CRAWLER CQCD…pump','BUY','PAPER_MARKET','2026-10-13','meme',5.0,NULL,50,'MEME_ENTRY','momentum with attention: 1h +11%, 5m +1.7%, buys 6696 vs sells 4054, liquidity $448,529, 24h volume $7,450,906, trending #8; modeled friction 4.0%','{}','{"token": "CQCDTp8rsFV3PhaPeYjcCW5LdGTxi6jFx7eC3UXnpump", "pair": "AnrCHvfJUzMtos8DGjpT2XKurVPPYAVLDturASNwXcd4"}','FILLED','bought 211.137','2026-10-13T23:44:10Z');
INSERT INTO "orders" VALUES('meme:CQCDTp8rsFV3PhaPeYjcCW5LdGTxi6jFx7eC3UXnpump:2026-10-13T23:44:04Z:SELL','2026-10-14T01:55:55Z','20261014T015555Z-meme','CRAWLER CQCD…pump','SELL','STOP','2026-10-13','meme',NULL,NULL,NULL,'STOP','STOP: price 0.013 vs entry 0.02277 (-42.9%); liquidity $340,920',NULL,NULL,'FILLED','STOP','2026-10-14T01:56:00Z');
INSERT INTO "orders" VALUES('meme:7jNwX4Me9zGEjmWY7zARDG2LYjVs1WXD6DZ1JvSfpump:2026-10-14T15:50:25Z:BUY','2026-10-14T15:50:25Z','20261014T155025Z-meme','HUMPH 7jNw…pump','BUY','PAPER_MARKET','2026-10-14','meme',5.0,NULL,50,'MEME_ENTRY','momentum with attention: 1h +9%, 5m +2.4%, buys 4489 vs sells 1929, liquidity $74,994, 24h volume $2,830,077, X link on profile; modeled friction 4.0%','{}','{"token": "7jNwX4Me9zGEjmWY7zARDG2LYjVs1WXD6DZ1JvSfpump", "pair": "9pQRnaHbKjD61KyS2K4FEnLCpvAi5hu5jbMbEsunHLJz"}','FILLED','bought 7918.1','2026-10-14T15:50:37Z');
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
INSERT INTO "runs" VALUES('20261012T174933Z-meme','2026-10-12T17:49:46Z','2026-10-12T17:49:46Z','OK','github-actions','starts 2026-10-13',NULL);
INSERT INTO "runs" VALUES('20261012T180719Z-meme','2026-10-12T18:07:31Z','2026-10-12T18:07:31Z','OK','github-actions','starts 2026-10-13',NULL);
INSERT INTO "runs" VALUES('20261012T213411Z-meme','2026-10-12T21:36:17Z','2026-10-12T21:36:17Z','OK','github-actions','starts 2026-10-13',NULL);
INSERT INTO "runs" VALUES('20261013T020022Z-meme','2026-10-13T02:00:27Z','2026-10-13T02:00:27Z','OK','github-actions','starts 2026-10-13',NULL);
INSERT INTO "runs" VALUES('20261013T021408Z-meme','2026-10-13T02:14:14Z','2026-10-13T02:14:14Z','OK','github-actions','starts 2026-10-13',NULL);
INSERT INTO "runs" VALUES('20261013T023504Z-meme','2026-10-13T02:35:10Z','2026-10-13T02:35:10Z','OK','github-actions','starts 2026-10-13',NULL);
INSERT INTO "runs" VALUES('20261013T024332Z-meme','2026-10-13T02:43:37Z','2026-10-13T02:43:37Z','OK','github-actions','starts 2026-10-13',NULL);
INSERT INTO "runs" VALUES('20261013T033510Z-meme','2026-10-13T03:35:16Z','2026-10-13T03:35:16Z','OK','github-actions','starts 2026-10-13',NULL);
INSERT INTO "runs" VALUES('20261013T094554Z-meme','2026-10-13T09:45:59Z','2026-10-13T09:46:00Z','OK','github-actions','candidates screened out: liquidity x11, age x9, 1h x5, 24h x4',NULL);
INSERT INTO "runs" VALUES('20261013T174833Z-meme','2026-10-13T17:49:45Z','2026-10-13T17:49:46Z','OK','github-actions','candidates screened out: liquidity x11, age x10, 1h x6, 24h x3',NULL);
INSERT INTO "runs" VALUES('20261013T194605Z-meme','2026-10-13T19:46:17Z','2026-10-13T19:46:17Z','OK','github-actions','candidates screened out: liquidity x11, age x9, 1h x5, 24h x2',NULL);
INSERT INTO "runs" VALUES('20261013T232833Z-meme','2026-10-13T23:30:26Z','2026-10-13T23:30:27Z','OK','github-actions','candidates screened out: age x11, liquidity x11, 1h x5, 24h x1',NULL);
INSERT INTO "runs" VALUES('20261013T234404Z-meme','2026-10-13T23:44:09Z','2026-10-13T23:44:10Z','OK','github-actions','bought CRAWLER $5.00',NULL);
INSERT INTO "runs" VALUES('20261013T235108Z-meme','2026-10-13T23:51:15Z','2026-10-13T23:51:15Z','OK','github-actions','candidates screened out: liquidity x13, age x10, 1h x2, 24h x1',NULL);
INSERT INTO "runs" VALUES('20261014T001753Z-meme','2026-10-14T00:17:59Z','2026-10-14T00:18:00Z','OK','github-actions','candidates screened out: liquidity x14, age x8, buys x2, 1h x2',NULL);
INSERT INTO "runs" VALUES('20261014T003700Z-meme','2026-10-14T00:37:06Z','2026-10-14T00:37:07Z','OK','github-actions','candidates screened out: liquidity x13, age x11, 1h x2, buys x2',NULL);
INSERT INTO "runs" VALUES('20261014T015555Z-meme','2026-10-14T01:56:00Z','2026-10-14T01:56:00Z','OK','github-actions','sold CRAWLER (STOP) -2.42; candidates screened out: age x14, liquidity x11, 1h x2, buys x1',NULL);
INSERT INTO "runs" VALUES('20261014T052204Z-meme','2026-10-14T05:22:11Z','2026-10-14T05:22:11Z','OK','github-actions','candidates screened out: age x10, liquidity x10, 1h x2, too x1',NULL);
INSERT INTO "runs" VALUES('20261014T103616Z-meme','2026-10-14T10:36:23Z','2026-10-14T10:36:24Z','OK','github-actions','candidates screened out: age x9, liquidity x9, too x3, 1h x1',NULL);
INSERT INTO "runs" VALUES('20261014T152847Z-meme','2026-10-14T15:30:01Z','2026-10-14T15:30:02Z','OK','github-actions','candidates screened out: age x14, liquidity x6, 1h x3, 24h x3',NULL);
INSERT INTO "runs" VALUES('20261014T153347Z-meme','2026-10-14T15:33:58Z','2026-10-14T15:33:59Z','OK','github-actions','candidates screened out: age x14, liquidity x6, 1h x4, 24h x2',NULL);
INSERT INTO "runs" VALUES('20261014T153847Z-meme','2026-10-14T15:39:01Z','2026-10-14T15:39:02Z','OK','github-actions','candidates screened out: age x16, liquidity x9, 1h x3, too x1',NULL);
INSERT INTO "runs" VALUES('20261014T154347Z-meme','2026-10-14T15:43:55Z','2026-10-14T15:43:56Z','OK','github-actions','candidates screened out: age x16, liquidity x8, 1h x3, too x1',NULL);
INSERT INTO "runs" VALUES('20261014T154847Z-meme','2026-10-14T15:48:57Z','2026-10-14T15:48:58Z','OK','github-actions','candidates screened out: age x13, liquidity x7, 1h x4, too x1',NULL);
INSERT INTO "runs" VALUES('20261014T155025Z-meme','2026-10-14T15:50:35Z','2026-10-14T15:50:37Z','OK','github-actions','bought HUMPH $5.00',NULL);
INSERT INTO "runs" VALUES('20261014T155525Z-meme','2026-10-14T15:55:35Z','2026-10-14T15:55:36Z','OK','github-actions','candidates screened out: age x15, liquidity x7, 1h x2, 5m x1',NULL);
INSERT INTO "runs" VALUES('20261014T160025Z-meme','2026-10-14T16:00:34Z','2026-10-14T16:00:34Z','OK','github-actions','candidates screened out: age x14, liquidity x7, 1h x3, 24h x2',NULL);
INSERT INTO "runs" VALUES('20261014T160525Z-meme','2026-10-14T16:05:36Z','2026-10-14T16:05:36Z','OK','github-actions','candidates screened out: liquidity x11, age x9, 1h x4, too x3',NULL);
INSERT INTO "runs" VALUES('20261014T161025Z-meme','2026-10-14T16:10:34Z','2026-10-14T16:10:35Z','OK','github-actions','candidates screened out: age x11, liquidity x8, 24h x3, 1h x2',NULL);
INSERT INTO "runs" VALUES('20261014T161157Z-meme','2026-10-14T16:12:07Z','2026-10-14T16:12:08Z','OK','github-actions','candidates screened out: age x12, liquidity x7, 24h x4, 1h x2',NULL);
INSERT INTO "runs" VALUES('20261014T161657Z-meme','2026-10-14T16:17:13Z','2026-10-14T16:17:14Z','OK','github-actions','candidates screened out: age x12, liquidity x8, 1h x3, too x2',NULL);
INSERT INTO "runs" VALUES('20261014T162157Z-meme','2026-10-14T16:22:08Z','2026-10-14T16:22:09Z','OK','github-actions','candidates screened out: age x12, liquidity x10, 1h x3, too x2',NULL);
INSERT INTO "runs" VALUES('20261014T162657Z-meme','2026-10-14T16:27:07Z','2026-10-14T16:27:08Z','OK','github-actions','candidates screened out: liquidity x12, age x11, 1h x3, too x1',NULL);
INSERT INTO "runs" VALUES('20261014T163157Z-meme','2026-10-14T16:32:07Z','2026-10-14T16:32:07Z','OK','github-actions','candidates screened out: age x12, liquidity x12, 1h x3, too x1',NULL);
CREATE TABLE snapshots (
  session TEXT PRIMARY KEY, created_at TEXT NOT NULL, run_id TEXT, equity REAL NOT NULL,
  cash REAL NOT NULL, positions_value REAL NOT NULL, spy_bh_equity REAL, cash_bh_equity REAL,
  peak REAL NOT NULL, drawdown REAL NOT NULL, regime TEXT, risk_state TEXT, marks TEXT, holdings TEXT
);
INSERT INTO "snapshots" VALUES('2026-10-13','2026-10-14T05:22:04Z','20261014T052204Z-meme',9.75800498111457273e+01,9.75800498111457273e+01,0.0,NULL,100.0,1.00081159441370857e+02,2.49908138972981808e-02,'0 open memecoin positions','{"peak": 100.08115944137086, "drawdown": 0.02499081389729818}','{"marks": {}, "flags": {}}','{}');
CREATE TABLE state (key TEXT PRIMARY KEY, value TEXT NOT NULL, updated_at TEXT NOT NULL);
INSERT INTO "state" VALUES('cash','92.58004981114573','2026-10-14T15:50:37Z');
INSERT INTO "state" VALUES('strategy_integrity_ok','true','2026-10-14T16:32:07Z');
INSERT INTO "state" VALUES('meme_positions','{"7jNwX4Me9zGEjmWY7zARDG2LYjVs1WXD6DZ1JvSfpump": {"symbol": "HUMPH", "label": "HUMPH 7jNw\u2026pump", "qty": 7918.095813002101, "cost": 5.0, "entry_price": 0.0006071, "peak": 0.0006202, "mark": 0.0005614, "entered_at": "2026-10-14T15:50:25Z", "entry_liq": 74994.18, "liq": 72045.4, "pair": "9pQRnaHbKjD61KyS2K4FEnLCpvAi5hu5jbMbEsunHLJz", "missing": 0}}','2026-10-14T16:32:07Z');
INSERT INTO "state" VALUES('risk','{"peak": 100.08115944137086, "drawdown": 0.02499081389729818}','2026-10-14T16:32:07Z');
INSERT INTO "state" VALUES('meme_day','{"date": "2026-10-14", "entries": 1, "realized": 0.0}','2026-10-14T16:32:07Z');
INSERT INTO "state" VALUES('meme_rug','{"CQCDTp8rsFV3PhaPeYjcCW5LdGTxi6jFx7eC3UXnpump": {"at": "2026-10-13T23:44:04Z", "summary": {"score": 1, "score_normalised": 1, "risks": [], "lpLockedPct": 99.99133929455358}}, "7jNwX4Me9zGEjmWY7zARDG2LYjVs1WXD6DZ1JvSfpump": {"at": "2026-10-14T15:50:25Z", "summary": {"score": 1, "score_normalised": 1, "risks": [], "lpLockedPct": 99.99993554061957}}}','2026-10-14T15:50:37Z');
INSERT INTO "state" VALUES('meme_seen','{"CQCDTp8rsFV3PhaPeYjcCW5LdGTxi6jFx7eC3UXnpump": "2026-10-14T01:55:55Z"}','2026-10-14T01:56:00Z');
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
INSERT INTO "sqlite_sequence" VALUES('events',10);
INSERT INTO "sqlite_sequence" VALUES('fills',3);
COMMIT;
