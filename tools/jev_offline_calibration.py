"""Offline calibration of Jev on the speed trader's exact question, using past 1-minute bars with known outcomes.

Why: the live book needs days to collect enough scored calls. Calls cost a fraction of a cent, so we ask the SAME question (same prompt, same
state format, same candidate selection: prefilter candidates, top 4 per minute by relative volume) about past minutes whose outcome is known.

PRE-DECLARED (written before any Jev answer to this sample existed):
  frame   7 complete sessions in the 8-day free window before 2026-10-12; 20 mega-caps; minute >= 22 through 15:45 ET.
  sample  up to 170 states per session, random.Random(12). No resampling, no second pass, no prompt variants.
  keep    the speed book ONLY IF (a) the p >= 0.50 calls number at least 30 and hit the target at >= 2x the sample's base rate, AND
          (b) the AUC of p for "target first" is >= 0.55 with the lower end of a session-block bootstrap 95% interval above 0.50.
          Otherwise: retire it (stop Jev calls) via a logged change. Never lower the 0.65 buy threshold to force trades.
  also    reported only: hit rate and assumed-cost net return of the top fifth of p; calls at or above the live 0.65 threshold.

usage:  python tools/jev_offline_calibration.py build            (local; writes states + labels)
        python tools/jev_offline_calibration.py ask   ...        (cloud; needs TYPESAFE_API_KEY)
        python tools/jev_offline_calibration.py score ...        (local; joins answers with labels)"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import random
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from types import SimpleNamespace

import numpy as np

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
OUT = HERE / "research" / "review_2026_10_12"
STATES, LABELS, RESULT = OUT / "jev_offline_states.jsonl", OUT / "jev_offline_labels.jsonl", OUT / "jev_offline_result.json"
SEED, PER_SESSION = 12, 170
# assumed per-side costs (fractions of price): entry, target exit, stop exit, time exit (same as the 2026-10-12 prefilter test)
C_IN, C_TP, C_ST, C_TM = 3e-4, 3e-4, 6e-4, 4e-4
BUCKETS = [(0.0, 0.42), (0.42, 0.46), (0.46, 0.50), (0.50, 1.01)]


def load_cfg() -> dict:
    return json.loads((HERE / "config" / "strategy_speed_v1.json").read_text())


def trade(bars: list[tuple], i: int, sp: dict) -> tuple[int, str, float]:
    """bars: (time, o, h, l, c, v). Decision at the close of bar i. Returns (hit, kind, net return) where hit follows the calibration
    definition (close of bar i as reference, next `hold` bars, stop first when one bar touches both) and the net return follows the
    book's fills (entry at the open of bar i+1+delay, fixed exits, assumed costs)."""
    tp, sl, hold, delay = sp["take_profit_pct"], sp["stop_pct"], sp["max_hold_minutes"], sp["entry_delay_bars"]
    ref, hit = bars[i][4], 0
    for b in bars[i + 1:i + 1 + hold]:
        if (b[3] / ref - 1) * 100 <= -sl:
            break
        if (b[2] / ref - 1) * 100 >= tp:
            hit = 1
            break
    f = i + 1 + delay
    e = bars[f][1]
    up, dn = e * (1 + tp / 100), e * (1 - sl / 100)
    for j in range(f, min(f + hold + 1, len(bars))):
        _, o, h, lo, c, _v = bars[j]
        if lo <= dn:
            return hit, "stop", min(dn, o) / e - 1 - C_IN - C_ST
        if h >= up:
            return hit, "target", up / e - 1 - C_IN - C_TP
    k = min(f + hold, len(bars) - 1)
    return hit, "time", bars[k][4] / e - 1 - C_IN - C_TM


