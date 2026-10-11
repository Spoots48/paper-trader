"""Speed trader (paper only): many short trades on liquid stocks, with Jev (TypeSafe System One) making every ENTRY decision.

Per completed 1-minute bar, strictly in time order (causal catch-up like the day trader):
  1) fill entries decided earlier at a later bar's open (decision at close of bar t, fill at the open of bar t+1+delay), after costs;
  2) apply fixed exits to open positions: stop, take-profit, time stop, flat before the close;
  3) a cheap rule prefilter picks momentum/volume candidates; Jev gets a compact state for each and returns the probability that
     price reaches +target before -stop within the hold window; buy only if it clears the threshold.
Jev is the only entry decision-maker: if it is unavailable the book does not trade (there is no rule-based fallback).
Hard caps bound API usage (per minute, per run, per day). Paper only: proceeds are reusable immediately (no pattern-day-trader or
settlement rules are modeled), so this cannot be transferred to a real small account. Costs are charged on every fill."""
from __future__ import annotations

import datetime as dt
import json
import os
import statistics

from .broker import Fill
from .day_engine import DayEngine
from .intraday import DayEvent, DayState, cost_bps
from .nyse_calendar import ET, iso, session_close, session_open, sessions_between
from .strategy import Decision

QUESTION = ("Here are the last 20 one-minute price changes (percent) and volume ratios (volume divided by its 20-minute average) of a large, liquid "
            "US stock, newest last. Will its price reach {target:.2f}% above the latest close before it falls {stop:.2f}% below the latest close, "
            "within the next {hold} minutes?")
LOG = "state/speed_calls.jsonl"


