"""Market maker: quote pricing and honest fill simulation."""
from papertrader.config import ROOT, load_json
from papertrader.mm import quote_prices, simulate_fill

CFG = load_json(ROOT / "config/strategy_mm_v1.json")


def test_quotes_stay_under_a_dollar_and_improve_only_with_room():
    q = quote_prices(0.45, 0.48, 0.50, 0.53, CFG)  # bids sum 0.95 -> improve both by 1c
    assert q["Up"] == 0.46 and q["Down"] == 0.51 and q["Up"] + q["Down"] <= 0.98
    q = quote_prices(0.48, 0.49, 0.50, 0.51, CFG)  # bids sum 0.98 -> join, don't improve
    assert q["Up"] == 0.48 and q["Down"] == 0.50 and not any(q["improved"].values())
    assert quote_prices(0.50, 0.51, 0.49, 0.50, CFG) is None  # 0.99: no room


def order(**kw):
    o = {"outcome": "Up", "price": 0.46, "shares": 20, "queue_ahead": 100, "placed_at": 1000, "expires_at": 1300}
    o.update(kw)
    return o


def test_queue_must_be_consumed_before_we_fill():
    t = [{"timestamp": 1100, "side": "SELL", "outcome": "Up", "price": 0.46, "size": 90}]
    assert simulate_fill(order(), t) == 0  # 90 < 100 queued ahead
    t.append({"timestamp": 1200, "side": "SELL", "outcome": "Up", "price": 0.46, "size": 25})
    assert simulate_fill(order(), t) == 15  # 115 - 100


def test_complementary_buy_counts_and_sweeps_fill_fully():
    t = [{"timestamp": 1100, "side": "BUY", "outcome": "Down", "price": 0.54, "size": 130}]  # 1 - 0.46 = 0.54
    assert simulate_fill(order(), t) == 20
    t = [{"timestamp": 1100, "side": "SELL", "outcome": "Up", "price": 0.44, "size": 1}]  # traded through our price
    assert simulate_fill(order(), t) == 20


def test_ignores_trades_before_placement_after_expiry_and_on_the_wrong_side():
    t = [{"timestamp": 900, "side": "SELL", "outcome": "Up", "price": 0.40, "size": 999},
         {"timestamp": 1400, "side": "SELL", "outcome": "Up", "price": 0.40, "size": 999},
         {"timestamp": 1100, "side": "BUY", "outcome": "Up", "price": 0.46, "size": 999},
         {"timestamp": 1100, "side": "SELL", "outcome": "Up", "price": 0.47, "size": 999}]
    assert simulate_fill(order(), t) == 0
