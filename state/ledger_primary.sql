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
INSERT INTO "decisions" VALUES(5,'decide:2026-09-28','20260925T202649Z-primary','2026-09-25T20:26:49Z','2026-09-25','2026-09-28','*','system','INFO','DECIDED','0 orders (MOO) for 2026-09-28; regime ON; SPY 771.35 vs 200d 718.45; VIX 14.899999618530273; 0 earnings reactions on 2026-09-25; rebalance=True','{"regime": "ON", "spy_close": 771.3499755859375, "spy_sma200": 718.4519995117188, "vix": 14.899999618530273, "order_type": "MOO", "data_through": "2026-09-25", "stock_bars_missing": 0, "risk": {"drawdown": 0.0025103459540762874, "halted": false, "paused": false}, "earnings_events_loaded": 0, "earnings_dates_failed": []}','[]');
INSERT INTO "decisions" VALUES(6,'decide:2026-09-29','20260928T202033Z-primary','2026-09-28T20:20:33Z','2026-09-28','2026-09-29','*','system','INFO','DECIDED','0 orders (MOO) for 2026-09-29; regime ON; SPY 765.61 vs 200d 718.86; VIX 16.06999969482422; 0 earnings reactions on 2026-09-28; rebalance=False','{"regime": "ON", "spy_close": 765.6099853515625, "spy_sma200": 718.8648495483399, "vix": 16.06999969482422, "order_type": "MOO", "data_through": "2026-09-28", "stock_bars_missing": 0, "risk": {"drawdown": 0.009784291178685733, "halted": false, "paused": false}, "earnings_events_loaded": 0, "earnings_dates_failed": []}','[]');
INSERT INTO "decisions" VALUES(7,'decide:2026-09-30','20260929T224020Z-primary','2026-09-29T22:40:20Z','2026-09-29','2026-09-30','*','system','INFO','DECIDED','0 orders (MOO) for 2026-09-30; regime ON; SPY 764.20 vs 200d 719.25; VIX 16.040000915527344; 0 earnings reactions on 2026-09-29; rebalance=False','{"regime": "ON", "spy_close": 764.2000122070312, "spy_sma200": 719.2479995727539, "vix": 16.040000915527344, "order_type": "MOO", "data_through": "2026-09-29", "stock_bars_missing": 0, "risk": {"drawdown": 0.011571065546361448, "halted": false, "paused": false}, "earnings_events_loaded": 0, "earnings_dates_failed": []}','[]');
INSERT INTO "decisions" VALUES(8,'decide:2026-10-01','20260930T223106Z-primary','2026-09-30T22:31:06Z','2026-09-30','2026-10-01','*','system','INFO','DECIDED','0 orders (MOO) for 2026-10-01; regime ON; SPY 762.63 vs 200d 719.62; VIX 16.34000015258789; 0 earnings reactions on 2026-09-30; rebalance=False','{"regime": "ON", "spy_close": 762.6300048828125, "spy_sma200": 719.6152996826172, "vix": 16.34000015258789, "order_type": "MOO", "data_through": "2026-09-30", "stock_bars_missing": 0, "risk": {"drawdown": 0.01356064162790449, "halted": false, "paused": false}, "earnings_events_loaded": 0, "earnings_dates_failed": []}','[]');
INSERT INTO "decisions" VALUES(9,'decide:2026-10-02','20261001T225655Z-primary','2026-10-01T22:56:55Z','2026-10-01','2026-10-02','*','system','INFO','DECIDED','0 orders (MOO) for 2026-10-02; regime ON; SPY 763.99 vs 200d 720.03; VIX 16.389999389648438; 0 earnings reactions on 2026-10-01; rebalance=False','{"regime": "ON", "spy_close": 763.989990234375, "spy_sma200": 720.0264495849609, "vix": 16.389999389648438, "order_type": "MOO", "data_through": "2026-10-01", "stock_bars_missing": 0, "risk": {"drawdown": 0.011837213790990453, "halted": false, "paused": false}, "earnings_events_loaded": 0, "earnings_dates_failed": []}','[]');
INSERT INTO "decisions" VALUES(10,'decide:2026-10-05','20261002T222904Z-primary','2026-10-02T22:29:04Z','2026-10-02','2026-10-05','*','system','INFO','DECIDED','0 orders (MOO) for 2026-10-05; regime ON; SPY 769.64 vs 200d 720.47; VIX 15.3100004196167; 0 earnings reactions on 2026-10-02; rebalance=True','{"regime": "ON", "spy_close": 769.6400146484375, "spy_sma200": 720.4709997558593, "vix": 15.3100004196167, "order_type": "MOO", "data_through": "2026-10-02", "stock_bars_missing": 0, "risk": {"drawdown": 0.004677276852513734, "halted": false, "paused": false}, "earnings_events_loaded": 0, "earnings_dates_failed": []}','[]');
INSERT INTO "decisions" VALUES(11,'2026-10-06:000:residual:SPY:FUNDING','20261005T220617Z-primary','2026-10-05T22:06:17Z','2026-10-05','2026-10-06','SPY','residual','SELL','FUNDING','sell $0.00 of SPY to fund new positions','{}','[]');
INSERT INTO "decisions" VALUES(12,'decide:2026-10-06','20261005T220617Z-primary','2026-10-05T22:06:17Z','2026-10-05','2026-10-06','*','system','INFO','DECIDED','1 orders (MOO) for 2026-10-06; regime ON; SPY 774.83 vs 200d 720.95; VIX 15.520000457763672; 0 earnings reactions on 2026-10-05; rebalance=False','{"regime": "ON", "spy_close": 774.8300170898438, "spy_sma200": 720.9507998657226, "vix": 15.520000457763672, "order_type": "MOO", "data_through": "2026-10-05", "stock_bars_missing": 0, "risk": {"drawdown": 0.0, "halted": false, "paused": false}, "earnings_events_loaded": 0, "earnings_dates_failed": []}','[]');
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
INSERT INTO "events" VALUES(12,'2026-09-25T20:26:56Z','20260925T202649Z-primary','snapshot','{"cash": 2.0004110984400256, "drawdown": 0.0025103459540762874, "equity": 99.74896540459237, "session": "2026-09-25", "spy_bh_equity": 99.743841175028}','b8a1d66739af6b27add2f62eb8263be493574317c1dae98f694148e53afcced5','9ef9ee590e2e4b9f73d4f292107d2571401d801ed011d99fa12651eeadeac2e7');
INSERT INTO "events" VALUES(13,'2026-09-25T20:26:58Z','20260925T202649Z-primary','decision','{"action": "INFO", "code": "DECIDED", "key": "decide:2026-09-28", "reason": "0 orders (MOO) for 2026-09-28; regime ON; SPY 771.35 vs 200d 718.45; VIX 14.899999618530273; 0 earnings reactions on 2026-09-25; rebalance=True", "ticker": "*"}','9ef9ee590e2e4b9f73d4f292107d2571401d801ed011d99fa12651eeadeac2e7','085ab588a555537885868b36db86cd551482e5f7ea4d78c02b2f6913124fe8e4');
INSERT INTO "events" VALUES(14,'2026-09-28T20:20:43Z','20260928T202033Z-primary','snapshot','{"cash": 2.0004110984400256, "drawdown": 0.009784291178685733, "equity": 99.02157088213143, "session": "2026-09-28", "spy_bh_equity": 99.00159875277498}','085ab588a555537885868b36db86cd551482e5f7ea4d78c02b2f6913124fe8e4','c7433b4e5f3e9709d270d9a73af7cb7c51db3ec5c3ec777c6ff477333c7ebd7e');
INSERT INTO "events" VALUES(15,'2026-09-28T20:20:44Z','20260928T202033Z-primary','decision','{"action": "INFO", "code": "DECIDED", "key": "decide:2026-09-29", "reason": "0 orders (MOO) for 2026-09-29; regime ON; SPY 765.61 vs 200d 718.86; VIX 16.06999969482422; 0 earnings reactions on 2026-09-28; rebalance=False", "ticker": "*"}','c7433b4e5f3e9709d270d9a73af7cb7c51db3ec5c3ec777c6ff477333c7ebd7e','909823b6c2bbe91e4d9056197200b1b2521beb2a212ac3d683944883d29962e7');
INSERT INTO "events" VALUES(16,'2026-09-29T22:40:30Z','20260929T224020Z-primary','snapshot','{"cash": 2.0004110984400256, "drawdown": 0.011571065546361448, "equity": 98.84289344536386, "session": "2026-09-29", "spy_bh_equity": 98.8192740728755}','909823b6c2bbe91e4d9056197200b1b2521beb2a212ac3d683944883d29962e7','d1e245c8e475228dbc3b7825f430bfab6ea695bc8ea16d903c88b0a96439ea19');
INSERT INTO "events" VALUES(17,'2026-09-29T22:40:31Z','20260929T224020Z-primary','decision','{"action": "INFO", "code": "DECIDED", "key": "decide:2026-09-30", "reason": "0 orders (MOO) for 2026-09-30; regime ON; SPY 764.20 vs 200d 719.25; VIX 16.040000915527344; 0 earnings reactions on 2026-09-29; rebalance=False", "ticker": "*"}','d1e245c8e475228dbc3b7825f430bfab6ea695bc8ea16d903c88b0a96439ea19','1a36e08d7b1d45a6b337a105e094bd270b8b02715f56eeb2ee4fbb2cf2c4fb11');
INSERT INTO "events" VALUES(18,'2026-09-30T22:31:16Z','20260930T223106Z-primary','snapshot','{"cash": 2.0004110984400256, "drawdown": 0.01356064162790449, "equity": 98.64393583720955, "session": "2026-09-30", "spy_bh_equity": 98.61625525373111}','1a36e08d7b1d45a6b337a105e094bd270b8b02715f56eeb2ee4fbb2cf2c4fb11','01d3d7a8c85828d0687dd4e910b1e2e639b357a78cdf07450d8fa8bb0c305959');
INSERT INTO "events" VALUES(19,'2026-09-30T22:31:17Z','20260930T223106Z-primary','decision','{"action": "INFO", "code": "DECIDED", "key": "decide:2026-10-01", "reason": "0 orders (MOO) for 2026-10-01; regime ON; SPY 762.63 vs 200d 719.62; VIX 16.34000015258789; 0 earnings reactions on 2026-09-30; rebalance=False", "ticker": "*"}','01d3d7a8c85828d0687dd4e910b1e2e639b357a78cdf07450d8fa8bb0c305959','de44171334efa26b8ad058fbefa969ff9bd2354e6d20c478b7ebc5b03d798c6b');
INSERT INTO "events" VALUES(20,'2026-10-01T22:57:03Z','20261001T225655Z-primary','snapshot','{"cash": 2.0004110984400256, "drawdown": 0.011837213790990453, "equity": 98.81627862090096, "session": "2026-10-01", "spy_bh_equity": 98.79211597480467}','de44171334efa26b8ad058fbefa969ff9bd2354e6d20c478b7ebc5b03d798c6b','749de86df3d5640ff8048523d1aacc85c786ec89cf3c5636d86fa934d1ec9d2b');
INSERT INTO "events" VALUES(21,'2026-10-01T22:57:05Z','20261001T225655Z-primary','decision','{"action": "INFO", "code": "DECIDED", "key": "decide:2026-10-02", "reason": "0 orders (MOO) for 2026-10-02; regime ON; SPY 763.99 vs 200d 720.03; VIX 16.389999389648438; 0 earnings reactions on 2026-10-01; rebalance=False", "ticker": "*"}','749de86df3d5640ff8048523d1aacc85c786ec89cf3c5636d86fa934d1ec9d2b','74bc221dc405d32e4d1669d023aad63fd0daa6d6222d05390a0e153e6ea2673e');
INSERT INTO "events" VALUES(22,'2026-10-02T22:29:13Z','20261002T222904Z-primary','snapshot','{"cash": 2.0004110984400256, "drawdown": 0.004677276852513734, "equity": 99.53227231474862, "session": "2026-10-02", "spy_bh_equity": 99.52272484967135}','74bc221dc405d32e4d1669d023aad63fd0daa6d6222d05390a0e153e6ea2673e','1a00cc4c119caa6724ab24adb2ac1d0ef8dd742ded182acaf08e24379645a003');
INSERT INTO "events" VALUES(23,'2026-10-02T22:29:14Z','20261002T222904Z-primary','decision','{"action": "INFO", "code": "DECIDED", "key": "decide:2026-10-05", "reason": "0 orders (MOO) for 2026-10-05; regime ON; SPY 769.64 vs 200d 720.47; VIX 15.3100004196167; 0 earnings reactions on 2026-10-02; rebalance=True", "ticker": "*"}','1a00cc4c119caa6724ab24adb2ac1d0ef8dd742ded182acaf08e24379645a003','ca368e7565f64537c0059305b8d7a366c1cf6df688a2543d6ab6b2220a26e50c');
INSERT INTO "events" VALUES(24,'2026-10-05T22:06:27Z','20261005T220617Z-primary','snapshot','{"cash": 2.0004110984400256, "drawdown": 0.0, "equity": 100.18997018413339, "session": "2026-10-05", "spy_bh_equity": 100.19384793983596}','ca368e7565f64537c0059305b8d7a366c1cf6df688a2543d6ab6b2220a26e50c','395ea9bbe1ca503047d1d6985f8c45b8e707c555cdae7bdac8084b859685285d');
INSERT INTO "events" VALUES(25,'2026-10-05T22:06:28Z','20261005T220617Z-primary','decision','{"action": "SELL", "code": "FUNDING", "key": "2026-10-06:000:residual:SPY:FUNDING", "reason": "sell $0.00 of SPY to fund new positions", "ticker": "SPY"}','395ea9bbe1ca503047d1d6985f8c45b8e707c555cdae7bdac8084b859685285d','71ef7676635641af0e19f571637473a17dcafffe08457043ccc237f6477b4c7f');
INSERT INTO "events" VALUES(26,'2026-10-05T22:06:28Z','20261005T220617Z-primary','order','{"key": "2026-10-06:residual:SPY:SELL:FUNDING", "notional": null, "qty": 4.416695558493839e-06, "reason": "sell $0.00 of SPY to fund new positions", "session": "2026-10-06", "side": "SELL", "ticker": "SPY", "type": "MOO"}','71ef7676635641af0e19f571637473a17dcafffe08457043ccc237f6477b4c7f','cfa5916655aaf1ce85953ec05c0b08af9b27486a14ef05ec8b76ffd7c914df05');
INSERT INTO "events" VALUES(27,'2026-10-05T22:06:28Z','20261005T220617Z-primary','decision','{"action": "INFO", "code": "DECIDED", "key": "decide:2026-10-06", "reason": "1 orders (MOO) for 2026-10-06; regime ON; SPY 774.83 vs 200d 720.95; VIX 15.520000457763672; 0 earnings reactions on 2026-10-05; rebalance=False", "ticker": "*"}','cfa5916655aaf1ce85953ec05c0b08af9b27486a14ef05ec8b76ffd7c914df05','363d388ea5a1142acf2e9c43a00a225f24b3115cbb819185db4cfa42541d8f2e');
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
INSERT INTO "orders" VALUES('2026-10-06:residual:SPY:SELL:FUNDING','2026-10-05T22:06:17Z','20261005T220617Z-primary','SPY','SELL','MOO','2026-10-06','residual',NULL,4.4166955584938386e-06,5,'FUNDING','sell $0.00 of SPY to fund new positions','{}','{}','OPEN',NULL,'2026-10-05T22:06:28Z');
CREATE TABLE positions (
  ticker TEXT PRIMARY KEY, qty REAL NOT NULL, avg_cost REAL NOT NULL, sleeve TEXT NOT NULL,
  entry_session TEXT NOT NULL, entry_price REAL NOT NULL, initial_stop REAL, trail_pct REAL,
  high_water REAL NOT NULL, max_hold_until TEXT, stop_checked_through TEXT, meta TEXT
);
INSERT INTO "positions" VALUES('SPY',0.126724,7.73330931011962775e+02,'residual','2026-09-23',7.73330931011962775e+02,NULL,NULL,776.60498046875,NULL,'2026-10-05T16:00:00-04:00','{}');
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
INSERT INTO "runs" VALUES('20260925T141337Z-primary','2026-09-25T14:14:01Z','2026-09-25T14:14:01Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260925T143435Z-primary','2026-09-25T14:34:47Z','2026-09-25T14:34:47Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260925T145527Z-primary','2026-09-25T14:55:39Z','2026-09-25T14:55:39Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260925T151624Z-primary','2026-09-25T15:16:43Z','2026-09-25T15:16:44Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260925T153714Z-primary','2026-09-25T15:37:22Z','2026-09-25T15:37:22Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260925T155759Z-primary','2026-09-25T15:58:06Z','2026-09-25T15:58:06Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260925T161857Z-primary','2026-09-25T16:19:08Z','2026-09-25T16:19:08Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260925T163948Z-primary','2026-09-25T16:40:00Z','2026-09-25T16:40:00Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260925T170038Z-primary','2026-09-25T17:00:48Z','2026-09-25T17:00:49Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260925T172140Z-primary','2026-09-25T17:21:52Z','2026-09-25T17:21:52Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260925T173654Z-primary','2026-09-25T17:37:06Z','2026-09-25T17:37:06Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260925T175711Z-primary','2026-09-25T17:57:21Z','2026-09-25T17:57:21Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260925T181803Z-primary','2026-09-25T18:18:19Z','2026-09-25T18:18:19Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260925T183854Z-primary','2026-09-25T18:39:03Z','2026-09-25T18:39:03Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260925T185904Z-primary','2026-09-25T18:59:12Z','2026-09-25T18:59:13Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260925T191937Z-primary','2026-09-25T19:19:47Z','2026-09-25T19:19:47Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260925T193943Z-primary','2026-09-25T19:39:50Z','2026-09-25T19:39:50Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260925T200005Z-primary','2026-09-25T20:00:10Z','2026-09-25T20:00:12Z','OK','github-actions','waiting for final data for 2026-09-25',NULL);
INSERT INTO "runs" VALUES('20260925T201027Z-primary','2026-09-25T20:10:36Z','2026-09-25T20:10:37Z','OK','github-actions','waiting for final data for 2026-09-25',NULL);
INSERT INTO "runs" VALUES('20260925T202649Z-primary','2026-09-25T20:26:55Z','2026-09-25T20:26:58Z','OK','github-actions','closed 2026-09-25; decided for 2026-09-28: 0 orders (MOO), regime ON',NULL);
INSERT INTO "runs" VALUES('20260925T203611Z-primary','2026-09-25T20:36:17Z','2026-09-25T20:36:17Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260925T204359Z-primary','2026-09-25T20:44:05Z','2026-09-25T20:44:05Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260925T231353Z-primary','2026-09-25T23:13:58Z','2026-09-25T23:13:58Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260925T232853Z-primary','2026-09-25T23:28:58Z','2026-09-25T23:28:58Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260925T235618Z-primary','2026-09-25T23:56:24Z','2026-09-25T23:56:24Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260926T000854Z-primary','2026-09-26T00:09:00Z','2026-09-26T00:09:00Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260926T012931Z-primary','2026-09-26T01:29:36Z','2026-09-26T01:29:36Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260926T052542Z-primary','2026-09-26T05:26:01Z','2026-09-26T05:26:01Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260926T101343Z-primary','2026-09-26T10:14:02Z','2026-09-26T10:14:02Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260926T144327Z-primary','2026-09-26T14:43:46Z','2026-09-26T14:43:46Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260926T154342Z-primary','2026-09-26T15:43:46Z','2026-09-26T15:43:46Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260926T160423Z-primary','2026-09-26T16:04:31Z','2026-09-26T16:04:31Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260926T160820Z-primary','2026-09-26T16:08:26Z','2026-09-26T16:08:26Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260926T170954Z-primary','2026-09-26T17:10:01Z','2026-09-26T17:10:01Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260926T172332Z-primary','2026-09-26T17:23:38Z','2026-09-26T17:23:38Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260926T174430Z-primary','2026-09-26T17:44:34Z','2026-09-26T17:44:34Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260926T200944Z-primary','2026-09-26T20:09:49Z','2026-09-26T20:09:49Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260926T231025Z-primary','2026-09-26T23:10:30Z','2026-09-26T23:10:30Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260926T235158Z-primary','2026-09-26T23:52:04Z','2026-09-26T23:52:04Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260927T054210Z-primary','2026-09-27T05:42:28Z','2026-09-27T05:42:28Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260927T104519Z-primary','2026-09-27T10:45:25Z','2026-09-27T10:45:25Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260927T154725Z-primary','2026-09-27T15:47:44Z','2026-09-27T15:47:44Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260927T175658Z-primary','2026-09-27T17:57:10Z','2026-09-27T17:57:10Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260927T213844Z-primary','2026-09-27T21:38:48Z','2026-09-27T21:38:48Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260927T235655Z-primary','2026-09-27T23:57:00Z','2026-09-27T23:57:00Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260928T005734Z-primary','2026-09-28T00:57:39Z','2026-09-28T00:57:39Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260928T054924Z-primary','2026-09-28T05:49:30Z','2026-09-28T05:49:30Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260928T102355Z-primary','2026-09-28T10:24:08Z','2026-09-28T10:24:08Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260928T134907Z-primary','2026-09-28T13:50:24Z','2026-09-28T13:50:24Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260928T142632Z-primary','2026-09-28T14:26:38Z','2026-09-28T14:26:38Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260928T154845Z-primary','2026-09-28T15:48:51Z','2026-09-28T15:48:52Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260928T175015Z-primary','2026-09-28T17:50:36Z','2026-09-28T17:50:37Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260928T193951Z-primary','2026-09-28T19:39:57Z','2026-09-28T19:39:57Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260928T200014Z-primary','2026-09-28T20:00:22Z','2026-09-28T20:00:23Z','OK','github-actions','waiting for final data for 2026-09-28',NULL);
INSERT INTO "runs" VALUES('20260928T202033Z-primary','2026-09-28T20:20:41Z','2026-09-28T20:20:44Z','OK','github-actions','closed 2026-09-28; decided for 2026-09-29: 0 orders (MOO), regime ON',NULL);
INSERT INTO "runs" VALUES('20260928T203606Z-primary','2026-09-28T20:36:11Z','2026-09-28T20:36:11Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260928T213658Z-primary','2026-09-28T21:37:04Z','2026-09-28T21:37:04Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260928T220434Z-primary','2026-09-28T22:04:41Z','2026-09-28T22:04:41Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260928T223852Z-primary','2026-09-28T22:38:56Z','2026-09-28T22:38:56Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260929T021942Z-primary','2026-09-29T02:19:48Z','2026-09-29T02:19:48Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260929T023635Z-primary','2026-09-29T02:36:41Z','2026-09-29T02:36:41Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260929T024257Z-primary','2026-09-29T02:43:02Z','2026-09-29T02:43:02Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260929T090435Z-primary','2026-09-29T09:04:43Z','2026-09-29T09:04:43Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260929T160825Z-primary','2026-09-29T16:09:07Z','2026-09-29T16:09:07Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260929T161325Z-primary','2026-09-29T16:13:31Z','2026-09-29T16:13:31Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260929T161825Z-primary','2026-09-29T16:18:33Z','2026-09-29T16:18:33Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260929T162325Z-primary','2026-09-29T16:23:32Z','2026-09-29T16:23:32Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260929T162825Z-primary','2026-09-29T16:28:32Z','2026-09-29T16:28:32Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260929T162948Z-primary','2026-09-29T16:29:54Z','2026-09-29T16:29:54Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260929T163448Z-primary','2026-09-29T16:34:55Z','2026-09-29T16:34:55Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260929T163948Z-primary','2026-09-29T16:39:54Z','2026-09-29T16:39:54Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260929T164448Z-primary','2026-09-29T16:44:53Z','2026-09-29T16:44:55Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260929T164948Z-primary','2026-09-29T16:49:54Z','2026-09-29T16:49:54Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260929T165112Z-primary','2026-09-29T16:51:20Z','2026-09-29T16:51:21Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260929T165612Z-primary','2026-09-29T16:56:20Z','2026-09-29T16:56:20Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260929T183131Z-primary','2026-09-29T18:31:39Z','2026-09-29T18:31:40Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260929T224020Z-primary','2026-09-29T22:40:28Z','2026-09-29T22:40:31Z','OK','github-actions','closed 2026-09-29; decided for 2026-09-30: 0 orders (MOO), regime ON',NULL);
INSERT INTO "runs" VALUES('20260929T233846Z-primary','2026-09-29T23:38:51Z','2026-09-29T23:38:51Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260929T235744Z-primary','2026-09-29T23:57:49Z','2026-09-29T23:57:49Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260930T002454Z-primary','2026-09-30T00:25:00Z','2026-09-30T00:25:00Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260930T004715Z-primary','2026-09-30T00:47:20Z','2026-09-30T00:47:20Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260930T020420Z-primary','2026-09-30T02:04:27Z','2026-09-30T02:04:27Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260930T072943Z-primary','2026-09-30T07:29:48Z','2026-09-30T07:29:48Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260930T141533Z-primary','2026-09-30T14:16:29Z','2026-09-30T14:16:29Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260930T182012Z-primary','2026-09-30T18:20:19Z','2026-09-30T18:20:19Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20260930T223106Z-primary','2026-09-30T22:31:14Z','2026-09-30T22:31:17Z','OK','github-actions','closed 2026-09-30; decided for 2026-10-01: 0 orders (MOO), regime ON',NULL);
INSERT INTO "runs" VALUES('20260930T234013Z-primary','2026-09-30T23:40:18Z','2026-09-30T23:40:18Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261001T001034Z-primary','2026-10-01T00:10:40Z','2026-10-01T00:10:40Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261001T003301Z-primary','2026-10-01T00:33:08Z','2026-10-01T00:33:08Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261001T005137Z-primary','2026-10-01T00:51:44Z','2026-10-01T00:51:44Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261001T020513Z-primary','2026-10-01T02:05:21Z','2026-10-01T02:05:21Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261001T074954Z-primary','2026-10-01T07:49:59Z','2026-10-01T07:49:59Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261001T154137Z-primary','2026-10-01T15:42:32Z','2026-10-01T15:42:33Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261001T184536Z-primary','2026-10-01T18:45:42Z','2026-10-01T18:45:42Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261001T225655Z-primary','2026-10-01T22:57:02Z','2026-10-01T22:57:05Z','OK','github-actions','closed 2026-10-01; decided for 2026-10-02: 0 orders (MOO), regime ON',NULL);
INSERT INTO "runs" VALUES('20261001T235136Z-primary','2026-10-01T23:51:43Z','2026-10-01T23:51:43Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261002T001103Z-primary','2026-10-02T00:11:10Z','2026-10-02T00:11:10Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261002T004559Z-primary','2026-10-02T00:46:06Z','2026-10-02T00:46:06Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261002T010554Z-primary','2026-10-02T01:06:01Z','2026-10-02T01:06:01Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261002T021125Z-primary','2026-10-02T02:11:31Z','2026-10-02T02:11:31Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261002T073315Z-primary','2026-10-02T07:33:22Z','2026-10-02T07:33:22Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261002T140954Z-primary','2026-10-02T14:10:47Z','2026-10-02T14:10:47Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261002T181715Z-primary','2026-10-02T18:17:21Z','2026-10-02T18:17:22Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261002T222904Z-primary','2026-10-02T22:29:11Z','2026-10-02T22:29:14Z','OK','github-actions','closed 2026-10-02; decided for 2026-10-05: 0 orders (MOO), regime ON',NULL);
INSERT INTO "runs" VALUES('20261002T234255Z-primary','2026-10-02T23:43:01Z','2026-10-02T23:43:01Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261002T235946Z-primary','2026-10-02T23:59:50Z','2026-10-02T23:59:50Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261003T002823Z-primary','2026-10-03T00:28:28Z','2026-10-03T00:28:28Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261003T004540Z-primary','2026-10-03T00:45:45Z','2026-10-03T00:45:45Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261003T015445Z-primary','2026-10-03T01:54:50Z','2026-10-03T01:54:50Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261003T070707Z-primary','2026-10-03T07:07:13Z','2026-10-03T07:07:13Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261003T124515Z-primary','2026-10-03T12:45:20Z','2026-10-03T12:45:20Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261003T173810Z-primary','2026-10-03T17:38:15Z','2026-10-03T17:38:15Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261003T201259Z-primary','2026-10-03T20:13:04Z','2026-10-03T20:13:04Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261003T232034Z-primary','2026-10-03T23:20:41Z','2026-10-03T23:20:41Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261004T000421Z-primary','2026-10-04T00:04:27Z','2026-10-04T00:04:27Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261004T062241Z-primary','2026-10-04T06:22:46Z','2026-10-04T06:22:46Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261004T125238Z-primary','2026-10-04T12:52:44Z','2026-10-04T12:52:44Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261004T175138Z-primary','2026-10-04T17:51:44Z','2026-10-04T17:51:44Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261004T215720Z-primary','2026-10-04T21:57:25Z','2026-10-04T21:57:25Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T001125Z-primary','2026-10-05T00:11:32Z','2026-10-05T00:11:32Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T061519Z-primary','2026-10-05T06:15:24Z','2026-10-05T06:15:24Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T073045Z-primary','2026-10-05T07:30:51Z','2026-10-05T07:30:51Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T073421Z-primary','2026-10-05T07:34:28Z','2026-10-05T07:34:28Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T073938Z-primary','2026-10-05T07:39:43Z','2026-10-05T07:39:43Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T080015Z-primary','2026-10-05T08:00:20Z','2026-10-05T08:00:20Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T080230Z-primary','2026-10-05T08:02:37Z','2026-10-05T08:02:37Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T082237Z-primary','2026-10-05T08:22:43Z','2026-10-05T08:22:43Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T082513Z-primary','2026-10-05T08:25:20Z','2026-10-05T08:25:20Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T084604Z-primary','2026-10-05T08:46:10Z','2026-10-05T08:46:10Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T090639Z-primary','2026-10-05T09:06:46Z','2026-10-05T09:06:46Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T092733Z-primary','2026-10-05T09:27:39Z','2026-10-05T09:27:39Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T094822Z-primary','2026-10-05T09:48:29Z','2026-10-05T09:48:29Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T100902Z-primary','2026-10-05T10:09:09Z','2026-10-05T10:09:09Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T102935Z-primary','2026-10-05T10:29:41Z','2026-10-05T10:29:41Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T105106Z-primary','2026-10-05T10:51:13Z','2026-10-05T10:51:13Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T111119Z-primary','2026-10-05T11:11:25Z','2026-10-05T11:11:25Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T113214Z-primary','2026-10-05T11:32:20Z','2026-10-05T11:32:20Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T115303Z-primary','2026-10-05T11:53:09Z','2026-10-05T11:53:09Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T121343Z-primary','2026-10-05T12:13:48Z','2026-10-05T12:13:48Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T133519Z-primary','2026-10-05T13:35:25Z','2026-10-05T13:35:25Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T134019Z-primary','2026-10-05T13:41:16Z','2026-10-05T13:41:16Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T134519Z-primary','2026-10-05T13:45:24Z','2026-10-05T13:45:24Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T135019Z-primary','2026-10-05T13:50:25Z','2026-10-05T13:50:25Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T135519Z-primary','2026-10-05T13:55:24Z','2026-10-05T13:55:24Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T135642Z-primary','2026-10-05T13:56:47Z','2026-10-05T13:56:48Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T140142Z-primary','2026-10-05T14:01:48Z','2026-10-05T14:01:48Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T140642Z-primary','2026-10-05T14:06:48Z','2026-10-05T14:06:49Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T141142Z-primary','2026-10-05T14:11:48Z','2026-10-05T14:11:48Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T141642Z-primary','2026-10-05T14:16:49Z','2026-10-05T14:16:50Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T141811Z-primary','2026-10-05T14:18:19Z','2026-10-05T14:18:20Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T142311Z-primary','2026-10-05T14:23:18Z','2026-10-05T14:23:19Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T142811Z-primary','2026-10-05T14:28:18Z','2026-10-05T14:28:18Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T143311Z-primary','2026-10-05T14:33:18Z','2026-10-05T14:33:19Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T143811Z-primary','2026-10-05T14:38:18Z','2026-10-05T14:38:18Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T143934Z-primary','2026-10-05T14:39:40Z','2026-10-05T14:39:40Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T144434Z-primary','2026-10-05T14:44:39Z','2026-10-05T14:44:40Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T144934Z-primary','2026-10-05T14:49:41Z','2026-10-05T14:49:46Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T145434Z-primary','2026-10-05T14:54:40Z','2026-10-05T14:54:40Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T145934Z-primary','2026-10-05T14:59:39Z','2026-10-05T14:59:39Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T150055Z-primary','2026-10-05T15:01:01Z','2026-10-05T15:01:02Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T150555Z-primary','2026-10-05T15:06:02Z','2026-10-05T15:06:03Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T151055Z-primary','2026-10-05T15:11:02Z','2026-10-05T15:11:02Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T151555Z-primary','2026-10-05T15:16:03Z','2026-10-05T15:16:03Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T152055Z-primary','2026-10-05T15:21:03Z','2026-10-05T15:21:04Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T152221Z-primary','2026-10-05T15:22:28Z','2026-10-05T15:22:29Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T152721Z-primary','2026-10-05T15:27:28Z','2026-10-05T15:27:28Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T153221Z-primary','2026-10-05T15:32:27Z','2026-10-05T15:32:28Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T153721Z-primary','2026-10-05T15:37:28Z','2026-10-05T15:37:28Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T154221Z-primary','2026-10-05T15:42:27Z','2026-10-05T15:42:27Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T154344Z-primary','2026-10-05T15:43:50Z','2026-10-05T15:43:50Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T154844Z-primary','2026-10-05T15:48:51Z','2026-10-05T15:48:51Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T155344Z-primary','2026-10-05T15:53:50Z','2026-10-05T15:53:51Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T155844Z-primary','2026-10-05T15:58:48Z','2026-10-05T15:58:48Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T160344Z-primary','2026-10-05T16:03:52Z','2026-10-05T16:03:53Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T160516Z-primary','2026-10-05T16:05:25Z','2026-10-05T16:05:25Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T161016Z-primary','2026-10-05T16:10:23Z','2026-10-05T16:10:23Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T161516Z-primary','2026-10-05T16:15:23Z','2026-10-05T16:15:23Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T162016Z-primary','2026-10-05T16:20:24Z','2026-10-05T16:20:24Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T162516Z-primary','2026-10-05T16:25:23Z','2026-10-05T16:25:23Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T162642Z-primary','2026-10-05T16:26:48Z','2026-10-05T16:26:49Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T163142Z-primary','2026-10-05T16:31:48Z','2026-10-05T16:31:49Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T163642Z-primary','2026-10-05T16:36:49Z','2026-10-05T16:36:49Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T164142Z-primary','2026-10-05T16:41:49Z','2026-10-05T16:41:49Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T164642Z-primary','2026-10-05T16:46:49Z','2026-10-05T16:46:49Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T164806Z-primary','2026-10-05T16:48:13Z','2026-10-05T16:48:13Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T165306Z-primary','2026-10-05T16:53:12Z','2026-10-05T16:53:12Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T165806Z-primary','2026-10-05T16:58:10Z','2026-10-05T16:58:10Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T172537Z-primary','2026-10-05T17:25:43Z','2026-10-05T17:25:44Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T220617Z-primary','2026-10-05T22:06:25Z','2026-10-05T22:06:28Z','OK','github-actions','closed 2026-10-05; decided for 2026-10-06: 1 orders (MOO), regime ON',NULL);
INSERT INTO "runs" VALUES('20261005T222657Z-primary','2026-10-05T22:27:12Z','2026-10-05T22:27:12Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261005T224741Z-primary','2026-10-05T22:47:48Z','2026-10-05T22:47:48Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261006T011528Z-primary','2026-10-06T01:15:35Z','2026-10-06T01:15:35Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261006T012613Z-primary','2026-10-06T01:26:20Z','2026-10-06T01:26:20Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261006T014518Z-primary','2026-10-06T01:45:25Z','2026-10-06T01:45:25Z','OK','github-actions','no action needed',NULL);
CREATE TABLE snapshots (
  session TEXT PRIMARY KEY, created_at TEXT NOT NULL, run_id TEXT, equity REAL NOT NULL,
  cash REAL NOT NULL, positions_value REAL NOT NULL, spy_bh_equity REAL, cash_bh_equity REAL,
  peak REAL NOT NULL, drawdown REAL NOT NULL, regime TEXT, risk_state TEXT, marks TEXT, holdings TEXT
);
INSERT INTO "snapshots" VALUES('2026-09-23','2026-09-23T21:54:08Z','20260923T215408Z-primary',9.93003652290552594e+01,2.00041109844002562e+00,9.72999541306152338e+01,9.92860839736302125e+01,100.0,100.0,6.99634770944745909e-03,'ON','{"peak": 100.0, "pause_until": null, "halt_until": null, "drawdown": 0.006996347709447459}','{"marks": {"SPY": 767.8099975585938}, "flags": {}}','{"SPY": {"qty": 0.126724, "avg_cost": 773.3309310119628, "sleeve": "residual", "stop": null, "entry_session": "2026-09-23", "max_hold_until": null}}');
INSERT INTO "snapshots" VALUES('2026-09-24','2026-09-24T20:38:13Z','20260924T203813Z-primary',9.922052849028573e+01,2.00041109844002562e+00,97.2201173918457,9.9204617571919357e+01,100.0,100.0,0.00779471509714269,'ON','{"peak": 100.0, "pause_until": null, "halt_until": null, "drawdown": 0.00779471509714269}','{"marks": {"SPY": 767.1799926757812}, "flags": {}}','{"SPY": {"qty": 0.126724, "avg_cost": 773.3309310119628, "sleeve": "residual", "stop": null, "entry_session": "2026-09-23", "max_hold_until": null}}');
INSERT INTO "snapshots" VALUES('2026-09-25','2026-09-25T20:26:49Z','20260925T202649Z-primary',9.97489654045923686e+01,2.00041109844002562e+00,9.77485543061523429e+01,99.743841175028,100.0,100.0,2.51034595407628735e-03,'ON','{"peak": 100.0, "pause_until": null, "halt_until": null, "drawdown": 0.0025103459540762874}','{"marks": {"SPY": 771.3499755859375}, "flags": {}}','{"SPY": {"qty": 0.126724, "avg_cost": 773.3309310119628, "sleeve": "residual", "stop": null, "entry_session": "2026-09-23", "max_hold_until": null}}');
INSERT INTO "snapshots" VALUES('2026-09-28','2026-09-28T20:20:33Z','20260928T202033Z-primary',9.90215708821314279e+01,2.00041109844002562e+00,97.0211597836914,9.90015987527749814e+01,100.0,100.0,9.78429117868573339e-03,'ON','{"peak": 100.0, "pause_until": null, "halt_until": null, "drawdown": 0.009784291178685733}','{"marks": {"SPY": 765.6099853515625}, "flags": {}}','{"SPY": {"qty": 0.126724, "avg_cost": 773.3309310119628, "sleeve": "residual", "stop": null, "entry_session": "2026-09-23", "max_hold_until": null}}');
INSERT INTO "snapshots" VALUES('2026-09-29','2026-09-29T22:40:20Z','20260929T224020Z-primary',9.88428934453638561e+01,2.00041109844002562e+00,9.68424823469238305e+01,98.8192740728755,100.0,100.0,1.15710655463614475e-02,'ON','{"peak": 100.0, "pause_until": null, "halt_until": null, "drawdown": 0.011571065546361448}','{"marks": {"SPY": 764.2000122070312}, "flags": {}}','{"SPY": {"qty": 0.126724, "avg_cost": 773.3309310119628, "sleeve": "residual", "stop": null, "entry_session": "2026-09-23", "max_hold_until": null}}');
INSERT INTO "snapshots" VALUES('2026-09-30','2026-09-30T22:31:06Z','20260930T223106Z-primary',9.8643935837209554e+01,2.00041109844002562e+00,9.66435247387695284e+01,9.86162552537311114e+01,100.0,100.0,1.35606416279044905e-02,'ON','{"peak": 100.0, "pause_until": null, "halt_until": null, "drawdown": 0.01356064162790449}','{"marks": {"SPY": 762.6300048828125}, "flags": {}}','{"SPY": {"qty": 0.126724, "avg_cost": 773.3309310119628, "sleeve": "residual", "stop": null, "entry_session": "2026-09-23", "max_hold_until": null}}');
INSERT INTO "snapshots" VALUES('2026-10-01','2026-10-01T22:56:55Z','20261001T225655Z-primary',9.88162786209009595e+01,2.00041109844002562e+00,9.68158675224609339e+01,9.87921159748046733e+01,100.0,100.0,1.18372137909904529e-02,'ON','{"peak": 100.0, "pause_until": null, "halt_until": null, "drawdown": 0.011837213790990453}','{"marks": {"SPY": 763.989990234375}, "flags": {}}','{"SPY": {"qty": 0.126724, "avg_cost": 773.3309310119628, "sleeve": "residual", "stop": null, "entry_session": "2026-09-23", "max_hold_until": null}}');
INSERT INTO "snapshots" VALUES('2026-10-02','2026-10-02T22:29:04Z','20261002T222904Z-primary',9.95322723147486243e+01,2.00041109844002562e+00,97.5318612163086,9.95227248496713485e+01,100.0,100.0,4.67727685251373426e-03,'ON','{"peak": 100.0, "pause_until": null, "halt_until": null, "drawdown": 0.004677276852513734}','{"marks": {"SPY": 769.6400146484375}, "flags": {}}','{"SPY": {"qty": 0.126724, "avg_cost": 773.3309310119628, "sleeve": "residual", "stop": null, "entry_session": "2026-09-23", "max_hold_until": null}}');
INSERT INTO "snapshots" VALUES('2026-10-05','2026-10-05T22:06:17Z','20261005T220617Z-primary',1.00189970184133386e+02,2.00041109844002562e+00,9.81895590856933608e+01,1.00193847939835961e+02,100.0,1.00189970184133386e+02,0.0,'ON','{"peak": 100.18997018413339, "pause_until": null, "halt_until": null, "drawdown": 0.0}','{"marks": {"SPY": 774.8300170898438}, "flags": {}}','{"SPY": {"qty": 0.126724, "avg_cost": 773.3309310119628, "sleeve": "residual", "stop": null, "entry_session": "2026-09-23", "max_hold_until": null}}');
CREATE TABLE state (key TEXT PRIMARY KEY, value TEXT NOT NULL, updated_at TEXT NOT NULL);
INSERT INTO "state" VALUES('cash','2.0004110984400256','2026-10-05T22:06:27Z');
INSERT INTO "state" VALUES('strategy_integrity_ok','true','2026-10-06T01:45:25Z');
INSERT INTO "state" VALUES('last_regime','"ON"','2026-10-05T22:06:28Z');
INSERT INTO "state" VALUES('benchmark','{"ticker": "SPY", "qty": 0.12931074652496097, "entry_price": 773.3309310119628, "entry_session": "2026-09-23", "div_cash": 0.0, "note": "SPY bought at the first session''s official open with the same cost model"}','2026-09-23T17:50:09Z');
INSERT INTO "state" VALUES('open_done:2026-09-23','true','2026-09-23T17:50:09Z');
INSERT INTO "state" VALUES('live_marks','{"as_of": "2026-10-05T17:25:37Z", "marks": {"SPY": [774.389892578125, "2026-10-05T13:20:00-04:00"]}}','2026-10-05T17:25:44Z');
INSERT INTO "state" VALUES('risk','{"peak": 100.18997018413339, "pause_until": null, "halt_until": null, "drawdown": 0.0}','2026-10-05T22:06:27Z');
INSERT INTO "state" VALUES('last_closed_session','"2026-10-05"','2026-10-05T22:06:27Z');
INSERT INTO "state" VALUES('open_done:2026-09-24','true','2026-09-24T13:42:01Z');
INSERT INTO "state" VALUES('open_done:2026-09-25','true','2026-09-25T13:38:34Z');
INSERT INTO "state" VALUES('open_done:2026-09-28','true','2026-09-28T13:50:24Z');
INSERT INTO "state" VALUES('open_done:2026-09-29','true','2026-09-29T16:09:07Z');
INSERT INTO "state" VALUES('open_done:2026-09-30','true','2026-09-30T14:16:29Z');
INSERT INTO "state" VALUES('open_done:2026-10-01','true','2026-10-01T15:42:33Z');
INSERT INTO "state" VALUES('open_done:2026-10-02','true','2026-10-02T14:10:47Z');
INSERT INTO "state" VALUES('open_done:2026-10-05','true','2026-10-05T13:35:25Z');
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
INSERT INTO "sqlite_sequence" VALUES('events',27);
INSERT INTO "sqlite_sequence" VALUES('decisions',12);
INSERT INTO "sqlite_sequence" VALUES('fills',1);
COMMIT;
