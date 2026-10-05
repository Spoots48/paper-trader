"""Shadow cross-check of the crypto candle feed against a second free, keyless exchange feed.

Observation only: it never gates, sizes or blocks a trade and any failure here is swallowed. It exists to measure
whether the Binance minute candles the crypto books rely on agree with an independent source (USDT vs USD basis is
expected to be a few bp), so a better-data upgrade is decided on evidence rather than guesswork."""
from __future__ import annotations

import statistics

COINBASE = "https://api.exchange.coinbase.com"
PRODUCTS = {"BTCUSDT": "BTC-USD", "ETHUSDT": "ETH-USD"}
MIN_OVERLAP = 20
MEDIAN_BP_LIMIT = 15.0   # typical USDT/USD basis is a few bp; more than this is a real disagreement
MAX_BP_LIMIT = 60.0


def parse_coinbase(rows: list) -> dict:
    """Coinbase rows are [time, low, high, open, close, volume]; keep closed-minute closes keyed by start time."""
    out = {}
    for r in rows:
        t = int(r[0])
        if t % 60 == 0 and float(r[4]) > 0:
            out[t] = float(r[4])
    return out


def compare(binance: dict, other: dict) -> dict:
    """binance: {start: (open, close)} as built by market_quality.parse_klines; other: {start: close}."""
    common = sorted(set(binance) & set(other))
    if len(common) < MIN_OVERLAP:
        return {"n": len(common), "ok": None, "reason": "too little overlap"}
    bp = [abs(binance[t][1] / other[t] - 1) * 1e4 for t in common]
    med, mx = statistics.median(bp), max(bp)
    return {"n": len(common), "median_bp": round(med, 2), "max_bp": round(mx, 2),
            "ok": med <= MEDIAN_BP_LIMIT and mx <= MAX_BP_LIMIT}


def check(symbol: str, candles: dict, get) -> dict | None:
    product = PRODUCTS.get(symbol)
    if product is None:
        return None
    rows = get(f"{COINBASE}/products/{product}/candles", granularity=60)
    return compare(candles, parse_coinbase(rows))
