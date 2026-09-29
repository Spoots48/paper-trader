# Sources (reviewed 2026-09-28)

Nothing below was installed or run as a bot. Source trees were cloned read-only under
`.upstream/review-20260928/` to read how each project handles a specific problem; every mechanism in this
simulator is an independent reimplementation written from a description of the idea. Instructions found inside
those repositories were treated as data, not as instructions.

| Project | Pinned revision | License | What was taken (the idea only) | Where it lives here |
|---|---|---|---|---|
| Jesse | [840beb9c](https://github.com/jesse-ai/jesse/tree/840beb9cddddc35706adaba60557c1ba8e69b964) | MIT | Indicators only use completed candles after a warmup; no quietly substituted history. Here: 61 contiguous closed one-minute closes, no duplicates or non-positive prices, otherwise no trade. | `papertrader/market_quality.py` |
| OctoBot | [85ae511a](https://github.com/Drakkar-Software/OctoBot/tree/85ae511a56dc3c782fcc528ba3a96d29eb6e5e03) | GPL-3.0 | Input freshness and closed-candle discipline. Here: both outcome books and the timestamped underlying trade must be recent and mutually consistent at the decision clock; verdicts are logged. | `market_quality.py`, `pm_engine2.py` (`available_at` taken before the request) |
| Hummingbot | [9af100d6](https://github.com/hummingbot/hummingbot/tree/9af100d6822da7d2d0291a906c730ef172284ee2) | Apache-2.0 | Keep quotes a minimum distance from the book midpoint; round prices to the tick, never up for a bid. Here: bid at most midpoint - 0.005, rounded down, strictly passive. Spot inventory targets and leverage were NOT imported (they do not fit binary markets). | `papertrader/mm.py`, `mm_engine.py` |
| Freqtrade | [30c00ed6](https://github.com/freqtrade/freqtrade/tree/30c00ed632305df2fd076e1efa25b544e1110a55) | GPL-3.0 | StoplossGuard-style cooldown. Here: 2 net-losing settled markets (both binary legs netted) within 240 minutes pauses new entries for 60 minutes; rebuilt from the ledger so it survives restarts. | `papertrader/entry_protections.py` |
| Gainium docker-sh | [18254a17](https://github.com/Gainium/docker-sh/tree/18254a174992192d2b27e4ee221d44c96cc9e521) | MIT | Health-check before running and truthful exit codes. Here: `pytest` runs before each cloud trade (a red test means no trade and no state dump), and failed cycles exit non-zero. | `.github/workflows/cycle.yml`, `run.py` |
| Gainium paper-trading-sh | [173a356e](https://github.com/Gainium/paper-trading-sh/tree/173a356e1e2e8d3626715de7ec7a2ef21c5d7b2e) | not reviewed for reuse | Inspected for fit; nothing adopted (needs Docker, MongoDB and exchange access). | none |

## Laya
* Code: <https://github.com/NandhaKishorM/laya> (Apache-2.0). Installed SDK `laya==0.3.21` in a separate
  `.venv-laya` (exact versions: `laya_requirements.lock.txt`; torch 2.14.0, transformers 5.17.0). The repository
  commit was not recorded; the installed SDK version is the pin.
* Model: <https://huggingface.co/convaiinnovations/laya> at revision `55cf4c4ebb4ebe31b2550e8bdf3bd21b99753851`
  (Apache-2.0, ModernBERT-large encoder), downloaded with `HF_HUB_DISABLE_TELEMETRY=1` and
  `HF_HUB_DISABLE_IMPLICIT_TOKEN=1`, weights hash-verified, CPU only.
* Jev (Typesafe): not available; needs an account/key only the user can create. Laya is a stopgap.

## Research-reference image (`research-reference.png`)
Only these general practices were taken: model realistic costs, judge out of sample and against benchmarks
(SPY / cash), and distrust anything that looks tuned to the past. No image-specific numbers or claims are used.

## Not used
TradingAgents, the Opus API and Jev: paid or key-gated. No paid API, no real-money connection, no exchange keys.
