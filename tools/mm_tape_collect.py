"""Collect settled Polymarket 15-minute BTC/ETH up/down markets and their public taker-trade tape for offline replay.
Read-only public endpoints; writes data/mm_tape/markets.jsonl (gitignored). Usage: python tools/mm_tape_collect.py DAYS"""
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests

UA = {"User-Agent": "Mozilla/5.0"}
OUT = Path(__file__).resolve().parent.parent / "data" / "mm_tape" / "markets.jsonl"


def get(url, **params):
    for i in range(4):
        try:
            r = requests.get(url, params=params, headers=UA, timeout=25)
            if r.status_code == 200:
                return r.json()
            if r.status_code == 429:
                time.sleep(2 + 3 * i)
        except Exception:
            time.sleep(1 + i)
    return None


def one(job):
    asset, ts = job
    slug = f"{asset}-updown-15m-{ts}"
    ev = get("https://gamma-api.polymarket.com/events", slug=slug)
    if not ev:
        return None
    m = ev[0]["markets"][0]
    prices = json.loads(m["outcomePrices"])
    if sorted(prices) != ["0", "1"]:
        return None  # unsettled or ambiguous
    outs = json.loads(m["outcomes"])
    trades, off = [], 0
    while off <= 3000:
        b = get("https://data-api.polymarket.com/trades", market=m["conditionId"], limit=500, offset=off, takerOnly="true")
        if b is None:
            return None
        trades += [[int(t["timestamp"]), t["side"], t["outcome"], float(t["price"]), float(t["size"])] for t in b]
        if len(b) < 500:
            break
        off += 500
    return {"slug": slug, "asset": asset, "start": ts, "winner": outs[prices.index("1")], "trades": sorted(trades)}


if __name__ == "__main__":
    days = int(sys.argv[1])
    now = int(time.time())
    last = (now - 3600) // 900 * 900
    jobs = [(a, t) for t in range(last - days * 86400, last + 1, 900) for a in ("btc", "eth")]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    done = set()
    if OUT.exists():
        done = {json.loads(l)["slug"] for l in OUT.read_text().splitlines() if l}
    jobs = [j for j in jobs if f"{j[0]}-updown-15m-{j[1]}" not in done]
    print(len(jobs), "markets to fetch", flush=True)
    n = 0
    with ThreadPoolExecutor(4) as ex, open(OUT, "a") as f:
        for r in ex.map(one, jobs):
            if r:
                f.write(json.dumps(r) + "\n")
                n += 1
                if n % 100 == 0:
                    f.flush()
                    print(n, flush=True)
    print("done", n, flush=True)
