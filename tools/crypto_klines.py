"""Fetch Binance 1-minute klines for the replay window (public data-api.binance.vision). Writes data/mm_tape/klines_<SYMBOL>.json."""
import json, sys, time
from pathlib import Path
import requests
D = Path(__file__).resolve().parent.parent / "data" / "mm_tape"
ms = [json.loads(l) for l in (D / "markets.jsonl").read_text().splitlines() if l]
lo, hi = min(m["start"] for m in ms) - 4000, max(m["start"] for m in ms) + 1000
for sym in ("BTCUSDT", "ETHUSDT"):
    out, t = {}, lo
    while t < hi:
        for a in range(4):
            r = requests.get("https://data-api.binance.vision/api/v3/klines", params={"symbol": sym, "interval": "1m", "startTime": t * 1000, "limit": 1000}, timeout=25)
            if r.status_code == 200: break
            time.sleep(2)
        k = r.json()
        if not k: break
        for row in k: out[int(row[0]) // 1000] = [float(row[1]), float(row[4])]
        t = int(k[-1][0]) // 1000 + 60
    (D / f"klines_{sym}.json").write_text(json.dumps(out))
    print(sym, len(out), "minutes", flush=True)
