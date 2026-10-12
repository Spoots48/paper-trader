"""Calibration check for the speed trader's Jev probabilities (diagnostic only; it never changes a rule).

Each logged call says "Jev put p on price reaching +target before -stop within `hold` minutes". After the close we replay the day's
1-minute bars and record whether that actually happened, then compare Jev's p with the hit rate: overall, by p bucket, against the
base rate over every bar, and by correlation. Per-session sums are stored in state/speed_calibration.jsonl so the totals survive the
short history window of the free 1-minute data. A reference price is the close of the call's bar; an ambiguous bar counts as a stop."""
from __future__ import annotations

import datetime as dt
import json
import math
from pathlib import Path

from .config import ROOT

LOG = "state/speed_calls.jsonl"
STORE = "state/speed_calibration.jsonl"
BUCKETS = [(0.0, 0.42), (0.42, 0.46), (0.46, 0.50), (0.50, 1.01)]


def outcome(bars: list[tuple], i: int, tp: float, sl: float, hold: int) -> int | None:
    """1 if +tp% is reached before -sl% within `hold` bars after bar i, 0 if not, None when the window is incomplete.
    bars: (time, high, low, close)."""
    if i + hold >= len(bars):
        return None
    ref = bars[i][3]
    for _, hi, lo, _c in bars[i + 1:i + 1 + hold]:
        if (lo / ref - 1) * 100 <= -sl:  # also taken when the same bar touches both: the stop is assumed first
            return 0
        if (hi / ref - 1) * 100 >= tp:
            return 1
    return 0


def score_session(calls: list[dict], bars: dict[str, list[tuple]], tp: float, sl: float, hold: int) -> dict:
    """bars: {ticker: [(datetime_utc, high, low, close), ...]} sorted by time."""
    out = {"n": 0, "sum_p": 0.0, "sum_o": 0, "sum_pp": 0.0, "sum_po": 0.0, "base_n": 0, "base_hits": 0, "buckets": {}}
    for tk, b in bars.items():
        for i in range(len(b)):
            o = outcome(b, i, tp, sl, hold)
            if o is not None:
                out["base_n"] += 1
                out["base_hits"] += o
    index = {tk: {t[0]: k for k, t in enumerate(b)} for tk, b in bars.items()}
    for c in calls:
        b = bars.get(c["ticker"])
        if not b:
            continue
        k = index[c["ticker"]].get(dt.datetime.fromisoformat(c["bar"]).astimezone(dt.timezone.utc))
        o = outcome(b, k, tp, sl, hold) if k is not None else None
        if o is None:
            continue
        p = float(c["p"])
        out["n"] += 1
        out["sum_p"] += p
        out["sum_o"] += o
        out["sum_pp"] += p * p
        out["sum_po"] += p * o
        for lo, hi in BUCKETS:
            if lo <= p < hi:
                cell = out["buckets"].setdefault(f"{lo:.2f}-{min(hi, 1.0):.2f}", [0, 0])
                cell[0] += 1
                cell[1] += o
    return out


def merge(parts: list[dict]) -> dict:
    tot = {"n": 0, "sum_p": 0.0, "sum_o": 0, "sum_pp": 0.0, "sum_po": 0.0, "base_n": 0, "base_hits": 0, "buckets": {}}
    for s in parts:
        for k in ("n", "sum_p", "sum_o", "sum_pp", "sum_po", "base_n", "base_hits"):
            tot[k] += s.get(k, 0)
        for name, (n, h) in s.get("buckets", {}).items():
            cell = tot["buckets"].setdefault(name, [0, 0])
            cell[0] += n
            cell[1] += h
    return tot


def correlation(s: dict) -> float | None:
    """Pearson correlation of p with the 0/1 outcome, from running sums (the outcome is binary, so o*o == o)."""
    n = s["n"]
    if n < 3:
        return None
    var_p = s["sum_pp"] / n - (s["sum_p"] / n) ** 2
    var_o = s["sum_o"] / n - (s["sum_o"] / n) ** 2
    if var_p <= 1e-12 or var_o <= 1e-12:
        return None
    return (s["sum_po"] / n - (s["sum_p"] / n) * (s["sum_o"] / n)) / math.sqrt(var_p * var_o)


def record(root: Path, session: str, summary: dict) -> None:
    path = root / STORE
    rows = [r for r in _read(path) if r.get("session") != session]
    rows.append({"session": session, **summary})
    path.write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in sorted(rows, key=lambda r: r["session"])))


def _read(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(x) for x in path.read_text().splitlines() if x.strip()]


def totals(root: Path = ROOT) -> dict:
    return merge([r for r in _read(root / STORE)])


def fetch_bars(tickers: list[str], day: dt.date) -> dict[str, list[tuple]]:
    """Free 1-minute bars for one session (regular hours only), as {ticker: [(utc_datetime, high, low, close)]}."""
    import yfinance as yf
    df = yf.download(sorted(set(tickers)), start=day.isoformat(), end=(day + dt.timedelta(days=1)).isoformat(), interval="1m",
                     auto_adjust=False, progress=False, group_by="ticker")
    out: dict[str, list[tuple]] = {}
    for tk in sorted(set(tickers)):
        try:
            sub = df[tk].dropna()
        except KeyError:
            continue
        rows = [(ts.tz_convert("UTC").to_pydatetime(), float(r["High"]), float(r["Low"]), float(r["Close"])) for ts, r in sub.iterrows()]
        if rows:
            out[tk] = rows
    return out


def run_for_day(day: dt.date, tp: float, sl: float, hold: int, root: Path = ROOT, bars=None) -> dict | None:
    """Score one session's logged calls and store the result. Returns the session summary, or None when there is nothing to score."""
    d = day.isoformat()
    calls = [c for c in _read(root / LOG) if c.get("session") == d]
    if not calls:
        return None
    if bars is None:
        bars = fetch_bars(sorted({c["ticker"] for c in calls}), day)
    if not bars:
        return None
    summary = score_session(calls, bars, tp, sl, hold)
    if summary["n"]:
        record(root, d, summary)
    return summary


def render(today: dict | None, cum: dict) -> list[str]:
    def rate(h, n):
        return f"{h / n:.1%}" if n else "n/a"
    lines = ["", "## Jev's speed-trader probabilities vs what happened (diagnostic)"]
    if not cum["n"]:
        return lines + ["No scored calls yet."]
    corr = correlation(cum)
    lines.append(f"Scored calls so far: {cum['n']}. Mean probability Jev gave: {cum['sum_p'] / cum['n']:.1%}. Share that actually reached the target "
                 f"before the stop: {rate(cum['sum_o'], cum['n'])}. Same event over every bar of the same stocks: {rate(cum['base_hits'], cum['base_n'])}. "
                 f"Correlation of p with the outcome: {'n/a' if corr is None else f'{corr:+.2f}'}.")
    for name in sorted(cum["buckets"]):
        n, h = cum["buckets"][name]
        lines.append(f"- p in {name}: {n} calls, {rate(h, n)} reached the target first")
    if today and today.get("n"):
        lines.append(f"Today alone: {today['n']} calls, mean p {today['sum_p'] / today['n']:.1%}, reached target first {rate(today['sum_o'], today['n'])}.")
    lines.append("Reading it: a useful signal needs high-p calls to hit more often than low-p calls, well above the base rate, and needs enough calls to "
                 "tell skill from luck (hundreds, over several days). Until then the rules stay frozen and the threshold is not touched.")
    return lines
