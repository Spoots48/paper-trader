import datetime as dt
import json
import sqlite3

import pytest

from papertrader import laya_news as L

NOW = dt.datetime(2026, 9, 28, 20, 0, tzinfo=dt.timezone.utc)


def _ledger(root, rows, name="ledger_x.sqlite"):
    (root / "data").mkdir(exist_ok=True)
    con = sqlite3.connect(root / "data" / name)
    con.execute("CREATE TABLE news (news_id INTEGER PRIMARY KEY AUTOINCREMENT, uid TEXT NOT NULL UNIQUE, ticker TEXT NOT NULL, "
                "source TEXT NOT NULL, provider TEXT, title TEXT NOT NULL, url TEXT, published_at TEXT, retrieved_at TEXT NOT NULL, "
                "categories TEXT, matched TEXT)")
    for uid, pub, ret in rows:
        con.execute("INSERT INTO news(uid,ticker,source,provider,title,published_at,retrieved_at,categories,matched) VALUES(?,?,?,?,?,?,?,?,?)",
                    (uid, "ACME", "s", "p", f"headline {uid}", pub, ret, "[]", "[]"))
    con.commit()
    con.close()


class FakeAgent:
    def __init__(self, low=False):
        self.calls = 0
        self.low = low

    def system_one(self, state, questions, min_confidence):
        self.calls += 1
        a = {"choice": "other", "answer_confidence": 0.9, "probabilities": {"other": 0.9}, "low_confidence": self.low}
        return {"answers": {q: dict(a, choice="neutral" if q == "tone" else "other") for q in questions}}


def test_load_news_rejects_future_old_and_unparseable_and_dedupes(tmp_path):
    ok = ("2026-09-28T18:00:00Z", "2026-09-28T18:05:00Z")
    _ledger(tmp_path, [("ok", *ok), ("future", "2026-09-29T18:00:00Z", "2026-09-28T18:05:00Z"),
                       ("future_ret", "2026-09-28T18:00:00Z", "2026-09-30T00:00:00Z"),
                       ("old", "2026-08-01T00:00:00Z", "2026-08-01T00:00:00Z"), ("bad", "not a date", "2026-09-28T18:05:00Z")])
    _ledger(tmp_path, [("ok", *ok)], name="ledger_y.sqlite")
    rows, skipped = L.load_news(tmp_path, NOW)
    assert [r["uid"] for r in rows] == ["ok"]
    assert skipped == {"future": 2, "old": 1, "unparseable": 1}


def test_load_news_is_read_only(tmp_path):
    _ledger(tmp_path, [("ok", "2026-09-28T18:00:00Z", "2026-09-28T18:05:00Z")])
    before = (tmp_path / "data" / "ledger_x.sqlite").read_bytes()
    L.load_news(tmp_path, NOW)
    assert (tmp_path / "data" / "ledger_x.sqlite").read_bytes() == before


def test_review_runs_once_per_uid_model_and_schema(tmp_path):
    _ledger(tmp_path, [(f"u{i}", "2026-09-28T18:00:00Z", "2026-09-28T18:05:00Z") for i in range(3)])
    agent = FakeAgent()
    st = L.run_review(tmp_path, "m", now=NOW, agent_factory=lambda _: agent)
    assert st["state"] == "done" and st["reviewed_now"] == 3 and agent.calls == 3
    again = FakeAgent()
    st2 = L.run_review(tmp_path, "m", now=NOW, agent_factory=lambda _: again)
    assert st2["state"] == "idle" and again.calls == 0
    lines = (tmp_path / "data" / "laya" / "reviews.jsonl").read_text().splitlines()
    assert len(lines) == 3 and json.loads(lines[0])["model_revision"] == L.MODEL_REVISION
    assert (tmp_path / "data" / "laya" / "latest.md").exists()


def test_idle_run_does_not_load_the_model(tmp_path):
    _ledger(tmp_path, [])
    def boom(_):
        raise AssertionError("model must not load when nothing is pending")
    assert L.run_review(tmp_path, "m", now=NOW, agent_factory=boom)["state"] == "idle"


def test_limit_bounds_work(tmp_path):
    _ledger(tmp_path, [(f"u{i}", "2026-09-28T18:00:00Z", "2026-09-28T18:05:00Z") for i in range(5)])
    agent = FakeAgent()
    assert L.run_review(tmp_path, "m", limit=2, now=NOW, agent_factory=lambda _: agent)["reviewed_now"] == 2


def test_low_confidence_is_an_abstention_not_a_label(tmp_path):
    r = L.classify(FakeAgent(low=True), "h", "T", "p")
    assert r["event"]["label"] is None and r["event"]["abstained"] and r["event"]["top"] == "other"


def test_error_is_recorded_and_raised(tmp_path):
    _ledger(tmp_path, [("u", "2026-09-28T18:00:00Z", "2026-09-28T18:05:00Z")])
    def boom(_):
        raise RuntimeError("no model")
    with pytest.raises(RuntimeError):
        L.run_review(tmp_path, "m", now=NOW, agent_factory=boom)
    assert json.loads((tmp_path / "data" / "laya" / "status.json").read_text())["state"] == "error"


def test_concurrent_run_is_skipped(tmp_path):
    import fcntl
    (tmp_path / "data" / "laya").mkdir(parents=True)
    held = open(tmp_path / "data" / "laya" / ".lock", "w")
    fcntl.flock(held, fcntl.LOCK_EX)
    assert L.run_review(tmp_path, "m", now=NOW, agent_factory=lambda _: FakeAgent())["state"] == "skipped"
    held.close()


def test_evaluate_counts_confident_mistakes(tmp_path):
    p = tmp_path / "set.json"
    p.write_text(json.dumps({"items": [{"id": "1", "ticker": "T", "headline": "h", "event": "other", "tone": "neutral"},
                                       {"id": "2", "ticker": "T", "headline": "h", "event": "material_adverse", "tone": "negative"}]}))
    res = L.evaluate(p, "m", agent_factory=lambda _: FakeAgent())
    assert res["stats"]["event"]["correct"] == 1 and res["stats"]["event"]["confident_wrong"] == 1
    assert res["stats"]["tone"]["accuracy_answered"] == 0.5


def test_trigger_requires_external_home_and_enabled(tmp_path):
    assert L.trigger_background(tmp_path)["launched"] is False
    (tmp_path / "data" / "laya").mkdir(parents=True)
    host = tmp_path / "data" / "laya" / "host.json"
    host.write_text(json.dumps({"enabled": False, "home": "/Volumes/X10 Pro/Paper Trading Sim", "python": "/x", "model_dir": "/y"}))
    assert L.trigger_background(tmp_path)["reason"] == "disabled"
    host.write_text(json.dumps({"enabled": True, "home": "/Volumes/X10 Pro/Paper Trading Sim", "python": "/usr/bin/python3", "model_dir": "/tmp/m"}))
    assert "external" in L.trigger_background(tmp_path)["reason"]
