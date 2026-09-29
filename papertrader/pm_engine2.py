"""Live paper engine for crypto odds bot v2 (see config/strategy_pm_v2.json). Never places real orders."""
from __future__ import annotations

import datetime as dt
import json
import math

from .broker import Fill as LFill, Order
from .nyse_calendar import ET, iso
from .pm2 import decide_v2, sigma_from_closes
from .market_quality import closed_closes, parse_klines
from .entry_protections import ledger_cooldown
from .pm_engine import PMEngine, _ts
from .pm_risk import marked_equity, protected_floor, settlement_floor
from .predmarket import walk_book
from .strategy import Decision

BINANCE = "https://data-api.binance.vision/api/v3"


class PMEngine2(PMEngine):
    def prices(self, symbol: str) -> dict:
        available_at = self.clock().timestamp()
        k = self.get(f"{BINANCE}/klines", symbol=symbol, interval="1m", limit=300)
        # A partial candle cannot become complete merely while later requests are running.
        candles = {t: bar for t,bar in parse_klines(k).items() if t+60 <= available_at}
        # Timestamped public trade, rather than a price-only ticker with unknown age.
        tick = self.get(f"{BINANCE}/trades", symbol=symbol, limit=1)[-1]
        price = float(tick['price'])
        if not math.isfinite(price) or price <= 0:
            raise ValueError('invalid underlying trade price')
        return {"candles": candles, "s_now": price, "tick_time": float(tick['time'])/1000}

    def risk_gate(self, positions: dict, cash: float) -> str | None:
        """Checked every run (v1 only checked once a day, which is why its loss limit never fired)."""
        R = self.cfg["risk"]
        equity = marked_equity(cash, positions)
        risk = self.L.get_state("risk", {"peak": self.cash0})
        risk["peak"] = max(risk.get("peak", self.cash0), equity)
        dd = 1 - equity / risk["peak"]
        today = self.now.astimezone(ET).date().isoformat()
        day = self.L.get_state("pm_day", {})
        if day.get("date") != today:
            day = {"date": today, "start_equity": equity}
        day["peak"] = max(day.get("peak", day["start_equity"]), equity)
        why = day.get("stop_reason")
        if risk.get("halt_until"):
            why = "drawdown halt active"
        elif dd >= R["drawdown_halt"]:
            risk["halt_until"] = self.end.isoformat()
            self.L.issue("CRITICAL", "risk", f"crypto bot v2 drawdown {dd:.1%}: no new bets for the rest of the experiment")
            why = "drawdown halt triggered"
        elif why:
            pass  # once tripped, the daily stop survives recoveries and restarts
        elif equity <= day["start_equity"] * (1 - R["daily_loss_limit"]):
            why = f"daily loss limit: down {1 - equity / day['start_equity']:.1%} today"
        elif equity <= protected_floor(risk, day, R):
            why = "daily profit protection: half of the peak gain given back"
        if why and not day.get("stop_reason"):
            day["stop_reason"] = why
            self.L.event("risk_stop", {"reason": why, "equity": equity, "date": today})
        day["protected_floor"] = protected_floor(risk, day, R)
        risk["drawdown"] = dd
        with self.L.tx():
            self.L.set_state("risk", risk)
            self.L.set_state("pm_day", day)
        return why

    def scan(self, positions: dict, cash: float) -> None:
        cfg, Mk, M = self.cfg, self.cfg["markets"], self.cfg["model"]
        self.now = self.clock()
        why = self.risk_gate(positions, cash)
        if why:
            self.note(f"no new bets: {why}")
            return
        lock = ledger_cooldown(self.L, self.now, cfg.get('protections', {}))
        if lock:
            self.note(f"entry cooldown until {lock['until']}: {lock['reason']}")
            return
        equity = marked_equity(cash, positions)
        exposure = sum(p["cost"] for p in positions.values())
        taken = {(p["end"], p["side"]) for p in positions.values()}
        scanned, trades = [], 0
        for name, asset in Mk["assets"].items():
            try:
                px = self.prices(asset["binance"])
            except Exception as e:
                self.L.issue("WARN", "predmarket", f"{name} Binance prices unavailable: {e}")
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
                key = ev["slug"]
                if any(k.startswith(key + ":") for k in positions) or self.L.db.execute(
                        "SELECT 1 FROM orders WHERE order_key LIKE ?", (f"pm:{key}:%",)).fetchone():
                    continue
                t0 = int(start.timestamp())
                if t0 not in px["candles"]:
                    continue
                if not math.isfinite(px['candles'][t0][0]) or px['candles'][t0][0] <= 0:
                    continue
                outs, toks = json.loads(m["outcomes"]), json.loads(m["clobTokenIds"])
                try:
                    books = {o: self.book(t) for o, t in zip(outs, toks)}
                except Exception as e:
                    self.L.issue("WARN", "predmarket", f"order book unavailable for {key}: {e}")
                    continue
                if set(outs) != {'Up', 'Down'} or not self.entry_quality(key, toks, px.get('tick_time'), require_underlying=True):
                    continue
                if not (start <= self.now < end-dt.timedelta(seconds=Mk['min_seconds_remaining'])):
                    continue
                try:
                    closes = closed_closes(px['candles'], self.now, M['vol_lookback_minutes'])
                except ValueError as ex:
                    scanned.append({'market': key, 'result': str(ex)})
                    continue
                sigma = sigma_from_closes(closes, M['min_vol_per_minute'])
                asks = {o: min((p for p, _ in b[0]), default=None) for o, b in books.items()}
                bu = books.get("Up", ([], []))
                mid = (min(p for p, _ in bu[0]) + max(p for p, _ in bu[1])) / 2 if bu[0] and bu[1] else None
                elapsed = (self.now - start).total_seconds() / (end - start).total_seconds()
                d = decide_v2(px["candles"][t0][0], px["s_now"], (end - self.now).total_seconds() / 60, sigma, elapsed, asks, mid, cfg)
                scanned.append({"market": key, "mid_up": mid, "model_up": round(d.get("model_up", 0) or 0, 3),
                                "result": d.get("skip") or f"BET {d['side']} edge {d['edge']:+.3f}"})
                if "skip" in d:
                    continue
                if (m["endDate"], d["side"]) in taken:
                    scanned[-1]["result"] = "skipped: already betting this direction for this settlement time (BTC and ETH move together)"
                    continue
                depth = sum(p * s for p, s in books[d["side"]][0] if p <= d["ask"] + 0.02)
                if depth < cfg["entry"]["min_depth_usd"]:
                    scanned[-1]["result"] = f"skipped: only ${depth:.0f} available near the best price"
                    continue
                S = cfg["sizing"]
                floor = self.L.get_state("pm_day")["protected_floor"]
                headroom = max(0.0, settlement_floor(cash, positions) - floor)
                stake = min(S["per_bet_fraction"] * equity, S["max_open_exposure"] * equity - exposure, cash, headroom)
                fill = walk_book(books[d["side"]][0], d["q"], stake, cfg["entry"]["min_edge"], cfg["fees"]["crypto_taker_fee_rate"])
                if not fill or fill.shares < cfg["portfolio"]["min_shares"]:
                    scanned[-1]["result"] = "skipped: remaining risk/cash budget cannot fund the 5-share minimum"
                    continue
                label = f"{name} {'1h' if minutes == 60 else ev['slug'].split('-')[2]} {start.astimezone(ET).strftime('%H:%M')} {d['side']}"
                okey = f"pm:{key}:{d['side']}:BUY"
                reason = (f"{ev['title']}: estimated chance of {d['side']} {d['q']:.0%} (model {d['model_up']:.0%} Up, market {d['mid_up']:.0%} Up) "
                          f"vs cost {d['unit']:.3f} incl. fee → edge {d['edge']:+.3f}; {name} {px['s_now']:,.2f} vs open {px['candles'][t0][0]:,.2f}, "
                          f"{elapsed:.0%} of window elapsed")
                with self.L.tx():
                    self.L.insert_order(Order(key=okey, ticker=label, side="BUY", order_type="PM_MARKET", session=self.now.astimezone(ET).date().isoformat(),
                                              created_at=iso(self.now), sleeve="predmarket", reason_code="PM_ENTRY", reason=reason, notional=fill.cost,
                                              meta={"slug": key, "token": toks[outs.index(d['side'])]}))
                    f = LFill(okey, label, "BUY", fill.shares, fill.avg_price, fill.cost / fill.shares, 0.0, fill.fees,
                              self.now.astimezone(ET).date().isoformat(), iso(self.now), "polymarket_order_book", "predmarket", "PM_ENTRY", reason)
                    if self.L.record_fill(f):
                        self.L.set_order_status(okey, "FILLED", f"bought {fill.shares} shares")
                        cash -= fill.cost
                        exposure += fill.cost
                        taken.add((m["endDate"], d["side"]))
                        positions[f"{key}:{d['side']}"] = {"slug": key, "side": d["side"], "label": label, "title": ev["title"], "shares": fill.shares,
                                                           "cost": fill.cost, "end": m["endDate"], "token": toks[outs.index(d["side"])],
                                                           "entry_time": iso(self.now), "prob": d["q"]}
                        self.L.set_state("cash", cash)
                        self.L.set_state("pm_positions", positions)
                        self._save_positions(positions)
                        self.L.insert_decision(f"pm:{key}:{d['side']}", iso(self.now), f.session,
                                               Decision(label, "predmarket", "BUY", "PM_ENTRY", reason,
                                                        {k: (round(v, 4) if isinstance(v, float) else v) for k, v in d.items()}), iso(self.now))
                        trades += 1
                        self.note(f"BET {label} {fill.shares} @ {fill.avg_price:.3f} (edge {d['edge']:+.3f})")
        with self.L.tx():
            self.L.insert_decision(f"pm:scan:{iso(self.now)}", iso(self.now), self.now.astimezone(ET).date().isoformat(), Decision(
                "*", "predmarket", "INFO", "PM_SCAN", f"scanned {len(scanned)} live markets; {trades} bet(s).", {"scanned": scanned}), iso(self.now))
