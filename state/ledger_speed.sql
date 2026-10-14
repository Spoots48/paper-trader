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
CREATE TABLE snapshots (
  session TEXT PRIMARY KEY, created_at TEXT NOT NULL, run_id TEXT, equity REAL NOT NULL,
  cash REAL NOT NULL, positions_value REAL NOT NULL, spy_bh_equity REAL, cash_bh_equity REAL,
  peak REAL NOT NULL, drawdown REAL NOT NULL, regime TEXT, risk_state TEXT, marks TEXT, holdings TEXT
);
INSERT INTO "snapshots" VALUES('2026-10-12','2026-10-12T21:34:11Z','20261012T213411Z-speed',100.0,100.0,0.0,9.98427870970617164e+01,100.0,100.0,0.0,'0 trades','{"peak": 100.0, "drawdown": 0.0}','{"marks": {}, "flags": {}}','{}');
INSERT INTO "snapshots" VALUES('2026-10-13','2026-10-13T23:28:33Z','20261013T232833Z-speed',100.0,100.0,0.0,99.8312430300712,100.0,100.0,0.0,'0 trades','{"peak": 100.0, "drawdown": 0.0}','{"marks": {}, "flags": {}}','{}');
CREATE TABLE state (key TEXT PRIMARY KEY, value TEXT NOT NULL, updated_at TEXT NOT NULL);
INSERT INTO "state" VALUES('cash','100.0','2026-10-13T23:30:25Z');
INSERT INTO "state" VALUES('strategy_integrity_ok','true','2026-10-14T01:56:00Z');
INSERT INTO "state" VALUES('benchmark','{"ticker": "SPY", "qty": 0.12831614217938572, "entry_price": 779.3251753173828, "entry_session": "2026-10-12", "div_cash": 0.0, "note": "SPY bought at this book''s first official open"}','2026-10-12T16:06:17Z');
INSERT INTO "state" VALUES('dt:2026-10-12','{"session": "2026-10-12", "cash_at_open": 100.0, "cash": 100.0, "buys_used": 0.0, "candidates": [], "pending": [], "positions": {}, "traded": [], "processed_through": "2026-10-12T15:59:00-04:00", "closed": true, "entry_signals": {}}','2026-10-12T21:36:16Z');
INSERT INTO "state" VALUES('sp:2026-10-12','{"pending": [], "calls": 274, "trades": 0, "held": {}}','2026-10-12T21:36:16Z');
INSERT INTO "state" VALUES('risk','{"peak": 100.0, "drawdown": 0.0}','2026-10-13T23:30:26Z');
INSERT INTO "state" VALUES('dt:2026-10-13','{"session": "2026-10-13", "cash_at_open": 100.0, "cash": 100.0, "buys_used": 0.0, "candidates": [], "pending": [], "positions": {}, "traded": [], "processed_through": "2026-10-13T15:59:00-04:00", "closed": true, "entry_signals": {}}','2026-10-13T23:30:25Z');
INSERT INTO "state" VALUES('sp:2026-10-13','{"pending": [], "calls": 0, "trades": 0, "held": {}}','2026-10-13T23:30:25Z');
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
INSERT INTO "sqlite_sequence" VALUES('events',4);
INSERT INTO "sqlite_sequence" VALUES('strategy_changes',1);
COMMIT;
