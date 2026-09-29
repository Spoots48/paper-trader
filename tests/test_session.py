import datetime as dt

from papertrader import session as S

U = dt.timezone.utc


def at(d, h, m=0):
    return dt.datetime(2026, 9, d, h, m, tzinfo=U)  # 2026-09-29 is a Tuesday, 09-26/27 the weekend


def test_window_is_weekday_morning_only():
    assert S.in_window(at(29, 13, 20)) and S.in_window(at(29, 16, 59))
    assert not S.in_window(at(29, 13, 19)) and not S.in_window(at(29, 17, 0))
    assert not S.in_window(at(26, 15)) and not S.in_window(at(27, 15))


def test_plan_is_every_five_minutes_and_capped():
    p = S.plan(at(29, 14, 0))
    assert [int((t - p[0]).total_seconds() // 60) for t in p] == [0, 5, 10, 15, 20]


def test_plan_stops_at_window_end():
    p = S.plan(at(29, 16, 50))
    assert [t.strftime("%H:%M") for t in p] == ["16:50", "16:55"]


def test_plan_outside_window_is_a_single_cycle():
    assert S.plan(at(26, 15)) == [at(26, 15)]


def test_loop_stops_on_first_failure_and_sleeps_between_cycles():
    clock = [at(29, 14, 0)]
    slept, calls = [], []

    def sleep(s):
        slept.append(s)
        clock[0] += dt.timedelta(seconds=s)

    def cycle():
        calls.append(clock[0])
        return 1 if len(calls) == 2 else 0

    assert S.loop(now=lambda: clock[0], sleep=sleep, cycle=cycle) == 1
    assert len(calls) == 2 and slept == [300]
