"""Paths, frozen configuration loading, and hashing."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = ROOT / "config"
DATA_DIR = ROOT / "data"
HISTORY_DIR = DATA_DIR / "history"
REPORTS_DIR = ROOT / "reports"
DASHBOARD_DIR = ROOT / "dashboard"
LOG_DIR = ROOT / "logs"
RESEARCH_DIR = ROOT / "research"

LEDGER_PATH = DATA_DIR / "ledger.sqlite"
MARKET_CACHE_PATH = DATA_DIR / "market_cache.sqlite"
LOCK_PATH = DATA_DIR / ".cycle.lock"

STRATEGY_PATH = CONFIG_DIR / "strategy_v1.json"
EXPERIMENT_PATH = CONFIG_DIR / "experiment.json"
UNIVERSE_PATH = CONFIG_DIR / "universe.json"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


def load_strategy(path: Path = STRATEGY_PATH) -> dict:
    return load_json(path)


def load_experiment() -> dict:
    return load_json(EXPERIMENT_PATH)


def load_universe() -> dict:
    return load_json(UNIVERSE_PATH)


def ensure_dirs() -> None:
    for d in (DATA_DIR, HISTORY_DIR, REPORTS_DIR, DASHBOARD_DIR, LOG_DIR, RESEARCH_DIR):
        d.mkdir(parents=True, exist_ok=True)

# The installed (live) runtime, its logs and every cache live on the external drive; nothing project-related is kept on the internal disk.
EXTERNAL_HOME = Path("/Volumes/X10 Pro/Paper Trading Sim")
LIVE_RUNTIME = EXTERNAL_HOME / "installed" / "runtime"


def is_live_copy() -> bool:
    return ROOT.resolve() == LIVE_RUNTIME.resolve() or not LIVE_RUNTIME.exists()
