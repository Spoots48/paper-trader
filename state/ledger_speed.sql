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
INSERT INTO "events" VALUES(1,'2026-10-11T23:42:41Z',NULL,'freeze','{"book": "speed", "end": "2026-10-22", "start": "2026-10-12", "strategy_sha256": "889754fd5be0a3250a777c1abe8c2a7b14a3689fc30365e2be766a28993df488", "universe_sha256": "172ba39de91f49af21ee2539df0b42cd5d6aa9c7afbd426114cb33bba2c27afa", "version": "speed-1.0.0"}','GENESIS','1e13d4391b42112a33284334e77b9852c9c23449cefc1bf53c6f70472efd9cd6');
INSERT INTO "events" VALUES(2,'2026-10-12T18:04:10Z',NULL,'strategy_change','{"book": "speed", "description": "Retire the speed book: switch Jev calls off (caps 0); the book stays flat. Jev showed no skill on this book''s exact question.", "to_sha256": "8a0d081b0128ac8cac564ad06320fc0739e129c2bb1fb12cb1381776755fa825"}','1e13d4391b42112a33284334e77b9852c9c23449cefc1bf53c6f70472efd9cd6','7f373cebc9daf3174d01ff2609b0e86e7af26469bf1458102ed736fdd0f45075');
INSERT INTO "events" VALUES(3,'2026-10-12T21:36:17Z','20261012T213411Z-speed','snapshot','{"cash": 100.0, "drawdown": 0.0, "equity": 100.0, "session": "2026-10-12", "spy_bh_equity": 99.84278709706172}','7f373cebc9daf3174d01ff2609b0e86e7af26469bf1458102ed736fdd0f45075','9c2a2f70ad7680666d4dde1e08b2309dc1910a222b6e552f63e612e7e1a6d820');
INSERT INTO "events" VALUES(4,'2026-10-13T23:30:26Z','20261013T232833Z-speed','snapshot','{"cash": 100.0, "drawdown": 0.0, "equity": 100.0, "session": "2026-10-13", "spy_bh_equity": 99.8312430300712}','9c2a2f70ad7680666d4dde1e08b2309dc1910a222b6e552f63e612e7e1a6d820','aa88d4e51a7e879455c19e5082c943ca1321610ce5da3f3e6f0ed3ae1759c420');
INSERT INTO "events" VALUES(5,'2026-10-14T21:20:13Z','20261014T211810Z-speed','snapshot','{"cash": 100.0, "drawdown": 0.0, "equity": 100.0, "session": "2026-10-14", "spy_bh_equity": 98.75209988853693}','aa88d4e51a7e879455c19e5082c943ca1321610ce5da3f3e6f0ed3ae1759c420','1ba3a1e91b0fe1e21f1c97ee4241d41105050f5a092edd234c2a54a74d292e4b');
INSERT INTO "events" VALUES(6,'2026-10-15T20:36:05Z','20261015T203351Z-speed','snapshot','{"cash": 100.0, "drawdown": 0.0, "equity": 100.0, "session": "2026-10-15", "spy_bh_equity": 99.03311255318162}','1ba3a1e91b0fe1e21f1c97ee4241d41105050f5a092edd234c2a54a74d292e4b','5f0fdd9831546b88e27122678e79b295cab8f937bd028e58bb2d3422424802ee');
INSERT INTO "events" VALUES(7,'2026-10-16T22:50:19Z','20261016T224818Z-speed','snapshot','{"cash": 100.0, "drawdown": 0.0, "equity": 100.0, "session": "2026-10-16", "spy_bh_equity": 97.93729551841615}','5f0fdd9831546b88e27122678e79b295cab8f937bd028e58bb2d3422424802ee','798bb796a16b789e53170a6a119a82a0692a5215e4ab404ddeb3629b4df87390');
INSERT INTO "events" VALUES(8,'2026-10-19T22:57:10Z','20261019T225519Z-speed','snapshot','{"cash": 100.0, "drawdown": 0.0, "equity": 100.0, "session": "2026-10-19", "spy_bh_equity": 98.35175415148092}','798bb796a16b789e53170a6a119a82a0692a5215e4ab404ddeb3629b4df87390','34eed2e9e0716f02a549caf24a84e9b275c5b182b3ab3788c2d948490d14f00d');
CREATE TABLE experiment (
  id INTEGER PRIMARY KEY CHECK (id = 1),
  frozen_at TEXT NOT NULL, start_date TEXT NOT NULL, end_date TEXT NOT NULL,
  starting_cash REAL NOT NULL, strategy_version TEXT NOT NULL,
  strategy_sha256 TEXT NOT NULL, universe_sha256 TEXT NOT NULL, report_days TEXT NOT NULL, notes TEXT
);
INSERT INTO "experiment" VALUES(1,'2026-10-11T23:42:41Z','2026-10-12','2026-10-22',100.0,'speed-1.0.0','889754fd5be0a3250a777c1abe8c2a7b14a3689fc30365e2be766a28993df488','172ba39de91f49af21ee2539df0b42cd5d6aa9c7afbd426114cb33bba2c27afa','[7, 14, 21, 28, 30]','book=speed; strategy=config/strategy_speed_v1.json');
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
INSERT INTO "runs" VALUES('20261011T234358Z-speed','2026-10-11T23:44:03Z','2026-10-11T23:44:03Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261012T000507Z-speed','2026-10-12T00:05:14Z','2026-10-12T00:05:14Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261012T002544Z-speed','2026-10-12T00:25:51Z','2026-10-12T00:25:51Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261012T004627Z-speed','2026-10-12T00:46:34Z','2026-10-12T00:46:34Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261012T010711Z-speed','2026-10-12T01:07:19Z','2026-10-12T01:07:19Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261012T012757Z-speed','2026-10-12T01:28:08Z','2026-10-12T01:28:08Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261012T014836Z-speed','2026-10-12T01:48:42Z','2026-10-12T01:48:42Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261012T020935Z-speed','2026-10-12T02:09:41Z','2026-10-12T02:09:41Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261012T023001Z-speed','2026-10-12T02:30:07Z','2026-10-12T02:30:07Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261012T025036Z-speed','2026-10-12T02:50:43Z','2026-10-12T02:50:43Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261012T031128Z-speed','2026-10-12T03:11:34Z','2026-10-12T03:11:34Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261012T033206Z-speed','2026-10-12T03:32:12Z','2026-10-12T03:32:12Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261012T035247Z-speed','2026-10-12T03:52:53Z','2026-10-12T03:52:53Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261012T041322Z-speed','2026-10-12T04:13:28Z','2026-10-12T04:13:28Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261012T043409Z-speed','2026-10-12T04:34:14Z','2026-10-12T04:34:14Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261012T045455Z-speed','2026-10-12T04:55:02Z','2026-10-12T04:55:02Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261012T063008Z-speed','2026-10-12T06:30:14Z','2026-10-12T06:30:14Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261012T160515Z-speed','2026-10-12T16:06:15Z','2026-10-12T16:06:36Z','OK','github-actions','2026-10-12: 0 buys, 0 sells this run; 120 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261012T161015Z-speed','2026-10-12T16:10:23Z','2026-10-12T16:10:27Z','OK','github-actions','2026-10-12: 0 buys, 0 sells this run; 133 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261012T161515Z-speed','2026-10-12T16:15:24Z','2026-10-12T16:15:27Z','OK','github-actions','2026-10-12: 0 buys, 0 sells this run; 138 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261012T162015Z-speed','2026-10-12T16:20:24Z','2026-10-12T16:20:28Z','OK','github-actions','2026-10-12: 0 buys, 0 sells this run; 153 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261012T162515Z-speed','2026-10-12T16:25:23Z','2026-10-12T16:25:25Z','OK','github-actions','2026-10-12: 0 buys, 0 sells this run; 155 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261012T162645Z-speed','2026-10-12T16:26:52Z','2026-10-12T16:26:53Z','OK','github-actions','2026-10-12: 0 buys, 0 sells this run; 156 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261012T163145Z-speed','2026-10-12T16:31:52Z','2026-10-12T16:31:54Z','OK','github-actions','2026-10-12: 0 buys, 0 sells this run; 161 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261012T163645Z-speed','2026-10-12T16:36:53Z','2026-10-12T16:36:54Z','OK','github-actions','2026-10-12: 0 buys, 0 sells this run; 166 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261012T164145Z-speed','2026-10-12T16:41:52Z','2026-10-12T16:41:54Z','OK','github-actions','2026-10-12: 0 buys, 0 sells this run; 172 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261012T164645Z-speed','2026-10-12T16:46:52Z','2026-10-12T16:46:53Z','OK','github-actions','2026-10-12: 0 buys, 0 sells this run; 176 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261012T164821Z-speed','2026-10-12T16:48:30Z','2026-10-12T16:48:33Z','OK','github-actions','2026-10-12: 0 buys, 0 sells this run; 178 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261012T165321Z-speed','2026-10-12T16:53:29Z','2026-10-12T16:53:31Z','OK','github-actions','2026-10-12: 0 buys, 0 sells this run; 184 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261012T165821Z-speed','2026-10-12T16:58:27Z','2026-10-12T16:58:30Z','OK','github-actions','2026-10-12: 0 buys, 0 sells this run; 193 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261012T173400Z-speed','2026-10-12T17:34:07Z','2026-10-12T17:34:17Z','OK','github-actions','2026-10-12: 0 buys, 0 sells this run; 250 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261012T174933Z-speed','2026-10-12T17:49:40Z','2026-10-12T17:49:46Z','OK','github-actions','2026-10-12: 0 buys, 0 sells this run; 274 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261012T180719Z-speed','2026-10-12T18:07:29Z','2026-10-12T18:07:31Z','OK','github-actions','2026-10-12: 0 buys, 0 sells this run; 274 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261012T213411Z-speed','2026-10-12T21:36:14Z','2026-10-12T21:36:17Z','OK','github-actions','closed 2026-10-12: equity $100.00 (0 trades); 2026-10-12: 0 buys, 0 sells this run; 274 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261013T020022Z-speed','2026-10-13T02:00:27Z','2026-10-13T02:00:27Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261013T021408Z-speed','2026-10-13T02:14:14Z','2026-10-13T02:14:14Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261013T023504Z-speed','2026-10-13T02:35:10Z','2026-10-13T02:35:10Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261013T024332Z-speed','2026-10-13T02:43:37Z','2026-10-13T02:43:37Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261013T033510Z-speed','2026-10-13T03:35:16Z','2026-10-13T03:35:16Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261013T094554Z-speed','2026-10-13T09:45:59Z','2026-10-13T09:45:59Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261013T174833Z-speed','2026-10-13T17:49:43Z','2026-10-13T17:49:45Z','OK','github-actions','2026-10-13: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261013T194605Z-speed','2026-10-13T19:46:13Z','2026-10-13T19:46:17Z','OK','github-actions','2026-10-13: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261013T232833Z-speed','2026-10-13T23:30:24Z','2026-10-13T23:30:26Z','OK','github-actions','closed 2026-10-13: equity $100.00 (0 trades); 2026-10-13: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261013T234404Z-speed','2026-10-13T23:44:09Z','2026-10-13T23:44:09Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261013T235108Z-speed','2026-10-13T23:51:15Z','2026-10-13T23:51:15Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261014T001753Z-speed','2026-10-14T00:17:59Z','2026-10-14T00:17:59Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261014T003700Z-speed','2026-10-14T00:37:06Z','2026-10-14T00:37:06Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261014T015555Z-speed','2026-10-14T01:56:00Z','2026-10-14T01:56:00Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261014T052204Z-speed','2026-10-14T05:22:11Z','2026-10-14T05:22:11Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261014T103616Z-speed','2026-10-14T10:36:23Z','2026-10-14T10:36:23Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261014T152847Z-speed','2026-10-14T15:29:59Z','2026-10-14T15:30:01Z','OK','github-actions','2026-10-14: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261014T153347Z-speed','2026-10-14T15:33:56Z','2026-10-14T15:33:58Z','OK','github-actions','2026-10-14: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261014T153847Z-speed','2026-10-14T15:39:00Z','2026-10-14T15:39:01Z','OK','github-actions','2026-10-14: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261014T154347Z-speed','2026-10-14T15:43:54Z','2026-10-14T15:43:55Z','OK','github-actions','2026-10-14: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261014T154847Z-speed','2026-10-14T15:48:56Z','2026-10-14T15:48:57Z','OK','github-actions','2026-10-14: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261014T155025Z-speed','2026-10-14T15:50:34Z','2026-10-14T15:50:35Z','OK','github-actions','2026-10-14: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261014T155525Z-speed','2026-10-14T15:55:34Z','2026-10-14T15:55:35Z','OK','github-actions','2026-10-14: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261014T160025Z-speed','2026-10-14T16:00:33Z','2026-10-14T16:00:34Z','OK','github-actions','2026-10-14: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261014T160525Z-speed','2026-10-14T16:05:34Z','2026-10-14T16:05:35Z','OK','github-actions','2026-10-14: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261014T161025Z-speed','2026-10-14T16:10:33Z','2026-10-14T16:10:34Z','OK','github-actions','2026-10-14: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261014T161157Z-speed','2026-10-14T16:12:06Z','2026-10-14T16:12:07Z','OK','github-actions','2026-10-14: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261014T161657Z-speed','2026-10-14T16:17:12Z','2026-10-14T16:17:13Z','OK','github-actions','2026-10-14: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261014T162157Z-speed','2026-10-14T16:22:07Z','2026-10-14T16:22:08Z','OK','github-actions','2026-10-14: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261014T162657Z-speed','2026-10-14T16:27:06Z','2026-10-14T16:27:07Z','OK','github-actions','2026-10-14: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261014T163157Z-speed','2026-10-14T16:32:06Z','2026-10-14T16:32:07Z','OK','github-actions','2026-10-14: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261014T163322Z-speed','2026-10-14T16:33:30Z','2026-10-14T16:33:31Z','OK','github-actions','2026-10-14: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261014T163822Z-speed','2026-10-14T16:38:28Z','2026-10-14T16:38:30Z','OK','github-actions','2026-10-14: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261014T164322Z-speed','2026-10-14T16:43:28Z','2026-10-14T16:43:29Z','OK','github-actions','2026-10-14: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261014T164822Z-speed','2026-10-14T16:48:29Z','2026-10-14T16:48:30Z','OK','github-actions','2026-10-14: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261014T165322Z-speed','2026-10-14T16:53:29Z','2026-10-14T16:53:30Z','OK','github-actions','2026-10-14: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261014T165457Z-speed','2026-10-14T16:55:06Z','2026-10-14T16:55:08Z','OK','github-actions','2026-10-14: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261014T165957Z-speed','2026-10-14T17:00:05Z','2026-10-14T17:00:07Z','OK','github-actions','2026-10-14: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261014T174737Z-speed','2026-10-14T17:47:46Z','2026-10-14T17:47:47Z','OK','github-actions','2026-10-14: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261014T211810Z-speed','2026-10-14T21:20:09Z','2026-10-14T21:20:13Z','OK','github-actions','closed 2026-10-14: equity $100.00 (0 trades); 2026-10-14: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261014T231110Z-speed','2026-10-14T23:11:17Z','2026-10-14T23:11:17Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261014T232450Z-speed','2026-10-14T23:24:56Z','2026-10-14T23:24:56Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261014T235511Z-speed','2026-10-14T23:55:16Z','2026-10-14T23:55:16Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261015T000621Z-speed','2026-10-15T00:06:29Z','2026-10-15T00:06:29Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261015T012959Z-speed','2026-10-15T01:30:06Z','2026-10-15T01:30:06Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261015T050906Z-speed','2026-10-15T05:09:13Z','2026-10-15T05:09:13Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261015T101811Z-speed','2026-10-15T10:18:19Z','2026-10-15T10:18:19Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261015T152026Z-speed','2026-10-15T15:21:17Z','2026-10-15T15:21:18Z','OK','github-actions','2026-10-15: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261015T152526Z-speed','2026-10-15T15:25:33Z','2026-10-15T15:25:35Z','OK','github-actions','2026-10-15: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261015T153026Z-speed','2026-10-15T15:30:33Z','2026-10-15T15:30:33Z','OK','github-actions','2026-10-15: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261015T153526Z-speed','2026-10-15T15:35:33Z','2026-10-15T15:35:34Z','OK','github-actions','2026-10-15: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261015T154026Z-speed','2026-10-15T15:40:32Z','2026-10-15T15:40:33Z','OK','github-actions','2026-10-15: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261015T154200Z-speed','2026-10-15T15:42:17Z','2026-10-15T15:42:19Z','OK','github-actions','2026-10-15: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261015T154700Z-speed','2026-10-15T15:47:19Z','2026-10-15T15:47:20Z','OK','github-actions','2026-10-15: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261015T155200Z-speed','2026-10-15T15:52:19Z','2026-10-15T15:52:20Z','OK','github-actions','2026-10-15: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261015T155700Z-speed','2026-10-15T15:57:17Z','2026-10-15T15:57:18Z','OK','github-actions','2026-10-15: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261015T160200Z-speed','2026-10-15T16:02:22Z','2026-10-15T16:02:23Z','OK','github-actions','2026-10-15: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261015T160352Z-speed','2026-10-15T16:04:02Z','2026-10-15T16:04:04Z','OK','github-actions','2026-10-15: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261015T160852Z-speed','2026-10-15T16:09:00Z','2026-10-15T16:09:02Z','OK','github-actions','2026-10-15: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261015T161352Z-speed','2026-10-15T16:13:59Z','2026-10-15T16:14:01Z','OK','github-actions','2026-10-15: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261015T161851Z-speed','2026-10-15T16:19:01Z','2026-10-15T16:19:03Z','OK','github-actions','2026-10-15: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261015T162352Z-speed','2026-10-15T16:24:00Z','2026-10-15T16:24:02Z','OK','github-actions','2026-10-15: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261015T162525Z-speed','2026-10-15T16:25:33Z','2026-10-15T16:25:34Z','OK','github-actions','2026-10-15: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261015T163025Z-speed','2026-10-15T16:30:32Z','2026-10-15T16:30:33Z','OK','github-actions','2026-10-15: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261015T163525Z-speed','2026-10-15T16:35:32Z','2026-10-15T16:35:33Z','OK','github-actions','2026-10-15: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261015T164025Z-speed','2026-10-15T16:40:32Z','2026-10-15T16:40:32Z','OK','github-actions','2026-10-15: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261015T164525Z-speed','2026-10-15T16:45:32Z','2026-10-15T16:45:33Z','OK','github-actions','2026-10-15: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261015T164659Z-speed','2026-10-15T16:47:06Z','2026-10-15T16:47:08Z','OK','github-actions','2026-10-15: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261015T165159Z-speed','2026-10-15T16:52:06Z','2026-10-15T16:52:08Z','OK','github-actions','2026-10-15: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261015T165659Z-speed','2026-10-15T16:57:06Z','2026-10-15T16:57:07Z','OK','github-actions','2026-10-15: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261015T173635Z-speed','2026-10-15T17:36:43Z','2026-10-15T17:36:44Z','OK','github-actions','2026-10-15: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261015T203351Z-speed','2026-10-15T20:36:01Z','2026-10-15T20:36:05Z','OK','github-actions','closed 2026-10-15: equity $100.00 (0 trades); 2026-10-15: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261015T230228Z-speed','2026-10-15T23:02:34Z','2026-10-15T23:02:34Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261015T231534Z-speed','2026-10-15T23:15:41Z','2026-10-15T23:15:41Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261015T234217Z-speed','2026-10-15T23:42:22Z','2026-10-15T23:42:22Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261015T235055Z-speed','2026-10-15T23:51:01Z','2026-10-15T23:51:01Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261016T012141Z-speed','2026-10-16T01:21:48Z','2026-10-16T01:21:48Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261016T045919Z-speed','2026-10-16T04:59:23Z','2026-10-16T04:59:23Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261016T100617Z-speed','2026-10-16T10:06:24Z','2026-10-16T10:06:24Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261016T150042Z-speed','2026-10-16T15:01:48Z','2026-10-16T15:01:49Z','OK','github-actions','2026-10-16: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261016T150542Z-speed','2026-10-16T15:05:49Z','2026-10-16T15:05:50Z','OK','github-actions','2026-10-16: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261016T151042Z-speed','2026-10-16T15:10:49Z','2026-10-16T15:10:50Z','OK','github-actions','2026-10-16: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261016T151542Z-speed','2026-10-16T15:15:49Z','2026-10-16T15:15:50Z','OK','github-actions','2026-10-16: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261016T152042Z-speed','2026-10-16T15:20:50Z','2026-10-16T15:20:51Z','OK','github-actions','2026-10-16: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261016T152216Z-speed','2026-10-16T15:22:25Z','2026-10-16T15:22:26Z','OK','github-actions','2026-10-16: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261016T152716Z-speed','2026-10-16T15:27:24Z','2026-10-16T15:27:25Z','OK','github-actions','2026-10-16: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261016T153216Z-speed','2026-10-16T15:32:23Z','2026-10-16T15:32:24Z','OK','github-actions','2026-10-16: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261016T153716Z-speed','2026-10-16T15:37:24Z','2026-10-16T15:37:25Z','OK','github-actions','2026-10-16: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261016T154216Z-speed','2026-10-16T15:42:23Z','2026-10-16T15:42:24Z','OK','github-actions','2026-10-16: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261016T154342Z-speed','2026-10-16T15:43:50Z','2026-10-16T15:43:52Z','OK','github-actions','2026-10-16: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261016T154842Z-speed','2026-10-16T15:48:50Z','2026-10-16T15:48:51Z','OK','github-actions','2026-10-16: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261016T155342Z-speed','2026-10-16T15:53:49Z','2026-10-16T15:53:51Z','OK','github-actions','2026-10-16: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261016T155842Z-speed','2026-10-16T15:58:47Z','2026-10-16T15:58:48Z','OK','github-actions','2026-10-16: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261016T160342Z-speed','2026-10-16T16:03:51Z','2026-10-16T16:03:52Z','OK','github-actions','2026-10-16: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261016T160520Z-speed','2026-10-16T16:05:28Z','2026-10-16T16:05:30Z','OK','github-actions','2026-10-16: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261016T161020Z-speed','2026-10-16T16:10:27Z','2026-10-16T16:10:28Z','OK','github-actions','2026-10-16: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261016T161520Z-speed','2026-10-16T16:15:28Z','2026-10-16T16:15:29Z','OK','github-actions','2026-10-16: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261016T162020Z-speed','2026-10-16T16:20:28Z','2026-10-16T16:20:29Z','OK','github-actions','2026-10-16: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261016T162520Z-speed','2026-10-16T16:25:28Z','2026-10-16T16:25:29Z','OK','github-actions','2026-10-16: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261016T162652Z-speed','2026-10-16T16:26:59Z','2026-10-16T16:27:00Z','OK','github-actions','2026-10-16: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261016T163152Z-speed','2026-10-16T16:31:59Z','2026-10-16T16:32:00Z','OK','github-actions','2026-10-16: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261016T163652Z-speed','2026-10-16T16:36:59Z','2026-10-16T16:37:00Z','OK','github-actions','2026-10-16: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261016T164152Z-speed','2026-10-16T16:41:58Z','2026-10-16T16:41:59Z','OK','github-actions','2026-10-16: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261016T164652Z-speed','2026-10-16T16:46:59Z','2026-10-16T16:47:00Z','OK','github-actions','2026-10-16: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261016T164827Z-speed','2026-10-16T16:48:34Z','2026-10-16T16:48:36Z','OK','github-actions','2026-10-16: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261016T165327Z-speed','2026-10-16T16:53:35Z','2026-10-16T16:53:36Z','OK','github-actions','2026-10-16: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261016T165827Z-speed','2026-10-16T16:58:32Z','2026-10-16T16:58:33Z','OK','github-actions','2026-10-16: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261016T171056Z-speed','2026-10-16T17:11:04Z','2026-10-16T17:11:05Z','OK','github-actions','2026-10-16: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261016T192136Z-speed','2026-10-16T19:21:45Z','2026-10-16T19:21:47Z','OK','github-actions','2026-10-16: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261016T195856Z-speed','2026-10-16T19:59:01Z','2026-10-16T19:59:03Z','OK','github-actions','2026-10-16: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261016T224818Z-speed','2026-10-16T22:50:16Z','2026-10-16T22:50:19Z','OK','github-actions','closed 2026-10-16: equity $100.00 (0 trades); 2026-10-16: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261016T230004Z-speed','2026-10-16T23:00:10Z','2026-10-16T23:00:10Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261016T233455Z-speed','2026-10-16T23:35:01Z','2026-10-16T23:35:01Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261016T235224Z-speed','2026-10-16T23:52:30Z','2026-10-16T23:52:30Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261017T012024Z-speed','2026-10-17T01:20:31Z','2026-10-17T01:20:31Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261017T045839Z-speed','2026-10-17T04:58:43Z','2026-10-17T04:58:43Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261017T051855Z-speed','2026-10-17T05:19:01Z','2026-10-17T05:19:01Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261017T094020Z-speed','2026-10-17T09:40:25Z','2026-10-17T09:40:25Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261017T131205Z-speed','2026-10-17T13:12:11Z','2026-10-17T13:12:11Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261017T164025Z-speed','2026-10-17T16:40:31Z','2026-10-17T16:40:31Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261017T185154Z-speed','2026-10-17T18:52:02Z','2026-10-17T18:52:02Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261017T214626Z-speed','2026-10-17T21:46:32Z','2026-10-17T21:46:32Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261017T232418Z-speed','2026-10-17T23:24:25Z','2026-10-17T23:24:25Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261018T013136Z-speed','2026-10-18T01:31:46Z','2026-10-18T01:31:46Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261018T063518Z-speed','2026-10-18T06:35:24Z','2026-10-18T06:35:24Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261018T114142Z-speed','2026-10-18T11:41:47Z','2026-10-18T11:41:47Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261018T144953Z-speed','2026-10-18T14:49:59Z','2026-10-18T14:49:59Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261018T165656Z-speed','2026-10-18T16:57:01Z','2026-10-18T16:57:01Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261018T194224Z-speed','2026-10-18T19:42:30Z','2026-10-18T19:42:30Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261018T215623Z-speed','2026-10-18T21:56:29Z','2026-10-18T21:56:29Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261018T233830Z-speed','2026-10-18T23:38:36Z','2026-10-18T23:38:36Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261019T013909Z-speed','2026-10-19T01:39:15Z','2026-10-19T01:39:15Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261019T064733Z-speed','2026-10-19T06:47:40Z','2026-10-19T06:47:40Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261019T145852Z-speed','2026-10-19T14:59:53Z','2026-10-19T14:59:54Z','OK','github-actions','2026-10-19: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261019T150352Z-speed','2026-10-19T15:04:00Z','2026-10-19T15:04:01Z','OK','github-actions','2026-10-19: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261019T150852Z-speed','2026-10-19T15:08:59Z','2026-10-19T15:09:00Z','OK','github-actions','2026-10-19: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261019T151352Z-speed','2026-10-19T15:13:58Z','2026-10-19T15:13:59Z','OK','github-actions','2026-10-19: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261019T151852Z-speed','2026-10-19T15:19:01Z','2026-10-19T15:19:02Z','OK','github-actions','2026-10-19: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261019T152024Z-speed','2026-10-19T15:20:31Z','2026-10-19T15:20:32Z','OK','github-actions','2026-10-19: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261019T152524Z-speed','2026-10-19T15:25:31Z','2026-10-19T15:25:32Z','OK','github-actions','2026-10-19: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261019T153024Z-speed','2026-10-19T15:30:30Z','2026-10-19T15:30:31Z','OK','github-actions','2026-10-19: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261019T153524Z-speed','2026-10-19T15:35:31Z','2026-10-19T15:35:32Z','OK','github-actions','2026-10-19: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261019T154024Z-speed','2026-10-19T15:40:30Z','2026-10-19T15:40:31Z','OK','github-actions','2026-10-19: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261019T154157Z-speed','2026-10-19T15:42:04Z','2026-10-19T15:42:06Z','OK','github-actions','2026-10-19: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261019T154657Z-speed','2026-10-19T15:47:04Z','2026-10-19T15:47:06Z','OK','github-actions','2026-10-19: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261019T155157Z-speed','2026-10-19T15:52:05Z','2026-10-19T15:52:06Z','OK','github-actions','2026-10-19: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261019T155657Z-speed','2026-10-19T15:57:04Z','2026-10-19T15:57:05Z','OK','github-actions','2026-10-19: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261019T160157Z-speed','2026-10-19T16:02:05Z','2026-10-19T16:02:07Z','OK','github-actions','2026-10-19: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261019T160325Z-speed','2026-10-19T16:03:33Z','2026-10-19T16:03:34Z','OK','github-actions','2026-10-19: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261019T160825Z-speed','2026-10-19T16:08:32Z','2026-10-19T16:08:33Z','OK','github-actions','2026-10-19: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261019T161325Z-speed','2026-10-19T16:13:31Z','2026-10-19T16:13:32Z','OK','github-actions','2026-10-19: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261019T161825Z-speed','2026-10-19T16:18:32Z','2026-10-19T16:18:33Z','OK','github-actions','2026-10-19: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261019T162325Z-speed','2026-10-19T16:23:32Z','2026-10-19T16:23:33Z','OK','github-actions','2026-10-19: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261019T162449Z-speed','2026-10-19T16:24:57Z','2026-10-19T16:24:58Z','OK','github-actions','2026-10-19: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261019T162949Z-speed','2026-10-19T16:29:56Z','2026-10-19T16:29:57Z','OK','github-actions','2026-10-19: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261019T163449Z-speed','2026-10-19T16:34:56Z','2026-10-19T16:34:57Z','OK','github-actions','2026-10-19: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261019T163949Z-speed','2026-10-19T16:39:55Z','2026-10-19T16:39:56Z','OK','github-actions','2026-10-19: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261019T164449Z-speed','2026-10-19T16:44:54Z','2026-10-19T16:44:55Z','OK','github-actions','2026-10-19: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261019T164623Z-speed','2026-10-19T16:46:33Z','2026-10-19T16:46:34Z','OK','github-actions','2026-10-19: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261019T165123Z-speed','2026-10-19T16:51:32Z','2026-10-19T16:51:33Z','OK','github-actions','2026-10-19: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261019T165623Z-speed','2026-10-19T16:56:31Z','2026-10-19T16:56:32Z','OK','github-actions','2026-10-19: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261019T190122Z-speed','2026-10-19T19:01:31Z','2026-10-19T19:01:33Z','OK','github-actions','2026-10-19: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261019T225519Z-speed','2026-10-19T22:57:08Z','2026-10-19T22:57:10Z','OK','github-actions','closed 2026-10-19: equity $100.00 (0 trades); 2026-10-19: 0 buys, 0 sells this run; 0 Jev calls today, 0 trades today',NULL);
INSERT INTO "runs" VALUES('20261019T233526Z-speed','2026-10-19T23:35:32Z','2026-10-19T23:35:32Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261019T235511Z-speed','2026-10-19T23:55:17Z','2026-10-19T23:55:17Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261020T001946Z-speed','2026-10-20T00:19:53Z','2026-10-20T00:19:53Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261020T003858Z-speed','2026-10-20T00:39:04Z','2026-10-20T00:39:04Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261020T015106Z-speed','2026-10-20T01:51:12Z','2026-10-20T01:51:12Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261020T051531Z-speed','2026-10-20T05:15:37Z','2026-10-20T05:15:37Z','OK','github-actions','no action needed',NULL);
CREATE TABLE snapshots (
  session TEXT PRIMARY KEY, created_at TEXT NOT NULL, run_id TEXT, equity REAL NOT NULL,
  cash REAL NOT NULL, positions_value REAL NOT NULL, spy_bh_equity REAL, cash_bh_equity REAL,
  peak REAL NOT NULL, drawdown REAL NOT NULL, regime TEXT, risk_state TEXT, marks TEXT, holdings TEXT
);
INSERT INTO "snapshots" VALUES('2026-10-12','2026-10-12T21:34:11Z','20261012T213411Z-speed',100.0,100.0,0.0,9.98427870970617164e+01,100.0,100.0,0.0,'0 trades','{"peak": 100.0, "drawdown": 0.0}','{"marks": {}, "flags": {}}','{}');
INSERT INTO "snapshots" VALUES('2026-10-13','2026-10-13T23:28:33Z','20261013T232833Z-speed',100.0,100.0,0.0,99.8312430300712,100.0,100.0,0.0,'0 trades','{"peak": 100.0, "drawdown": 0.0}','{"marks": {}, "flags": {}}','{}');
INSERT INTO "snapshots" VALUES('2026-10-14','2026-10-14T21:18:10Z','20261014T211810Z-speed',100.0,100.0,0.0,9.87520998885369323e+01,100.0,100.0,0.0,'0 trades','{"peak": 100.0, "drawdown": 0.0}','{"marks": {}, "flags": {}}','{}');
INSERT INTO "snapshots" VALUES('2026-10-15','2026-10-15T20:33:51Z','20261015T203351Z-speed',100.0,100.0,0.0,9.90331125531816241e+01,100.0,100.0,0.0,'0 trades','{"peak": 100.0, "drawdown": 0.0}','{"marks": {}, "flags": {}}','{}');
INSERT INTO "snapshots" VALUES('2026-10-16','2026-10-16T22:48:18Z','20261016T224818Z-speed',100.0,100.0,0.0,9.79372955184161497e+01,100.0,100.0,0.0,'0 trades','{"peak": 100.0, "drawdown": 0.0}','{"marks": {}, "flags": {}}','{}');
INSERT INTO "snapshots" VALUES('2026-10-19','2026-10-19T22:55:19Z','20261019T225519Z-speed',100.0,100.0,0.0,9.83517541514809181e+01,100.0,100.0,0.0,'0 trades','{"peak": 100.0, "drawdown": 0.0}','{"marks": {}, "flags": {}}','{}');
CREATE TABLE state (key TEXT PRIMARY KEY, value TEXT NOT NULL, updated_at TEXT NOT NULL);
INSERT INTO "state" VALUES('cash','100.0','2026-10-19T22:57:09Z');
INSERT INTO "state" VALUES('strategy_integrity_ok','true','2026-10-20T05:15:37Z');
INSERT INTO "state" VALUES('benchmark','{"ticker": "SPY", "qty": 0.12831614217938572, "entry_price": 779.3251753173828, "entry_session": "2026-10-12", "div_cash": 0.0, "note": "SPY bought at this book''s first official open"}','2026-10-12T16:06:17Z');
INSERT INTO "state" VALUES('dt:2026-10-12','{"session": "2026-10-12", "cash_at_open": 100.0, "cash": 100.0, "buys_used": 0.0, "candidates": [], "pending": [], "positions": {}, "traded": [], "processed_through": "2026-10-12T15:59:00-04:00", "closed": true, "entry_signals": {}}','2026-10-12T21:36:16Z');
INSERT INTO "state" VALUES('sp:2026-10-12','{"pending": [], "calls": 274, "trades": 0, "held": {}}','2026-10-12T21:36:16Z');
INSERT INTO "state" VALUES('risk','{"peak": 100.0, "drawdown": 0.0}','2026-10-19T22:57:10Z');
INSERT INTO "state" VALUES('dt:2026-10-13','{"session": "2026-10-13", "cash_at_open": 100.0, "cash": 100.0, "buys_used": 0.0, "candidates": [], "pending": [], "positions": {}, "traded": [], "processed_through": "2026-10-13T15:59:00-04:00", "closed": true, "entry_signals": {}}','2026-10-13T23:30:25Z');
INSERT INTO "state" VALUES('sp:2026-10-13','{"pending": [], "calls": 0, "trades": 0, "held": {}}','2026-10-13T23:30:25Z');
INSERT INTO "state" VALUES('dt:2026-10-14','{"session": "2026-10-14", "cash_at_open": 100.0, "cash": 100.0, "buys_used": 0.0, "candidates": [], "pending": [], "positions": {}, "traded": [], "processed_through": "2026-10-14T15:59:00-04:00", "closed": true, "entry_signals": {}}','2026-10-14T21:20:12Z');
INSERT INTO "state" VALUES('sp:2026-10-14','{"pending": [], "calls": 0, "trades": 0, "held": {}}','2026-10-14T21:20:12Z');
INSERT INTO "state" VALUES('dt:2026-10-15','{"session": "2026-10-15", "cash_at_open": 100.0, "cash": 100.0, "buys_used": 0.0, "candidates": [], "pending": [], "positions": {}, "traded": [], "processed_through": "2026-10-15T15:59:00-04:00", "closed": true, "entry_signals": {}}','2026-10-15T20:36:04Z');
INSERT INTO "state" VALUES('sp:2026-10-15','{"pending": [], "calls": 0, "trades": 0, "held": {}}','2026-10-15T20:36:04Z');
INSERT INTO "state" VALUES('dt:2026-10-16','{"session": "2026-10-16", "cash_at_open": 100.0, "cash": 100.0, "buys_used": 0.0, "candidates": [], "pending": [], "positions": {}, "traded": [], "processed_through": "2026-10-16T15:59:00-04:00", "closed": true, "entry_signals": {}}','2026-10-16T22:50:18Z');
INSERT INTO "state" VALUES('sp:2026-10-16','{"pending": [], "calls": 0, "trades": 0, "held": {}}','2026-10-16T22:50:18Z');
INSERT INTO "state" VALUES('dt:2026-10-19','{"session": "2026-10-19", "cash_at_open": 100.0, "cash": 100.0, "buys_used": 0.0, "candidates": [], "pending": [], "positions": {}, "traded": [], "processed_through": "2026-10-19T15:59:00-04:00", "closed": true, "entry_signals": {}}','2026-10-19T22:57:09Z');
INSERT INTO "state" VALUES('sp:2026-10-19','{"pending": [], "calls": 0, "trades": 0, "held": {}}','2026-10-19T22:57:09Z');
CREATE TABLE strategy_changes (
  id INTEGER PRIMARY KEY AUTOINCREMENT, logged_at TEXT NOT NULL, from_version TEXT, to_version TEXT,
  from_sha256 TEXT, to_sha256 TEXT, effective_session TEXT, description TEXT NOT NULL, evidence TEXT
);
INSERT INTO "strategy_changes" VALUES(1,'2026-10-12T18:04:10Z','speed-1.0.0','speed-1.1.0','889754fd5be0a3250a777c1abe8c2a7b14a3689fc30365e2be766a28993df488','8a0d081b0128ac8cac564ad06320fc0739e129c2bb1fb12cb1381776755fa825','next decision','Retire the speed book: switch Jev calls off (caps 0); the book stays flat. Jev showed no skill on this book''s exact question.','research/review_2026_10_12/jev_offline_output.txt: 1,190 past-minute states, 7 sessions, AUC 0.491 (95% CI 0.468-0.515), p>=0.50 hit 14.2% vs 15.0% base, no call reached 0.65; rule written before the run. Live Oct 12: 274 calls, corr -0.10.');
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
INSERT INTO "sqlite_sequence" VALUES('strategy_changes',1);
COMMIT;
