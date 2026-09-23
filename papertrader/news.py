"""Free news retrieval (Yahoo Finance ticker news + Google News RSS) and a transparent keyword classifier.

News is only ever used to *confirm* or *veto* a price-based signal. Every
item is stored with its publication timestamp (from the source) and its
retrieval timestamp (our clock). Items published after the decision time are
never used.
"""
from __future__ import annotations

import datetime as dt
import email.utils
import hashlib
import re
import time
import urllib.parse
import xml.etree.ElementTree as ET_XML

import requests

from .nyse_calendar import ET, UTC, iso, now_utc, prev_session
from .strategy import NewsVerdict

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0 Safari/537.36"}

LEX = {
    "earnings": [r"\bearnings\b", r"\bresults\b", r"\bquarter(ly)?\b", r"\bq[1-4]\b", r"\beps\b", r"\brevenue\b",
                 r"\bguidance\b", r"\boutlook\b", r"\bforecast\b", r"\bprofit\b", r"\bfiscal\b", r"\bsales\b"],
    "positive": [r"\bbeats?\b", r"\btops?\b", r"\bexceed", r"\bsurpass", r"\braises? (its |full-year |annual )?(guidance|outlook|forecast)",
                 r"\blifts? (guidance|outlook|forecast)", r"\bboosts? (guidance|outlook|forecast)", r"\brecord (revenue|quarter|sales|profit)",
                 r"\bstrong (demand|results|quarter)", r"\bupgrade", r"\bsoar", r"\bsurg", r"\bjumps?\b", r"\brall(y|ies)",
                 r"better[- ]than[- ]expected", r"\babove (estimates|expectations)", r"\bblowout\b", r"\bbuyback\b"],
    "negative": [r"\bmiss(es)?\b", r"falls? short", r"\bbelow (estimates|expectations)", r"\b(cuts?|lowers?|slashes?) (its |full-year |annual )?(guidance|outlook|forecast)",
                 r"\bweak (guidance|outlook|demand)", r"\bdisappoint", r"\bdowngrade", r"\bplunge", r"\btumbl", r"\bsinks?\b",
                 r"\bslump", r"worse[- ]than[- ]expected", r"\bwarns?\b", r"\brecall\b", r"\blawsuit\b"],
    "hard_negative": [r"(public|secondary|stock|share|equity) offering", r"\bshare sale\b", r"\bdilut", r"\binvestigation\b",
                      r"\bprobe\b", r"\bsubpoena", r"\bsec charges\b", r"\bfraud\b", r"\brestat(e|ement)", r"accounting irregular",
                      r"\bbankruptcy\b", r"\bchapter 11\b", r"\bdelist", r"going concern", r"short[- ]seller report", r"\bhalted\b"],
    "deal_target": [r"to be acquired", r"agrees? to be (bought|acquired)", r"\bbuyout\b", r"takeover (bid|offer)", r"acquired by",
                    r"go(ing)? private", r"\bto sell itself\b", r"merger agreement"],
}
# Law-firm solicitation headlines ("INVESTOR ALERT: ... investigates") are ignored, not treated as hard negatives.
SPAM = [r"law firm", r"shareholder alert", r"investor alert", r"class action", r"pomerantz", r"rosen law", r"bragar",
        r"levi & korsinsky", r"kessler topaz", r"faruqi", r"bronstein", r"deadline", r"securities fraud lawsuit",
        r"investors who lost", r"schall law", r"glancy", r"robbins geller", r"halper sadeh"]
_C = {k: [re.compile(p, re.I) for p in v] for k, v in LEX.items()}
_SPAM = [re.compile(p, re.I) for p in SPAM]
NAME_SUFFIX = re.compile(r"\b(inc\.?|incorporated|corp\.?|corporation|company|co\.?|plc|ltd\.?|limited|holdings?|group|"
                         r"the|n\.?v\.?|s\.?a\.?|class [a-c])\b", re.I)


def clean_name(name: str) -> str:
    n = NAME_SUFFIX.sub("", name.replace(",", " ").replace("(The)", ""))
    return re.sub(r"\s+", " ", n).strip(" .&-")


def classify(text: str) -> tuple[list[str], list[str]]:
    if any(p.search(text) for p in _SPAM):
        return ["law_firm_ad"], []
    cats, matched = [], []
    for k, pats in _C.items():
        hits = [p.pattern for p in pats if p.search(text)]
        if hits:
            cats.append(k)
            matched += hits
    return cats, matched


def _uid(source: str, url: str | None, title: str, published: str | None) -> str:
    return hashlib.sha1(f"{source}|{url or ''}|{title}|{published or ''}".encode()).hexdigest()


def fetch_yahoo(ticker: str, timeout: float = 15) -> list[dict]:
    import yfinance as yf
    retrieved = iso(now_utc())
    out = []
    for it in (yf.Ticker(ticker).news or []):
        c = it.get("content", it)
        title = (c.get("title") or "").strip()
        if not title:
            continue
        pub = c.get("pubDate") or c.get("displayTime")
        url = ((c.get("canonicalUrl") or {}).get("url") or (c.get("clickThroughUrl") or {}).get("url"))
        summary = re.sub(r"<[^>]+>", " ", c.get("summary") or c.get("description") or "")
        out.append({"ticker": ticker, "source": "yahoo", "provider": (c.get("provider") or {}).get("displayName"),
                    "title": title, "summary": summary[:600], "url": url,
                    "published_at": iso(dt.datetime.fromisoformat(pub.replace("Z", "+00:00"))) if pub else None,
                    "retrieved_at": retrieved})
    return out


