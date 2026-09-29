"""Freqtrade-inspired temporary entry protection, netting binary legs before counting losses.

Independent implementation; pinned upstream sources are in research/upstream_2026_09_28/SOURCES.md.
Use when the result became known (recorded_at), not the earlier market expiry.
"""
import datetime as dt


def market_loss_cooldown(fills, incomplete: set, now, cfg: dict) -> dict | None:
    if not cfg:
        return None
    markets = {}
    for f in fills:
        key = f['order_key'].split(':')
        if len(key) != 4 or key[0] != 'pm' or key[-1] != 'SETTLE':
            continue
        slug = key[1]
        known = dt.datetime.fromisoformat(f['recorded_at'].replace('Z', '+00:00'))
        if slug in incomplete or known > now:
            continue
        group = markets.setdefault(slug, {'pnl': 0., 'known': known})
        group['pnl'] += f['realized_pnl']
        group['known'] = max(group['known'], known)
    losses = sorted((g['known'], slug) for slug,g in markets.items() if g['pnl'] < -1e-9)
    lookback = dt.timedelta(minutes=cfg['lookback_minutes'])
    duration = dt.timedelta(minutes=cfg['cooldown_minutes'])
    result = None
    for i,(known,slug) in enumerate(losses):
        if known + duration <= now:
            continue
        recent = [s for t,s in losses[:i+1] if t > known-lookback]
        if len(recent) >= cfg['loss_limit']:
            result = {'until': (known+duration).isoformat(), 'markets': recent,
                      'reason': f'{len(recent)} net losing markets within {cfg["lookback_minutes"]} minutes'}
    return result


def ledger_cooldown(ledger, now, cfg: dict) -> dict | None:
    if not cfg:
        return None
    positions = ledger.get_state('pm_positions', {}) or {}
    orders = ledger.get_state('mm_orders', []) or []
    incomplete = {p['slug'] for p in positions.values()} | {o['slug'] for o in orders}
    fills = ledger.db.execute("SELECT order_key, recorded_at, realized_pnl FROM fills "
                              "WHERE side='SELL' AND reason_code IN ('PM_WIN','PM_LOSS')").fetchall()
    lock = market_loss_cooldown(fills, incomplete, now, cfg)
    ledger.set_state('entry_cooldown', lock)
    return lock
