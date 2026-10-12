"""Memecoin rules as pure functions (paper only; no wallet, no keys, no real orders).

Honest scope: reading X/Twitter posts costs money (pay per post), so this book does not read tweets. Its "attention" inputs are free and public:
GeckoTerminal trending pools, DexScreener boosted tokens and token profiles (a profile with an X link is a weak presence check, a boost is paid
promotion by the team), and the pool's own trade counts. Memecoins are the riskiest thing in this project: most lose, many are rugs, and a 15-minute
cycle cannot react the way a bot sitting on the chain can. Fills are therefore modeled pessimistically (see friction) and exits happen at the price seen
on the next run, never at the trigger price. Nothing here is a profit claim."""
from __future__ import annotations

import datetime as dt


def pool_from_pair(p: dict, social: bool = False, trending_rank: int | None = None) -> dict | None:
    """Normalize a DexScreener pair object. Returns None when it lacks a usable price/liquidity."""
    try:
        price = float(p["priceUsd"])
        liq = float((p.get("liquidity") or {}).get("usd") or 0.0)
    except (KeyError, TypeError, ValueError):
        return None
    if price <= 0 or liq <= 0:
        return None
    tx, vol, chg = p.get("txns") or {}, p.get("volume") or {}, p.get("priceChange") or {}

    def n(d, k, f):
        return float((d.get(k) or {}).get(f, 0) or 0) if isinstance(d.get(k), dict) else 0.0

    created = p.get("pairCreatedAt")
    return {"chain": p.get("chainId"), "token": (p.get("baseToken") or {}).get("address"), "symbol": (p.get("baseToken") or {}).get("symbol", "?"),
            "pair": p.get("pairAddress"), "dex": p.get("dexId"), "price": price, "liq": liq,
            "vol_h24": float((vol or {}).get("h24") or 0.0), "vol_h1": float((vol or {}).get("h1") or 0.0),
            "buys_h1": n(tx, "h1", "buys"), "sells_h1": n(tx, "h1", "sells"), "buys_m5": n(tx, "m5", "buys"), "sells_m5": n(tx, "m5", "sells"),
            "chg_m5": float((chg or {}).get("m5") or 0.0), "chg_h1": float((chg or {}).get("h1") or 0.0),
            "chg_h6": float((chg or {}).get("h6") or 0.0), "chg_h24": float((chg or {}).get("h24") or 0.0),
            "created_ms": created, "social": social, "trending_rank": trending_rank}


def age_hours(pool: dict, now: dt.datetime) -> float | None:
    if not pool.get("created_ms"):
        return None
    return (now.timestamp() * 1000 - pool["created_ms"]) / 3_600_000


def screen(pool: dict, now: dt.datetime, cfg: dict) -> str | None:
    """None when the pool may be considered; otherwise the reason it is excluded."""
    s = cfg["screen"]
    if pool["chain"] != s["chain"]:
        return "wrong chain"
    if pool["liq"] < s["min_liquidity_usd"]:
        return f"liquidity ${pool['liq']:,.0f} below ${s['min_liquidity_usd']:,.0f}"
    if pool["vol_h24"] < s["min_volume_h24_usd"]:
        return f"24h volume ${pool['vol_h24']:,.0f} below ${s['min_volume_h24_usd']:,.0f}"
    a = age_hours(pool, now)
    if a is None or a < s["min_age_hours"] or a > s["max_age_hours"]:
        return f"age {a if a is None else round(a, 1)} h outside {s['min_age_hours']}-{s['max_age_hours']} h"
    if pool["buys_h1"] + pool["sells_h1"] < s["min_txns_h1"]:
        return "too few trades in the last hour"
    if not (pool["social"] or (pool["trending_rank"] is not None and pool["trending_rank"] <= s["max_trending_rank"])):
        return "no X link on its profile and not trending"
    return None


def entry_signal(pool: dict, cfg: dict) -> str | None:
    """None when the momentum entry is satisfied (reason string when not)."""
    e = cfg["entry"]
    if not (e["min_h1_change_pct"] <= pool["chg_h1"] <= e["max_h1_change_pct"]):
        return f"1h change {pool['chg_h1']:+.0f}% outside {e['min_h1_change_pct']:+.0f}..{e['max_h1_change_pct']:+.0f}%"
    if pool["chg_m5"] < e["min_m5_change_pct"]:
        return f"5m change {pool['chg_m5']:+.1f}% shows the move fading"
    if pool["chg_h6"] < e["min_h6_change_pct"]:
        return f"6h change {pool['chg_h6']:+.0f}% is negative"
    if pool["chg_h24"] > e["max_h24_change_pct"]:
        return f"24h change {pool['chg_h24']:+.0f}% is a blow-off, not a trend"
    if pool["buys_h1"] < e["min_buy_sell_ratio"] * max(pool["sells_h1"], 1.0):
        return f"buys {pool['buys_h1']:.0f} vs sells {pool['sells_h1']:.0f} below ratio {e['min_buy_sell_ratio']}"
    return None


def friction(side: str, size_usd: float, liq_usd: float, cfg: dict, reason: str = "") -> float:
    """Fractional price penalty against us: swap fee + latency/MEV allowance + price impact (about 2*size/liquidity for a constant-product pool).
    Stops and liquidity exits are charged more because those are the moments the price gaps through the trigger."""
    f = cfg["friction"]
    extra = f["stop_extra"] if reason in ("STOP", "LIQUIDITY_COLLAPSE", "TRAIL") else 0.0
    base = f["entry_latency"] if side == "BUY" else f["exit_latency"]
    return f["fee"] + base + extra + 2.0 * size_usd / max(liq_usd, 1.0)


def exit_signal(pos: dict, price: float, liq: float, now: dt.datetime, cfg: dict) -> str | None:
    """Exit reason code, evaluated on the price seen at this run. pos holds entry_price, peak, entered_at (ISO)."""
    x = cfg["exit"]
    ret = price / pos["entry_price"] - 1.0
    peak_ret = pos["peak"] / pos["entry_price"] - 1.0
    if liq < x["min_liquidity_usd"] or liq < x["liquidity_collapse_frac"] * pos["entry_liq"]:
        return "LIQUIDITY_COLLAPSE"
    if ret <= -x["stop_pct"] / 100.0:
        return "STOP"
    if ret >= x["take_profit_pct"] / 100.0:
        return "TAKE_PROFIT"
    if peak_ret >= x["trail_after_pct"] / 100.0 and price <= pos["peak"] * (1.0 - x["trail_pct"] / 100.0):
        return "TRAIL"
    held_h = (now - dt.datetime.fromisoformat(pos["entered_at"])).total_seconds() / 3600.0
    if held_h >= x["max_hold_hours"]:
        return "TIME_EXIT"
    return None


def rug_ok(summary: dict | None, cfg: dict) -> tuple[bool, str]:
    """RugCheck summary: refuse on any danger-level risk. Unknown (no answer) is refused, not assumed safe."""
    if not summary:
        return False, "no rug-check answer"
    danger = [r.get("name", "?") for r in summary.get("risks") or [] if str(r.get("level", "")).lower() == "danger"]
    if danger:
        return False, "danger flags: " + ", ".join(danger[:3])
    if float(summary.get("score_normalised", 100)) > cfg["screen"]["max_rug_score"]:
        return False, f"rug score {summary.get('score_normalised')} above {cfg['screen']['max_rug_score']}"
    return True, "ok"
