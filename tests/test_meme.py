import datetime as dt

from papertrader import meme
from papertrader.config import ROOT, UNIVERSE_PATH, load_json, sha256_file
from papertrader.ledger import Ledger
from papertrader.meme_engine import DEX, GECKO, MemeEngine

CFG = load_json(ROOT / "config" / "strategy_meme_v1.json")
NOW = dt.datetime(2026, 10, 13, 15, 0, tzinfo=dt.timezone.utc)
TOK = "TokenAAAA11111111111111111111111111111111111"


def pair(price=0.0010, liq=120_000, h1=25.0, m5=1.0, h6=10.0, h24=60.0, buys=500, sells=300, age_h=30, vol=400_000):
    return {"chainId": "solana", "dexId": "pumpswap", "pairAddress": "PairAAAA", "baseToken": {"address": TOK, "symbol": "AAA"},
            "priceUsd": str(price), "liquidity": {"usd": liq}, "volume": {"h24": vol, "h1": vol / 10},
            "txns": {"h1": {"buys": buys, "sells": sells}, "m5": {"buys": 50, "sells": 30}},
            "priceChange": {"m5": m5, "h1": h1, "h6": h6, "h24": h24}, "pairCreatedAt": int((NOW.timestamp() - age_h * 3600) * 1000)}


def make_fetch(state):
    def fetch(url, **params):
        if url.startswith(f"{GECKO}/networks/solana/trending_pools"):
            return {"data": [{"relationships": {"base_token": {"data": {"id": "solana_" + TOK}}}}]}
        if url.endswith("token-boosts/latest/v1") or url.endswith("token-profiles/latest/v1"):
            return []
        if url.startswith(f"{DEX}/latest/dex/tokens/"):
            return {"pairs": [state["pair"]] if state.get("pair") else []}
        if "rugcheck" in url:
            return state.get("rug", {"score": 1, "score_normalised": 1, "risks": [], "lpLockedPct": 100})
        raise RuntimeError("unexpected " + url)
    return fetch


def engine(tmp_path, state, now=NOW, cfg=CFG):
    exp = {"name": "x", "start_date": "2026-10-13", "end_date": "2026-10-22", "starting_cash": 100.0, "report_days": [7]}
    book = {"id": "meme", "name": "m", "subtitle": "m", "strategy": "config/strategy_meme_v1.json", "ledger": "x", "start_date": "2026-10-13"}
    L = Ledger(tmp_path / "l.sqlite")
    if not L.experiment():
        L.freeze(exp, book, cfg["version"], sha256_file(ROOT / "config" / "strategy_meme_v1.json"), sha256_file(UNIVERSE_PATH))
    L.start_run("r" + now.isoformat(), "t")
    return MemeEngine(L, None, cfg, {**exp, "book": "meme"}, now, fetch=make_fetch(state)), L


def reconciles(L):
    buys = L.db.execute("SELECT COALESCE(SUM(qty*fill_price),0) s FROM fills WHERE side='BUY'").fetchone()["s"]
    sells = L.db.execute("SELECT COALESCE(SUM(qty*fill_price),0) s FROM fills WHERE side='SELL'").fetchone()["s"]
    return abs(100.0 - buys + sells - L.get_state("cash", 100.0)) < 1e-9


def test_screen_and_entry_rules():
    p = meme.pool_from_pair(pair(), trending_rank=3)
    assert meme.screen(p, NOW, CFG) is None and meme.entry_signal(p, CFG) is None
    assert "liquidity" in meme.screen(meme.pool_from_pair(pair(liq=20_000), trending_rank=3), NOW, CFG)
    assert "age" in meme.screen(meme.pool_from_pair(pair(age_h=1), trending_rank=3), NOW, CFG)
    assert "no X link" in meme.screen(meme.pool_from_pair(pair()), NOW, CFG)
    assert meme.screen(meme.pool_from_pair(pair(), social=True), NOW, CFG) is None
    assert "blow-off" in meme.entry_signal(meme.pool_from_pair(pair(h24=2000), trending_rank=1), CFG)
    assert "fading" in meme.entry_signal(meme.pool_from_pair(pair(m5=-6), trending_rank=1), CFG)
    assert "buys" in meme.entry_signal(meme.pool_from_pair(pair(buys=300, sells=300), trending_rank=1), CFG)
    assert meme.entry_signal(meme.pool_from_pair(pair(h1=90), trending_rank=1), CFG)


