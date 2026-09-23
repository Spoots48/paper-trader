"""NYSE trading calendar and Eastern-time helpers.

Holidays are hard-coded from the published NYSE schedule. The live engine also
cross-checks against actual data: a weekday session with no SPY bar is logged
as a possible unscheduled closure or data outage.
"""
from __future__ import annotations

import datetime as dt
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
UTC = dt.timezone.utc

HOLIDAYS = {
    # 2025
    "2025-01-01", "2025-01-09", "2025-01-20", "2025-02-17", "2025-04-18", "2025-05-26",
    "2025-06-19", "2025-07-04", "2025-09-01", "2025-11-27", "2025-12-25",
    # 2026
    "2026-01-01", "2026-01-19", "2026-02-16", "2026-04-03", "2026-05-25", "2026-06-19",
    "2026-07-03", "2026-09-07", "2026-11-26", "2026-12-25",
    # 2027
    "2027-01-01", "2027-01-18", "2027-02-15", "2027-03-26", "2027-05-31", "2027-06-18",
    "2027-07-05", "2027-09-06", "2027-11-25", "2027-12-24",
}
EARLY_CLOSES = {"2025-07-03", "2025-11-28", "2025-12-24", "2026-11-27", "2026-12-24", "2027-11-26"}

OPEN_TIME = dt.time(9, 30)
CLOSE_TIME = dt.time(16, 0)
EARLY_CLOSE_TIME = dt.time(13, 0)


def now_utc() -> dt.datetime:
    return dt.datetime.now(UTC)


def iso(ts: dt.datetime) -> str:
    """UTC ISO-8601 with seconds, e.g. 2026-09-23T13:31:05Z."""
    return ts.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_iso(s: str) -> dt.datetime:
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(UTC)


def is_session(d: dt.date) -> bool:
    return d.weekday() < 5 and d.isoformat() not in HOLIDAYS


def session_open(d: dt.date) -> dt.datetime:
    return dt.datetime.combine(d, OPEN_TIME, ET)


def session_close(d: dt.date) -> dt.datetime:
    t = EARLY_CLOSE_TIME if d.isoformat() in EARLY_CLOSES else CLOSE_TIME
    return dt.datetime.combine(d, t, ET)


def next_session(d: dt.date) -> dt.date:
    d = d + dt.timedelta(days=1)
    while not is_session(d):
        d += dt.timedelta(days=1)
    return d


def prev_session(d: dt.date) -> dt.date:
    d = d - dt.timedelta(days=1)
    while not is_session(d):
        d -= dt.timedelta(days=1)
    return d


def sessions_between(start: dt.date, end: dt.date) -> list[dt.date]:
    """Sessions in [start, end] inclusive."""
    out, d = [], start
    while d <= end:
        if is_session(d):
            out.append(d)
        d += dt.timedelta(days=1)
    return out


def add_sessions(d: dt.date, n: int) -> dt.date:
    for _ in range(n):
        d = next_session(d)
    return d


def last_completed_session(now: dt.datetime) -> dt.date:
    """Most recent session whose regular-hours close is at or before `now`."""
    et_now = now.astimezone(ET)
    d = et_now.date()
    if is_session(d) and et_now >= session_close(d):
        return d
    return prev_session(d)


def current_session(now: dt.datetime) -> dt.date | None:
    """The session in progress at `now`, or None when the market is closed."""
    et_now = now.astimezone(ET)
    d = et_now.date()
    if is_session(d) and session_open(d) <= et_now < session_close(d):
        return d
    return None
