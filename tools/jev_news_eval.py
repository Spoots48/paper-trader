"""Score Jev's news reviewer (papertrader/jev_news.py, the same questions the shadow reviewer asks) on the 48 hand-labeled synthetic headlines
that Laya was scored on (research/upstream_2026_09_28/laya_eval_set.json; labels were written before any model output was seen).
A CLASSIFICATION check only: it says nothing about whether headline labels make money.

  python tools/jev_news_eval.py ask   --out jev_news_eval_answers.jsonl      (cloud, needs TYPESAFE_API_KEY)
  python tools/jev_news_eval.py score  answers.jsonl                         (local)"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
SET = HERE / "research" / "upstream_2026_09_28" / "laya_eval_set.json"
LAYA = HERE / "research" / "upstream_2026_09_28" / "laya_eval_result.json"
OUT = HERE / "research" / "review_2026_10_12" / "jev_news_eval_output.txt"


def ask(out_path: str) -> None:
    from typesafe_sdk import TypeSafeClient
    from papertrader.jev_news import judge
    client, items = TypeSafeClient(), json.loads(SET.read_text())["items"]
    with open(out_path, "w") as f:
        for it in items:
            try:
                row = {"id": it["id"], **judge(client, {"ticker": it["ticker"], "title": it["headline"], "provider": "eval"})}
            except Exception as ex:  # noqa: BLE001
                row = {"id": it["id"], "error": f"{type(ex).__name__}: {str(ex)[:160]}"}
            f.write(json.dumps(row) + "\n")
    print("done", len(items))


def auc(scores: list[float], gold: list[int]) -> float:
    pos = [s for s, g in zip(scores, gold) if g]
    neg = [s for s, g in zip(scores, gold) if not g]
    return sum((p > n) + 0.5 * (p == n) for p in pos for n in neg) / (len(pos) * len(neg))


def score(path: str) -> None:
    items = {i["id"]: i for i in json.loads(SET.read_text())["items"]}
    rows = {r["id"]: r for r in map(json.loads, Path(path).read_text().splitlines()) if "error" not in r}
    ids = [i for i in items if i in rows]
    print(f"headlines scored: {len(ids)} of {len(items)}")
    gold = [int(items[i]["event"] == "material_adverse") for i in ids]
    adv = [rows[i]["material_adverse"] if rows[i]["material_adverse"] is not None else 0.0 for i in ids]
    print(f"material_adverse (12 adverse vs 36 not): AUC of Jev's score {auc(adv, gold):.3f}")
    for th in (0.3, 0.5, 0.7):
        tp = sum(1 for a, g in zip(adv, gold) if a >= th and g)
        fp = sum(1 for a, g in zip(adv, gold) if a >= th and not g)
        print(f"  flag when score >= {th}: caught {tp}/{sum(gold)}, false alarms {fp}/{len(gold) - sum(gold)}")
    tone_ok = sum(rows[i]["tone"] == items[i]["tone"] for i in ids)
    print(f"tone (always answers): {tone_ok}/{len(ids)} = {tone_ok / len(ids):.1%}")
    L = json.loads(LAYA.read_text())["stats"]
    print(f"Laya on the same set: material_adverse caught 9/12 with 9/36 false alarms when forced (answered confidently on only {L['event']['answered']}/48 "
          f"event labels, abstain {L['event']['abstain_rate']:.0%}); tone forced {L['tone']['accuracy_if_forced']:.1%}, confident-only {L['tone']['accuracy_answered']:.1%} "
          f"on {L['tone']['answered']}/48")
    # which adverse headlines Jev missed (at 0.5) and which non-adverse it flagged
    miss = [items[i]["headline"] for i, a, g in zip(ids, adv, gold) if g and a < 0.5]
    fa = [(items[i]["event"], items[i]["headline"]) for i, a, g in zip(ids, adv, gold) if not g and a >= 0.5]
    print("missed adverse (score < 0.5):", *[f"\n  - {m}" for m in miss])
    print("false alarms (score >= 0.5):", *[f"\n  - [{k}] {m}" for k, m in fa])


if __name__ == "__main__":
    if sys.argv[1] == "ask":
        ask(sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else "jev_news_eval_answers.jsonl")
    else:
        score(sys.argv[2])
