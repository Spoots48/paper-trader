"""Advisory news review with the Laya text classifier (local, shadow-only).

Runs on the Mac in a separate Python environment (the model needs torch); it is never imported by the
trading cycle and never runs on GitHub Actions. It reads the ledgers' `news` tables read-only, labels each
headline once per (uid, model revision, schema version), and writes a review log under data/laya/.
Nothing here places, sizes, blocks or unblocks an order: labels are a text classification, not an expected return.
"""
from __future__ import annotations

import argparse
import datetime as dt
import fcntl
import hashlib
import json
import os
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

MODEL_REPO = "convaiinnovations/laya"
MODEL_REVISION = "55cf4c4ebb4ebe31b2550e8bdf3bd21b99753851"
SCHEMA_VERSION = "news-risk-1"
FUTURE_TOLERANCE_S = 300
MAX_AGE_DAYS = 14
DEFAULT_LIMIT = 200
MIN_CONFIDENCE = 0.8

QUESTIONS = {
    "event": {
        "type": "choice",
        "instructions": "Classify only what the headline itself states. A rumor, opinion, price target, law-firm solicitation or "
                        "price-move recap is not a confirmed company event. A denial or 'no evidence of' statement is not an adverse event.",
        "criteria": {
            "material_adverse": "The company confirms or a regulator/court states a serious adverse event: investigation, recall, breach, "
                                "bankruptcy, delisting notice, going-concern doubt, rejected drug, withdrawn guidance, executive fraud.",
            "earnings_update": "Reported or scheduled earnings, revenue or guidance results (beat, miss, raise, cut, reaffirm).",
            "promotional_or_opinion": "Analyst opinion, price target, stock-pick list, commentary, unconfirmed rumor, or law-firm advertisement.",
            "other": "Routine filings, dividends, hires, product news, partnerships, or price-move recaps.",
        },
    },
    "tone": {
        "type": "choice",
        "instructions": "Judge the effect on shareholders using only the headline.",
        "criteria": {
            "negative": "The headline is bad news for shareholders.",
            "positive": "The headline is good news for shareholders.",
            "neutral": "Routine, mixed or unclear effect on shareholders.",
        },
    },
}


def _utc(s: str | None) -> dt.datetime | None:
    if not s:
        return None
    try:
        t = dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None
    return t if t.tzinfo else t.replace(tzinfo=dt.timezone.utc)


def _iso(t: dt.datetime) -> str:
    return t.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def review_key(uid: str) -> str:
    return f"{uid}|{MODEL_REVISION}|{SCHEMA_VERSION}"


def load_news(root: Path, now: dt.datetime, max_age_days: int = MAX_AGE_DAYS) -> tuple[list[dict], dict]:
    """Read-only, de-duplicated news rows that are not future-dated and not older than max_age_days."""
    rows: dict[str, dict] = {}
    skipped = {"future": 0, "old": 0, "unparseable": 0}
    for db in sorted((root / "data").glob("ledger_*.sqlite")):
        con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
        try:
            con.row_factory = sqlite3.Row
            for r in con.execute("SELECT uid,ticker,source,provider,title,url,published_at,retrieved_at,categories,matched FROM news"):
                if r["uid"] in rows:
                    continue
                pub, ret = _utc(r["published_at"]), _utc(r["retrieved_at"])
                if pub is None or ret is None:
                    skipped["unparseable"] += 1
                    continue
                if (pub - now).total_seconds() > FUTURE_TOLERANCE_S or (ret - now).total_seconds() > FUTURE_TOLERANCE_S:
                    skipped["future"] += 1
                    continue
                if now - pub > dt.timedelta(days=max_age_days):
                    skipped["old"] += 1
                    continue
                rows[r["uid"]] = {**dict(r), "ledger": db.name}
        except sqlite3.OperationalError:
            continue
        finally:
            con.close()
    return sorted(rows.values(), key=lambda x: x["published_at"], reverse=True), skipped


def read_done(path: Path) -> set[str]:
    done: set[str] = set()
    if path.exists():
        for line in path.read_text().splitlines():
            try:
                done.add(json.loads(line)["key"])
            except (ValueError, KeyError):
                continue
    return done


def interpret(res: dict) -> dict:
    """Flatten one system_one answer. Low-confidence answers are recorded as abstentions, never as labels."""
    out = {}
    for q in QUESTIONS:
        a = res["answers"][q]
        low = bool(a.get("low_confidence"))
        out[q] = {"label": None if low else a["choice"], "top": a["choice"], "answer_confidence": a.get("answer_confidence"),
                  "probabilities": a.get("probabilities"), "abstained": low}
    return out


