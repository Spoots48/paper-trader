"""Research only: is the fair-value model better calibrated than Polymarket's own prices?

For settled Up/Down windows over the last few days, rebuild what the model would have said at each point
where Polymarket's price history has a sample (~10-minute spacing), using only exchange candles up to that
time. Compare Brier scores (model vs market) and simulate the bets the frozen rules would have made.
Limitation: the history gives last-trade/mid prices, not asks; a 1-cent half-spread is added as the entry price.
"""
from __future__ import annotations

import datetime as dt
import json
import math
import sys
import time

import requests

from .config import RESEARCH_DIR, ROOT, load_json
from .nyse_calendar import ET, UTC
from .predmarket import fair_prob_up, kelly_budget, taker_fee_per_share

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


def candles(product: str, start: int, end: int) -> dict[int, tuple[float, float]]:
    out = {}
    t = start
    while t < end:
        e = min(t + 299 * 60, end)
        c = get(f"https://api.exchange.coinbase.com/products/{product}/candles", granularity=60,
                start=dt.datetime.fromtimestamp(t, UTC).isoformat(), end=dt.datetime.fromtimestamp(e, UTC).isoformat()) or []
        for r in c:
            out[int(r[0])] = (float(r[3]), float(r[4]))  # open, close
        t = e + 60
        time.sleep(0.25)
    return out


def hourly_slug(asset: dict, start_utc: dt.datetime) -> list[str]:
    et = start_utc.astimezone(ET)
    h = et.hour % 12 or 12
    base = f"{asset['long']}-up-or-down-{et.strftime('%B').lower()}-{et.day}-{et.year}-{h}{'am' if et.hour < 12 else 'pm'}"
    return [base + "-et", base]


