"""Live paper engine for the prediction-market book (book_type = predmarket). Never places real orders.

Each run: 1) settle finished bets from Polymarket's official outcome, 2) scan the in-progress Up/Down
windows for each asset, 3) paper-buy when the conservative fair probability beats ask + fee by the
threshold (walking the real order book), 4) mark open bets at the current best bid, 5) daily snapshot.
Data: Polymarket Gamma + CLOB public APIs, Coinbase Exchange public API. No keys, no wallet.
"""
from __future__ import annotations

import datetime as dt
import json
import math
import time

import requests

from .broker import Fill as LFill
from .ledger import Ledger
from .nyse_calendar import ET, UTC, iso
from .predmarket import decide_market, kelly_budget, taker_fee_per_share, walk_book
from .strategy import Decision

GAMMA = "https://gamma-api.polymarket.com"
CLOB = "https://clob.polymarket.com"
COINBASE = "https://api.exchange.coinbase.com"
UA = {"User-Agent": "Mozilla/5.0 (PaperTradingSim; paper trading research)"}


def _get(url: str, **params):
    last = None
    for attempt in range(3):
        try:
            r = requests.get(url, params=params, headers=UA, timeout=15)
            if r.status_code == 200:
                return r.json()
            last = f"HTTP {r.status_code}"
        except Exception as e:  # retried; persistent failures surface as data issues
            last = f"{type(e).__name__}: {e}"
        time.sleep(1 + attempt)
    raise RuntimeError(f"{url}: {last}")


def _ts(s: str) -> dt.datetime:
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(UTC)


