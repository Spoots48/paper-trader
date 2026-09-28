"""Optional, causal entry/exit policies used by the intraday research challengers."""
import datetime as dt


def update_confirmations(state, bar_time, bars, cfg):
    mode = cfg['entry'].get('confirmation')
    if not mode:
        return
    start = dt.datetime.fromisoformat(bar_time)
    end = start + dt.timedelta(minutes=cfg.get('execution', {}).get('bar_minutes', 1))
    window = start.replace(minute=start.minute // 5 * 5, second=0, microsecond=0).isoformat()
    candidates = {c['ticker']: c for c in state.candidates}
    for ticker in state.pending:
        if ticker not in bars:
            continue
        signal = state.entry_signals.setdefault(ticker, {})
        if signal.get('window') != window:
            signal.update(window=window, low=bars[ticker][2])
        else:
            signal['low'] = min(signal['low'], bars[ticker][2])
        if end.minute % 5:
            continue
        above = bars[ticker][3] >= candidates[ticker]['trigger']
        if mode == 'close':
            signal['ready'] = above
        elif mode == 'retest':
            if signal.get('breakout_window') and signal['breakout_window'] != window:
                signal['ready'] = above and signal['low'] <= candidates[ticker]['trigger']
            elif above:
                signal['breakout_window'] = window


def schedule_stagnation_exits(state, bar_time, bars, cfg):
    minutes = cfg['exit'].get('stagnation_minutes')
    if minutes is None:
        return
    end = dt.datetime.fromisoformat(bar_time) + dt.timedelta(minutes=cfg.get('execution', {}).get('bar_minutes', 1))
    for ticker, position in state.positions.items():
        if ticker not in bars:
            continue
        age = (end - dt.datetime.fromisoformat(position['entry_time'])).total_seconds() / 60
        target = position['entry_ref'] + cfg['exit']['stagnation_min_r'] * position['initial_risk']
        if age >= minutes and bars[ticker][3] < target:
            position['exit_next_open'] = True
