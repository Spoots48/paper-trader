"""Live paper engine for the market-maker book (engine = "mm"). Never places real orders.

Each run: settle finished markets -> resolve expired quotes against the public trade tape -> check loss
limits -> post new 5-minute quotes on the live BTC/ETH Up/Down markets -> mark -> daily snapshot.
"""
from __future__ import annotations

import datetime as dt
import json

from .broker import Fill as LFill, Order
from .entry_protections import ledger_cooldown
from .mm import plan_quotes, quote_prices, simulate_fill
from .nyse_calendar import ET, iso
from .pm_engine import _ts
from .pm_engine2 import PMEngine2
from .strategy import Decision

DATA = "https://data-api.polymarket.com"


class MMEngine(PMEngine2):
    def step(self) -> str:
        if self.L.get_state("experiment_finished"):
            return "experiment finished; nothing to do"
        self.now = self.clock()
        today = self.now.astimezone(ET).date()
        if today < self.start:
            return f"starts {self.start}"
        self.process_orders()
        self.settle()
        marks_ok = self.mark()
        positions = self.L.get_state("pm_positions", {}) or {}
        cash = self.L.get_state("cash", self.cash0)
        why = self.risk_gate(positions, cash)
        if not self.L.get_state("strategy_integrity_ok", True):
            why = "strategy integrity check failed"
        elif not marks_ok:
            why = "current position marks unavailable"
        if why:
            self.note(f"no new quotes: {why}")
            self.process_orders(cancel=True)
        elif today <= self.end and not self.retired:
            self.quote(positions, cash)
        self.mark()
        self.snapshot()
        return "; ".join(self.log) or "no action needed"

    def settle(self) -> None:
        pending = {o["slug"] for o in self.L.get_state("mm_orders", []) or []}
        super().settle(pending_slugs=pending)

    # ------------------------------------------------------------------ fills
    def trades(self, cid: str, since: int) -> list[dict]:
        out, off = [], 0
        while off <= 3000:
            tr = self.get(f"{DATA}/trades", market=cid, limit=500, offset=off, takerOnly="true")
            if not tr:
                break
            out += tr
            if min(int(t["timestamp"]) for t in tr) <= since:
                break
            off += 500
        if off > 3000:
            raise ValueError("trade tape pagination did not reach quote placement time")
        return out

    def process_orders(self, cancel: bool = False) -> None:
        with self.L.tx():
            self._process_orders(cancel)

    def _process_orders(self, cancel: bool) -> None:
        orders = self.L.get_state("mm_orders", []) or []
        now_ts = int(self.now.timestamp())
        keep = []
        R = self.cfg["rebates"]
        for original in orders:
            od = dict(original)
            if cancel:
                od["expires_at"] = min(now_ts, od["expires_at"])
            if now_ts < od["expires_at"]:
                keep.append(od)
                continue
            try:
                trades = self.trades(od["cid"], od["placed_at"])
            except Exception as e:
                self.L.issue("WARN", "marketmaker", f"trade tape unavailable for {od['slug']}; reservation retained: {e}")
                keep.append(od)
                continue
            filled = simulate_fill(od, trades)
            self.L.set_state("mm_reserved", max(0.0, self.L.get_state("mm_reserved", 0.0) - od["price"] * od["shares"]))
            if filled <= 0:
                self.L.set_order_status(od["key"], "EXPIRED", f"no fill: {od['queue_ahead']:.0f} shares were queued ahead")
                continue
            cash = self.L.get_state("cash", self.cash0) - filled * od["price"]
            reason = (f"{od['title']}: our bid for {od['outcome']} at {od['price']:.2f} was filled by sellers "
                      f"({filled:g} of {od['shares']:g} shares; {od['queue_ahead']:.0f} were queued ahead of us)")
            f = LFill(od["key"], od["label"], "BUY", filled, od["price"], od["price"], 0.0, 0.0,
                      self.now.astimezone(ET).date().isoformat(), dt.datetime.fromtimestamp(od["expires_at"], ET).isoformat(),
                      "polymarket_trade_tape", "predmarket", "MM_FILL", reason)
            if not self.L.record_fill(f):
                continue
            self.L.set_order_status(od["key"], "FILLED" if filled >= od["shares"] else "PARTIAL", f"{filled:g} shares")
            rebate = R["maker_share_of_taker_fee"] * R["taker_fee_rate"] * od["price"] * (1 - od["price"]) * filled
            if rebate > 0 and R.get("credit_estimates_to_cash", False):
                self.L.db.execute("INSERT OR IGNORE INTO dividends VALUES (?,?,?,?,?,?)",
                                  (f"REBATE {od['label']}", od["key"], rebate / filled, filled, rebate, iso(self.now)))
                cash += rebate
            positions = self.L.get_state("pm_positions", {}) or {}
            pk = f"{od['slug']}:{od['outcome']}"
            p = positions.get(pk) or {"slug": od["slug"], "side": od["outcome"], "label": od["label"], "title": od["title"],
                                      "shares": 0.0, "cost": 0.0, "end": od["end"], "token": od["token"], "entry_time": iso(self.now), "prob": None}
            p["shares"] = round(p["shares"] + filled, 2)
            p["cost"] += filled * od["price"]
            positions[pk] = p
            self.L.set_state("pm_positions", positions)
            self.L.set_state("cash", cash)
            self._save_positions(positions)
            self.L.insert_decision(f"mm:fill:{od['key']}", iso(self.now), f.session,
                                   Decision(od["label"], "predmarket", "BUY", "MM_FILL", reason + f"; est. rebate ${rebate:.4f}",
                                            {"filled": filled, "price": od["price"], "queue_ahead": od["queue_ahead"], "rebate": rebate}), iso(self.now))
            self.note(f"FILL {od['label']} {filled:g} @ {od['price']:.2f}")
        self.L.set_state("mm_orders", keep)


    # ------------------------------------------------------------------ quoting
    def quote(self, positions: dict, cash: float) -> None:
        with self.L.tx():
            self._quote(positions, cash)

    def _quote(self, positions: dict, cash: float) -> None:
        cfg, Mk, S = self.cfg, self.cfg["markets"], self.cfg["sizing"]
        equity = cash + sum(p.get("mark", p["cost"] / max(p["shares"], 1e-9)) * p["shares"] for p in positions.values())
        reserved = self.L.get_state("mm_reserved", 0.0)
        orders = self.L.get_state("mm_orders", []) or []
        resting = {o["slug"] for o in orders}
        now_ts = int(self.now.timestamp())
        lock = ledger_cooldown(self.L, self.clock(), cfg.get("protections", {}))
        quoted, notes = 0, []
        for name, asset in Mk["assets"].items():
            for minutes in Mk["windows_minutes"]:
                if quoted >= S["max_markets_per_run"]:
                    break
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
                elapsed = (self.now - start).total_seconds() / (end - start).total_seconds()
                left = (end - self.now).total_seconds() / 60
                if not (0 <= elapsed <= Mk["max_elapsed_fraction"] and left >= Mk["min_minutes_remaining"]):
                    notes.append(f"{ev['slug']}: {elapsed:.0%} elapsed, not quoting")
                    continue
                if ev["slug"] in resting:
                    continue
                if lock and not any(p['slug']==ev['slug'] for p in positions.values()):
                    notes.append(f"{ev['slug']}: entry cooldown until {lock['until']}")
                    continue
                outs, toks = json.loads(m["outcomes"]), json.loads(m["clobTokenIds"])
                try:
                    books = {o: self.book(t) for o, t in zip(outs, toks)}
                except Exception as e:
                    self.L.issue("WARN", "marketmaker", f"order book unavailable for {ev['slug']}: {e}")
                    continue
                if set(outs) != {'Up', 'Down'} or not self.entry_quality(ev['slug'], toks):
                    continue
                elapsed = (self.now-start).total_seconds()/(end-start).total_seconds()
                if not (0 <= elapsed <= Mk['max_elapsed_fraction'] and (end-self.now).total_seconds() >= Mk['min_minutes_remaining']*60):
                    continue
                now_ts = int(self.now.timestamp())
                bb = {o: max((p for p, _ in b[1]), default=None) for o, b in books.items()}
                ba = {o: min((p for p, _ in b[0]), default=None) for o, b in books.items()}
                qp = quote_prices(bb.get("Up"), ba.get("Up"), bb.get("Down"), ba.get("Down"), cfg)
                if not qp:
                    notes.append(f"{ev['slug']}: best bids {bb.get('Up')}+{bb.get('Down')} leave no room under $1")
                    continue
                plan = plan_quotes(ev['slug'], qp, positions, orders, cash, equity,
                                   self.L.get_state('pm_day')['protected_floor'], cfg)
                if not plan:
                    notes.append(f"{ev['slug']}: skipped: inventory, minimum size or capital-at-risk limit")
                    continue
                sides = list(plan)
                placed = 0
                # Both legs have been checked as one batch before either is placed.
                for side, shares in plan.items():
                    price = qp[side]
                    queue = 0.0 if qp["improved"][side] else sum(s for p, s in books[side][1] if abs(p - price) < 1e-9)
                    label = f"{name} {'1h' if minutes == 60 else '15m'} {start.astimezone(ET).strftime('%H:%M')} {side}"
                    od = {"key": f"mm:{ev['slug']}:{side}:{now_ts}", "slug": ev["slug"], "cid": m["conditionId"], "token": toks[outs.index(side)],
                          "outcome": side, "price": price, "shares": shares, "queue_ahead": queue, "placed_at": now_ts,
                          "expires_at": min(int(end.timestamp()), now_ts + int(cfg["quoting"]["order_lifetime_minutes"] * 60)), "end": m["endDate"],
                          "title": ev["title"], "label": label}
                    self.L.insert_order(Order(key=od["key"], ticker=label, side="BUY", order_type="PM_LIMIT_GTD",
                                              session=self.now.astimezone(ET).date().isoformat(), created_at=iso(self.now), sleeve="predmarket",
                                              reason_code="MM_QUOTE", reason=f"passive bid {price:.2f} for {side}; {queue:.0f} shares ahead at this price; midpoint spread floor {cfg['quoting'].get('min_midpoint_distance', 0):.3f}; expires in {cfg['quoting']['order_lifetime_minutes']} min",
                                              notional=price * shares, meta={"queue_ahead": queue}))
                    orders.append(od)
                    reserved += price * shares
                    self.L.set_state("mm_orders", orders)
                    self.L.set_state("mm_reserved", reserved)
                    placed += 1
                if placed:
                    quoted += 1
                    notes.append(f"{ev['slug']}: quoted {', '.join(sides)} at {qp['Up']:.2f}/{qp['Down']:.2f} (pair costs {qp['Up'] + qp['Down']:.2f})")
        self.L.insert_decision(f"mm:quote:{iso(self.now)}", iso(self.now), self.now.astimezone(ET).date().isoformat(), Decision(
                "*", "predmarket", "INFO", "MM_QUOTES", f"quoted {quoted} market(s)" + (": " + "; ".join(notes[:6]) if notes else ""),
                {"notes": notes}), iso(self.now))
