import datetime as dt

from papertrader import jev_calibration as jc

T0 = dt.datetime(2026, 10, 12, 13, 30, tzinfo=dt.timezone.utc)


def _bars(spec):
    """spec: [(high, low, close)] one per minute."""
    return [(T0 + dt.timedelta(minutes=i), h, lo, c) for i, (h, lo, c) in enumerate(spec)]


def test_outcome_target_first_stop_first_and_ambiguous():
    flat = (100.0, 100.0, 100.0)
    up = _bars([flat, (100.31, 100.0, 100.2), flat, flat])
    assert jc.outcome(up, 0, 0.30, 0.25, 2) == 1
    down = _bars([flat, (100.0, 99.7, 99.8), (100.5, 100.0, 100.4), flat])
    assert jc.outcome(down, 0, 0.30, 0.25, 2) == 0           # stop comes first
    both = _bars([flat, (100.4, 99.7, 100.0), flat, flat])
    assert jc.outcome(both, 0, 0.30, 0.25, 2) == 0           # same bar touches both: assume the stop
    assert jc.outcome(up, 2, 0.30, 0.25, 2) is None          # window runs past the data


def test_score_and_correlation_detects_skill_and_no_skill():
    flat = (100.0, 100.0, 100.0)
    # bar 0 is followed by a +0.31% bar (hit), bar 4 by nothing (miss)
    bars = {"AAA": _bars([flat, (100.31, 100.0, 100.0), flat, flat, flat, flat, flat, flat, flat])}
    calls = [{"ticker": "AAA", "bar": (T0).isoformat(), "p": 0.7}, {"ticker": "AAA", "bar": (T0 + dt.timedelta(minutes=4)).isoformat(), "p": 0.3},
             {"ticker": "AAA", "bar": (T0 + dt.timedelta(minutes=5)).isoformat(), "p": 0.4}]
    s = jc.score_session(calls, bars, 0.30, 0.25, 2)
    assert s["n"] == 3 and s["sum_o"] == 1
    assert abs(s["sum_p"] - 1.4) < 1e-9
    assert jc.correlation(s) > 0.9                           # the high-p call was the hit
    assert s["base_n"] > 0 and 0 < s["base_hits"] < s["base_n"]
    # high p on the miss and low p on the hit gives a negative correlation
    calls2 = [{"ticker": "AAA", "bar": (T0).isoformat(), "p": 0.3}, {"ticker": "AAA", "bar": (T0 + dt.timedelta(minutes=4)).isoformat(), "p": 0.7},
              {"ticker": "AAA", "bar": (T0 + dt.timedelta(minutes=5)).isoformat(), "p": 0.6}]
    assert jc.correlation(jc.score_session(calls2, bars, 0.30, 0.25, 2)) < -0.5


def test_merge_record_and_render(tmp_path):
    (tmp_path / "state").mkdir()
    s1 = {"n": 4, "sum_p": 2.0, "sum_o": 1, "sum_pp": 1.1, "sum_po": 0.6, "base_n": 100, "base_hits": 8, "buckets": {"0.42-0.46": [4, 1]}}
    s2 = {"n": 6, "sum_p": 3.0, "sum_o": 0, "sum_pp": 1.6, "sum_po": 0.0, "base_n": 100, "base_hits": 6, "buckets": {"0.42-0.46": [2, 0], "0.50-1.00": [4, 0]}}
    jc.record(tmp_path, "2026-10-12", s1)
    jc.record(tmp_path, "2026-10-13", s2)
    jc.record(tmp_path, "2026-10-12", s1)                    # re-recording a session replaces it, never double counts
    cum = jc.totals(tmp_path)
    assert cum["n"] == 10 and cum["base_n"] == 200 and cum["buckets"]["0.42-0.46"] == [6, 1]
    text = "\n".join(jc.render(s2, cum))
    assert "Scored calls so far: 10" in text
    assert "Today alone: 6 calls" in text


def test_run_for_day_uses_logged_calls_only_for_that_session(tmp_path):
    (tmp_path / "state").mkdir()
    flat = (100.0, 100.0, 100.0)
    bars = {"AAA": _bars([flat, (100.31, 100.0, 100.0), flat, flat, flat, flat])}
    log = [{"session": "2026-10-12", "ticker": "AAA", "bar": T0.isoformat(), "p": 0.5},
           {"session": "2026-10-09", "ticker": "AAA", "bar": T0.isoformat(), "p": 0.9}]
    (tmp_path / "state/speed_calls.jsonl").write_text("".join(__import__("json").dumps(r) + "\n" for r in log))
    out = jc.run_for_day(dt.date(2026, 10, 12), 0.30, 0.25, 2, root=tmp_path, bars=bars)
    assert out["n"] == 1 and out["sum_o"] == 1
    assert jc.run_for_day(dt.date(2026, 10, 11), 0.30, 0.25, 2, root=tmp_path, bars=bars) is None