def main(days: float = 3.0) -> dict:
    cfg = load_json(ROOT / "config" / "strategy_pm_v1.json")
    M, rate = cfg["model"], cfg["fees"]["crypto_taker_fee_rate"]
    now = int(time.time())
    t_end = now - 3600
    t_start = t_end - int(days * 86400)
    rows = []
    plan = [("BTC", 15), ("ETH", 15), ("BTC", 60), ("ETH", 60), ("SOL", 60), ("XRP", 60), ("DOGE", 60),
            ("BTC", 240), ("ETH", 240), ("SOL", 240), ("XRP", 240), ("DOGE", 240)]
    cache: dict[str, dict] = {}
    for name, minutes in plan:
        asset = cfg["markets"]["assets"][name]
        if name not in cache:
            cache[name] = candles(asset["coinbase"], t_start - 7200, t_end + 3600)
        cs = cache[name]
        step = minutes * 60
        for w0 in range((t_start // step + 1) * step, t_end - step, step):
            s_utc = dt.datetime.fromtimestamp(w0, UTC)
            slugs = hourly_slug(asset, s_utc) if minutes == 60 else [f"{asset['short']}-updown-{ {15: '15m', 240: '4h'}[minutes]}-{w0}"]
            ev = None
            for sl in slugs:
                r = get("https://gamma-api.polymarket.com/events", slug=sl)
                if r:
                    ev = r[0]
                    break
            if not ev or not ev.get("markets"):
                continue
            m = ev["markets"][0]
            try:
                outs, px, toks = json.loads(m["outcomes"]), json.loads(m["outcomePrices"]), json.loads(m["clobTokenIds"])
            except Exception:
                continue
            if max(float(x) for x in px) < 0.99 or "Up" not in outs:
                continue
            up_won = float(px[outs.index("Up")]) >= 0.99
            hist = (get("https://clob.polymarket.com/prices-history", market=toks[outs.index("Up")], interval="max", fidelity=1) or {}).get("history", [])
            w1 = w0 + step
            if w0 not in cs:
                continue
            s0 = cs[w0][0]
            for h in hist:
                t = int(h["t"])
                e = (t - w0) / step
                if not (cfg["markets"]["min_elapsed_fraction"] <= e and t < w1 - cfg["markets"]["min_seconds_remaining"]):
                    continue
                done = [cs[k][1] for k in range(w0, t - 59, 60) if k in cs and k + 60 <= t]
                last_min = (t // 60) * 60 - 60
                if last_min not in cs or not done:
                    continue
                s_now = cs[last_min][1]  # most recent completed minute (conservative: no look-ahead)
                back = [cs[k][1] for k in range(last_min - 60 * M["vol_lookback_minutes"], last_min + 1, 60) if k in cs]
                rets = [math.log(b / a) for a, b in zip(back[:-1], back[1:])]
                sd = (sum((r - sum(rets) / len(rets)) ** 2 for r in rets) / (len(rets) - 1)) ** 0.5 if len(rets) > 5 else 0
                sig = max(sd, M["min_vol_per_minute"])
                ml = (w1 - t) / 60
                avg = sum(done) / len(done)
                buf = s0 * M["basis_buffer_bps"] / 1e4
                p_mid = fair_prob_up(s0, avg, s_now, e, ml, sig)
                p_up = min(fair_prob_up(s0, avg, s_now, e, ml, sig, +buf), M["probability_cap"])
                p_dn = min(1 - fair_prob_up(s0, avg, s_now, e, ml, sig, -buf), M["probability_cap"])
                mkt = float(h["p"])
                rows.append({"asset": name, "window": minutes, "t": t, "elapsed": round(e, 3), "market_up": mkt, "model_up": p_mid,
                             "p_up_cons": p_up, "p_dn_cons": p_dn, "up_won": up_won})
            time.sleep(0.15)
        print(f"{name} {minutes}m: {len(rows)} samples so far", flush=True)
    # scoring
    def brier(key):
        return sum((r[key] - (1.0 if r["up_won"] else 0.0)) ** 2 for r in rows) / max(len(rows), 1)
    # simulated bets under the frozen entry rule (entry = history price + 1c half-spread)
    bets = []
    for r in rows:
        for side, q, price in (("Up", r["p_up_cons"], r["market_up"] + 0.01), ("Down", r["p_dn_cons"], 1 - r["market_up"] + 0.01)):
            if not 0.01 <= price <= 0.99:
                continue
            unit = price + taker_fee_per_share(price, rate)
            if q - unit >= cfg["entry"]["min_edge"]:
                won = r["up_won"] == (side == "Up")
                bets.append({**r, "side": side, "unit": unit, "q": q, "pnl_per_share": (1.0 if won else 0.0) - unit, "won": won})
    by_bucket = {}
    for r in rows:
        b = min(int(r["model_up"] * 10), 9)
        x = by_bucket.setdefault(b, [0, 0, 0.0])
        x[0] += 1
        x[1] += r["up_won"]
        x[2] += r["market_up"]
    res = {
        "note": "Research only. Model vs Polymarket price calibration on settled windows; market price = history sample (not the ask).",
        "period_utc": [dt.datetime.fromtimestamp(t_start, UTC).isoformat(), dt.datetime.fromtimestamp(t_end, UTC).isoformat()],
        "samples": len(rows), "brier_model": brier("model_up"), "brier_market": brier("market_up"),
        "bets": len(bets), "bet_win_rate": sum(b["won"] for b in bets) / len(bets) if bets else None,
        "avg_pnl_per_share": sum(b["pnl_per_share"] for b in bets) / len(bets) if bets else None,
        "avg_cost_per_share": sum(b["unit"] for b in bets) / len(bets) if bets else None,
        "avg_model_prob_on_bets": sum(b["q"] for b in bets) / len(bets) if bets else None,
        "calibration_by_model_decile": {f"{k/10:.1f}-{(k+1)/10:.1f}": {"n": v[0], "actual_up_rate": v[1] / v[0], "avg_market_up": v[2] / v[0]} for k, v in sorted(by_bucket.items())},
        "bets_by_window": {w: {"n": len(bb), "win_rate": sum(b["won"] for b in bb) / len(bb), "avg_pnl_per_share": sum(b["pnl_per_share"] for b in bb) / len(bb)}
                           for w in (15, 60, 240) for bb in [[b for b in bets if b["window"] == w]] if bb},
    }
    RESEARCH_DIR.mkdir(exist_ok=True)
    (RESEARCH_DIR / "pm_calibration.json").write_text(json.dumps({**res, "rows": rows[:5000]}, indent=1, default=str))
    return res


if __name__ == "__main__":
    r = main(float(sys.argv[1]) if len(sys.argv) > 1 else 3.0)
    print(json.dumps(r, indent=1, default=str))
