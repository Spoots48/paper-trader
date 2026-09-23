"""Freeze the trading universe: current S&P 500 constituents (Wikipedia) plus SPY.

Run once before the experiment starts. The file's SHA-256 is recorded in the
ledger at freeze time, so later edits are detectable.
"""
from __future__ import annotations

import io
import json
import sys
from pathlib import Path

import pandas as pd
import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from papertrader.config import UNIVERSE_PATH  # noqa: E402
from papertrader.nyse_calendar import iso, now_utc  # noqa: E402

URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"


def main() -> None:
    retrieved = iso(now_utc())
    r = requests.get(URL, headers={"User-Agent": "PaperTradingSim/1.0 (research)"}, timeout=30)
    r.raise_for_status()
    t = pd.read_html(io.StringIO(r.text))[0]
    members = []
    for _, row in t.iterrows():
        sym = str(row["Symbol"]).strip()
        members.append({
            "ticker": sym.replace(".", "-"),  # Yahoo format: BRK.B -> BRK-B
            "name": str(row["Security"]).strip(),
            "sector": str(row["GICS Sector"]).strip(),
            "date_added": str(row["Date added"]).strip()[:10],
        })
    members.sort(key=lambda m: m["ticker"])
    out = {
        "description": "S&P 500 constituents as listed on Wikipedia at retrieval time, plus SPY (benchmark / residual cash sleeve).",
        "source_url": URL,
        "retrieved_at": retrieved,
        "benchmark": "SPY",
        "volatility_index": "^VIX",
        "members": members,
    }
    UNIVERSE_PATH.write_text(json.dumps(out, indent=1))
    print(f"wrote {len(members)} members to {UNIVERSE_PATH}")


if __name__ == "__main__":
    main()
