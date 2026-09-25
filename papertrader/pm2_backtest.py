"""Research only: replay the v2 rules on settled BTC/ETH Up/Down markets.

At each Polymarket price-history sample (~10-minute spacing) the model uses only Binance 1-minute candles
completed before that time. Entry price = history price + 1c (history gives last trades, not asks),
Polymarket's crypto taker fee, v2 sizing (3% of equity, one bet per settlement time and direction),
one bet per market, settled on the official outcome. The last 2 days are reported separately.
"""
from __future__ import annotations

import datetime as dt
import json
import sys
import time

import requests

from .config import RESEARCH_DIR, ROOT, load_json
from .nyse_calendar import ET, UTC
from .pm2 import decide_v2, sigma_from_closes

H = {"User-Agent": "Mozilla/5.0 (PaperTradingSim research)"}


def get(url, **p):
    for a in range(4):
        try:
            r = requests.get(url, params=p, headers=H, timeout=20)
            if r.status_code == 200:
                return r.json()
        except Exception:
            pass
        time.sleep(1.5 * (a + 1))
    return None


def klines(symbol: str, start: int, end: int) -> dict[int, tuple[float, float]]:
    out, t = {}, start
    while t < end:
        k = get("https://data-api.binance.vision/api/v3/klines", symbol=symbol, interval="1m", startTime=t * 1000, limit=1000) or []
        if not k:
            break
        for r in k:
            out[int(r[0]) // 1000] = (float(r[1]), float(r[4]))
        t = int(k[-1][0]) // 1000 + 60
        time.sleep(0.2)
    return out


def slug_for(asset: dict, minutes: int, w0: int) -> list[str]:
    if minutes == 60:
        et = dt.datetime.fromtimestamp(w0, UTC).astimezone(ET)
        h = et.hour % 12 or 12
        base = f"{asset['long']}-up-or-down-{et.strftime('%B').lower()}-{et.day}-{et.year}-{h}{'am' if et.hour < 12 else 'pm'}"
        return [base + "-et", base]
    return [f"{asset['short']}-updown-{ {15: '15m', 240: '4h'}[minutes]}-{w0}"]


def main(days: float = 6.0, oos_days: float = 2.0) -> dict:
    cfg = load_json(ROOT / "config" / "strategy_pm_v2.json")
    Mk, M = cfg["markets"], cfg["model"]
    now = int(time.time())
    t_end = now - 1800
    t_start = t_end - int(days * 86400)
    oos_from = t_end - int(oos_days * 86400)
    cands = []  # (t, asset, minutes, w_end, decision, up_won)
    from concurrent.futures import ThreadPoolExecutor

    def fetch_window(args):
        name, asset, minutes, w0 = args
        ev = None
        for sl in slug_for(asset, minutes, w0):
            r = get("https://gamma-api.polymarket.com/events", slug=sl)
            if r:
                ev = r[0]
                break
        if not ev or not ev.get("markets"):
            return None
        m = ev["markets"][0]
        try:
            outs, px, toks = json.loads(m["outcomes"]), json.loads(m["outcomePrices"]), json.loads(m["clobTokenIds"])
        except Exception:
            return None
        if max(float(x) for x in px) < 0.99:
            return None
        hist = (get("https://clob.polymarket.com/prices-history", market=toks[outs.index("Up")], interval="max", fidelity=1) or {}).get("history", [])
        return (name, minutes, w0, float(px[outs.index("Up")]) >= 0.99, hist)

    for name, asset in Mk["assets"].items():
        ks = klines(asset["binance"], t_start - 7200, t_end + 3600)
        print(f"{name}: {len(ks)} candles", flush=True)
        jobs = [(name, asset, minutes, w0) for minutes in Mk["windows_minutes"]
                for w0 in range((t_start // (minutes * 60) + 1) * minutes * 60, t_end - minutes * 60, minutes * 60)]
        with ThreadPoolExecutor(8) as ex:
            got = []
            for i, r in enumerate(ex.map(fetch_window, jobs)):
                if r:
                    got.append(r)
                if i % 100 == 0:
                    print(f"  {name}: fetched {i}/{len(jobs)} windows", flush=True)
        for (_, minutes, w0, up_won, hist) in got:
            if w0 not in ks:
                continue
            step = minutes * 60
            w1 = w0 + step
            s_open = ks[w0][0]
            for h in sorted(hist, key=lambda x: x["t"]):
                t = int(h["t"])
                if not (w0 < t < w1 - Mk["min_seconds_remaining"]):
                    continue
                last = (t // 60) * 60 - 60
                if last not in ks:
                    continue
                closes = [ks[k][1] for k in range(last - 60 * M["vol_lookback_minutes"], last + 1, 60) if k in ks]
                sig = sigma_from_closes(closes, M["min_vol_per_minute"])
                mid = float(h["p"])
                d = decide_v2(s_open, ks[last][1], (w1 - t) / 60, sig, (t - w0) / step,
                              {"Up": min(mid + 0.01, 0.99), "Down": min(1 - mid + 0.01, 0.99)}, mid, cfg)
                if "skip" not in d:
                    cands.append((t, name, minutes, w1, d, up_won))
                    break  # one bet per market
        print(f"{name} done: {len(got)} settled markets, {len(cands)} candidate bets so far", flush=True)
    # simulate sizing and the correlation rule in time order
    cash, open_bets, used, results = 100.0, [], set(), []
    for t, name, minutes, w1, d, up_won in sorted(cands):
        for ob in [b for b in open_bets if b["w1"] <= t]:
            cash += ob["payout"]
            open_bets.remove(ob)
        key = (w1, d["side"])
        if key in used:
            continue
        equity = cash + sum(b["stake"] for b in open_bets)
        stake = min(cfg["sizing"]["per_bet_fraction"] * equity, cfg["sizing"]["max_open_exposure"] * equity - sum(b["stake"] for b in open_bets), cash)
        if stake < d["unit"] * cfg["portfolio"]["min_shares"]:
            continue
        shares = stake / d["unit"]
        won = up_won == (d["side"] == "Up")
        cash -= stake
        used.add(key)
        open_bets.append({"w1": w1, "stake": stake, "payout": shares if won else 0.0})
        results.append({"t": t, "asset": name, "window": minutes, "side": d["side"], "ask": d["ask"], "q": round(d["q"], 3),
                        "model_up": round(d["model_up"], 3), "mid_up": d["mid_up"], "stake": round(stake, 3),
                        "pnl": round((shares if won else 0.0) - stake, 3), "won": won, "oos": t >= oos_from})
    for ob in open_bets:
        cash += ob["payout"]

    def summ(rs):
        if not rs:
            return {"bets": 0}
        st = sum(r["stake"] for r in rs)
        pnl = sum(r["pnl"] for r in rs)
        return {"bets": len(rs), "win_rate": round(sum(r["won"] for r in rs) / len(rs), 3), "staked": round(st, 2),
                "pnl": round(pnl, 2), "return_on_stake": round(pnl / st, 4), "avg_entry": round(sum(r["ask"] for r in rs) / len(rs), 3)}
    res = {"note": "Research only; v2 rules replayed on settled markets; entry = history price + 1c (not true asks).",
           "config_version": cfg["version"], "period_utc": [dt.datetime.fromtimestamp(t_start, UTC).isoformat(), dt.datetime.fromtimestamp(t_end, UTC).isoformat()],
           "ending_equity_from_100": round(cash, 2), "all": summ(results),
           "in_sample": summ([r for r in results if not r["oos"]]), "out_of_sample_last_days": summ([r for r in results if r["oos"]]),
           "by_window": {w: summ([r for r in results if r["window"] == w]) for w in Mk["windows_minutes"]},
           "trades": results}
    RESEARCH_DIR.mkdir(exist_ok=True)
    (RESEARCH_DIR / "pm2_backtest.json").write_text(json.dumps(res, indent=1, default=str))
    return res


if __name__ == "__main__":
    r = main(*(float(x) for x in sys.argv[1:3]))
    print(json.dumps({k: v for k, v in r.items() if k != "trades"}, indent=1, default=str))