class SpeedEngine(DayEngine):
    def __init__(self, ledger, md, cfg, exp, now, client_factory=None, root=None):
        cfg = {**cfg, "execution": {"bar_minutes": 1}}
        super().__init__(ledger, md, cfg, exp, now)
        self.sp = cfg["speed"]
        self.universe = list(cfg["universe"]["tickers"])
        self.client_factory = client_factory
        self.client = None
        self.root = root
        self.calls_this_run = 0

    # ------------------------------------------------------------------ main
    def step(self) -> str:
        if self.L.get_state("experiment_finished"):
            return "experiment finished; nothing to do"
        today = self.now.astimezone(ET).date()
        for S in sessions_between(self.start, min(today, self.end)):
            sj = self.L.get_state(f"dt:{S}")
            if sj and sj.get("closed") and self.L.db.execute("SELECT 1 FROM snapshots WHERE session=?", (S.isoformat(),)).fetchone():
                continue
            if self.now < session_open(S) + dt.timedelta(minutes=3):
                break
            st = DayState.from_json(sj) if sj else self._new_state(S)
            self.advance(S, st)
            if not st.closed:
                break
        return "; ".join(self.log) or "no action needed"

    def _new_state(self, S: dt.date) -> DayState:
        last = self.L.db.execute("SELECT equity FROM snapshots WHERE session<? ORDER BY session DESC LIMIT 1", (S.isoformat(),)).fetchone()
        cash = last["equity"] if last else self.cash0
        return DayState(session=S.isoformat(), cash_at_open=cash, cash=cash)

    def _jev(self):
        if self.client is not None:
            return self.client
        factory = self.client_factory
        if factory is None:
            if not os.environ.get("TYPESAFE_API_KEY"):
                return None
            try:
                from typesafe_sdk import TypeSafeClient
            except ImportError:
                return None
            factory = TypeSafeClient
        self.client = factory()
        return self.client

    # ------------------------------------------------------------------ data
    def _bars_v(self, S: dt.date) -> dict[str, dict[str, tuple]]:
        """{bar_time_iso: {ticker: (o, h, l, c, v)}} for completed 1-minute bars of S."""
        df = self.md._download(sorted(set(self.universe)), start=S.isoformat(), end=(S + dt.timedelta(days=1)).isoformat(),
                               interval="1m", prepost=False)
        out: dict[str, dict[str, tuple]] = {}
        if df is None:
            return out
        now_et = self.now.astimezone(ET)
        for t in set(self.universe):
            if t not in df.columns.get_level_values(0):
                continue
            for ts, r in df[t].dropna(subset=["Open", "Low", "Close"]).iterrows():
                et = ts.astimezone(ET)
                if et.date() != S or et + dt.timedelta(minutes=1) > now_et:
                    continue
                out.setdefault(et.isoformat(), {})[t] = (float(r["Open"]), float(r["High"]), float(r["Low"]), float(r["Close"]), float(r.get("Volume") or 0))
        return out

    # ------------------------------------------------------------------ logic
    def features(self, hist: list[tuple]) -> dict | None:
        """hist: bars of one ticker up to and including the decision bar, as (time, o, h, l, c, v)."""
        if len(hist) < 22:
            return None
        w = hist[-21:]
        closes = [b[4] for b in w]
        vols = [b[5] for b in w]
        base = statistics.mean(vols[:-1]) or 0.0
        if base <= 0 or closes[-1] <= 0:
            return None
        chg = [(closes[i] / closes[i - 1] - 1) * 100 for i in range(1, 21)]
        vr = [round(v / base, 2) for v in vols[1:]]
        r5 = closes[-1] / closes[-6] - 1
        return {"chg": [round(x, 3) for x in chg], "vr": vr, "r5": r5, "vol_ratio": vols[-1] / base, "up_bar": w[-1][4] >= w[-1][1], "price": closes[-1]}

    def is_candidate(self, f: dict) -> bool:
        P = self.sp["prefilter"]
        return f["up_bar"] and (f["r5"] >= P["min_5m_return"] or f["vol_ratio"] >= P["min_volume_ratio"])

    def ask_jev(self, client, ticker: str, f: dict, minute: int) -> float:
        from typesafe_sdk import Noul
        q = QUESTION.format(target=self.sp["take_profit_pct"], stop=self.sp["stop_pct"], hold=self.sp["max_hold_minutes"])
        resp = client.system_one(state={"ticker": ticker, "minutes_since_open": minute, "last_20_minute_changes_pct": f["chg"],
                                        "last_20_minute_volume_ratios": f["vr"]}, questions={"reach_target_first": Noul(instructions=q)})
        return float(resp.nouls["reach_target_first"].noul)

    def advance(self, S: dt.date, st: DayState) -> None:
        sp, P = self.sp, self.cfg["portfolio"]
        if not self.L.get_state("benchmark"):
            with self.L.tx():
                self._init_benchmark(S)
        ss = self.L.get_state(f"sp:{S}") or {"pending": [], "calls": 0, "trades": 0, "held": {}}
        bars = self._bars_v(S)
        close_t = session_close(S)
        last_start = (close_t - dt.timedelta(minutes=1)).isoformat()
        entry_cut = (close_t - dt.timedelta(minutes=sp["no_entries_last_minutes"])).isoformat()
        start_t = (session_open(S) + dt.timedelta(minutes=1)).isoformat()
        times = sorted(bars)
        events: list[tuple[str, DayEvent, dict]] = []
        log_rows: list[dict] = []
        hist: dict[str, list[tuple]] = {t: [] for t in self.universe}
        new_times = [bt for bt in times if bt >= start_t and (st.processed_through is None or bt > st.processed_through)]
        client = None
        for bt in times:
            for t, b in bars[bt].items():
                hist[t].append((bt, *b))
            if bt not in new_times:
                continue
            is_last = bt >= last_start
            cur = bars[bt]

            def sell(t, ref, kind, code, why):
                p = st.positions.pop(t)
                bps = cost_bps(self.cfg, 1e10, kind)
                px = ref * (1 - bps / 1e4)
                st.cash += p["qty"] * px
                ss["held"].pop(t, None)
                events.append((bt, DayEvent("SELL", t, p["qty"], ref, px, bps, bt, code, why, (px - p["entry_price"]) * p["qty"]), {}))

            # 1) pending entries become fills at this bar's open once their delay has elapsed
            still = []
            for it in ss["pending"]:
                it["wait"] -= 1
                if it["wait"] > 0:
                    still.append(it)
                    continue
                t = it["ticker"]
                b = cur.get(t)
                if not b or t in st.positions or bt > entry_cut:
                    continue
                equity = st.cash + sum(p["qty"] * (cur[k][3] if k in cur else p["entry_ref"]) for k, p in st.positions.items())
                if equity < st.cash_at_open * (1 - sp["daily_loss_limit"]) or len(st.positions) >= P["max_positions"] or ss["trades"] >= sp["max_trades_per_day"]:
                    continue
                ref = b[0]
                bps = cost_bps(self.cfg, 1e10, "entry")
                px = ref * (1 + bps / 1e4)
                budget = min(P["position_usd"], st.cash)
                if budget < P["min_order_usd"]:
                    continue
                q = int(budget / px * 10 ** P["fractional_decimals"]) / 10 ** P["fractional_decimals"]
                if q * px < P["min_order_usd"]:
                    continue
                st.cash -= q * px
                stop, target = ref * (1 - sp["stop_pct"] / 100), ref * (1 + sp["take_profit_pct"] / 100)
                st.positions[t] = {"ticker": t, "qty": q, "entry_price": px, "entry_ref": ref, "stop": stop, "entry_time": bt, "target": target, "held": 0}
                ss["trades"] += 1
                events.append((bt, DayEvent("BUY", t, q, ref, px, bps, bt, "JEV_ENTRY",
                                            f"Jev put {it['p']:.2f} on reaching +{sp['take_profit_pct']}% before -{sp['stop_pct']}% within {sp['max_hold_minutes']} min "
                                            f"(decided {it['decided']}); stop {stop:.2f}, target {target:.2f}"), {"p": it["p"], "decided": it["decided"]}))
            ss["pending"] = still
            # 2) exits (stop first if a bar touches both: worst case)
            for t in list(st.positions):
                b = cur.get(t)
                if not b:
                    continue
                o, h, l, c, _ = b
                p = st.positions[t]
                p["held"] = p.get("held", 0) + (0 if p["entry_time"] == bt else 1)
                if o <= p["stop"]:
                    sell(t, o, "stop", "STOP_GAP", f"bar opened {o:.2f} below stop {p['stop']:.2f}")
                elif l <= p["stop"]:
                    sell(t, p["stop"], "stop", "STOP", f"low {l:.2f} hit stop {p['stop']:.2f}")
                elif h >= p["target"]:
                    sell(t, p["target"], "close", "TARGET", f"high {h:.2f} reached target {p['target']:.2f}")
                elif p["held"] >= sp["max_hold_minutes"]:
                    sell(t, c, "close", "TIME_EXIT", f"held {p['held']} minutes without reaching the target")
            # 3) Jev entry decisions on this completed bar
            if is_last:
                for t in list(st.positions):
                    b = cur.get(t)
                    sell(t, b[3] if b else st.positions[t]["entry_ref"], "close", "CLOSE_EXIT", "flat before the close")
                ss["pending"] = []
                st.closed = True
            elif bt <= entry_cut and len(st.positions) + len(ss["pending"]) < P["max_positions"]:
                cands = []
                for t in self.universe:
                    if t in st.positions or any(i["ticker"] == t for i in ss["pending"]) or t not in cur:
                        continue
                    f = self.features(hist[t])
                    if f and self.is_candidate(f):
                        cands.append((f["vol_ratio"], t, f))
                cands.sort(reverse=True)
                minute = int((dt.datetime.fromisoformat(bt) - session_open(S)).total_seconds() // 60)
                for _, t, f in cands[:sp["max_jev_calls_per_minute"]]:
                    if ss["calls"] >= sp["max_jev_calls_per_day"] or self.calls_this_run >= sp["max_jev_calls_per_run"]:
                        break
                    client = client or self._jev()
                    if client is None:
                        self.note("Jev unavailable (no key or SDK): no entries")
                        break
                    try:
                        p = self.ask_jev(client, t, f, minute)
                    except Exception as e:
                        self.L.issue("WARN", "jev", f"{type(e).__name__}: {e}"[:200], t)
                        self.calls_this_run += 1
                        continue
                    ss["calls"] += 1
                    self.calls_this_run += 1
                    log_rows.append({"session": S.isoformat(), "bar": bt, "ticker": t, "p": p, "price": f["price"], "r5": round(f["r5"], 5),
                                     "vol_ratio": round(f["vol_ratio"], 2)})
                    if p >= sp["buy_threshold"]:
                        ss["pending"].append({"ticker": t, "p": p, "decided": bt, "wait": 1 + sp["entry_delay_bars"]})
            st.processed_through = bt
            if st.closed:
                break
        if not st.closed and self.now >= close_t + dt.timedelta(minutes=30):
            lastpx = {t: h[-1][4] for t, h in hist.items() if h}
            for t in list(st.positions):
                p = st.positions.pop(t)
                bps = cost_bps(self.cfg, 1e10, "close")
                px = lastpx.get(t, p["entry_ref"]) * (1 - bps / 1e4)
                st.cash += p["qty"] * px
                events.append((last_start, DayEvent("SELL", t, p["qty"], lastpx.get(t, p["entry_ref"]), px, bps, last_start, "CLOSE_EXIT",
                                                    "bars missing after the close: flattened at the last known price", (px - p["entry_price"]) * p["qty"]), {}))
            self.L.issue("WARN", "marketdata", f"{S}: final 1-minute bars missing; positions closed at last available prices")
            st.closed = True
        with self.L.tx():
            for bt, e, meta in events:
                key = f"{S}:speed:{e.ticker}:{e.kind}:{bt}"
                f = Fill(key, e.ticker, e.kind, e.qty, e.ref_price, e.fill_price, e.cost_bps, e.qty * abs(e.fill_price - e.ref_price),
                         S.isoformat(), bt, "yahoo_1m_bar", "speed", e.reason_code, e.reason, e.realized_pnl)
                self.L.ensure_order_row(key, f, bt)
                if self.L.record_fill(f):
                    self.L.set_order_status(key, "FILLED", f"{e.kind} {e.qty:.6f} {e.ticker} @ {e.fill_price:.4f}")
                    self.L.insert_decision(f"{S}:sp:{e.kind}:{e.ticker}:{bt}", bt, S.isoformat(),
                                           Decision(e.ticker, "speed", e.kind, e.reason_code, e.reason, meta), iso(self.now))
            self.L.set_state("cash", st.cash)
            self._save_positions(st, S)
            self.L.set_state(f"dt:{S}", st.to_json())
            self.L.set_state(f"sp:{S}", ss)
            if st.closed:
                self._snapshot(S, st)
        if log_rows and self.root is not None:
            path = self.root / LOG
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "a") as fh:
                fh.writelines(json.dumps(r) + "\n" for r in log_rows)
        n = len([1 for _, e, _ in events if e.kind == "BUY"])
        self.note(f"{S}: {n} buys, {len(events) - n} sells this run; {ss['calls']} Jev calls today, {ss['trades']} trades today")
