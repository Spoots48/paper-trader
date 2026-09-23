"""Check which free data sources answer from this machine (run on GitHub's servers before migrating)."""
import json
import os
import time
import traceback

import requests
import yfinance as yf

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
      "Accept": "application/json, text/plain, */*"}
UNIVERSE = [m["ticker"] for m in json.load(open("config/universe.json"))["members"]]
results = {}


def probe(name, fn):
    t = time.time()
    try:
        results[name] = {"ok": True, "detail": fn(), "secs": round(time.time() - t, 1)}
    except Exception as e:
        results[name] = {"ok": False, "detail": f"{type(e).__name__}: {str(e)[:300]}", "secs": round(time.time() - t, 1)}


def daily_universe():
    ok = 0
    for i in range(0, len(UNIVERSE), 100):
        df = yf.download(UNIVERSE[i:i + 100], period="10d", interval="1d", group_by="ticker", progress=False, auto_adjust=False)
        ok += sum(1 for t in UNIVERSE[i:i + 100] if t in df.columns.get_level_values(0) and df[t]["Close"].notna().any())
        time.sleep(1)
    if ok < 450:
        raise RuntimeError(f"only {ok}/{len(UNIVERSE)} tickers returned data")
    return f"{ok}/{len(UNIVERSE)} tickers"


def intraday():
    df = yf.download(["SPY", "AAPL", "DELL"], period="5d", interval="5m", group_by="ticker", progress=False)
    n = len(df.dropna(how="all"))
    if n < 100:
        raise RuntimeError(f"only {n} bars")
    return f"{n} bars, last {df.index[-1]}"


def news():
    n = yf.Ticker("DELL").news
    if not n:
        raise RuntimeError("empty")
    return f"{len(n)} items, first pubDate {n[0].get('content', {}).get('pubDate')}"


def earnings_hist():
    e = yf.Ticker("NKE").get_earnings_dates(limit=8)
    return f"{len(e)} rows"


def nasdaq():
    r = requests.get("https://api.nasdaq.com/api/calendar/earnings?date=2026-09-24", headers=UA, timeout=20)
    r.raise_for_status()
    return f"{len(((r.json().get('data') or {}).get('rows')) or [])} rows"


def gnews():
    r = requests.get("https://news.google.com/rss/search?q=%22Dell%22+stock+when:2d&hl=en-US&gl=US&ceid=US:en", headers=UA, timeout=20)
    r.raise_for_status()
    return f"{r.text.count('<item>')} items"


def vix():
    v = yf.download("^VIX", period="5d", progress=False)
    return f"last {float(v['Close'].iloc[-1].iloc[0]):.2f}"


for name, fn in [("yahoo_daily_universe", daily_universe), ("yahoo_5m", intraday), ("yahoo_news", news),
                 ("yahoo_earnings_history", earnings_hist), ("yahoo_vix", vix), ("nasdaq_earnings_calendar", nasdaq),
                 ("google_news_rss", gnews)]:
    probe(name, fn)
    print(name, json.dumps(results[name]), flush=True)
    time.sleep(2)

lines = ["| source | ok | detail | secs |", "|---|---|---|---|"] + [
    f"| {k} | {'✅' if v['ok'] else '❌'} | {v['detail']} | {v['secs']} |" for k, v in results.items()]
if os.environ.get("GITHUB_STEP_SUMMARY"):
    open(os.environ["GITHUB_STEP_SUMMARY"], "a").write("\n".join(lines) + "\n")
print("\n".join(lines))
print("PROBE_RESULT", json.dumps({k: v["ok"] for k, v in results.items()}))
