import datetime as dt
import json
import sqlite3
from types import SimpleNamespace as NS

from papertrader import jev_news as J

NOW = dt.datetime(2026, 10, 12, 20, 0, tzinfo=dt.timezone.utc)


def _ledger(root, n):
    (root / "data").mkdir(exist_ok=True)
    (root / "state").mkdir(exist_ok=True)
    con = sqlite3.connect(root / "data" / "ledger_x.sqlite")
    con.execute("CREATE TABLE news (news_id INTEGER PRIMARY KEY, uid TEXT UNIQUE, ticker TEXT, source TEXT, provider TEXT, title TEXT, url TEXT, "
                "published_at TEXT, retrieved_at TEXT, categories TEXT, matched TEXT)")
    for i in range(n):
        con.execute("INSERT INTO news(uid,ticker,source,provider,title,published_at,retrieved_at,categories,matched) VALUES (?,?,?,?,?,?,?,?,?)",
                    (f"u{i}", "ACME", "s", "p", f"headline {i}", "2026-10-12T18:00:00Z", "2026-10-12T18:05:00Z", "[]", "[]"))
    con.commit()
    con.close()


class FakeClient:
    calls = 0
    fail = False

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def system_one(self, state, questions):
        type(self).calls += 1
        if type(self).fail:
            raise RuntimeError("quota")
        return NS(nouls={k: NS(noul=0.1) for k in ("material_adverse", "material_positive", "price_move_only")}, choices={"tone": NS(choice="neutral")})


def _setup(monkeypatch):
    FakeClient.calls, FakeClient.fail = 0, False
    monkeypatch.setattr(J, "questions", lambda: {})


def test_reviews_each_headline_once_and_writes_shadow_log(tmp_path, monkeypatch):
    _setup(monkeypatch)
    _ledger(tmp_path, 3)
    s = J.run(tmp_path, NOW, FakeClient)
    assert s["state"] == "done" and s["reviewed_now"] == 3 and "never gates" in s["role"]
    lines = [json.loads(x) for x in (tmp_path / J.OUT).read_text().splitlines()]
    assert len(lines) == 3 and lines[0]["tone"] == "neutral" and lines[0]["material_adverse"] == 0.1
    assert J.run(tmp_path, NOW, FakeClient)["state"] == "idle" and FakeClient.calls == 3


def test_per_run_cap_and_stops_after_repeated_errors_without_raising(tmp_path, monkeypatch):
    _setup(monkeypatch)
    _ledger(tmp_path, J.MAX_PER_RUN + 10)
    assert J.run(tmp_path, NOW, FakeClient)["reviewed_now"] == J.MAX_PER_RUN
    FakeClient.fail = True
    calls_before = FakeClient.calls
    s = J.run(tmp_path, NOW, FakeClient)
    assert "stopped" in s["state"] and FakeClient.calls - calls_before == J.MAX_CONSECUTIVE_ERRORS and "RuntimeError" in s["last_error"]


def test_missing_key_is_a_quiet_skip(tmp_path, monkeypatch):
    _setup(monkeypatch)
    monkeypatch.delenv("TYPESAFE_API_KEY", raising=False)
    _ledger(tmp_path, 1)
    assert J.run(tmp_path, NOW)["state"] == "skipped" and not (tmp_path / J.OUT).exists()


def test_internal_failure_is_recorded_not_raised(tmp_path, monkeypatch):
    _setup(monkeypatch)
    monkeypatch.setattr(J, "load_news", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom")))
    (tmp_path / "state").mkdir()
    s = J.run(tmp_path, NOW, FakeClient)
    assert s["state"] == "error" and json.loads((tmp_path / J.STATUS).read_text())["state"] == "error"