def test_friction_is_charged_against_us_and_stops_cost_more():
    assert meme.friction("BUY", 5, 100_000, CFG) > CFG["friction"]["fee"] + CFG["friction"]["entry_latency"]
    assert meme.friction("SELL", 5, 100_000, CFG, "STOP") > meme.friction("SELL", 5, 100_000, CFG, "TAKE_PROFIT")
    assert meme.friction("BUY", 5, 5_000, CFG) > meme.friction("BUY", 5, 500_000, CFG)  # thin pools cost more


def test_rug_check_refuses_danger_unknown_and_high_scores():
    assert meme.rug_ok({"score_normalised": 1, "risks": []}, CFG)[0]
    assert not meme.rug_ok(None, CFG)[0]
    assert not meme.rug_ok({"score_normalised": 5, "risks": [{"name": "Large Amount of LP Unlocked", "level": "danger"}]}, CFG)[0]
    assert not meme.rug_ok({"score_normalised": 55, "risks": []}, CFG)[0]


def test_enter_then_stop_out_reconciles_cash_and_blocks_reentry(tmp_path):
    state = {"pair": pair()}
    e, L = engine(tmp_path, state)
    assert "bought AAA" in e.step()
    buy = dict(L.db.execute("SELECT * FROM fills").fetchone())
    assert buy["side"] == "BUY" and buy["fill_price"] > buy["ref_price"] and abs(buy["qty"] * buy["fill_price"] - 5.0) < 1e-9
    state["pair"] = pair(price=0.0007)                       # -30%: through the 18% stop
    e2 = MemeEngine(L, None, CFG, {"book": "meme", "start_date": "2026-10-13"}, NOW + dt.timedelta(minutes=15), fetch=make_fetch(state))
    out = e2.step()
    assert "STOP" in out
    sell = dict(L.db.execute("SELECT * FROM fills WHERE side='SELL'").fetchone())
    assert sell["reason_code"] == "STOP" and sell["fill_price"] < 0.0007 and sell["realized_pnl"] < 0   # gap-through plus stop slippage, not the trigger price
    assert reconciles(L)
    state["pair"] = pair()                                    # looks good again, but the token is in its cool-down
    e3 = MemeEngine(L, None, CFG, {"book": "meme", "start_date": "2026-10-13"}, NOW + dt.timedelta(minutes=30), fetch=make_fetch(state))
    assert "bought" not in e3.step()
    assert L.db.execute("SELECT COUNT(*) n FROM fills WHERE side='BUY'").fetchone()["n"] == 1


def test_unknown_rug_status_means_no_trade_and_missing_pool_is_written_off(tmp_path):
    state = {"pair": pair(), "rug": {"score_normalised": 40, "risks": []}}
    e, L = engine(tmp_path, state)
    assert "bought" not in e.step() and not L.db.execute("SELECT 1 FROM fills").fetchone()
    state["rug"] = {"score_normalised": 1, "risks": []}
    e.now = NOW + dt.timedelta(hours=7)                      # past the 6h rug-check cache so the new answer is used
    e.session = e.now.astimezone(dt.timezone.utc).date().isoformat()
    assert "bought AAA" in e.step()
    state["pair"] = None                                      # pool vanishes
    for i in range(3):
        MemeEngine(L, None, CFG, {"book": "meme"}, NOW + dt.timedelta(hours=8 + i), fetch=make_fetch(state)).step()
    sell = dict(L.db.execute("SELECT * FROM fills WHERE side='SELL'").fetchone())
    assert sell["reason_code"] == "WRITE_OFF" and sell["fill_price"] == 0.0 and abs(sell["realized_pnl"] + 5.0) < 0.01
    assert reconciles(L) and L.verify_chain()[0]


def test_experiment_end_liquidates_everything(tmp_path):
    state = {"pair": pair()}
    e, L = engine(tmp_path, state)
    e.step()
    end = dt.datetime(2026, 10, 22, 12, 0, tzinfo=dt.timezone.utc)
    MemeEngine(L, None, CFG, {"book": "meme"}, end, fetch=make_fetch(state)).step()
    assert L.db.execute("SELECT reason_code FROM fills WHERE side='SELL'").fetchone()["reason_code"] == "END_OF_EXPERIMENT"
    assert not (L.get_state("meme_positions") or {})
