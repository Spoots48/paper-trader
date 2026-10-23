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
INSERT INTO "decisions" VALUES(5,'decide:2026-10-09','20261008T234842Z-ctrend','2026-10-08T23:48:42Z','2026-10-08','2026-10-09','*','system','INFO','DECIDED','0 orders (MOO) for 2026-10-09; rebalance=False (weekly)','{"rebalance": false, "order_type": "MOO", "data_through": "2026-10-08", "detail": {}, "halted": false}','[]');
INSERT INTO "decisions" VALUES(6,'decide:2026-10-12','20261009T225719Z-ctrend','2026-10-09T22:57:19Z','2026-10-09','2026-10-12','*','system','INFO','DECIDED','0 orders (MOO) for 2026-10-12; rebalance=True; trend weights IBIT 50%, ETHA 50%','{"rebalance": true, "order_type": "MOO", "data_through": "2026-10-09", "detail": {"IBIT": {"close": 46.54999923706055, "above_sma_sessions": [50, 100, 200], "weight_fraction": 1.0}, "ETHA": {"close": 55.9900016784668, "above_sma_sessions": [50, 100, 200], "weight_fraction": 1.0}}, "halted": false}','[]');
INSERT INTO "decisions" VALUES(7,'decide:2026-10-13','20261012T213411Z-ctrend','2026-10-12T21:34:11Z','2026-10-12','2026-10-13','*','system','INFO','DECIDED','0 orders (MOO) for 2026-10-13; rebalance=False (weekly)','{"rebalance": false, "order_type": "MOO", "data_through": "2026-10-12", "detail": {}, "halted": false}','[]');
INSERT INTO "decisions" VALUES(8,'decide:2026-10-14','20261013T232833Z-ctrend','2026-10-13T23:28:33Z','2026-10-13','2026-10-14','*','system','INFO','DECIDED','0 orders (MOO) for 2026-10-14; rebalance=False (weekly)','{"rebalance": false, "order_type": "MOO", "data_through": "2026-10-13", "detail": {}, "halted": false}','[]');
INSERT INTO "decisions" VALUES(9,'decide:2026-10-15','20261014T211810Z-ctrend','2026-10-14T21:18:10Z','2026-10-14','2026-10-15','*','system','INFO','DECIDED','0 orders (MOO) for 2026-10-15; rebalance=False (weekly)','{"rebalance": false, "order_type": "MOO", "data_through": "2026-10-14", "detail": {}, "halted": false}','[]');
INSERT INTO "decisions" VALUES(10,'decide:2026-10-16','20261015T203351Z-ctrend','2026-10-15T20:33:51Z','2026-10-15','2026-10-16','*','system','INFO','DECIDED','0 orders (MOO) for 2026-10-16; rebalance=False (weekly)','{"rebalance": false, "order_type": "MOO", "data_through": "2026-10-15", "detail": {}, "halted": false}','[]');
INSERT INTO "decisions" VALUES(11,'2026-10-19:000:trend:ETHA:TREND_TRIM','20261016T224818Z-ctrend','2026-10-16T22:48:18Z','2026-10-16','2026-10-19','ETHA','trend','SELL','TREND_TRIM','week-end trend rebalance; ETHA: above [100, 200]-session averages','{"value": 14.600114156972488, "close": 54.5099983215332, "above_sma_sessions": [100, 200], "weight_fraction": 0.6666666666666666}','[]');
INSERT INTO "decisions" VALUES(12,'2026-10-19:001:trend:SHY:TREND_BUY','20261016T224818Z-ctrend','2026-10-16T22:48:18Z','2026-10-16','2026-10-19','SHY','trend','BUY','TREND_BUY','week-end trend rebalance; SHY: unallocated capital held in short-term Treasuries','{"value": 15.84731390376207}','[]');
INSERT INTO "decisions" VALUES(13,'decide:2026-10-19','20261016T224818Z-ctrend','2026-10-16T22:48:18Z','2026-10-16','2026-10-19','*','system','INFO','DECIDED','2 orders (MOO) for 2026-10-19; rebalance=True; trend weights IBIT 50%, ETHA 33%','{"rebalance": true, "order_type": "MOO", "data_through": "2026-10-16", "detail": {"IBIT": {"close": 46.150001525878906, "above_sma_sessions": [50, 100, 200], "weight_fraction": 1.0}, "ETHA": {"close": 54.5099983215332, "above_sma_sessions": [100, 200], "weight_fraction": 0.6666666666666666}}, "halted": false}','[]');
INSERT INTO "decisions" VALUES(14,'decide:2026-10-20','20261019T225519Z-ctrend','2026-10-19T22:55:19Z','2026-10-19','2026-10-20','*','system','INFO','DECIDED','0 orders (MOO) for 2026-10-20; rebalance=False (weekly)','{"rebalance": false, "order_type": "MOO", "data_through": "2026-10-19", "detail": {}, "halted": false}','[]');
INSERT INTO "decisions" VALUES(15,'decide:2026-10-21','20261020T211541Z-ctrend','2026-10-20T21:15:41Z','2026-10-20','2026-10-21','*','system','INFO','DECIDED','0 orders (MOO) for 2026-10-21; rebalance=False (weekly)','{"rebalance": false, "order_type": "MOO", "data_through": "2026-10-20", "detail": {}, "halted": false}','[]');
INSERT INTO "decisions" VALUES(16,'decide:2026-10-22','20261021T211617Z-ctrend','2026-10-21T21:16:17Z','2026-10-21','2026-10-22','*','system','INFO','DECIDED','0 orders (MOO) for 2026-10-22; rebalance=False (weekly)','{"rebalance": false, "order_type": "MOO", "data_through": "2026-10-21", "detail": {}, "halted": false}','[]');
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
INSERT INTO "events" VALUES(14,'2026-10-08T23:50:36Z','20261008T234842Z-ctrend','snapshot','{"cash": 1.4950508295084006, "drawdown": 0.030255146169803515, "equity": 97.16999554245623, "session": "2026-10-08", "spy_bh_equity": 99.69302772342807}','23ccbf78917bd2aea97e3f6ebfc76bd4d768f5cc357134471fa9b90af62071fa','6aa1449e353a40b938b68c11889942fd7b71c4d254af0ad97fdc35a221417a68');
INSERT INTO "events" VALUES(15,'2026-10-08T23:50:37Z','20261008T234842Z-ctrend','decision','{"action": "INFO", "code": "DECIDED", "key": "decide:2026-10-09", "reason": "0 orders (MOO) for 2026-10-09; rebalance=False (weekly)", "ticker": "*"}','6aa1449e353a40b938b68c11889942fd7b71c4d254af0ad97fdc35a221417a68','1f41eaddc533b8e6cf200df76373fdcbb359c37b9da28061d2be2f7fe4573f6c');
INSERT INTO "events" VALUES(16,'2026-10-09T22:58:42Z','20261009T225719Z-ctrend','snapshot','{"cash": 1.4950508295084006, "drawdown": 0.02477100149994116, "equity": 97.71951566728076, "session": "2026-10-09", "spy_bh_equity": 100.2907266281888}','1f41eaddc533b8e6cf200df76373fdcbb359c37b9da28061d2be2f7fe4573f6c','1046afa74b82d655ed3347524f5ebdeb296df726cbfdb619872f5cb76b9883e3');
INSERT INTO "events" VALUES(17,'2026-10-09T22:58:44Z','20261009T225719Z-ctrend','decision','{"action": "INFO", "code": "DECIDED", "key": "decide:2026-10-12", "reason": "0 orders (MOO) for 2026-10-12; rebalance=True; trend weights IBIT 50%, ETHA 50%", "ticker": "*"}','1046afa74b82d655ed3347524f5ebdeb296df726cbfdb619872f5cb76b9883e3','b01b55953c9f4bbc8744ffb3317254a29c9c1d1c01694769e4423a07cb6ee7e1');
INSERT INTO "events" VALUES(18,'2026-10-12T21:36:12Z','20261012T213411Z-ctrend','snapshot','{"cash": 1.4950508295084006, "drawdown": 0.013399380629302904, "equity": 98.8589703856493, "session": "2026-10-12", "spy_bh_equity": 100.23017995399499}','b01b55953c9f4bbc8744ffb3317254a29c9c1d1c01694769e4423a07cb6ee7e1','5635d753bfda56a4df10303750646e2381cca7f8c6cac32cefd3f224c80a35c7');
INSERT INTO "events" VALUES(19,'2026-10-12T21:36:14Z','20261012T213411Z-ctrend','decision','{"action": "INFO", "code": "DECIDED", "key": "decide:2026-10-13", "reason": "0 orders (MOO) for 2026-10-13; rebalance=False (weekly)", "ticker": "*"}','5635d753bfda56a4df10303750646e2381cca7f8c6cac32cefd3f224c80a35c7','d96146ada3d1303c5fa764f350591650c4a7c133e3472e2b6853f55a69a24ba6');
INSERT INTO "events" VALUES(20,'2026-10-13T23:30:22Z','20261013T232833Z-ctrend','snapshot','{"cash": 1.4950508295084006, "drawdown": 0.012870401105722462, "equity": 98.91197498551425, "session": "2026-10-13", "spy_bh_equity": 100.21859109569584}','d96146ada3d1303c5fa764f350591650c4a7c133e3472e2b6853f55a69a24ba6','7d523fe9b4ec537ad2ab3eac8a0b451d6c810fe1c6ad3c008417a95c1c64949a');
INSERT INTO "events" VALUES(21,'2026-10-13T23:30:24Z','20261013T232833Z-ctrend','decision','{"action": "INFO", "code": "DECIDED", "key": "decide:2026-10-14", "reason": "0 orders (MOO) for 2026-10-14; rebalance=False (weekly)", "ticker": "*"}','7d523fe9b4ec537ad2ab3eac8a0b451d6c810fe1c6ad3c008417a95c1c64949a','b6f772f453dd91f6d842207017abe34dec24ba3bac6acad3b2dbf96083f58550');
INSERT INTO "events" VALUES(22,'2026-10-14T21:20:08Z','20261014T211810Z-ctrend','snapshot','{"cash": 1.4950508295084006, "drawdown": 0.03732922199590971, "equity": 96.46116175615177, "session": "2026-10-14", "spy_bh_equity": 99.13526084804411}','b6f772f453dd91f6d842207017abe34dec24ba3bac6acad3b2dbf96083f58550','1a229c00b0dbf5081a4930682d510557106799dddec51ed66875b63def3ba3c6');
INSERT INTO "events" VALUES(23,'2026-10-14T21:20:09Z','20261014T211810Z-ctrend','decision','{"action": "INFO", "code": "DECIDED", "key": "decide:2026-10-15", "reason": "0 orders (MOO) for 2026-10-15; rebalance=False (weekly)", "ticker": "*"}','1a229c00b0dbf5081a4930682d510557106799dddec51ed66875b63def3ba3c6','cf3c7b2c427676459cfe377b6bc4afcbe7488f320030be13e16dc29f095c1180');
INSERT INTO "events" VALUES(24,'2026-10-15T20:36:00Z','20261015T203351Z-ctrend','snapshot','{"cash": 1.4950508295084006, "drawdown": 0.029269573312148522, "equity": 97.26875152946339, "session": "2026-10-15", "spy_bh_equity": 99.41736384982937}','cf3c7b2c427676459cfe377b6bc4afcbe7488f320030be13e16dc29f095c1180','5eb254528b5643a7ff2177d8e5208421cebca3e6d112b9e5fa484e33ca524eaa');
INSERT INTO "events" VALUES(25,'2026-10-15T20:36:01Z','20261015T203351Z-ctrend','decision','{"action": "INFO", "code": "DECIDED", "key": "decide:2026-10-16", "reason": "0 orders (MOO) for 2026-10-16; rebalance=False (weekly)", "ticker": "*"}','5eb254528b5643a7ff2177d8e5208421cebca3e6d112b9e5fa484e33ca524eaa','07dd126e15c8cb225ffb35d571acc3f7175acb646fb1f5f1510fb672e3e00e3b');
INSERT INTO "events" VALUES(26,'2026-10-16T22:50:15Z','20261016T224818Z-ctrend','snapshot','{"cash": 1.4950508295084006, "drawdown": 0.041489185764116976, "equity": 96.04432668946704, "session": "2026-10-16", "spy_bh_equity": 98.31729501376591}','07dd126e15c8cb225ffb35d571acc3f7175acb646fb1f5f1510fb672e3e00e3b','93c59d4f6655ad1fcfc6b71cb88de248e1a983f298ddfd331a6901295cfb057f');
INSERT INTO "events" VALUES(27,'2026-10-16T22:50:16Z','20261016T224818Z-ctrend','decision','{"action": "SELL", "code": "TREND_TRIM", "key": "2026-10-19:000:trend:ETHA:TREND_TRIM", "reason": "week-end trend rebalance; ETHA: above [100, 200]-session averages", "ticker": "ETHA"}','93c59d4f6655ad1fcfc6b71cb88de248e1a983f298ddfd331a6901295cfb057f','71da95f95c8961a9c34a5ab2f83ecf23237d6d1ff96d1e215573c31956f9d698');
INSERT INTO "events" VALUES(28,'2026-10-16T22:50:16Z','20261016T224818Z-ctrend','decision','{"action": "BUY", "code": "TREND_BUY", "key": "2026-10-19:001:trend:SHY:TREND_BUY", "reason": "week-end trend rebalance; SHY: unallocated capital held in short-term Treasuries", "ticker": "SHY"}','71da95f95c8961a9c34a5ab2f83ecf23237d6d1ff96d1e215573c31956f9d698','e40754eb1b39bfd88b6144ece569eec9d20da57e8e0a7801beaadaafa214a3c4');
INSERT INTO "events" VALUES(29,'2026-10-16T22:50:16Z','20261016T224818Z-ctrend','order','{"key": "2026-10-19:trend:ETHA:SELL:TREND_TRIM", "notional": null, "qty": 0.2678428656491991, "reason": "week-end trend rebalance; ETHA: above [100, 200]-session averages", "session": "2026-10-19", "side": "SELL", "ticker": "ETHA", "type": "MOO"}','e40754eb1b39bfd88b6144ece569eec9d20da57e8e0a7801beaadaafa214a3c4','a52c70b5abd3e11f7d4d063652aa0a436994e9dfcc0a1be6b17551a5522263b1');
INSERT INTO "events" VALUES(30,'2026-10-16T22:50:16Z','20261016T224818Z-ctrend','order','{"key": "2026-10-19:trend:SHY:BUY:TREND_BUY", "notional": 15.02999388381591, "qty": null, "reason": "week-end trend rebalance; SHY: unallocated capital held in short-term Treasuries", "session": "2026-10-19", "side": "BUY", "ticker": "SHY", "type": "MOO"}','a52c70b5abd3e11f7d4d063652aa0a436994e9dfcc0a1be6b17551a5522263b1','390bcae61d7be0a91a3261397d78d88ac1fe6ee86b3bfc02192faa986275bef7');
INSERT INTO "events" VALUES(31,'2026-10-16T22:50:16Z','20261016T224818Z-ctrend','decision','{"action": "INFO", "code": "DECIDED", "key": "decide:2026-10-19", "reason": "2 orders (MOO) for 2026-10-19; rebalance=True; trend weights IBIT 50%, ETHA 33%", "ticker": "*"}','390bcae61d7be0a91a3261397d78d88ac1fe6ee86b3bfc02192faa986275bef7','61974cc53d37fd3b76bdeaed0207ee2f9a17765c05ee8f4c4f9eb7c4e0e2b35a');
INSERT INTO "events" VALUES(32,'2026-10-19T14:59:53Z','20261019T145852Z-ctrend','fill','{"fill_price": 54.7100325, "key": "2026-10-19:trend:ETHA:SELL:TREND_TRIM", "price_time": "2026-10-19T09:30:00-04:00 (official open)", "qty": 0.2678428656491991, "ref_price": 54.75, "side": "SELL", "source": "yahoo_daily_open", "ticker": "ETHA"}','61974cc53d37fd3b76bdeaed0207ee2f9a17765c05ee8f4c4f9eb7c4e0e2b35a','d7378f877933550e55798de58a44f8a531556e4d0ecebc0035f3a306a6727c7e');
INSERT INTO "events" VALUES(33,'2026-10-19T14:59:53Z','20261019T145852Z-ctrend','order_status','{"key": "2026-10-19:trend:ETHA:SELL:TREND_TRIM", "reason": "SELL 0.267843 ETHA @ 54.7100", "status": "FILLED"}','d7378f877933550e55798de58a44f8a531556e4d0ecebc0035f3a306a6727c7e','f65b1d7866a6b9de8373cb137f03375bb69bde2635f86013239ccba2add0b345');
INSERT INTO "events" VALUES(34,'2026-10-19T14:59:53Z','20261019T145852Z-ctrend','fill','{"fill_price": 81.39693433532715, "key": "2026-10-19:trend:SHY:BUY:TREND_BUY", "price_time": "2026-10-19T09:30:00-04:00 (official open)", "qty": 0.18465, "ref_price": 81.33999633789062, "side": "BUY", "source": "yahoo_daily_open", "ticker": "SHY"}','f65b1d7866a6b9de8373cb137f03375bb69bde2635f86013239ccba2add0b345','97013b0b52e60bc67366e633db13d3ba66cd02c169a159e68511d2eaad872e41');
INSERT INTO "events" VALUES(35,'2026-10-19T14:59:53Z','20261019T145852Z-ctrend','order_status','{"key": "2026-10-19:trend:SHY:BUY:TREND_BUY", "reason": "BUY 0.184650 SHY @ 81.3969", "status": "FILLED"}','97013b0b52e60bc67366e633db13d3ba66cd02c169a159e68511d2eaad872e41','ab6a9c565230518e7a39d2d4837c3a1f6b046b300009c85467a2c76dc0920a40');
INSERT INTO "events" VALUES(36,'2026-10-19T22:57:06Z','20261019T225519Z-ctrend','snapshot','{"cash": 1.118798789051061, "drawdown": 0.04187063306926242, "equity": 96.00610505540085, "session": "2026-10-19", "spy_bh_equity": 98.73336175812857}','ab6a9c565230518e7a39d2d4837c3a1f6b046b300009c85467a2c76dc0920a40','d62dc7883dbd64dd6a017e501fb6648b5589ab3d37adfad8f0a30dab69b737ef');
INSERT INTO "events" VALUES(37,'2026-10-19T22:57:08Z','20261019T225519Z-ctrend','decision','{"action": "INFO", "code": "DECIDED", "key": "decide:2026-10-20", "reason": "0 orders (MOO) for 2026-10-20; rebalance=False (weekly)", "ticker": "*"}','d62dc7883dbd64dd6a017e501fb6648b5589ab3d37adfad8f0a30dab69b737ef','f4c6b3c24ea13fa98aa7ce16fefcc730604202df1aed24320c2f5dd73286bcc8');
INSERT INTO "events" VALUES(38,'2026-10-20T21:17:20Z','20261020T211541Z-ctrend','snapshot','{"cash": 1.118798789051061, "drawdown": 0.032040064444106786, "equity": 96.99114385783768, "session": "2026-10-20", "spy_bh_equity": 99.06441471362514}','f4c6b3c24ea13fa98aa7ce16fefcc730604202df1aed24320c2f5dd73286bcc8','287b2699beada2a8a13ea45e91d887ebfcd10eea924671279b2f8145308c2b0b');
INSERT INTO "events" VALUES(39,'2026-10-20T21:17:22Z','20261020T211541Z-ctrend','decision','{"action": "INFO", "code": "DECIDED", "key": "decide:2026-10-21", "reason": "0 orders (MOO) for 2026-10-21; rebalance=False (weekly)", "ticker": "*"}','287b2699beada2a8a13ea45e91d887ebfcd10eea924671279b2f8145308c2b0b','da8d9481da7ab5d1c38d7fd87be5c97526fd4abdc0600b22328ae026cefd6f2b');
INSERT INTO "events" VALUES(40,'2026-10-21T21:18:22Z','20261021T211617Z-ctrend','snapshot','{"cash": 1.118798789051061, "drawdown": 0.012375196790844534, "equity": 98.96159525509262, "session": "2026-10-21", "spy_bh_equity": 99.58482835578033}','da8d9481da7ab5d1c38d7fd87be5c97526fd4abdc0600b22328ae026cefd6f2b','2ed24307db02aea30203876919980862e7759ee47ac6038ea63971c740eece44');
INSERT INTO "events" VALUES(41,'2026-10-21T21:18:24Z','20261021T211617Z-ctrend','decision','{"action": "INFO", "code": "DECIDED", "key": "decide:2026-10-22", "reason": "0 orders (MOO) for 2026-10-22; rebalance=False (weekly)", "ticker": "*"}','2ed24307db02aea30203876919980862e7759ee47ac6038ea63971c740eece44','3cf5076b07c241a5141c0753f946d62e4e2efe965967b8914d451610d720e68c');
INSERT INTO "events" VALUES(42,'2026-10-22T21:13:11Z','20261022T211258Z-ctrend','snapshot','{"cash": 1.118798789051061, "drawdown": 0.04532265574233463, "equity": 95.66020682616042, "session": "2026-10-22", "spy_bh_equity": 98.40875579300194}','3cf5076b07c241a5141c0753f946d62e4e2efe965967b8914d451610d720e68c','6adedce2727a26da0474dce2fdcfaf56e2d21ba81c832286f3c2527faaf02d65');
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
INSERT INTO "fills" VALUES(3,'2026-10-19:trend:ETHA:SELL:TREND_TRIM','20261019T145852Z-ctrend','2026-10-19T14:59:53Z','2026-10-19','ETHA','SELL',2.67842865649199124e-01,54.75,54.7100325,7.3,1.07050097328351811e-02,'2026-10-19T09:30:00-04:00 (official open)','yahoo_daily_open','residual','TREND_TRIM','week-end trend rebalance; ETHA: above [100, 200]-session averages',-8.79210998290876344e-01);
INSERT INTO "fills" VALUES(4,'2026-10-19:trend:SHY:BUY:TREND_BUY','20261019T145852Z-ctrend','2026-10-19T14:59:53Z','2026-10-19','SHY','BUY',0.18465,8.1339996337890625e+01,8.13969343353271455e+01,7.0,1.0513601226653511e-02,'2026-10-19T09:30:00-04:00 (official open)','yahoo_daily_open','residual','TREND_BUY','week-end trend rebalance; SHY: unallocated capital held in short-term Treasuries',NULL);
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
INSERT INTO "orders" VALUES('2026-10-19:trend:ETHA:SELL:TREND_TRIM','2026-10-16T22:48:18Z','20261016T224818Z-ctrend','ETHA','SELL','MOO','2026-10-19','residual',NULL,2.67842865649199124e-01,10,'TREND_TRIM','week-end trend rebalance; ETHA: above [100, 200]-session averages','{}','{}','FILLED','SELL 0.267843 ETHA @ 54.7100','2026-10-19T14:59:53Z');
INSERT INTO "orders" VALUES('2026-10-19:trend:SHY:BUY:TREND_BUY','2026-10-16T22:48:18Z','20261016T224818Z-ctrend','SHY','BUY','MOO','2026-10-19','residual',1.50299938838159103e+01,NULL,50,'TREND_BUY','week-end trend rebalance; SHY: unallocated capital held in short-term Treasuries','{}','{}','FILLED','BUY 0.184650 SHY @ 81.3969','2026-10-19T14:59:53Z');
CREATE TABLE positions (
  ticker TEXT PRIMARY KEY, qty REAL NOT NULL, avg_cost REAL NOT NULL, sleeve TEXT NOT NULL,
  entry_session TEXT NOT NULL, entry_price REAL NOT NULL, initial_stop REAL, trail_pct REAL,
  high_water REAL NOT NULL, max_hold_until TEXT, stop_checked_through TEXT, meta TEXT
);
INSERT INTO "positions" VALUES('ETHA',0.581446,5.79925951927185039e+01,'residual','2026-10-07',5.79925951927185039e+01,NULL,NULL,5.83050003051757812e+01,NULL,'2026-10-22T16:00:00-04:00','{"entry_time": "2026-10-07T11:35:00-04:00"}');
INSERT INTO "positions" VALUES('IBIT',1.045602,4.71044202209472615e+01,'residual','2026-10-07',4.71044202209472615e+01,NULL,NULL,4.80699996948242187e+01,NULL,'2026-10-22T16:00:00-04:00','{"entry_time": "2026-10-07T11:35:00-04:00"}');
INSERT INTO "positions" VALUES('SHY',0.18465,8.13969343353271455e+01,'residual','2026-10-19',8.13969343353271455e+01,NULL,NULL,8.156500244140625e+01,NULL,'2026-10-22T16:00:00-04:00','{}');
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
INSERT INTO "runs" VALUES('20261008T024148Z-ctrend','2026-10-08T02:41:53Z','2026-10-08T02:41:53Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261008T075925Z-ctrend','2026-10-08T07:59:28Z','2026-10-08T07:59:28Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261008T155221Z-ctrend','2026-10-08T15:53:15Z','2026-10-08T15:53:16Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261008T155721Z-ctrend','2026-10-08T15:57:27Z','2026-10-08T15:57:28Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261008T160221Z-ctrend','2026-10-08T16:02:29Z','2026-10-08T16:02:30Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261008T160721Z-ctrend','2026-10-08T16:07:30Z','2026-10-08T16:07:30Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261008T161221Z-ctrend','2026-10-08T16:12:28Z','2026-10-08T16:12:28Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261008T161349Z-ctrend','2026-10-08T16:13:55Z','2026-10-08T16:13:55Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261008T161849Z-ctrend','2026-10-08T16:18:57Z','2026-10-08T16:18:57Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261008T162349Z-ctrend','2026-10-08T16:23:55Z','2026-10-08T16:23:56Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261008T162849Z-ctrend','2026-10-08T16:28:55Z','2026-10-08T16:28:55Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261008T163349Z-ctrend','2026-10-08T16:33:56Z','2026-10-08T16:33:56Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261008T163521Z-ctrend','2026-10-08T16:35:36Z','2026-10-08T16:35:36Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261008T164022Z-ctrend','2026-10-08T16:40:34Z','2026-10-08T16:40:35Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261008T164522Z-ctrend','2026-10-08T16:45:35Z','2026-10-08T16:45:36Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261008T165022Z-ctrend','2026-10-08T16:50:35Z','2026-10-08T16:50:35Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261008T165521Z-ctrend','2026-10-08T16:55:34Z','2026-10-08T16:55:35Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261008T191442Z-ctrend','2026-10-08T19:14:50Z','2026-10-08T19:14:51Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261008T234842Z-ctrend','2026-10-08T23:50:34Z','2026-10-08T23:50:37Z','OK','github-actions','closed 2026-10-08; decided for 2026-10-09: 0 orders (MOO), rebalance=False',NULL);
INSERT INTO "runs" VALUES('20261009T001928Z-ctrend','2026-10-09T00:19:35Z','2026-10-09T00:19:35Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261009T003813Z-ctrend','2026-10-09T00:38:19Z','2026-10-09T00:38:19Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261009T011421Z-ctrend','2026-10-09T01:14:27Z','2026-10-09T01:14:27Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261009T012731Z-ctrend','2026-10-09T01:27:37Z','2026-10-09T01:27:37Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261009T025621Z-ctrend','2026-10-09T02:56:27Z','2026-10-09T02:56:27Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261009T080112Z-ctrend','2026-10-09T08:01:20Z','2026-10-09T08:01:20Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261009T153448Z-ctrend','2026-10-09T15:35:58Z','2026-10-09T15:35:59Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261009T153948Z-ctrend','2026-10-09T15:39:55Z','2026-10-09T15:39:55Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261009T154448Z-ctrend','2026-10-09T15:44:55Z','2026-10-09T15:44:55Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261009T154948Z-ctrend','2026-10-09T15:49:56Z','2026-10-09T15:49:56Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261009T155448Z-ctrend','2026-10-09T15:54:55Z','2026-10-09T15:54:55Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261009T155616Z-ctrend','2026-10-09T15:56:23Z','2026-10-09T15:56:23Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261009T160116Z-ctrend','2026-10-09T16:01:24Z','2026-10-09T16:01:24Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261009T160616Z-ctrend','2026-10-09T16:06:23Z','2026-10-09T16:06:23Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261009T161116Z-ctrend','2026-10-09T16:11:22Z','2026-10-09T16:11:23Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261009T161616Z-ctrend','2026-10-09T16:16:23Z','2026-10-09T16:16:24Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261009T161737Z-ctrend','2026-10-09T16:17:46Z','2026-10-09T16:17:47Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261009T162237Z-ctrend','2026-10-09T16:22:45Z','2026-10-09T16:22:45Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261009T162737Z-ctrend','2026-10-09T16:27:45Z','2026-10-09T16:27:45Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261009T163237Z-ctrend','2026-10-09T16:32:45Z','2026-10-09T16:32:45Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261009T163737Z-ctrend','2026-10-09T16:37:44Z','2026-10-09T16:37:44Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261009T163857Z-ctrend','2026-10-09T16:39:05Z','2026-10-09T16:39:06Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261009T164357Z-ctrend','2026-10-09T16:44:04Z','2026-10-09T16:44:04Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261009T164857Z-ctrend','2026-10-09T16:49:05Z','2026-10-09T16:49:05Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261009T165357Z-ctrend','2026-10-09T16:54:05Z','2026-10-09T16:54:05Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261009T165857Z-ctrend','2026-10-09T16:59:03Z','2026-10-09T16:59:03Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261009T184514Z-ctrend','2026-10-09T18:45:22Z','2026-10-09T18:45:23Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261009T225719Z-ctrend','2026-10-09T22:58:41Z','2026-10-09T22:58:44Z','OK','github-actions','closed 2026-10-09; decided for 2026-10-12: 0 orders (MOO), rebalance=True',NULL);
INSERT INTO "runs" VALUES('20261010T000048Z-ctrend','2026-10-10T00:00:53Z','2026-10-10T00:00:53Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261010T001940Z-ctrend','2026-10-10T00:19:47Z','2026-10-10T00:19:47Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261010T005018Z-ctrend','2026-10-10T00:50:24Z','2026-10-10T00:50:24Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261010T011553Z-ctrend','2026-10-10T01:15:59Z','2026-10-10T01:15:59Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261010T021852Z-ctrend','2026-10-10T02:18:59Z','2026-10-10T02:18:59Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261010T074527Z-ctrend','2026-10-10T07:45:32Z','2026-10-10T07:45:32Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261010T144454Z-ctrend','2026-10-10T14:44:58Z','2026-10-10T14:44:58Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261010T180002Z-ctrend','2026-10-10T18:00:10Z','2026-10-10T18:00:10Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261010T215936Z-ctrend','2026-10-10T21:59:40Z','2026-10-10T21:59:40Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261010T232652Z-ctrend','2026-10-10T23:26:58Z','2026-10-10T23:26:58Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261011T002944Z-ctrend','2026-10-11T00:29:49Z','2026-10-11T00:29:49Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261011T062652Z-ctrend','2026-10-11T06:27:00Z','2026-10-11T06:27:00Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261011T133204Z-ctrend','2026-10-11T13:32:09Z','2026-10-11T13:32:09Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261011T182707Z-ctrend','2026-10-11T18:27:14Z','2026-10-11T18:27:14Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261011T222659Z-ctrend','2026-10-11T22:27:06Z','2026-10-11T22:27:06Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261011T233349Z-ctrend','2026-10-11T23:33:55Z','2026-10-11T23:33:55Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261011T233703Z-ctrend','2026-10-11T23:37:09Z','2026-10-11T23:37:09Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261011T234358Z-ctrend','2026-10-11T23:44:03Z','2026-10-11T23:44:03Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261012T000507Z-ctrend','2026-10-12T00:05:14Z','2026-10-12T00:05:14Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261012T002544Z-ctrend','2026-10-12T00:25:51Z','2026-10-12T00:25:51Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261012T004627Z-ctrend','2026-10-12T00:46:34Z','2026-10-12T00:46:34Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261012T010711Z-ctrend','2026-10-12T01:07:19Z','2026-10-12T01:07:19Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261012T012757Z-ctrend','2026-10-12T01:28:08Z','2026-10-12T01:28:08Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261012T014836Z-ctrend','2026-10-12T01:48:42Z','2026-10-12T01:48:42Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261012T020935Z-ctrend','2026-10-12T02:09:41Z','2026-10-12T02:09:41Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261012T023001Z-ctrend','2026-10-12T02:30:07Z','2026-10-12T02:30:07Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261012T025036Z-ctrend','2026-10-12T02:50:43Z','2026-10-12T02:50:43Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261012T031128Z-ctrend','2026-10-12T03:11:34Z','2026-10-12T03:11:34Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261012T033206Z-ctrend','2026-10-12T03:32:12Z','2026-10-12T03:32:12Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261012T035247Z-ctrend','2026-10-12T03:52:53Z','2026-10-12T03:52:53Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261012T041322Z-ctrend','2026-10-12T04:13:28Z','2026-10-12T04:13:28Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261012T043409Z-ctrend','2026-10-12T04:34:14Z','2026-10-12T04:34:14Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261012T045455Z-ctrend','2026-10-12T04:55:02Z','2026-10-12T04:55:02Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261012T063008Z-ctrend','2026-10-12T06:30:14Z','2026-10-12T06:30:14Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261012T160515Z-ctrend','2026-10-12T16:06:15Z','2026-10-12T16:06:15Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261012T161015Z-ctrend','2026-10-12T16:10:23Z','2026-10-12T16:10:23Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261012T161515Z-ctrend','2026-10-12T16:15:24Z','2026-10-12T16:15:24Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261012T162015Z-ctrend','2026-10-12T16:20:24Z','2026-10-12T16:20:24Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261012T162515Z-ctrend','2026-10-12T16:25:23Z','2026-10-12T16:25:23Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261012T162645Z-ctrend','2026-10-12T16:26:52Z','2026-10-12T16:26:52Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261012T163145Z-ctrend','2026-10-12T16:31:52Z','2026-10-12T16:31:52Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261012T163645Z-ctrend','2026-10-12T16:36:52Z','2026-10-12T16:36:53Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261012T164145Z-ctrend','2026-10-12T16:41:52Z','2026-10-12T16:41:52Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261012T164645Z-ctrend','2026-10-12T16:46:52Z','2026-10-12T16:46:52Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261012T164821Z-ctrend','2026-10-12T16:48:30Z','2026-10-12T16:48:30Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261012T165321Z-ctrend','2026-10-12T16:53:28Z','2026-10-12T16:53:29Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261012T165821Z-ctrend','2026-10-12T16:58:27Z','2026-10-12T16:58:27Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261012T173400Z-ctrend','2026-10-12T17:34:07Z','2026-10-12T17:34:07Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261012T174933Z-ctrend','2026-10-12T17:49:40Z','2026-10-12T17:49:40Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261012T180719Z-ctrend','2026-10-12T18:07:29Z','2026-10-12T18:07:29Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261012T213411Z-ctrend','2026-10-12T21:36:11Z','2026-10-12T21:36:14Z','OK','github-actions','closed 2026-10-12; decided for 2026-10-13: 0 orders (MOO), rebalance=False',NULL);
INSERT INTO "runs" VALUES('20261013T020022Z-ctrend','2026-10-13T02:00:27Z','2026-10-13T02:00:27Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261013T021408Z-ctrend','2026-10-13T02:14:14Z','2026-10-13T02:14:14Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261013T023504Z-ctrend','2026-10-13T02:35:10Z','2026-10-13T02:35:10Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261013T024332Z-ctrend','2026-10-13T02:43:37Z','2026-10-13T02:43:37Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261013T033510Z-ctrend','2026-10-13T03:35:16Z','2026-10-13T03:35:16Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261013T094554Z-ctrend','2026-10-13T09:45:59Z','2026-10-13T09:45:59Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261013T174833Z-ctrend','2026-10-13T17:49:42Z','2026-10-13T17:49:43Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261013T194605Z-ctrend','2026-10-13T19:46:13Z','2026-10-13T19:46:13Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261013T232833Z-ctrend','2026-10-13T23:30:21Z','2026-10-13T23:30:24Z','OK','github-actions','closed 2026-10-13; decided for 2026-10-14: 0 orders (MOO), rebalance=False',NULL);
INSERT INTO "runs" VALUES('20261013T234404Z-ctrend','2026-10-13T23:44:09Z','2026-10-13T23:44:09Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261013T235108Z-ctrend','2026-10-13T23:51:15Z','2026-10-13T23:51:15Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261014T001753Z-ctrend','2026-10-14T00:17:59Z','2026-10-14T00:17:59Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261014T003700Z-ctrend','2026-10-14T00:37:06Z','2026-10-14T00:37:06Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261014T015555Z-ctrend','2026-10-14T01:56:00Z','2026-10-14T01:56:00Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261014T052204Z-ctrend','2026-10-14T05:22:11Z','2026-10-14T05:22:11Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261014T103616Z-ctrend','2026-10-14T10:36:23Z','2026-10-14T10:36:23Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261014T152847Z-ctrend','2026-10-14T15:29:59Z','2026-10-14T15:29:59Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261014T153347Z-ctrend','2026-10-14T15:33:56Z','2026-10-14T15:33:56Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261014T153847Z-ctrend','2026-10-14T15:38:59Z','2026-10-14T15:39:00Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261014T154347Z-ctrend','2026-10-14T15:43:54Z','2026-10-14T15:43:54Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261014T154847Z-ctrend','2026-10-14T15:48:55Z','2026-10-14T15:48:56Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261014T155025Z-ctrend','2026-10-14T15:50:34Z','2026-10-14T15:50:34Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261014T155525Z-ctrend','2026-10-14T15:55:33Z','2026-10-14T15:55:34Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261014T160025Z-ctrend','2026-10-14T16:00:32Z','2026-10-14T16:00:33Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261014T160525Z-ctrend','2026-10-14T16:05:34Z','2026-10-14T16:05:34Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261014T161025Z-ctrend','2026-10-14T16:10:33Z','2026-10-14T16:10:33Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261014T161157Z-ctrend','2026-10-14T16:12:05Z','2026-10-14T16:12:06Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261014T161657Z-ctrend','2026-10-14T16:17:11Z','2026-10-14T16:17:12Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261014T162157Z-ctrend','2026-10-14T16:22:07Z','2026-10-14T16:22:07Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261014T162657Z-ctrend','2026-10-14T16:27:06Z','2026-10-14T16:27:06Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261014T163157Z-ctrend','2026-10-14T16:32:05Z','2026-10-14T16:32:06Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261014T163322Z-ctrend','2026-10-14T16:33:29Z','2026-10-14T16:33:30Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261014T163822Z-ctrend','2026-10-14T16:38:28Z','2026-10-14T16:38:28Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261014T164322Z-ctrend','2026-10-14T16:43:27Z','2026-10-14T16:43:28Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261014T164822Z-ctrend','2026-10-14T16:48:29Z','2026-10-14T16:48:29Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261014T165322Z-ctrend','2026-10-14T16:53:29Z','2026-10-14T16:53:29Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261014T165457Z-ctrend','2026-10-14T16:55:06Z','2026-10-14T16:55:06Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261014T165957Z-ctrend','2026-10-14T17:00:05Z','2026-10-14T17:00:05Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261014T174737Z-ctrend','2026-10-14T17:47:45Z','2026-10-14T17:47:46Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261014T211810Z-ctrend','2026-10-14T21:20:06Z','2026-10-14T21:20:09Z','OK','github-actions','closed 2026-10-14; decided for 2026-10-15: 0 orders (MOO), rebalance=False',NULL);
INSERT INTO "runs" VALUES('20261014T231110Z-ctrend','2026-10-14T23:11:17Z','2026-10-14T23:11:17Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261014T232450Z-ctrend','2026-10-14T23:24:56Z','2026-10-14T23:24:56Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261014T235511Z-ctrend','2026-10-14T23:55:16Z','2026-10-14T23:55:16Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261015T000621Z-ctrend','2026-10-15T00:06:29Z','2026-10-15T00:06:29Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261015T012959Z-ctrend','2026-10-15T01:30:06Z','2026-10-15T01:30:06Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261015T050906Z-ctrend','2026-10-15T05:09:13Z','2026-10-15T05:09:13Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261015T101811Z-ctrend','2026-10-15T10:18:19Z','2026-10-15T10:18:19Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261015T152026Z-ctrend','2026-10-15T15:21:17Z','2026-10-15T15:21:17Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261015T152526Z-ctrend','2026-10-15T15:25:32Z','2026-10-15T15:25:33Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261015T153026Z-ctrend','2026-10-15T15:30:32Z','2026-10-15T15:30:33Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261015T153526Z-ctrend','2026-10-15T15:35:33Z','2026-10-15T15:35:33Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261015T154026Z-ctrend','2026-10-15T15:40:32Z','2026-10-15T15:40:32Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261015T154200Z-ctrend','2026-10-15T15:42:17Z','2026-10-15T15:42:17Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261015T154700Z-ctrend','2026-10-15T15:47:19Z','2026-10-15T15:47:19Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261015T155200Z-ctrend','2026-10-15T15:52:19Z','2026-10-15T15:52:19Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261015T155700Z-ctrend','2026-10-15T15:57:17Z','2026-10-15T15:57:17Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261015T160200Z-ctrend','2026-10-15T16:02:21Z','2026-10-15T16:02:22Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261015T160352Z-ctrend','2026-10-15T16:04:02Z','2026-10-15T16:04:02Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261015T160852Z-ctrend','2026-10-15T16:09:00Z','2026-10-15T16:09:00Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261015T161352Z-ctrend','2026-10-15T16:13:59Z','2026-10-15T16:13:59Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261015T161851Z-ctrend','2026-10-15T16:19:01Z','2026-10-15T16:19:01Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261015T162352Z-ctrend','2026-10-15T16:24:00Z','2026-10-15T16:24:00Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261015T162525Z-ctrend','2026-10-15T16:25:32Z','2026-10-15T16:25:33Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261015T163025Z-ctrend','2026-10-15T16:30:32Z','2026-10-15T16:30:32Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261015T163525Z-ctrend','2026-10-15T16:35:32Z','2026-10-15T16:35:32Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261015T164025Z-ctrend','2026-10-15T16:40:31Z','2026-10-15T16:40:31Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261015T164525Z-ctrend','2026-10-15T16:45:32Z','2026-10-15T16:45:32Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261015T164659Z-ctrend','2026-10-15T16:47:06Z','2026-10-15T16:47:06Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261015T165159Z-ctrend','2026-10-15T16:52:06Z','2026-10-15T16:52:06Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261015T165659Z-ctrend','2026-10-15T16:57:06Z','2026-10-15T16:57:06Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261015T173635Z-ctrend','2026-10-15T17:36:43Z','2026-10-15T17:36:43Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261015T203351Z-ctrend','2026-10-15T20:35:58Z','2026-10-15T20:36:01Z','OK','github-actions','closed 2026-10-15; decided for 2026-10-16: 0 orders (MOO), rebalance=False',NULL);
INSERT INTO "runs" VALUES('20261015T230228Z-ctrend','2026-10-15T23:02:34Z','2026-10-15T23:02:34Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261015T231534Z-ctrend','2026-10-15T23:15:41Z','2026-10-15T23:15:41Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261015T234217Z-ctrend','2026-10-15T23:42:22Z','2026-10-15T23:42:22Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261015T235055Z-ctrend','2026-10-15T23:51:01Z','2026-10-15T23:51:01Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261016T012141Z-ctrend','2026-10-16T01:21:47Z','2026-10-16T01:21:48Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261016T045919Z-ctrend','2026-10-16T04:59:23Z','2026-10-16T04:59:23Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261016T100617Z-ctrend','2026-10-16T10:06:24Z','2026-10-16T10:06:24Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261016T150042Z-ctrend','2026-10-16T15:01:48Z','2026-10-16T15:01:48Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261016T150542Z-ctrend','2026-10-16T15:05:49Z','2026-10-16T15:05:49Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261016T151042Z-ctrend','2026-10-16T15:10:49Z','2026-10-16T15:10:49Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261016T151542Z-ctrend','2026-10-16T15:15:49Z','2026-10-16T15:15:49Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261016T152042Z-ctrend','2026-10-16T15:20:50Z','2026-10-16T15:20:50Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261016T152216Z-ctrend','2026-10-16T15:22:24Z','2026-10-16T15:22:25Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261016T152716Z-ctrend','2026-10-16T15:27:24Z','2026-10-16T15:27:24Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261016T153216Z-ctrend','2026-10-16T15:32:23Z','2026-10-16T15:32:23Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261016T153716Z-ctrend','2026-10-16T15:37:24Z','2026-10-16T15:37:24Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261016T154216Z-ctrend','2026-10-16T15:42:23Z','2026-10-16T15:42:23Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261016T154342Z-ctrend','2026-10-16T15:43:49Z','2026-10-16T15:43:50Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261016T154842Z-ctrend','2026-10-16T15:48:50Z','2026-10-16T15:48:50Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261016T155342Z-ctrend','2026-10-16T15:53:49Z','2026-10-16T15:53:49Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261016T155842Z-ctrend','2026-10-16T15:58:47Z','2026-10-16T15:58:47Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261016T160342Z-ctrend','2026-10-16T16:03:51Z','2026-10-16T16:03:51Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261016T160520Z-ctrend','2026-10-16T16:05:28Z','2026-10-16T16:05:28Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261016T161020Z-ctrend','2026-10-16T16:10:27Z','2026-10-16T16:10:27Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261016T161520Z-ctrend','2026-10-16T16:15:28Z','2026-10-16T16:15:28Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261016T162020Z-ctrend','2026-10-16T16:20:27Z','2026-10-16T16:20:28Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261016T162520Z-ctrend','2026-10-16T16:25:28Z','2026-10-16T16:25:28Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261016T162652Z-ctrend','2026-10-16T16:26:59Z','2026-10-16T16:26:59Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261016T163152Z-ctrend','2026-10-16T16:31:59Z','2026-10-16T16:31:59Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261016T163652Z-ctrend','2026-10-16T16:36:58Z','2026-10-16T16:36:59Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261016T164152Z-ctrend','2026-10-16T16:41:58Z','2026-10-16T16:41:58Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261016T164652Z-ctrend','2026-10-16T16:46:59Z','2026-10-16T16:46:59Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261016T164827Z-ctrend','2026-10-16T16:48:34Z','2026-10-16T16:48:34Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261016T165327Z-ctrend','2026-10-16T16:53:34Z','2026-10-16T16:53:35Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261016T165827Z-ctrend','2026-10-16T16:58:32Z','2026-10-16T16:58:32Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261016T171056Z-ctrend','2026-10-16T17:11:04Z','2026-10-16T17:11:04Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261016T192136Z-ctrend','2026-10-16T19:21:45Z','2026-10-16T19:21:45Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261016T195856Z-ctrend','2026-10-16T19:59:00Z','2026-10-16T19:59:01Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261016T224818Z-ctrend','2026-10-16T22:50:13Z','2026-10-16T22:50:16Z','OK','github-actions','closed 2026-10-16; decided for 2026-10-19: 2 orders (MOO), rebalance=True',NULL);
INSERT INTO "runs" VALUES('20261016T230004Z-ctrend','2026-10-16T23:00:10Z','2026-10-16T23:00:10Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261016T233455Z-ctrend','2026-10-16T23:35:01Z','2026-10-16T23:35:01Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261016T235224Z-ctrend','2026-10-16T23:52:30Z','2026-10-16T23:52:30Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261017T012024Z-ctrend','2026-10-17T01:20:31Z','2026-10-17T01:20:31Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261017T045839Z-ctrend','2026-10-17T04:58:43Z','2026-10-17T04:58:43Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261017T051855Z-ctrend','2026-10-17T05:19:01Z','2026-10-17T05:19:01Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261017T094020Z-ctrend','2026-10-17T09:40:25Z','2026-10-17T09:40:25Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261017T131205Z-ctrend','2026-10-17T13:12:11Z','2026-10-17T13:12:11Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261017T164025Z-ctrend','2026-10-17T16:40:31Z','2026-10-17T16:40:31Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261017T185154Z-ctrend','2026-10-17T18:52:02Z','2026-10-17T18:52:02Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261017T214626Z-ctrend','2026-10-17T21:46:32Z','2026-10-17T21:46:32Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261017T232418Z-ctrend','2026-10-17T23:24:25Z','2026-10-17T23:24:25Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261018T013136Z-ctrend','2026-10-18T01:31:46Z','2026-10-18T01:31:46Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261018T063518Z-ctrend','2026-10-18T06:35:24Z','2026-10-18T06:35:24Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261018T114142Z-ctrend','2026-10-18T11:41:47Z','2026-10-18T11:41:47Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261018T144953Z-ctrend','2026-10-18T14:49:59Z','2026-10-18T14:49:59Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261018T165656Z-ctrend','2026-10-18T16:57:01Z','2026-10-18T16:57:01Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261018T194224Z-ctrend','2026-10-18T19:42:30Z','2026-10-18T19:42:30Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261018T215623Z-ctrend','2026-10-18T21:56:29Z','2026-10-18T21:56:29Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261018T233830Z-ctrend','2026-10-18T23:38:36Z','2026-10-18T23:38:36Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261019T013909Z-ctrend','2026-10-19T01:39:15Z','2026-10-19T01:39:15Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261019T064733Z-ctrend','2026-10-19T06:47:40Z','2026-10-19T06:47:40Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261019T145852Z-ctrend','2026-10-19T14:59:52Z','2026-10-19T14:59:53Z','OK','github-actions','FILL SELL ETHA 0.2678 @ 54.71 (TREND_TRIM); FILL BUY SHY 0.1847 @ 81.40 (TREND_BUY)',NULL);
INSERT INTO "runs" VALUES('20261019T150352Z-ctrend','2026-10-19T15:04:00Z','2026-10-19T15:04:00Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261019T150852Z-ctrend','2026-10-19T15:08:59Z','2026-10-19T15:08:59Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261019T151352Z-ctrend','2026-10-19T15:13:58Z','2026-10-19T15:13:58Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261019T151852Z-ctrend','2026-10-19T15:19:00Z','2026-10-19T15:19:01Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261019T152024Z-ctrend','2026-10-19T15:20:31Z','2026-10-19T15:20:31Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261019T152524Z-ctrend','2026-10-19T15:25:31Z','2026-10-19T15:25:31Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261019T153024Z-ctrend','2026-10-19T15:30:30Z','2026-10-19T15:30:30Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261019T153524Z-ctrend','2026-10-19T15:35:31Z','2026-10-19T15:35:31Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261019T154024Z-ctrend','2026-10-19T15:40:30Z','2026-10-19T15:40:30Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261019T154157Z-ctrend','2026-10-19T15:42:04Z','2026-10-19T15:42:04Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261019T154657Z-ctrend','2026-10-19T15:47:04Z','2026-10-19T15:47:04Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261019T155157Z-ctrend','2026-10-19T15:52:04Z','2026-10-19T15:52:05Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261019T155657Z-ctrend','2026-10-19T15:57:04Z','2026-10-19T15:57:04Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261019T160157Z-ctrend','2026-10-19T16:02:05Z','2026-10-19T16:02:05Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261019T160325Z-ctrend','2026-10-19T16:03:33Z','2026-10-19T16:03:33Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261019T160825Z-ctrend','2026-10-19T16:08:32Z','2026-10-19T16:08:32Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261019T161325Z-ctrend','2026-10-19T16:13:31Z','2026-10-19T16:13:31Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261019T161825Z-ctrend','2026-10-19T16:18:32Z','2026-10-19T16:18:32Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261019T162325Z-ctrend','2026-10-19T16:23:31Z','2026-10-19T16:23:32Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261019T162449Z-ctrend','2026-10-19T16:24:56Z','2026-10-19T16:24:57Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261019T162949Z-ctrend','2026-10-19T16:29:56Z','2026-10-19T16:29:56Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261019T163449Z-ctrend','2026-10-19T16:34:56Z','2026-10-19T16:34:56Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261019T163949Z-ctrend','2026-10-19T16:39:55Z','2026-10-19T16:39:55Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261019T164449Z-ctrend','2026-10-19T16:44:54Z','2026-10-19T16:44:54Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261019T164623Z-ctrend','2026-10-19T16:46:32Z','2026-10-19T16:46:33Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261019T165123Z-ctrend','2026-10-19T16:51:32Z','2026-10-19T16:51:32Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261019T165623Z-ctrend','2026-10-19T16:56:30Z','2026-10-19T16:56:31Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261019T190122Z-ctrend','2026-10-19T19:01:30Z','2026-10-19T19:01:31Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261019T225519Z-ctrend','2026-10-19T22:57:05Z','2026-10-19T22:57:08Z','OK','github-actions','closed 2026-10-19; decided for 2026-10-20: 0 orders (MOO), rebalance=False',NULL);
INSERT INTO "runs" VALUES('20261019T233526Z-ctrend','2026-10-19T23:35:32Z','2026-10-19T23:35:32Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261019T235511Z-ctrend','2026-10-19T23:55:17Z','2026-10-19T23:55:17Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261020T001946Z-ctrend','2026-10-20T00:19:53Z','2026-10-20T00:19:53Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261020T003858Z-ctrend','2026-10-20T00:39:04Z','2026-10-20T00:39:04Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261020T015106Z-ctrend','2026-10-20T01:51:12Z','2026-10-20T01:51:12Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261020T051531Z-ctrend','2026-10-20T05:15:37Z','2026-10-20T05:15:37Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261020T102508Z-ctrend','2026-10-20T10:25:14Z','2026-10-20T10:25:14Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261020T152238Z-ctrend','2026-10-20T15:23:47Z','2026-10-20T15:23:48Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261020T152738Z-ctrend','2026-10-20T15:27:47Z','2026-10-20T15:27:47Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261020T153238Z-ctrend','2026-10-20T15:32:46Z','2026-10-20T15:32:47Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261020T153738Z-ctrend','2026-10-20T15:37:45Z','2026-10-20T15:37:46Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261020T154238Z-ctrend','2026-10-20T15:42:45Z','2026-10-20T15:42:45Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261020T154410Z-ctrend','2026-10-20T15:44:16Z','2026-10-20T15:44:17Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261020T154910Z-ctrend','2026-10-20T15:49:17Z','2026-10-20T15:49:17Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261020T155410Z-ctrend','2026-10-20T15:54:16Z','2026-10-20T15:54:17Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261020T155910Z-ctrend','2026-10-20T15:59:15Z','2026-10-20T15:59:15Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261020T160410Z-ctrend','2026-10-20T16:04:18Z','2026-10-20T16:04:18Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261020T160541Z-ctrend','2026-10-20T16:05:48Z','2026-10-20T16:05:48Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261020T161040Z-ctrend','2026-10-20T16:10:48Z','2026-10-20T16:10:48Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261020T161540Z-ctrend','2026-10-20T16:15:48Z','2026-10-20T16:15:48Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261020T162041Z-ctrend','2026-10-20T16:20:48Z','2026-10-20T16:20:48Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261020T162541Z-ctrend','2026-10-20T16:25:48Z','2026-10-20T16:25:48Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261020T162722Z-ctrend','2026-10-20T16:27:29Z','2026-10-20T16:27:30Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261020T163222Z-ctrend','2026-10-20T16:32:29Z','2026-10-20T16:32:29Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261020T163722Z-ctrend','2026-10-20T16:37:30Z','2026-10-20T16:37:30Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261020T164222Z-ctrend','2026-10-20T16:42:29Z','2026-10-20T16:42:29Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261020T164722Z-ctrend','2026-10-20T16:47:29Z','2026-10-20T16:47:29Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261020T164901Z-ctrend','2026-10-20T16:49:09Z','2026-10-20T16:49:10Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261020T165401Z-ctrend','2026-10-20T16:54:08Z','2026-10-20T16:54:08Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261020T165901Z-ctrend','2026-10-20T16:59:06Z','2026-10-20T16:59:07Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261020T174716Z-ctrend','2026-10-20T17:47:24Z','2026-10-20T17:47:24Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261020T211541Z-ctrend','2026-10-20T21:17:19Z','2026-10-20T21:17:22Z','OK','github-actions','closed 2026-10-20; decided for 2026-10-21: 0 orders (MOO), rebalance=False',NULL);
INSERT INTO "runs" VALUES('20261020T230949Z-ctrend','2026-10-20T23:09:55Z','2026-10-20T23:09:55Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261020T232227Z-ctrend','2026-10-20T23:22:34Z','2026-10-20T23:22:34Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261020T235216Z-ctrend','2026-10-20T23:52:22Z','2026-10-20T23:52:22Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261021T000813Z-ctrend','2026-10-21T00:08:20Z','2026-10-21T00:08:20Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261021T013651Z-ctrend','2026-10-21T01:36:58Z','2026-10-21T01:36:58Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261021T051742Z-ctrend','2026-10-21T05:17:49Z','2026-10-21T05:17:49Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261021T103441Z-ctrend','2026-10-21T10:34:47Z','2026-10-21T10:34:47Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261021T153646Z-ctrend','2026-10-21T15:37:53Z','2026-10-21T15:37:53Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261021T154146Z-ctrend','2026-10-21T15:41:54Z','2026-10-21T15:41:54Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261021T154646Z-ctrend','2026-10-21T15:46:53Z','2026-10-21T15:46:53Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261021T155146Z-ctrend','2026-10-21T15:51:53Z','2026-10-21T15:51:54Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261021T155646Z-ctrend','2026-10-21T15:56:52Z','2026-10-21T15:56:52Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261021T155819Z-ctrend','2026-10-21T15:58:25Z','2026-10-21T15:58:25Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261021T160319Z-ctrend','2026-10-21T16:03:27Z','2026-10-21T16:03:27Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261021T160819Z-ctrend','2026-10-21T16:08:27Z','2026-10-21T16:08:27Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261021T161319Z-ctrend','2026-10-21T16:13:26Z','2026-10-21T16:13:26Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261021T161819Z-ctrend','2026-10-21T16:18:27Z','2026-10-21T16:18:28Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261021T161952Z-ctrend','2026-10-21T16:20:03Z','2026-10-21T16:20:03Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261021T162452Z-ctrend','2026-10-21T16:24:59Z','2026-10-21T16:24:59Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261021T162952Z-ctrend','2026-10-21T16:30:00Z','2026-10-21T16:30:00Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261021T163452Z-ctrend','2026-10-21T16:34:59Z','2026-10-21T16:34:59Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261021T163952Z-ctrend','2026-10-21T16:39:59Z','2026-10-21T16:39:59Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261021T164123Z-ctrend','2026-10-21T16:41:32Z','2026-10-21T16:41:32Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261021T164624Z-ctrend','2026-10-21T16:46:31Z','2026-10-21T16:46:31Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261021T165123Z-ctrend','2026-10-21T16:51:31Z','2026-10-21T16:51:31Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261021T165623Z-ctrend','2026-10-21T16:56:31Z','2026-10-21T16:56:31Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261021T175515Z-ctrend','2026-10-21T17:55:24Z','2026-10-21T17:55:24Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261021T211617Z-ctrend','2026-10-21T21:18:21Z','2026-10-21T21:18:24Z','OK','github-actions','closed 2026-10-21; decided for 2026-10-22: 0 orders (MOO), rebalance=False',NULL);
INSERT INTO "runs" VALUES('20261021T231503Z-ctrend','2026-10-21T23:15:09Z','2026-10-21T23:15:09Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261021T233530Z-ctrend','2026-10-21T23:35:36Z','2026-10-21T23:35:36Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261022T000058Z-ctrend','2026-10-22T00:01:04Z','2026-10-22T00:01:04Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261022T001201Z-ctrend','2026-10-22T00:12:07Z','2026-10-22T00:12:07Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261022T013336Z-ctrend','2026-10-22T01:33:43Z','2026-10-22T01:33:43Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261022T052032Z-ctrend','2026-10-22T05:20:39Z','2026-10-22T05:20:39Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261022T103742Z-ctrend','2026-10-22T10:37:48Z','2026-10-22T10:37:48Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261022T153826Z-ctrend','2026-10-22T15:39:47Z','2026-10-22T15:39:47Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261022T154326Z-ctrend','2026-10-22T15:43:34Z','2026-10-22T15:43:35Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261022T154826Z-ctrend','2026-10-22T15:48:33Z','2026-10-22T15:48:34Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261022T155326Z-ctrend','2026-10-22T15:53:33Z','2026-10-22T15:53:33Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261022T155826Z-ctrend','2026-10-22T15:58:32Z','2026-10-22T15:58:32Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261022T155958Z-ctrend','2026-10-22T16:00:06Z','2026-10-22T16:00:06Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261022T160458Z-ctrend','2026-10-22T16:05:08Z','2026-10-22T16:05:08Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261022T160958Z-ctrend','2026-10-22T16:10:07Z','2026-10-22T16:10:07Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261022T161458Z-ctrend','2026-10-22T16:15:07Z','2026-10-22T16:15:07Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261022T161958Z-ctrend','2026-10-22T16:20:07Z','2026-10-22T16:20:08Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261022T162129Z-ctrend','2026-10-22T16:21:37Z','2026-10-22T16:21:37Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261022T162629Z-ctrend','2026-10-22T16:26:36Z','2026-10-22T16:26:36Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261022T163129Z-ctrend','2026-10-22T16:31:37Z','2026-10-22T16:31:37Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261022T163629Z-ctrend','2026-10-22T16:36:36Z','2026-10-22T16:36:36Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261022T164129Z-ctrend','2026-10-22T16:41:36Z','2026-10-22T16:41:36Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261022T164253Z-ctrend','2026-10-22T16:43:01Z','2026-10-22T16:43:02Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261022T164754Z-ctrend','2026-10-22T16:48:02Z','2026-10-22T16:48:02Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261022T165254Z-ctrend','2026-10-22T16:53:01Z','2026-10-22T16:53:01Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261022T165753Z-ctrend','2026-10-22T16:58:01Z','2026-10-22T16:58:01Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261022T175208Z-ctrend','2026-10-22T17:52:17Z','2026-10-22T17:52:17Z','OK','github-actions','no action needed',NULL);
INSERT INTO "runs" VALUES('20261022T211258Z-ctrend','2026-10-22T21:13:10Z','2026-10-22T21:13:11Z','OK','github-actions','closed 2026-10-22; experiment end date reached',NULL);
INSERT INTO "runs" VALUES('20261022T231859Z-ctrend','2026-10-22T23:18:59Z','2026-10-22T23:18:59Z','OK','github-actions','experiment finished; nothing to do',NULL);
INSERT INTO "runs" VALUES('20261022T233253Z-ctrend','2026-10-22T23:32:53Z','2026-10-22T23:32:53Z','OK','github-actions','experiment finished; nothing to do',NULL);
INSERT INTO "runs" VALUES('20261022T235939Z-ctrend','2026-10-22T23:59:39Z','2026-10-22T23:59:39Z','OK','github-actions','experiment finished; nothing to do',NULL);
INSERT INTO "runs" VALUES('20261023T000933Z-ctrend','2026-10-23T00:09:33Z','2026-10-23T00:09:33Z','OK','github-actions','experiment finished; nothing to do',NULL);
INSERT INTO "runs" VALUES('20261023T013224Z-ctrend','2026-10-23T01:32:24Z','2026-10-23T01:32:24Z','OK','github-actions','experiment finished; nothing to do',NULL);
INSERT INTO "runs" VALUES('20261023T052013Z-ctrend','2026-10-23T05:20:13Z','2026-10-23T05:20:13Z','OK','github-actions','experiment finished; nothing to do',NULL);
INSERT INTO "runs" VALUES('20261023T103047Z-ctrend','2026-10-23T10:30:47Z','2026-10-23T10:30:47Z','OK','github-actions','experiment finished; nothing to do',NULL);
INSERT INTO "runs" VALUES('20261023T152749Z-ctrend','2026-10-23T15:27:49Z','2026-10-23T15:27:49Z','OK','github-actions','experiment finished; nothing to do',NULL);
INSERT INTO "runs" VALUES('20261023T153249Z-ctrend','2026-10-23T15:32:49Z','2026-10-23T15:32:49Z','OK','github-actions','experiment finished; nothing to do',NULL);
INSERT INTO "runs" VALUES('20261023T153749Z-ctrend','2026-10-23T15:37:49Z','2026-10-23T15:37:49Z','OK','github-actions','experiment finished; nothing to do',NULL);
INSERT INTO "runs" VALUES('20261023T154249Z-ctrend','2026-10-23T15:42:49Z','2026-10-23T15:42:49Z','OK','github-actions','experiment finished; nothing to do',NULL);
INSERT INTO "runs" VALUES('20261023T154749Z-ctrend','2026-10-23T15:47:49Z','2026-10-23T15:47:49Z','OK','github-actions','experiment finished; nothing to do',NULL);
INSERT INTO "runs" VALUES('20261023T154911Z-ctrend','2026-10-23T15:49:11Z','2026-10-23T15:49:11Z','OK','github-actions','experiment finished; nothing to do',NULL);
INSERT INTO "runs" VALUES('20261023T155411Z-ctrend','2026-10-23T15:54:11Z','2026-10-23T15:54:11Z','OK','github-actions','experiment finished; nothing to do',NULL);
INSERT INTO "runs" VALUES('20261023T155911Z-ctrend','2026-10-23T15:59:11Z','2026-10-23T15:59:11Z','OK','github-actions','experiment finished; nothing to do',NULL);
INSERT INTO "runs" VALUES('20261023T160411Z-ctrend','2026-10-23T16:04:11Z','2026-10-23T16:04:11Z','OK','github-actions','experiment finished; nothing to do',NULL);
INSERT INTO "runs" VALUES('20261023T160911Z-ctrend','2026-10-23T16:09:11Z','2026-10-23T16:09:11Z','OK','github-actions','experiment finished; nothing to do',NULL);
INSERT INTO "runs" VALUES('20261023T161034Z-ctrend','2026-10-23T16:10:34Z','2026-10-23T16:10:34Z','OK','github-actions','experiment finished; nothing to do',NULL);
INSERT INTO "runs" VALUES('20261023T161534Z-ctrend','2026-10-23T16:15:34Z','2026-10-23T16:15:34Z','OK','github-actions','experiment finished; nothing to do',NULL);
INSERT INTO "runs" VALUES('20261023T162034Z-ctrend','2026-10-23T16:20:34Z','2026-10-23T16:20:34Z','OK','github-actions','experiment finished; nothing to do',NULL);
INSERT INTO "runs" VALUES('20261023T162534Z-ctrend','2026-10-23T16:25:34Z','2026-10-23T16:25:34Z','OK','github-actions','experiment finished; nothing to do',NULL);
INSERT INTO "runs" VALUES('20261023T163034Z-ctrend','2026-10-23T16:30:34Z','2026-10-23T16:30:34Z','OK','github-actions','experiment finished; nothing to do',NULL);
INSERT INTO "runs" VALUES('20261023T163155Z-ctrend','2026-10-23T16:31:55Z','2026-10-23T16:31:55Z','OK','github-actions','experiment finished; nothing to do',NULL);
INSERT INTO "runs" VALUES('20261023T163655Z-ctrend','2026-10-23T16:36:55Z','2026-10-23T16:36:55Z','OK','github-actions','experiment finished; nothing to do',NULL);
INSERT INTO "runs" VALUES('20261023T164155Z-ctrend','2026-10-23T16:41:55Z','2026-10-23T16:41:55Z','OK','github-actions','experiment finished; nothing to do',NULL);
INSERT INTO "runs" VALUES('20261023T164655Z-ctrend','2026-10-23T16:46:55Z','2026-10-23T16:46:55Z','OK','github-actions','experiment finished; nothing to do',NULL);
INSERT INTO "runs" VALUES('20261023T165155Z-ctrend','2026-10-23T16:51:55Z','2026-10-23T16:51:55Z','OK','github-actions','experiment finished; nothing to do',NULL);
CREATE TABLE snapshots (
  session TEXT PRIMARY KEY, created_at TEXT NOT NULL, run_id TEXT, equity REAL NOT NULL,
  cash REAL NOT NULL, positions_value REAL NOT NULL, spy_bh_equity REAL, cash_bh_equity REAL,
  peak REAL NOT NULL, drawdown REAL NOT NULL, regime TEXT, risk_state TEXT, marks TEXT, holdings TEXT
);
INSERT INTO "snapshots" VALUES('2026-10-07','2026-10-07T20:46:12Z','20261007T204612Z-ctrend',100.201609896319,1.49505082950840062e+00,98.7065590668106,1.0011682299405129e+02,100.0,100.201609896319,0.0,'TREND','{"peak": 100.201609896319, "pause_until": null, "halt_until": null, "drawdown": 0.0}','{"marks": {"ETHA": 58.099998474121094, "IBIT": 47.209999084472656}, "flags": {}}','{"ETHA": {"qty": 0.849289, "avg_cost": 57.992595192718504, "sleeve": "residual", "stop": null, "entry_session": "2026-10-07", "max_hold_until": null}, "IBIT": {"qty": 1.045602, "avg_cost": 47.10442022094726, "sleeve": "residual", "stop": null, "entry_session": "2026-10-07", "max_hold_until": null}}');
INSERT INTO "snapshots" VALUES('2026-10-08','2026-10-08T23:48:42Z','20261008T234842Z-ctrend',9.71699955424562347e+01,1.49505082950840062e+00,9.5674944712947834e+01,9.96930277234280737e+01,100.0,100.201609896319,3.02551461698035151e-02,'TREND','{"peak": 100.201609896319, "pause_until": null, "halt_until": null, "drawdown": 0.030255146169803515}','{"marks": {"ETHA": 55.70000076293945, "IBIT": 46.2599983215332}, "flags": {}}','{"ETHA": {"qty": 0.849289, "avg_cost": 57.992595192718504, "sleeve": "residual", "stop": null, "entry_session": "2026-10-07", "max_hold_until": null}, "IBIT": {"qty": 1.045602, "avg_cost": 47.10442022094726, "sleeve": "residual", "stop": null, "entry_session": "2026-10-07", "max_hold_until": null}}');
INSERT INTO "snapshots" VALUES('2026-10-09','2026-10-09T22:57:19Z','20261009T225719Z-ctrend',9.77195156672807598e+01,1.49505082950840062e+00,9.62244648377723592e+01,1.00290726628188807e+02,100.0,100.201609896319,2.47710014999411587e-02,'TREND','{"peak": 100.201609896319, "pause_until": null, "halt_until": null, "drawdown": 0.02477100149994116}','{"marks": {"ETHA": 55.9900016784668, "IBIT": 46.54999923706055}, "flags": {}}','{"ETHA": {"qty": 0.849289, "avg_cost": 57.992595192718504, "sleeve": "residual", "stop": null, "entry_session": "2026-10-07", "max_hold_until": null}, "IBIT": {"qty": 1.045602, "avg_cost": 47.10442022094726, "sleeve": "residual", "stop": null, "entry_session": "2026-10-07", "max_hold_until": null}}');
INSERT INTO "snapshots" VALUES('2026-10-12','2026-10-12T21:34:11Z','20261012T213411Z-ctrend',98.8589703856493,1.49505082950840062e+00,97.3639195561409,1.00230179953994991e+02,100.0,100.201609896319,1.33993806293029038e-02,'TREND','{"peak": 100.201609896319, "pause_until": null, "halt_until": null, "drawdown": 0.013399380629302904}','{"marks": {"ETHA": 56.95000076293945, "IBIT": 46.86000061035156}, "flags": {}}','{"ETHA": {"qty": 0.849289, "avg_cost": 57.992595192718504, "sleeve": "residual", "stop": null, "entry_session": "2026-10-07", "max_hold_until": null}, "IBIT": {"qty": 1.045602, "avg_cost": 47.10442022094726, "sleeve": "residual", "stop": null, "entry_session": "2026-10-07", "max_hold_until": null}}');
INSERT INTO "snapshots" VALUES('2026-10-13','2026-10-13T23:28:33Z','20261013T232833Z-ctrend',9.89119749855142487e+01,1.49505082950840062e+00,9.7416924156005848e+01,1.00218591095695842e+02,100.0,100.201609896319,1.2870401105722462e-02,'TREND','{"peak": 100.201609896319, "pause_until": null, "halt_until": null, "drawdown": 0.012870401105722462}','{"marks": {"ETHA": 56.68000030517578, "IBIT": 47.130001068115234}, "flags": {}}','{"ETHA": {"qty": 0.849289, "avg_cost": 57.992595192718504, "sleeve": "residual", "stop": null, "entry_session": "2026-10-07", "max_hold_until": null}, "IBIT": {"qty": 1.045602, "avg_cost": 47.10442022094726, "sleeve": "residual", "stop": null, "entry_session": "2026-10-07", "max_hold_until": null}}');
INSERT INTO "snapshots" VALUES('2026-10-14','2026-10-14T21:18:10Z','20261014T211810Z-ctrend',9.64611617561517675e+01,1.49505082950840062e+00,9.49661109266433669e+01,9.91352608480441119e+01,100.0,100.201609896319,3.73292219959097115e-02,'TREND','{"peak": 100.201609896319, "pause_until": null, "halt_until": null, "drawdown": 0.03732922199590971}','{"marks": {"ETHA": 54.88999938964844, "IBIT": 46.2400016784668}, "flags": {}}','{"ETHA": {"qty": 0.849289, "avg_cost": 57.992595192718504, "sleeve": "residual", "stop": null, "entry_session": "2026-10-07", "max_hold_until": null}, "IBIT": {"qty": 1.045602, "avg_cost": 47.10442022094726, "sleeve": "residual", "stop": null, "entry_session": "2026-10-07", "max_hold_until": null}}');
INSERT INTO "snapshots" VALUES('2026-10-15','2026-10-15T20:33:51Z','20261015T203351Z-ctrend',9.72687515294633868e+01,1.49505082950840062e+00,9.57737006999549862e+01,9.94173638498293712e+01,100.0,100.201609896319,2.92695733121485224e-02,'TREND','{"peak": 100.201609896319, "pause_until": null, "halt_until": null, "drawdown": 0.029269573312148522}','{"marks": {"ETHA": 55.40999984741211, "IBIT": 46.59000015258789}, "flags": {}}','{"ETHA": {"qty": 0.849289, "avg_cost": 57.992595192718504, "sleeve": "residual", "stop": null, "entry_session": "2026-10-07", "max_hold_until": null}, "IBIT": {"qty": 1.045602, "avg_cost": 47.10442022094726, "sleeve": "residual", "stop": null, "entry_session": "2026-10-07", "max_hold_until": null}}');
INSERT INTO "snapshots" VALUES('2026-10-16','2026-10-16T22:48:18Z','20261016T224818Z-ctrend',9.60443266894670415e+01,1.49505082950840062e+00,9.45492758599586409e+01,9.83172950137659143e+01,100.0,100.201609896319,4.14891857641169759e-02,'TREND','{"peak": 100.201609896319, "pause_until": null, "halt_until": null, "drawdown": 0.041489185764116976}','{"marks": {"ETHA": 54.5099983215332, "IBIT": 46.150001525878906}, "flags": {}}','{"ETHA": {"qty": 0.849289, "avg_cost": 57.992595192718504, "sleeve": "residual", "stop": null, "entry_session": "2026-10-07", "max_hold_until": null}, "IBIT": {"qty": 1.045602, "avg_cost": 47.10442022094726, "sleeve": "residual", "stop": null, "entry_session": "2026-10-07", "max_hold_until": null}}');
INSERT INTO "snapshots" VALUES('2026-10-19','2026-10-19T22:55:19Z','20261019T225519Z-ctrend',9.60061050554008517e+01,1.11879878905106089e+00,94.8873062663498,9.87333617581285665e+01,100.0,100.201609896319,4.18706330692624195e-02,'TREND','{"peak": 100.201609896319, "pause_until": null, "halt_until": null, "drawdown": 0.04187063306926242}','{"marks": {"ETHA": 54.11000061035156, "IBIT": 46.29999923706055, "SHY": 81.30999755859375}, "flags": {}}','{"ETHA": {"qty": 0.581446, "avg_cost": 57.992595192718504, "sleeve": "residual", "stop": null, "entry_session": "2026-10-07", "max_hold_until": null}, "IBIT": {"qty": 1.045602, "avg_cost": 47.10442022094726, "sleeve": "residual", "stop": null, "entry_session": "2026-10-07", "max_hold_until": null}, "SHY": {"qty": 0.18465, "avg_cost": 81.39693433532715, "sleeve": "residual", "stop": null, "entry_session": "2026-10-19", "max_hold_until": null}}');
INSERT INTO "snapshots" VALUES('2026-10-20','2026-10-20T21:15:41Z','20261020T211541Z-ctrend',9.69911438578376845e+01,1.11879878905106089e+00,9.58723450687866289e+01,9.90644147136251405e+01,100.0,100.201609896319,3.20400644441067861e-02,'TREND','{"peak": 100.201609896319, "pause_until": null, "halt_until": null, "drawdown": 0.032040064444106786}','{"marks": {"ETHA": 55.06999969482422, "IBIT": 46.709999084472656, "SHY": 81.30000305175781}, "flags": {}}','{"ETHA": {"qty": 0.581446, "avg_cost": 57.992595192718504, "sleeve": "residual", "stop": null, "entry_session": "2026-10-07", "max_hold_until": null}, "IBIT": {"qty": 1.045602, "avg_cost": 47.10442022094726, "sleeve": "residual", "stop": null, "entry_session": "2026-10-07", "max_hold_until": null}, "SHY": {"qty": 0.18465, "avg_cost": 81.39693433532715, "sleeve": "residual", "stop": null, "entry_session": "2026-10-19", "max_hold_until": null}}');
INSERT INTO "snapshots" VALUES('2026-10-21','2026-10-21T21:16:17Z','20261021T211617Z-ctrend',9.89615952550926181e+01,1.11879878905106089e+00,9.78427964660415625e+01,9.95848283557803313e+01,100.0,100.201609896319,1.23751967908445337e-02,'TREND','{"peak": 100.201609896319, "pause_until": null, "halt_until": null, "drawdown": 0.012375196790844534}','{"marks": {"ETHA": 56.43000030517578, "IBIT": 47.84000015258789, "SHY": 81.29000091552734}, "flags": {}}','{"ETHA": {"qty": 0.581446, "avg_cost": 57.992595192718504, "sleeve": "residual", "stop": null, "entry_session": "2026-10-07", "max_hold_until": null}, "IBIT": {"qty": 1.045602, "avg_cost": 47.10442022094726, "sleeve": "residual", "stop": null, "entry_session": "2026-10-07", "max_hold_until": null}, "SHY": {"qty": 0.18465, "avg_cost": 81.39693433532715, "sleeve": "residual", "stop": null, "entry_session": "2026-10-19", "max_hold_until": null}}');
INSERT INTO "snapshots" VALUES('2026-10-22','2026-10-22T21:12:58Z','20261022T211258Z-ctrend',9.56602068261604188e+01,1.11879878905106089e+00,9.45414080371093632e+01,9.84087557930019443e+01,100.0,100.201609896319,4.53226557423346276e-02,'TREND','{"peak": 100.201609896319, "pause_until": null, "halt_until": null, "drawdown": 0.04532265574233463}','{"marks": {"ETHA": 53.880001068115234, "IBIT": 46.060001373291016, "SHY": 81.5199966430664}, "flags": {}}','{"ETHA": {"qty": 0.581446, "avg_cost": 57.992595192718504, "sleeve": "residual", "stop": null, "entry_session": "2026-10-07", "max_hold_until": null}, "IBIT": {"qty": 1.045602, "avg_cost": 47.10442022094726, "sleeve": "residual", "stop": null, "entry_session": "2026-10-07", "max_hold_until": null}, "SHY": {"qty": 0.18465, "avg_cost": 81.39693433532715, "sleeve": "residual", "stop": null, "entry_session": "2026-10-19", "max_hold_until": null}}');
CREATE TABLE state (key TEXT PRIMARY KEY, value TEXT NOT NULL, updated_at TEXT NOT NULL);
INSERT INTO "state" VALUES('cash','1.118798789051061','2026-10-22T21:13:11Z');
INSERT INTO "state" VALUES('strategy_integrity_ok','true','2026-10-23T16:51:55Z');
INSERT INTO "state" VALUES('benchmark','{"ticker": "SPY", "qty": 0.12881401246480959, "entry_price": 776.3130585449218, "entry_session": "2026-10-07", "div_cash": 0.0, "note": "SPY bought at the first session''s official open with the same cost model"}','2026-10-07T15:27:53Z');
INSERT INTO "state" VALUES('open_done:2026-10-07','true','2026-10-07T15:27:53Z');
INSERT INTO "state" VALUES('live_marks','{"as_of": "2026-10-22T17:52:08Z", "marks": {"IBIT": [45.92499923706055, "2026-10-22T13:45:00-04:00"], "ETHA": [53.755001068115234, "2026-10-22T13:45:00-04:00"], "SHY": [81.52179718017578, "2026-10-22T13:45:00-04:00"]}}','2026-10-22T17:52:17Z');
INSERT INTO "state" VALUES('last_regime','"TREND"','2026-10-21T21:18:24Z');
INSERT INTO "state" VALUES('risk','{"peak": 100.201609896319, "pause_until": null, "halt_until": null, "drawdown": 0.04532265574233463}','2026-10-22T21:13:11Z');
INSERT INTO "state" VALUES('last_closed_session','"2026-10-22"','2026-10-22T21:13:11Z');
INSERT INTO "state" VALUES('open_done:2026-10-08','true','2026-10-08T15:53:16Z');
INSERT INTO "state" VALUES('open_done:2026-10-09','true','2026-10-09T15:35:59Z');
INSERT INTO "state" VALUES('open_done:2026-10-12','true','2026-10-12T16:06:15Z');
INSERT INTO "state" VALUES('open_done:2026-10-13','true','2026-10-13T17:49:43Z');
INSERT INTO "state" VALUES('open_done:2026-10-14','true','2026-10-14T15:29:59Z');
INSERT INTO "state" VALUES('open_done:2026-10-15','true','2026-10-15T15:21:17Z');
INSERT INTO "state" VALUES('open_done:2026-10-16','true','2026-10-16T15:01:48Z');
INSERT INTO "state" VALUES('open_done:2026-10-19','true','2026-10-19T14:59:53Z');
INSERT INTO "state" VALUES('open_done:2026-10-20','true','2026-10-20T15:23:48Z');
INSERT INTO "state" VALUES('open_done:2026-10-21','true','2026-10-21T15:37:53Z');
INSERT INTO "state" VALUES('open_done:2026-10-22','true','2026-10-22T15:39:47Z');
INSERT INTO "state" VALUES('experiment_finished','"2026-10-22T21:12:58Z"','2026-10-22T21:13:15Z');
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
INSERT INTO "sqlite_sequence" VALUES('events',42);
INSERT INTO "sqlite_sequence" VALUES('data_issues',2);
INSERT INTO "sqlite_sequence" VALUES('decisions',16);
INSERT INTO "sqlite_sequence" VALUES('fills',4);
COMMIT;
