from papertrader import crosscheck as X


def _binance(n, off_bp=0.0):
    return {60 * i: (100.0, 100.0 * (1 + off_bp / 1e4)) for i in range(n)}


def test_parse_coinbase_keeps_aligned_positive_closes():
    assert X.parse_coinbase([[120, 1, 2, 1, 1.5, 3], [121, 1, 2, 1, 1.5, 3], [180, 1, 2, 1, 0, 3]]) == {120: 1.5}


def test_small_basis_is_ok_and_large_gap_is_flagged():
    other = {60 * i: 100.0 for i in range(30)}
    assert X.compare(_binance(30, 3.0), other)["ok"] is True
    assert X.compare(_binance(30, 40.0), other)["ok"] is False


def test_too_little_overlap_is_inconclusive():
    r = X.compare(_binance(5), {60 * i: 100.0 for i in range(5)})
    assert r["ok"] is None


def test_unknown_symbol_is_skipped_and_check_uses_given_getter():
    assert X.check("DOGEUSDT", {}, lambda *a, **k: []) is None
    rows = [[60 * i, 1, 2, 1, 100.0, 1] for i in range(30)]
    assert X.check("BTCUSDT", _binance(30), lambda url, **k: rows)["ok"] is True


def test_engine_crosscheck_errors_are_swallowed(monkeypatch):
    from papertrader.pm_engine2 import PMEngine2
    eng = PMEngine2.__new__(PMEngine2)
    eng.get = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("down"))
    eng._shadow_crosscheck("BTCUSDT", {})  # must not raise
