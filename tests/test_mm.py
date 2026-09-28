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


def test_complementary_buy_counts_and_sweeps_are_volume_limited():
    t = [{"timestamp": 1100, "side": "BUY", "outcome": "Down", "price": 0.54, "size": 130}]  # 1 - 0.46 = 0.54
    assert simulate_fill(order(), t) == 20
    t = [{"timestamp": 1100, "side": "SELL", "outcome": "Up", "price": 0.44, "size": 1}]  # traded through our price
    assert simulate_fill(order(), t) == 1


def test_ignores_trades_before_placement_after_expiry_and_on_the_wrong_side():
    t = [{"timestamp": 900, "side": "SELL", "outcome": "Up", "price": 0.40, "size": 999},
         {"timestamp": 1400, "side": "SELL", "outcome": "Up", "price": 0.40, "size": 999},
         {"timestamp": 1100, "side": "BUY", "outcome": "Up", "price": 0.46, "size": 999},
         {"timestamp": 1100, "side": "SELL", "outcome": "Up", "price": 0.47, "size": 999}]
    assert simulate_fill(order(), t) == 0


def test_tiny_trade_through_cannot_fill_more_shares_than_traded():
    tape = [{'timestamp': 1100, 'side': 'SELL', 'outcome': 'Up', 'price': .44, 'size': 1}]
    assert simulate_fill(order(), tape) == 1


def test_inventory_completion_uses_actual_acquisition_cost():
    from papertrader.mm import plan_quotes
    cfg = load_json(ROOT / 'config/strategy_mm_v1.json')
    cfg['sizing'].update(max_open_markets=1, max_market_loss_fraction=.03, max_open_exposure=.10)
    pos = {'x:Up': {'slug': 'x', 'side': 'Up', 'shares': 5, 'cost': 3.5}}
    # Market moved: current bid sum is .98, but completing old 70c inventory
    # at 60c would lock a 30c LOSS per pair.
    assert plan_quotes('x', {'Up': .38, 'Down': .60}, pos, [], 96.5, 100, 97, cfg) == {}


def test_quotes_require_both_legs_to_fit_cash_and_risk_budget():
    from papertrader.mm import plan_quotes
    cfg = load_json(ROOT / 'config/strategy_mm_v1.json')
    cfg['sizing'].update(max_open_markets=1, max_market_loss_fraction=.03, max_open_exposure=.10)
    assert plan_quotes('x', {'Up': .48, 'Down': .50}, {}, [], 3, 100, 0, cfg) == {}
    plan = plan_quotes('x', {'Up': .48, 'Down': .50}, {}, [], 100, 100, 97, cfg)
    assert set(plan) == {'Up', 'Down'} and plan['Up'] == plan['Down']
    assert max(plan[s] * p for s,p in {'Up': .48, 'Down': .50}.items()) <= 3 + 1e-8
    assert plan_quotes('x', {'Up': .48, 'Down': .50}, {}, [], 100, 100, 99, cfg) == {}


def test_outstanding_inventory_and_quotes_consume_exposure():
    from papertrader.mm import plan_quotes
    cfg = load_json(ROOT / 'config/strategy_mm_v1.json')
    cfg['sizing'].update(max_open_markets=1, max_market_loss_fraction=.03, max_open_exposure=.10)
    pos = {'y:Up': {'slug': 'y', 'side': 'Up', 'shares': 5, 'cost': 2.5}}
    assert plan_quotes('x', {'Up': .48, 'Down': .50}, pos, [], 97.5, 100, 97, cfg) == {}


def test_rejects_crossed_missing_and_nonfinite_quotes():
    assert quote_prices(.5, .49, .45, .46, CFG) is None
    assert quote_prices(.48, None, .5, .51, CFG) is None
    assert quote_prices(float('nan'), .49, .5, .51, CFG) is None