def build() -> None:
    import pandas as pd
    import yfinance as yf
    from papertrader.speed_engine import SpeedEngine
    cfg = load_cfg()
    sp, tickers = cfg["speed"], cfg["universe"]["tickers"]
    shim = SimpleNamespace(sp=sp)
    df = yf.download(sorted(tickers), period="8d", interval="1m", auto_adjust=False, progress=False, group_by="ticker")
    per: dict[str, dict[dt.date, list]] = {}
    for t in tickers:
        b = df[t].dropna(subset=["Open", "Low", "Close"])
        b.index = b.index.tz_convert("America/New_York")
        b = b[(b.index.time >= dt.time(9, 30)) & (b.index.time <= dt.time(15, 59))]
        for d, g in b.groupby(b.index.date):
            per.setdefault(t, {})[d] = [(ts, float(r["Open"]), float(r["High"]), float(r["Low"]), float(r["Close"]), float(r.get("Volume") or 0.0))
                                        for ts, r in g.iterrows()]
    today = dt.datetime.now().date()
    sessions = sorted({d for t in per for d in per[t] if d < dt.date(2026, 10, 12) and d < today and len(per[t][d]) >= 385})
    sessions = sorted(d for d in sessions if sum(1 for t in per if d in per[t]) >= len(tickers) - 1)
    rng, states, labels, frame = random.Random(SEED), [], [], {}
    for S in sessions:
        pool = []
        times = sorted({b[0] for t in per for b in per[t].get(S, [])})
        index = {t: {b[0]: k for k, b in enumerate(per[t][S])} for t in per if S in per[t]}
        for ts in times:
            if ts.time() > dt.time(15, 45):
                continue
            cands = []
            for t, ix in index.items():
                k = ix.get(ts)
                if k is None or k + 1 < 22:
                    continue
                f = SpeedEngine.features(shim, [(b[0].isoformat(), b[1], b[2], b[3], b[4], b[5]) for b in per[t][S][max(0, k - 21):k + 1]])
                if f and SpeedEngine.is_candidate(shim, f):
                    cands.append((f["vol_ratio"], t, k, f))
            cands.sort(reverse=True, key=lambda x: x[0])
            for vr, t, k, f in cands[:sp["max_jev_calls_per_minute"]]:
                if k + 1 + sp["entry_delay_bars"] + sp["max_hold_minutes"] >= len(per[t][S]):
                    continue
                minute = int((ts - ts.replace(hour=9, minute=30, second=0, microsecond=0)).total_seconds() // 60)
                pool.append((S, ts, t, k, minute, f))
        frame[S.isoformat()] = len(pool)
        for S_, ts, t, k, minute, f in rng.sample(pool, min(PER_SESSION, len(pool))):
            hit, kind, net = trade(per[t][S], k, sp)
            sid = f"{S_.isoformat()}|{ts.isoformat()}|{t}"
            states.append({"id": sid, "session": S_.isoformat(), "bar": ts.isoformat(), "ticker": t, "minute": minute,
                           "f": {"chg": f["chg"], "vr": f["vr"]}})
            labels.append({"id": sid, "session": S_.isoformat(), "hit": hit, "kind": kind, "net": net, "r5": round(f["r5"], 5)})
    OUT.mkdir(parents=True, exist_ok=True)
    STATES.write_text("".join(json.dumps(s) + "\n" for s in states))
    LABELS.write_text("".join(json.dumps(x) + "\n" for x in labels))
    print(f"sessions {len(sessions)}: {[d.isoformat() for d in sessions]}\nframe sizes {frame}\nsampled {len(states)} states -> {STATES.name}, {LABELS.name}")
    print(f"base hit rate of the sample {np.mean([x['hit'] for x in labels]):.3f}; kinds {dict(zip(*np.unique([x['kind'] for x in labels], return_counts=True)))}")


def ask(states_path: str, out_path: str, max_calls: int, workers: int) -> None:
    from papertrader.speed_engine import SpeedEngine
    from typesafe_sdk import TypeSafeClient
    shim = SimpleNamespace(sp=load_cfg()["speed"])
    states = [json.loads(x) for x in Path(states_path).read_text().splitlines() if x.strip()]
    random.Random(SEED).shuffle(states)          # any interruption leaves an unbiased subset
    states = states[:max_calls]
    local, lock, stats = threading.local(), threading.Lock(), {"done": 0, "err": 0}
    out = open(out_path, "w")

    def one(s: dict) -> None:
        if stats["err"] >= 40 and stats["err"] > 0.3 * max(stats["done"], 1):
            return                                # too many failures: stop spending
        client = getattr(local, "c", None) or TypeSafeClient()
        local.c = client
        row = {"id": s["id"]}
        for attempt in range(5):
            try:
                row["p"] = SpeedEngine.ask_jev(shim, client, s["ticker"], s["f"], s["minute"])
                row.pop("error", None)
                break
            except Exception as ex:               # noqa: BLE001
                row["error"] = f"{type(ex).__name__}: {str(ex)[:160]}"
                time.sleep(min(60, 2 ** attempt * (5 if "429" in row["error"] or "rate" in row["error"].lower() else 1)))
        with lock:
            stats["done"] += 1
            stats["err"] += "error" in row
            out.write(json.dumps(row) + "\n")
            out.flush()
            if stats["done"] % 50 == 0:
                print(f"{stats['done']} asked, {stats['err']} errors", flush=True)

    with ThreadPoolExecutor(workers) as ex:
        list(ex.map(one, states))
    out.close()
    print(f"finished: {stats['done']} asked, {stats['err']} errors")


def auc(p: np.ndarray, y: np.ndarray) -> float:
    """Probability that a random hit has a higher p than a random miss (ties count half)."""
    pos, neg = p[y == 1], p[y == 0]
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")
    gt = (pos[:, None] > neg[None, :]).sum() + 0.5 * (pos[:, None] == neg[None, :]).sum()
    return float(gt / (len(pos) * len(neg)))


def verdict(p: np.ndarray, y: np.ndarray, sessions: np.ndarray, boots: int = 2000) -> dict:
    base = float(y.mean())
    top = p >= 0.50
    n_top, hit_top = int(top.sum()), (float(y[top].mean()) if top.any() else float("nan"))
    a = auc(p, y)
    rng, days = np.random.default_rng(SEED), np.unique(sessions)
    ba = []
    for _ in range(boots):
        pick = rng.choice(days, len(days))
        idx = np.concatenate([np.flatnonzero(sessions == d) for d in pick])
        v = auc(p[idx], y[idx])
        if v == v:
            ba.append(v)
    lo, hi = (float(np.percentile(ba, 2.5)), float(np.percentile(ba, 97.5))) if ba else (float("nan"), float("nan"))
    cond_a = n_top >= 30 and hit_top >= 2 * base
    cond_b = a >= 0.55 and lo > 0.50
    return {"n": int(len(p)), "base_rate": base, "mean_p": float(p.mean()), "n_top": n_top, "hit_top": hit_top, "auc": a, "auc_ci": [lo, hi],
            "cond_a": bool(cond_a), "cond_b": bool(cond_b), "decision": "KEEP" if cond_a and cond_b else "RETIRE"}


def score(answers_path: str) -> None:
    labels = {x["id"]: x for x in map(json.loads, LABELS.read_text().splitlines())}
    rows = [json.loads(x) for x in Path(answers_path).read_text().splitlines() if x.strip()]
    ok = [r for r in rows if "p" in r and r["id"] in labels]
    print(f"answers {len(rows)}, usable {len(ok)}, errors {sum('error' in r for r in rows)}")
    p = np.array([r["p"] for r in ok])
    lab = [labels[r["id"]] for r in ok]
    y, net, sess = np.array([x["hit"] for x in lab]), np.array([x["net"] for x in lab]), np.array([x["session"] for x in lab])
    v = verdict(p, y, sess)
    print(f"calls {v['n']}, mean p {v['mean_p']:.3f}, base hit rate {v['base_rate']:.3f}, corr(p, hit) {np.corrcoef(p, y)[0, 1]:+.3f}")
    print(f"AUC {v['auc']:.3f}  (95% session-bootstrap {v['auc_ci'][0]:.3f}-{v['auc_ci'][1]:.3f})")
    for lo, hi in BUCKETS:
        m = (p >= lo) & (p < hi)
        if m.any():
            print(f"  p in [{lo:.2f},{min(hi, 1):.2f}): n={int(m.sum()):4d} hit={y[m].mean():.3f} net/trade={net[m].mean() * 1e4:+.1f} bp")
    q = p >= np.quantile(p, 0.8)
    se = net[q].std(ddof=1) / np.sqrt(q.sum()) if q.sum() > 1 else float("nan")
    print(f"top fifth of p (>= {np.quantile(p, 0.8):.2f}): n={int(q.sum())} hit={y[q].mean():.3f} net/trade={net[q].mean() * 1e4:+.1f} bp (se {se * 1e4:.1f})")
    print(f"all calls: net/trade {net.mean() * 1e4:+.1f} bp;  calls at or above the live threshold 0.65: {int((p >= 0.65).sum())}")
    for d in sorted(set(sess)):
        m = sess == d
        print(f"  {d}: n={int(m.sum()):3d} mean p {p[m].mean():.3f} hit {y[m].mean():.3f} auc {auc(p[m], y[m]):.2f}")
    print(f"(a) top bucket >= 30 calls and >= 2x base: {v['cond_a']}   (b) AUC >= 0.55 with CI above 0.50: {v['cond_b']}   => {v['decision']}")
    RESULT.write_text(json.dumps(v, indent=1))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("build")
    a = sub.add_parser("ask")
    a.add_argument("--states", default=str(STATES))
    a.add_argument("--out", default="jev_offline_answers.jsonl")
    a.add_argument("--max-calls", type=int, default=1300)
    a.add_argument("--workers", type=int, default=4)
    s = sub.add_parser("score")
    s.add_argument("answers")
    args = ap.parse_args()
    if args.cmd == "build":
        build()
    elif args.cmd == "ask":
        ask(args.states, args.out, args.max_calls, args.workers)
    else:
        score(args.answers)
