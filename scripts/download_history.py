"""Download historical data for the backtest (research only; never used by live decisions).

Outputs in data/history/:
  daily_<field>.pkl   wide DataFrames (sessions x tickers) for open/high/low/close/volume/dividends/splits
  earnings.pkl        long DataFrame: ticker, announce_ts (ET), eps_estimate, eps_reported, surprise_pct
  download_meta.json  what was requested, what failed, retrieval timestamps
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import pandas as pd
import yfinance as yf

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from papertrader.config import HISTORY_DIR, load_universe  # noqa: E402
from papertrader.nyse_calendar import iso, now_utc  # noqa: E402

START = "2015-01-01"
FIELDS = ["Open", "High", "Low", "Close", "Volume", "Dividends", "Stock Splits"]


def download_prices(tickers: list[str], meta: dict) -> None:
    frames = {f: [] for f in FIELDS}
    failed = []
    for i in range(0, len(tickers), 80):
        batch = tickers[i:i + 80]
        for attempt in range(3):
            try:
                df = yf.download(batch, start=START, interval="1d", auto_adjust=False, actions=True,
                                 group_by="ticker", progress=False, threads=True)
                break
            except Exception as e:  # network hiccup: back off and retry
                print(f"batch {i} attempt {attempt} failed: {e}", flush=True)
                time.sleep(10 * (attempt + 1))
        else:
            failed.extend(batch)
            continue
        for t in batch:
            if t not in df.columns.get_level_values(0):
                failed.append(t)
                continue
            sub = df[t]
            if sub["Close"].dropna().empty:
                failed.append(t)
                continue
            for f in FIELDS:
                frames[f].append(sub[f].rename(t))
        print(f"prices: {min(i + 80, len(tickers))}/{len(tickers)}", flush=True)
        time.sleep(2)
    for f in FIELDS:
        wide = pd.concat(frames[f], axis=1).sort_index()
        wide.index = pd.to_datetime(wide.index).tz_localize(None).normalize()
        name = f.lower().replace("stock ", "")
        wide.to_pickle(HISTORY_DIR / f"daily_{name}.pkl")
    meta["price_failed"] = failed


def download_earnings(tickers: list[str], meta: dict) -> None:
    rows, failed = [], []
    for n, t in enumerate(tickers):
        for attempt in range(3):
            try:
                e = yf.Ticker(t).get_earnings_dates(limit=60)
                break
            except Exception as ex:
                print(f"earnings {t} attempt {attempt}: {ex}", flush=True)
                time.sleep(5 * (attempt + 1))
        else:
            failed.append(t)
            continue
        if e is None or e.empty:
            failed.append(t)
            continue
        for ts, r in e.iterrows():
            rows.append({
                "ticker": t,
                "announce_ts": ts.tz_convert("America/New_York").strftime("%Y-%m-%d %H:%M"),
                "eps_estimate": r.get("EPS Estimate"),
                "eps_reported": r.get("Reported EPS"),
                "surprise_pct": r.get("Surprise(%)"),
            })
        if n % 50 == 0:
            print(f"earnings: {n}/{len(tickers)}", flush=True)
        time.sleep(0.4)
    pd.DataFrame(rows).to_pickle(HISTORY_DIR / "earnings.pkl")
    meta["earnings_failed"] = failed


def main() -> None:
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    u = load_universe()
    stocks = [m["ticker"] for m in u["members"]]
    meta = {"started_at": iso(now_utc()), "start": START, "n_stocks": len(stocks)}
    download_prices(stocks + ["SPY", "^VIX"], meta)
    meta["prices_done_at"] = iso(now_utc())
    download_earnings(stocks, meta)
    meta["finished_at"] = iso(now_utc())
    (HISTORY_DIR / "download_meta.json").write_text(json.dumps(meta, indent=1))
    print("done", json.dumps({k: (len(v) if isinstance(v, list) else v) for k, v in meta.items()}))


if __name__ == "__main__":
    main()