class PMEngine:
    def __init__(self, ledger: Ledger, md, cfg: dict, exp: dict, now: dt.datetime, fetch=None):
        self.L, self.cfg, self.now = ledger, cfg, now
        e = ledger.experiment()
        self.start = dt.date.fromisoformat(e["start_date"])
        self.end = dt.date.fromisoformat(e["end_date"])
        self.cash0 = e["starting_cash"]
        self.get = fetch or _get
        self.log: list[str] = []

    def note(self, m: str) -> None:
        self.log.append(m)

    # ------------------------------------------------------------------ data
    def slugs(self, asset: dict, minutes: int) -> list[str]:
        t = int(self.now.timestamp())
        if minutes in (5, 15, 240):
            step = minutes * 60
            return [f"{asset['short']}-updown-{ {5: '5m', 15: '15m', 240: '4h'}[minutes]}-{t // step * step}"]
        et = self.now.astimezone(ET).replace(minute=0, second=0, microsecond=0)
        h = et.hour % 12 or 12
        base = f"{asset['long']}-up-or-down-{et.strftime('%B').lower()}-{et.day}-{et.year}-{h}{'am' if et.hour < 12 else 'pm'}"
        return [base + "-et", base]

    def event(self, slug: str) -> dict | None:
        ev = self.get(f"{GAMMA}/events", slug=slug)
        return ev[0] if ev else None

    def book(self, token: str) -> tuple[list, list]:
        b = self.get(f"{CLOB}/book", token_id=token)
        asks = [(float(x["price"]), float(x["size"])) for x in b.get("asks", [])]
        bids = [(float(x["price"]), float(x["size"])) for x in b.get("bids", [])]
        return asks, bids

    def prices(self, product: str) -> dict:
        end = self.now.replace(second=0, microsecond=0)
        c = self.get(f"{COINBASE}/products/{product}/candles", granularity=60,
                     start=iso(end - dt.timedelta(minutes=299)), end=iso(end))
        candles = sorted((int(r[0]), float(r[3]), float(r[4])) for r in c)  # (bucket start, open, close)
        tick = self.get(f"{COINBASE}/products/{product}/ticker")
        return {"candles": candles, "s_now": float(tick["price"]), "tick_time": tick.get("time")}

    def context(self, px: dict, start: dt.datetime, end: dt.datetime) -> dict | None:
        M = self.cfg["model"]
        cs = px["candles"]
        t0 = int(start.timestamp())
        first = [c for c in cs if c[0] == t0]
        if not first:
            return None
        inside = [c for c in cs if t0 <= c[0] and c[0] + 60 <= self.now.timestamp()]
        closes = [c[2] for c in inside] or [first[0][1]]
        rets = [math.log(b[2] / a[2]) for a, b in zip(cs[-M["vol_lookback_minutes"] - 1:-1], cs[-M["vol_lookback_minutes"]:])]
        sd = (sum((r - sum(rets) / len(rets)) ** 2 for r in rets) / max(len(rets) - 1, 1)) ** 0.5 if len(rets) > 5 else 0
        total = (end - start).total_seconds()
        return {"s0": first[0][1], "avg": sum(closes) / len(closes), "s_now": px["s_now"],
                "elapsed": (self.now - start).total_seconds() / total,
                "minutes_left": (end - self.now).total_seconds() / 60, "sigma": max(sd, M["min_vol_per_minute"])}

    # ------------------------------------------------------------------ main
    def step(self) -> str:
        if self.L.get_state("experiment_finished"):
            return "experiment finished; nothing to do"
        today = self.now.astimezone(ET).date()
        if today < self.start:
            return f"starts {self.start}"
        self.settle()
        positions = self.L.get_state("pm_positions", {}) or {}
        cash = self.L.get_state("cash", self.cash0)
        risk = self.L.get_state("risk", {"peak": self.cash0})
        if today <= self.end and not risk.get("halt_until"):
            self.scan(positions, cash)
        self.mark()
        self.snapshot()
        return "; ".join(self.log) or "no action needed"

    def settle(self) -> None:
        positions = self.L.get_state("pm_positions", {}) or {}
        for key, p in list(positions.items()):
            if self.now < _ts(p["end"]) + dt.timedelta(minutes=1):
                continue
            try:
                ev = self.event(p["slug"])
            except Exception as e:
                self.L.issue("WARN", "predmarket", f"could not check settlement for {p['slug']}: {e}")
                continue
            m = (ev or {}).get("markets", [{}])[0]
            outs = json.loads(m.get("outcomes") or "[]")
            px = json.loads(m.get("outcomePrices") or "[]")
            if not (m.get("closed") and outs and px and max(float(x) for x in px) >= 0.99):
                if self.now > _ts(p["end"]) + dt.timedelta(hours=24):
                    self.L.issue("WARN", "predmarket", f"{p['slug']} still unresolved 24h after its window ended")
                continue
            won = float(px[outs.index(p["side"])]) >= 0.99
            payout = p["shares"] * (1.0 if won else 0.0)
            with self.L.tx():
                cash = self.L.get_state("cash", self.cash0) + payout
                f = LFill(f"pm:{p['slug']}:{p['side']}:SETTLE", p["label"], "SELL", p["shares"], 1.0 if won else 0.0,
                          1.0 if won else 0.0, 0.0, 0.0, self.now.astimezone(ET).date().isoformat(), p["end"],
                          "polymarket_resolution", "predmarket", "PM_WIN" if won else "PM_LOSS",
                          f"{p['title']}: settled {outs[[float(x) for x in px].index(max(float(x) for x in px))]}",
                          payout - p["cost"])
                self.L.ensure_order_row(f.order_key, f, iso(self.now))
                if self.L.record_fill(f):
                    self.L.set_order_status(f.order_key, "FILLED", "settled")
                    positions.pop(key)
                    self.L.set_state("cash", cash)
                    self.L.set_state("pm_positions", positions)
                    self._save_positions(positions)
                    self.note(f"{'WON' if won else 'LOST'} {p['label']} {payout - p['cost']:+.2f}")

    def scan(self, positions: dict, cash: float) -> None:
        cfg, Mk = self.cfg, self.cfg["markets"]
        equity = cash + sum(p.get("mark", p["cost"] / p["shares"]) * p["shares"] for p in positions.values())
        exposure = sum(p["cost"] for p in positions.values())
        scanned, trades = [], 0
        for name, asset in Mk["assets"].items():
            try:
                px = self.prices(asset["coinbase"])
            except Exception as e:
                self.L.issue("WARN", "predmarket", f"{name} prices unavailable: {e}")
                continue
            for minutes in Mk["windows_minutes"]:
                ev = None
                for slug in self.slugs(asset, minutes):
                    try:
                        ev = self.event(slug)
                    except Exception:
                        ev = None
                    if ev:
                        break
                if not ev or not ev.get("markets"):
                    continue
                m = ev["markets"][0]
                if not m.get("eventStartTime") or not m.get("acceptingOrders", True):
                    continue
                start, end = _ts(m["eventStartTime"]), _ts(m["endDate"])
                if not (start <= self.now < end - dt.timedelta(seconds=Mk["min_seconds_remaining"])):
                    continue
                ctx = self.context(px, start, end)
                if not ctx or ctx["elapsed"] < Mk["min_elapsed_fraction"]:
                    continue
                key = f"{ev['slug']}"
                if any(k.startswith(key + ":") for k in positions) or self.L.db.execute(
                        "SELECT 1 FROM orders WHERE order_key LIKE ?", (f"pm:{key}:%",)).fetchone():
                    continue
                outs, toks = json.loads(m["outcomes"]), json.loads(m["clobTokenIds"])
                books = {}
                try:
                    for o, t in zip(outs, toks):
                        books[o] = self.book(t)
                except Exception as e:
                    self.L.issue("WARN", "predmarket", f"order book unavailable for {key}: {e}")
                    continue
                d = decide_market({"asks": {o: b[0] for o, b in books.items()}}, ctx, cfg)
                best = d["best"]
                scanned.append({"market": key, "p_up": round(d["p_up_model"], 3),
                                "best_side": best and best["side"], "edge": best and round(best["edge"], 3)})
                if not best or best["edge"] < cfg["entry"]["min_edge"]:
                    continue
                budget = kelly_budget(best["prob"], best["unit_cost"], equity, cfg, exposure)
                budget = min(budget, cash)
                fill = walk_book(books[best["side"]][0], best["prob"], budget, cfg["entry"]["min_edge"], cfg["fees"]["crypto_taker_fee_rate"])
                if not fill or fill.shares < cfg["portfolio"]["min_shares"]:
                    continue
                label = f"{name} {ev['slug'].split('-')[2] if 'updown' in ev['slug'] else '1h'} {start.astimezone(ET).strftime('%H:%M')} {best['side']}"
                okey = f"pm:{key}:{best['side']}:BUY"
                reason = (f"{ev['title']}: fair chance of {best['side']} {best['prob']:.0%} vs price {best['best_ask']:.2f} + fee "
                          f"{taker_fee_per_share(best['best_ask'], cfg['fees']['crypto_taker_fee_rate']):.3f} → edge {best['edge']:.2f}; "
                          f"{name} {ctx['s_now']:,.2f} vs start {ctx['s0']:,.2f}, {ctx['elapsed']:.0%} of window elapsed")
                metrics = {**{k: round(v, 6) if isinstance(v, float) else v for k, v in ctx.items()}, **{k: (round(v, 4) if isinstance(v, float) else v) for k, v in best.items()},
                           "shares": fill.shares, "cost": round(fill.cost, 4), "fees": round(fill.fees, 4), "book_levels": fill.levels}
                with self.L.tx():
                    from .broker import Order
                    self.L.insert_order(Order(key=okey, ticker=label, side="BUY", order_type="PM_MARKET", session=self.now.astimezone(ET).date().isoformat(),
                                              created_at=iso(self.now), sleeve="predmarket", reason_code="PM_ENTRY", reason=reason, notional=fill.cost,
                                              meta={"slug": key, "token": toks[outs.index(best['side'])]}))
                    f = LFill(okey, label, "BUY", fill.shares, fill.avg_price, fill.cost / fill.shares, 0.0, fill.fees,
                              self.now.astimezone(ET).date().isoformat(), iso(self.now), "polymarket_order_book", "predmarket",
                              "PM_ENTRY", reason)
                    if self.L.record_fill(f):
                        self.L.set_order_status(okey, "FILLED", f"bought {fill.shares} shares")
                        cash -= fill.cost
                        exposure += fill.cost
                        positions[f"{key}:{best['side']}"] = {
                            "slug": key, "side": best["side"], "label": label, "title": ev["title"], "shares": fill.shares,
                            "cost": fill.cost, "end": m["endDate"], "token": toks[outs.index(best["side"])], "entry_time": iso(self.now),
                            "prob": best["prob"]}
                        self.L.set_state("cash", cash)
                        self.L.set_state("pm_positions", positions)
                        self._save_positions(positions)
                        self.L.insert_decision(f"pm:{key}:{best['side']}", iso(self.now), f.session,
                                               Decision(label, "predmarket", "BUY", "PM_ENTRY", reason, metrics), iso(self.now))
                        trades += 1
                        self.note(f"BET {label} {fill.shares} @ {fill.avg_price:.3f} (edge {best['edge']:.2f})")
        if scanned:
            top = sorted([s for s in scanned if s["edge"] is not None], key=lambda s: -s["edge"])[:5]
            with self.L.tx():
                self.L.insert_decision(f"pm:scan:{iso(self.now)}", iso(self.now), self.now.astimezone(ET).date().isoformat(), Decision(
                    "*", "predmarket", "INFO", "PM_SCAN",
                    f"scanned {len(scanned)} live markets; {trades} bet(s). Best gaps: " +
                    ", ".join(f"{s['market']} {s['best_side']} {s['edge']:+.2f}" for s in top), {"scanned": scanned}), iso(self.now))

    def mark(self) -> None:
        positions = self.L.get_state("pm_positions", {}) or {}
        marks = {}
        for k, p in positions.items():
            try:
                _, bids = self.book(p["token"])
                bid = max((b for b, _ in bids), default=0.0)
            except Exception:
                continue
            p["mark"] = bid
            marks[p["label"]] = (bid, iso(self.now))
        with self.L.tx():
            self.L.set_state("pm_positions", positions)
            self._save_positions(positions)
            self.L.set_state("live_marks", {"as_of": iso(self.now), "marks": marks})

    def _save_positions(self, positions: dict) -> None:
        self.L.db.execute("DELETE FROM positions")
        for p in positions.values():
            self.L.db.execute(
                "INSERT INTO positions (ticker, qty, avg_cost, sleeve, entry_session, entry_price, initial_stop, trail_pct, high_water, "
                "max_hold_until, stop_checked_through, meta) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                (p["label"], p["shares"], p["cost"] / p["shares"], "predmarket", p["entry_time"][:10], p["cost"] / p["shares"], None, None,
                 p["cost"] / p["shares"], p["end"][:10], None, json.dumps({k: p[k] for k in ("slug", "side", "title", "end", "prob")})))

    def snapshot(self) -> None:
        """One end-of-day valuation per ET calendar date, written at the first run after midnight ET."""
        today = self.now.astimezone(ET).date()
        day = today - dt.timedelta(days=1)
        if day < self.start or self.L.db.execute("SELECT 1 FROM snapshots WHERE session=?", (day.isoformat(),)).fetchone():
            return
        positions = self.L.get_state("pm_positions", {}) or {}
        cash = self.L.get_state("cash", self.cash0)
        pos_val = sum(p.get("mark", 0.0) * p["shares"] for p in positions.values())
        equity = cash + pos_val
        risk = self.L.get_state("risk", {"peak": self.cash0})
        risk["peak"] = max(risk.get("peak", self.cash0), equity)
        dd = 1 - equity / risk["peak"]
        if dd >= self.cfg["risk"]["drawdown_halt"] and not risk.get("halt_until"):
            risk["halt_until"] = self.end.isoformat()
            self.L.issue("CRITICAL", "risk", f"prediction-market drawdown {dd:.1%}: no new bets for the rest of the experiment")
        risk["drawdown"] = dd
        with self.L.tx():
            self.L.set_state("risk", risk)
            self.L.insert_snapshot({"session": day.isoformat(), "created_at": iso(self.now), "run_id": self.L.run_id, "equity": equity,
                                    "cash": cash, "positions_value": pos_val, "spy_bh_equity": None, "cash_bh_equity": self.cash0,
                                    "peak": risk["peak"], "drawdown": dd, "regime": f"{len(positions)} open bets", "risk_state": json.dumps(risk),
                                    "marks": json.dumps({"marks": {}, "flags": {}}), "holdings": json.dumps({})})