def fetch_google(ticker: str, name: str, timeout: float = 15) -> list[dict]:
    q = f'"{clean_name(name)}" (stock OR shares OR earnings) when:3d'
    url = "https://news.google.com/rss/search?" + urllib.parse.urlencode({"q": q, "hl": "en-US", "gl": "US", "ceid": "US:en"})
    retrieved = iso(now_utc())
    r = requests.get(url, headers=UA, timeout=timeout)
    r.raise_for_status()
    root = ET_XML.fromstring(r.content)
    out = []
    for item in root.iter("item"):
        title = (item.findtext("title") or "").strip()
        pub = item.findtext("pubDate")
        src = item.find("source")
        try:
            pub_iso = iso(email.utils.parsedate_to_datetime(pub)) if pub else None
        except (TypeError, ValueError):
            pub_iso = None
        out.append({"ticker": ticker, "source": "google_news", "provider": src.text if src is not None else None,
                    "title": title, "summary": "", "url": item.findtext("link"), "published_at": pub_iso,
                    "retrieved_at": retrieved})
    return out


def relevant(item: dict, ticker: str, name: str) -> bool:
    text = f"{item['title']} {item.get('summary', '')}"
    cn = clean_name(name)
    first = cn.split()[0] if cn else ""
    return bool(re.search(rf"\b{re.escape(ticker)}\b", text) or (cn and cn.lower() in text.lower())
                or (len(first) >= 4 and re.search(rf"\b{re.escape(first)}\b", text, re.I)))


class NewsService:
    """Builds the news_check callback used by strategy.decide in the live engine."""

    def __init__(self, ledger, names: dict[str, str], cfg: dict, decision_time: dt.datetime, reaction_day=None):
        self.ledger = ledger
        self.names = names
        self.cfg = cfg
        self.decision_time = decision_time
        self.reaction_day = reaction_day
        self.cache: dict[str, tuple[list[dict], list[str]]] = {}

    def _gather(self, ticker: str) -> tuple[list[dict], list[str]]:
        if ticker in self.cache:
            return self.cache[ticker]
        items, errors = [], []
        name = self.names.get(ticker, ticker)
        for src, fn in (("yahoo", lambda: fetch_yahoo(ticker)), ("google_news", lambda: fetch_google(ticker, name))):
            for attempt in range(2):
                try:
                    items += fn()
                    break
                except Exception as e:  # recorded; a single failing source doesn't block the other
                    if attempt == 1:
                        errors.append(f"{src}: {type(e).__name__}: {str(e)[:120]}")
                        self.ledger.issue("WARN", "news", f"{src} fetch failed: {e}", ticker)
                    time.sleep(1.5)
            time.sleep(0.5)
        for it in items:
            cats, matched = classify(f"{it['title']} {it.get('summary', '')}")
            it["categories"], it["matched"] = cats, matched
            it["relevant"] = relevant(it, ticker, name)
            it["uid"] = _uid(it["source"], it.get("url"), it["title"], it.get("published_at"))
            it["news_id"] = self.ledger.insert_news(it)
        self.cache[ticker] = (items, errors)
        return items, errors

    def check(self, ticker: str, purpose: str, metrics: dict) -> NewsVerdict:
        items, errors = self._gather(ticker)
        if not items and len(errors) >= 2:
            return NewsVerdict(False, "unavailable", "news sources unavailable: " + "; ".join(errors))
        if purpose == "catalyst":
            D = dt.date.fromisoformat(metrics["reaction_session"])
            start = dt.datetime.combine(prev_session(D), dt.time(12, 0), ET).astimezone(UTC)
        else:
            start = self.decision_time - dt.timedelta(hours=self.cfg["momentum"]["news_lookback_hours"])
        window = []
        for it in items:
            if not it["relevant"] or not it.get("published_at"):
                continue
            p = dt.datetime.fromisoformat(it["published_at"].replace("Z", "+00:00"))
            if start <= p <= self.decision_time:  # never use items published after the decision
                window.append(it)
        ids = sorted({it["news_id"] for it in window})
        cats = [set(it["categories"]) for it in window]
        hard = [it for it, c in zip(window, cats) if "hard_negative" in c]
        deal = [it for it, c in zip(window, cats) if "deal_target" in c]
        if hard:
            return NewsVerdict(False, "vetoed", f"hard-negative headline: \"{hard[0]['title'][:110]}\" ({hard[0]['provider']}, {hard[0]['published_at']})", ids)
        if deal:
            return NewsVerdict(False, "vetoed", f"deal/takeover headline (price likely pinned): \"{deal[0]['title'][:110]}\"", ids)
        if purpose == "momentum":
            return NewsVerdict(True, "no_veto", f"{len(window)} relevant headlines in last {self.cfg['momentum']['news_lookback_hours']}h, no hard negatives", ids)
        earn = [it for it, c in zip(window, cats) if "earnings" in c]
        pos = sum(1 for c in cats if "positive" in c)
        neg = sum(1 for c in cats if "negative" in c)
        if not earn:
            return NewsVerdict(False, "unconfirmed", f"no timestamped earnings headline found since {iso(start)} ({len(window)} relevant items)", ids)
        if neg > pos:
            return NewsVerdict(False, "vetoed", f"headline tone net negative ({pos} positive vs {neg} negative)", ids)
        e = earn[0]
        return NewsVerdict(True, "confirmed", f"{len(earn)} earnings headlines (e.g. \"{e['title'][:90]}\" — {e['provider']}, "
                                              f"published {e['published_at']}); tone +{pos}/-{neg}", ids)
