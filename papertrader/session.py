"""Cloud session mode: GitHub delivers only a handful of the scheduled runs, so during the morning trading window one run
keeps cycling every few minutes and then starts its successor. Outside the window (or if anything fails) the normal
cron schedule takes over again. Paper trading only; this changes how often the frozen strategies are evaluated, never
their rules."""
from __future__ import annotations

import datetime as dt
import subprocess
import sys
import time

WINDOW_START = dt.time(13, 20)  # 09:20 ET (US daylight time through 2026-10-22)
WINDOW_END = dt.time(17, 0)     # 13:00 ET
STEP_SECONDS = 300
MAX_LOOP_SECONDS = 20 * 60      # stays well inside the job's 30 minute timeout


def in_window(now: dt.datetime) -> bool:
    now = now.astimezone(dt.timezone.utc)
    return now.weekday() < 5 and WINDOW_START <= now.time() < WINDOW_END


def plan(start: dt.datetime) -> list[dt.datetime]:
    """Times (UTC) of the cycles to run: now, then every STEP_SECONDS while inside the window and the time budget."""
    out = [start]
    t = start
    while True:
        t = t + dt.timedelta(seconds=STEP_SECONDS)
        if (t - start).total_seconds() > MAX_LOOP_SECONDS or not in_window(t):
            return out
        out.append(t)


def run_once() -> int:
    return subprocess.run([sys.executable, "run.py", "cycle", "--trigger", "github-actions"]).returncode


def loop(now=lambda: dt.datetime.now(dt.timezone.utc), sleep=time.sleep, cycle=run_once) -> int:
    start = now()
    code = 0
    for i, at in enumerate(plan(start)):
        wait = (at - now()).total_seconds()
        if wait > 0:
            sleep(wait)
        code = cycle()
        if code != 0:
            return code
    return code


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "loop"
    if cmd == "loop":
        sys.exit(loop())
    if cmd == "chain":
        # exit 0 = start a successor: still in the window five minutes from now
        sys.exit(0 if in_window(dt.datetime.now(dt.timezone.utc) + dt.timedelta(seconds=STEP_SECONDS)) else 1)
    sys.exit(2)
