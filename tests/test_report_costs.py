import json

from papertrader import reporting as R
from papertrader.config import load_experiment


def test_report_costs_come_from_a_book_that_defines_them():
    c = R._stock_costs(load_experiment())
    assert all(k in c for k in R._COST_KEYS)


def test_daytrade_first_does_not_break_cost_lookup(tmp_path, monkeypatch):
    (tmp_path / "a.json").write_text(json.dumps({"costs": {"stock_bps_other": 20.0}}))
    (tmp_path / "b.json").write_text(json.dumps({"costs": {k: 1.0 for k in R._COST_KEYS}}))
    monkeypatch.setattr(R, "ROOT", tmp_path)
    assert R._stock_costs({"books": [{"strategy": "a.json"}, {"strategy": "b.json"}]})["etf_bps"] == 1.0
