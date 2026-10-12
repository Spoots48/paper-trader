"""Live paper engine for the memecoin book (book_type = meme). Never places real orders: no wallet, no keys.

Each run: fetch candidates (GeckoTerminal trending, DexScreener boosts/profiles) and prices -> manage open positions (exits at the price seen now)
-> apply risk gates -> enter new momentum candidates that pass the screen and the rug check -> daily snapshot. All rules are in meme.py and
config/strategy_meme_v1.json. Fills carry the modeled friction in their price so cash reconciles exactly from the fills table."""
from __future__ import annotations

import datetime as dt
import json

from . import meme
from .broker import Fill as LFill, Order
from .nyse_calendar import ET, iso
from .pm_engine import _get

GECKO = "https://api.geckoterminal.com/api/v2"
DEX = "https://api.dexscreener.com"
RUG = "https://api.rugcheck.xyz/v1/tokens"
SOURCE = "dexscreener_pair_price"


class MemeEngine:
    def __init__(self, ledger, md, cfg: dict, exp: dict, now: dt.datetime, fetch=None):
        self.L, self.cfg, self.now = ledger, cfg, now
        e = ledger.experiment()
        self.start = dt.date.fromisoformat(e["start_date"])
        self.end = dt.date.fromisoformat(e["end_date"])
        self.cash0 = e["starting_cash"]
        self.get = fetch or _get
        self.log: list[str] = []
        self.session = now.astimezone(ET).date().isoformat()

    def note(self, m: str) -> None:
        self.log.append(m)

    # ------------------------------------------------------------------ data
    def candidates(self) -> tuple[list[str], dict[str, int], set[str]]:
        rank: dict[str, int] = {}
        try:
            for i, p in enumerate(self.get(f"{GECKO}/networks/{self.cfg['screen']['chain']}/trending_pools", duration="1h")["data"], 1):
                rank[p["relationships"]["base_token"]["data"]["id"].split("_", 1)[1]] = i
        except Exception as ex:  # one source down must not stop the book: others still give candidates
            self.L.issue("WARN", "meme", f"trending pools unavailable: {type(ex).__name__}: {str(ex)[:120]}")
        social, extra = set(), []
        for path in ("token-boosts/latest/v1", "token-profiles/latest/v1"):
            try:
                for x in self.get(f"{DEX}/{path}") or []:
                    if x.get("chainId") != self.cfg["screen"]["chain"]:
                        continue
                    extra.append(x["tokenAddress"])
                    if any(link.get("type") == "twitter" for link in x.get("links") or []):
                        social.add(x["tokenAddress"])
            except Exception as ex:
                self.L.issue("WARN", "meme", f"{path} unavailable: {type(ex).__name__}: {str(ex)[:120]}")
        return list(dict.fromkeys(list(rank) + extra)), rank, social

    def pools(self, tokens: list[str], rank: dict, social: set) -> dict[str, dict]:
        out: dict[str, dict] = {}
        for i in range(0, len(tokens), 30):
            data = self.get(f"{DEX}/latest/dex/tokens/" + ",".join(tokens[i:i + 30]))
            for p in (data or {}).get("pairs") or []:
                tok = (p.get("baseToken") or {}).get("address")
                q = meme.pool_from_pair(p, social=tok in social, trending_rank=rank.get(tok))
                if q and q["chain"] == self.cfg["screen"]["chain"] and (tok not in out or q["liq"] > out[tok]["liq"]):
                    out[tok] = q
        return out

    def rug_summary(self, token: str) -> dict | None:
        cache = self.L.get_state("meme_rug", {}) or {}
        hit = cache.get(token)
        if hit and (self.now - dt.datetime.fromisoformat(hit["at"])).total_seconds() < 6 * 3600:
            return hit["summary"]
        try:
            summary = self.get(f"{RUG}/{token}/report/summary")
        except Exception:
            return None  # unknown is refused by rug_ok
        cache[token] = {"at": iso(self.now), "summary": {k: summary.get(k) for k in ("score", "score_normalised", "risks", "lpLockedPct")}}
        cache = dict(sorted(cache.items(), key=lambda kv: kv[1]["at"])[-200:])
        self.L.set_state("meme_rug", cache)
        return cache[token]["summary"]

    # ------------------------------------------------------------------ step
    def step(self) -> str:
        if self.L.get_state("experiment_finished"):
            return "experiment finished; nothing to do"
        today = self.now.astimezone(ET).date()
        if today < self.start:
            return f"starts {self.start}"
        P = self.cfg["portfolio"]
        positions = self.L.get_state("meme_positions", {}) or {}
        tokens, rank, social = self.candidates()
        want = list(dict.fromkeys(list(positions) + tokens))[:P["max_positions"] + self.cfg["data"]["max_candidates_per_run"] + len(positions)]
        pools = self.pools(want, rank, social) if want else {}
        self.manage(positions, pools, final=today >= self.end)
        if not self.L.get_state("strategy_integrity_ok", True):
            self.note("no new entries: strategy integrity check failed")
        elif today < self.end:
            self.enter(positions, pools, today)
        self.snapshot(positions)
        return "; ".join(self.log) or f"scanned {len(pools)} pools; nothing to do"

    # ------------------------------------------------------------------ exits
    def manage(self, positions: dict, pools: dict, final: bool) -> None:
        X = self.cfg["exit"]
        for tok in list(positions):
            pos = positions[tok]
            q = pools.get(tok)
            if q is None:
                pos["missing"] = pos.get("missing", 0) + 1
                if pos["missing"] >= X["write_off_after_missing_runs"]:
                    self.sell(positions, tok, 0.0, 0.0, "WRITE_OFF", "pool not found for several runs: written off at zero (likely rugged or delisted)")
                else:
                    self.note(f"{pos['symbol']}: pool not found this run ({pos['missing']}/{X['write_off_after_missing_runs']})")
                continue
            pos["missing"] = 0
            pos["mark"], pos["peak"], pos["liq"] = q["price"], max(pos["peak"], q["price"]), q["liq"]
            reason = "END_OF_EXPERIMENT" if final else meme.exit_signal(pos, q["price"], q["liq"], self.now, self.cfg)
            if reason:
                self.sell(positions, tok, q["price"], q["liq"], reason,
                          f"{reason}: price {q['price']:.8g} vs entry {pos['entry_price']:.8g} ({q['price'] / pos['entry_price'] - 1:+.1%}); liquidity ${q['liq']:,.0f}")
        self.L.set_state("meme_positions", positions)

    def sell(self, positions: dict, tok: str, price: float, liq: float, reason: str, why: str) -> None:
        pos = positions[tok]
        fr = meme.friction("SELL", pos["qty"] * price, liq, self.cfg, reason) if price > 0 else 0.0
        fill_price = price * max(1.0 - fr, 0.0)
        proceeds = pos["qty"] * fill_price
        key = f"meme:{tok}:{pos['entered_at']}:SELL"
        f = LFill(key, pos["label"], "SELL", pos["qty"], price, fill_price, round(fr * 1e4, 1), pos["qty"] * price * fr, self.session, iso(self.now),
                  SOURCE, "meme", reason, why, proceeds - pos["cost"])
        with self.L.tx():
            self.L.ensure_order_row(key, f, iso(self.now))
            if self.L.record_fill(f):
                self.L.set_order_status(key, "FILLED", reason)
                self.L.set_state("cash", self.L.get_state("cash", self.cash0) + proceeds)
                seen = self.L.get_state("meme_seen", {}) or {}
                seen[tok] = iso(self.now)
                self.L.set_state("meme_seen", seen)
                day = self.day_state()
                day["realized"] += proceeds - pos["cost"]
                self.L.set_state("meme_day", day)
                positions.pop(tok)
        self.note(f"sold {pos['symbol']} ({reason}) {proceeds - pos['cost']:+.2f}")

    # ------------------------------------------------------------------ entries
    def day_state(self) -> dict:
        d = self.L.get_state("meme_day", {}) or {}
        if d.get("date") != self.session:
            d = {"date": self.session, "entries": 0, "realized": 0.0}
        return d

    def equity(self, positions: dict) -> float:
        k = 1.0 - self.cfg["friction"]["exit_latency"] - self.cfg["friction"]["fee"]
        return self.L.get_state("cash", self.cash0) + sum(p["qty"] * p.get("mark", p["entry_price"]) * k for p in positions.values())

    def enter(self, positions: dict, pools: dict, today: dt.date) -> None:
        P, S = self.cfg["portfolio"], self.cfg["screen"]
        risk = self.L.get_state("risk", {"peak": self.cash0}) or {"peak": self.cash0}
        eq = self.equity(positions)
        risk["peak"] = max(risk.get("peak", self.cash0), eq)
        self.L.set_state("risk", risk)
        if 1 - eq / risk["peak"] >= P["drawdown_halt"]:
            self.note(f"no new entries: drawdown {1 - eq / risk['peak']:.0%} reached the halt level")
            return
        day = self.day_state()
        if day["realized"] <= -P["daily_loss_limit"] * self.cash0:
            self.note("no new entries: daily loss limit reached")
            return
        seen = self.L.get_state("meme_seen", {}) or {}
        ranked, skipped = [], {}
        for tok, q in pools.items():
            if tok in positions:
                continue
            if tok in seen and (self.now - dt.datetime.fromisoformat(seen[tok])).total_seconds() < P["cooldown_hours_per_token"] * 3600:
                continue
            why = meme.screen(q, self.now, self.cfg) or meme.entry_signal(q, self.cfg)
            if why:
                skipped[why.split(" ")[0]] = skipped.get(why.split(" ")[0], 0) + 1
                continue
            ranked.append(q)
        ranked.sort(key=lambda q: q["buys_h1"] / max(q["sells_h1"], 1.0), reverse=True)
        for q in ranked:
            if len(positions) >= P["max_positions"] or day["entries"] >= P["max_entries_per_day"]:
                break
            cash = self.L.get_state("cash", self.cash0)
            if cash < P["position_usd"]:
                self.note("no new entries: not enough cash")
                break
            ok, why = meme.rug_ok(self.rug_summary(q["token"]), self.cfg) if self.cfg["data"]["rugcheck"] else (True, "skipped")
            if not ok:
                self.note(f"skipped {q['symbol']}: {why}")
                continue
            self.buy(positions, q, day)
        self.L.set_state("meme_day", day)
        if skipped and not ranked:
            self.note("candidates screened out: " + ", ".join(f"{k} x{v}" for k, v in sorted(skipped.items(), key=lambda kv: -kv[1])[:4]))

    def buy(self, positions: dict, q: dict, day: dict) -> None:
        P = self.cfg["portfolio"]
        fr = meme.friction("BUY", P["position_usd"], q["liq"], self.cfg)
        fill_price = q["price"] * (1.0 + fr)
        qty = P["position_usd"] / fill_price
        label = f"{q['symbol']} {q['token'][:4]}…{q['token'][-4:]}"
        key = f"meme:{q['token']}:{iso(self.now)}:BUY"
        why = (f"momentum with attention: 1h {q['chg_h1']:+.0f}%, 5m {q['chg_m5']:+.1f}%, buys {q['buys_h1']:.0f} vs sells {q['sells_h1']:.0f}, "
               f"liquidity ${q['liq']:,.0f}, 24h volume ${q['vol_h24']:,.0f}, "
               f"{'X link on profile' if q['social'] else 'trending #' + str(q['trending_rank'])}; modeled friction {fr:.1%}")
        with self.L.tx():
            self.L.insert_order(Order(key=key, ticker=label, side="BUY", order_type="PAPER_MARKET", session=self.session, created_at=iso(self.now),
                                      sleeve="meme", reason_code="MEME_ENTRY", reason=why, notional=P["position_usd"], meta={"token": q["token"], "pair": q["pair"]}))
            f = LFill(key, label, "BUY", qty, q["price"], fill_price, round(fr * 1e4, 1), qty * q["price"] * fr, self.session, iso(self.now), SOURCE, "meme",
                      "MEME_ENTRY", why)
            if self.L.record_fill(f):
                self.L.set_order_status(key, "FILLED", f"bought {qty:.6g}")
                self.L.set_state("cash", self.L.get_state("cash", self.cash0) - qty * fill_price)
                positions[q["token"]] = {"symbol": q["symbol"], "label": label, "qty": qty, "cost": qty * fill_price, "entry_price": q["price"],
                                         "peak": q["price"], "mark": q["price"], "entered_at": iso(self.now), "entry_liq": q["liq"], "liq": q["liq"],
                                         "pair": q["pair"], "missing": 0}
                day["entries"] += 1
        self.L.set_state("meme_positions", positions)
        self.note(f"bought {q['symbol']} ${P['position_usd']:.2f}")

    # ------------------------------------------------------------------ snapshot
    def snapshot(self, positions: dict) -> None:
        """One end-of-day valuation per ET calendar date, written at the first run after midnight ET (same convention as the other crypto books)."""
        day = self.now.astimezone(ET).date() - dt.timedelta(days=1)
        if day < self.start or self.L.db.execute("SELECT 1 FROM snapshots WHERE session=?", (day.isoformat(),)).fetchone():
            return
        cash = self.L.get_state("cash", self.cash0)
        equity = self.equity(positions)
        risk = self.L.get_state("risk", {"peak": self.cash0})
        risk["peak"] = max(risk.get("peak", self.cash0), equity)
        risk["drawdown"] = 1 - equity / risk["peak"]
        with self.L.tx():
            self.L.set_state("risk", risk)
            self.L.insert_snapshot({"session": day.isoformat(), "created_at": iso(self.now), "run_id": self.L.run_id, "equity": equity, "cash": cash,
                                    "positions_value": equity - cash, "spy_bh_equity": None, "cash_bh_equity": self.cash0, "peak": risk["peak"],
                                    "drawdown": risk["drawdown"], "regime": f"{len(positions)} open memecoin positions", "risk_state": json.dumps(risk),
                                    "marks": json.dumps({"marks": {p["label"]: p.get("mark") for p in positions.values()}, "flags": {}}),
                                    "holdings": json.dumps({})})