def classify(agent, headline: str, ticker: str, provider: str, min_confidence: float = MIN_CONFIDENCE) -> dict:
    res = agent.system_one(state={"headline": headline, "ticker": ticker or "", "provider": provider or ""},
                           questions=QUESTIONS, min_confidence=min_confidence)
    return interpret(res)


def load_agent(model_dir: str):
    from laya import Agent  # imported lazily: only the separate Laya environment has it
    return Agent(model_dir, device="cpu")


def run_review(root: Path, model_dir: str, limit: int = DEFAULT_LIMIT, now: dt.datetime | None = None, agent_factory=load_agent) -> dict:
    now = now or dt.datetime.now(dt.timezone.utc)
    out_dir = root / "data" / "laya"
    out_dir.mkdir(parents=True, exist_ok=True)
    status_path = out_dir / "status.json"
    lock = open(out_dir / ".lock", "w")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        return {"state": "skipped", "reason": "another review is running"}
    status = {"model_repo": MODEL_REPO, "model_revision": MODEL_REVISION, "schema_version": SCHEMA_VERSION, "started_at": _iso(now),
              "role": "advisory only: never gates, sizes or places orders"}
    try:
        news, skipped = load_news(root, now)
        log = out_dir / "reviews.jsonl"
        done = read_done(log)
        todo = [n for n in news if review_key(n["uid"]) not in done][:limit]
        status.update(state="running", candidates=len(news), pending=len(todo), skipped=skipped)
        if not todo:
            status.update(state="idle", finished_at=_iso(dt.datetime.now(dt.timezone.utc)), reviewed_now=0)
            status_path.write_text(json.dumps(status, indent=1))
            return status
        status_path.write_text(json.dumps(status, indent=1))
        agent = agent_factory(model_dir)
        n = 0
        with log.open("a") as f:
            for item in todo:
                r = classify(agent, item["title"], item["ticker"], item["provider"])
                f.write(json.dumps({"key": review_key(item["uid"]), "uid": item["uid"], "ticker": item["ticker"], "title": item["title"],
                                    "published_at": item["published_at"], "retrieved_at": item["retrieved_at"],
                                    "reviewed_at": _iso(dt.datetime.now(dt.timezone.utc)), "model_revision": MODEL_REVISION,
                                    "schema_version": SCHEMA_VERSION, "rule_tags": {"categories": item["categories"], "matched": item["matched"]},
                                    "result": r}) + "\n")
                f.flush()
                n += 1
        status.update(state="done", reviewed_now=n, finished_at=_iso(dt.datetime.now(dt.timezone.utc)))
        write_latest(out_dir)
    except Exception as e:  # recorded, never swallowed: the status file is what the app shows
        status.update(state="error", error=f"{type(e).__name__}: {e}"[:400], finished_at=_iso(dt.datetime.now(dt.timezone.utc)))
        status_path.write_text(json.dumps(status, indent=1))
        raise
    status_path.write_text(json.dumps(status, indent=1))
    return status


def write_latest(out_dir: Path, top: int = 25) -> None:
    rows = [json.loads(x) for x in (out_dir / "reviews.jsonl").read_text().splitlines() if x.strip()]
    adverse = [r for r in rows if r["result"]["event"]["label"] == "material_adverse"]
    negative = [r for r in rows if r["result"]["tone"]["label"] == "negative" and r not in adverse]
    ab = {q: sum(r["result"][q]["abstained"] for r in rows) for q in QUESTIONS}
    lines = ["# Laya news review (advisory, shadow mode)", "",
             f"Model `{MODEL_REPO}` @ `{MODEL_REVISION[:12]}`, schema `{SCHEMA_VERSION}`. {len(rows)} headlines reviewed; abstentions "
             f"(confidence below {MIN_CONFIDENCE}): event {ab['event']}, tone {ab['tone']}.",
             "These labels classify text. They are not forecasts, are not used to place or block trades, and confidence is not expected profit.",
             "On the labelled check set the event label abstained on most true adverse headlines, so an absent flag means nothing.", ""]
    for title, group in ((f"Confident 'material adverse' event ({len(adverse)})", adverse), (f"Confident negative tone, not already above ({len(negative)})", negative)):
        lines += [f"## {title}", ""]
        for r in group[:top]:
            lines.append(f"- {r['published_at']} **{r['ticker']}**: {r['title']}")
        lines.append("")
    (out_dir / "latest.md").write_text("\n".join(lines) + "\n")


