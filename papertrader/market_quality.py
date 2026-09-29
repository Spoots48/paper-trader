"""Closed-candle and synchronized-input checks. Provenance: research/upstream_2026_09_28/SOURCES.md.

Independent implementations of Jesse's completed-candle and OctoBot's freshness principles.
All clocks are explicit so the same checks can be replayed without wall-clock lookahead.
"""
from __future__ import annotations

import math


def parse_klines(rows: list) -> dict:
    candles = {}
    for row in rows:
        millis = int(row[0])
        if millis % 60000 or float(row[0]) != millis:
            raise ValueError('unaligned candle timestamp')
        timestamp = millis // 1000
        if timestamp in candles:
            raise ValueError('duplicate candle timestamp')
        candles[timestamp] = (float(row[1]), float(row[4]))
    return candles


def closed_closes(candles: dict, now, lookback: int) -> list[float]:
    """Exactly lookback returns, requiring lookback+1 contiguous completed minute closes."""
    last = int(now.timestamp()) // 60 * 60 - 60
    closes = []
    for timestamp in range(last - lookback * 60, last + 1, 60):
        if timestamp not in candles:
            raise ValueError(f'missing closed candle at {timestamp}')
        price = candles[timestamp][1]
        if not math.isfinite(price) or price <= 0:
            raise ValueError('invalid closed candle price')
        closes.append(price)
    return closes


def freshness_checks(observations: dict, now, cfg: dict) -> list[dict]:
    checks, valid = [], []
    for name, timestamp in observations.items():
        finite = isinstance(timestamp, (int, float)) and math.isfinite(timestamp)
        age = now.timestamp() - timestamp if finite else None
        ok = finite and -cfg['future_tolerance_seconds'] <= age <= cfg['max_age_seconds']
        checks.append({'name': name, 'ok': bool(ok), 'age_seconds': age,
                       'reason': 'fresh' if ok else 'missing, stale or future timestamp'})
        if finite:
            valid.append(timestamp)
    skew = max(valid)-min(valid) if valid else None
    checks.append({'name': 'snapshot_skew', 'ok': len(valid)==len(observations)>0 and skew <= cfg['max_skew_seconds'],
                   'skew_seconds': skew, 'reason': 'maximum separation between input timestamps'})
    return checks


def parse_book(raw: dict) -> tuple[list, list]:
    levels = []
    for side in ('asks', 'bids'):
        rows = [(float(x['price']), float(x['size'])) for x in raw.get(side, [])]
        if any(not math.isfinite(p) or not math.isfinite(q) or not 0 < p < 1 or q <= 0 for p,q in rows):
            raise ValueError('invalid binary order-book price or size')
        levels.append(sorted(rows, reverse=side=='bids'))
    asks, bids = levels
    if asks and bids and bids[0][0] >= asks[0][0]:
        raise ValueError('crossed order book')
    return asks, bids