def evaluate(eval_path: Path, model_dir: str, agent_factory=load_agent) -> dict:
    data = json.loads(eval_path.read_text())
    agent = agent_factory(model_dir)
    stats: dict = {}
    details = []
    for q in QUESTIONS:
        stats[q] = {"n": 0, "answered": 0, "correct": 0, "confident_wrong": 0, "confusion": {}}
    for it in data["items"]:
        r = classify(agent, it["headline"], it["ticker"], "eval")
        row = {"id": it["id"], "headline": it["headline"]}
        for q in QUESTIONS:
            s, want, got = stats[q], it[q], r[q]
            s["n"] += 1
            key = f"{want}->{got['top']}"
            s["confusion"][key] = s["confusion"].get(key, 0) + 1
            if not got["abstained"]:
                s["answered"] += 1
                if got["label"] == want:
                    s["correct"] += 1
                else:
                    s["confident_wrong"] += 1
            row[q] = {"want": want, "got": got["label"], "top": got["top"], "conf": got["answer_confidence"]}
        details.append(row)
    for s in stats.values():
        s["accuracy_answered"] = round(s["correct"] / s["answered"], 3) if s["answered"] else None
        s["accuracy_if_forced"] = round(sum(v for k, v in s["confusion"].items() if k.split("->")[0] == k.split("->")[1]) / s["n"], 3)
        s["abstain_rate"] = round(1 - s["answered"] / s["n"], 3)
        s["confident_wrong_rate"] = round(s["confident_wrong"] / s["answered"], 3) if s["answered"] else None
    return {"model_revision": MODEL_REVISION, "schema_version": SCHEMA_VERSION, "min_confidence": MIN_CONFIDENCE,
            "eval_set_sha256": hashlib.sha256(eval_path.read_bytes()).hexdigest(), "stats": stats, "details": details}


def _launch(root: Path, host: dict) -> subprocess.Popen:
    home = host["home"]
    env = {**os.environ, "HF_HUB_OFFLINE": "1", "HF_HUB_DISABLE_TELEMETRY": "1", "HF_HUB_DISABLE_IMPLICIT_TOKEN": "1",
           "HF_HOME": f"{home}/.cache/huggingface", "TORCH_HOME": f"{home}/.cache/torch", "TMPDIR": f"{home}/.cache/tmp",
           "PYTHONDONTWRITEBYTECODE": "1", "TOKENIZERS_PARALLELISM": "false"}
    out = root / "data" / "laya"
    out.mkdir(parents=True, exist_ok=True)
    log = open(root.parent / "logs" / "laya_review.log", "a")
    return subprocess.Popen([host["python"], "-m", "papertrader.laya_news", "review", "--root", str(root), "--model-dir", host["model_dir"]],
                            cwd=str(root), env=env, stdout=log, stderr=log, stdin=subprocess.DEVNULL, start_new_session=True)


def trigger_background(root: Path) -> dict:
    """Called after a successful cloud sync. No-ops unless data/laya/host.json enables it and its paths are on the external drive."""
    host_path = root / "data" / "laya" / "host.json"
    if not host_path.exists():
        return {"launched": False, "reason": "not configured"}
    host = json.loads(host_path.read_text())
    if not host.get("enabled"):
        return {"launched": False, "reason": "disabled"}
    prefix = str(host["home"]).rstrip("/") + "/"
    if not all(str(host[k]).startswith(prefix) for k in ("python", "model_dir")) or not str(root.resolve()).startswith(prefix):
        return {"launched": False, "reason": "paths are not all inside the external project home"}
    if not (Path(host["python"]).exists() and Path(host["model_dir"]).exists()):
        return {"launched": False, "reason": "python or model missing (drive unplugged?)"}
    _launch(root, host)
    return {"launched": True}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("review")
    r.add_argument("--root", required=True)
    r.add_argument("--model-dir", required=True)
    r.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    e = sub.add_parser("eval")
    e.add_argument("--eval-set", required=True)
    e.add_argument("--model-dir", required=True)
    e.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    t0 = time.time()
    if a.cmd == "review":
        st = run_review(Path(a.root), a.model_dir, a.limit)
        print(json.dumps({k: st.get(k) for k in ("state", "reviewed_now", "pending", "error")}), f"{time.time() - t0:.1f}s")
        return 1 if st.get("state") == "error" else 0
    res = evaluate(Path(a.eval_set), a.model_dir)
    Path(a.out).write_text(json.dumps(res, indent=1))
    print(json.dumps(res["stats"], indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
