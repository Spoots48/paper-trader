"""Conservative capital accounting for binary Up/Down paper markets."""
from collections import defaultdict


def settlement_floor(cash: float, positions: dict, orders=()) -> float:
    """Worst terminal equity, even if only the losing side of every quote fills.

    Winning resting orders are allowed to remain unfilled. Existing matched
    shares pay $1 per pair; unrelated markets are never assumed to hedge.
    """
    markets = defaultdict(lambda: {'Up': 0.0, 'Down': 0.0})
    for p in positions.values():
        markets[p['slug']][p['side']] += p['shares']
    for o in orders:
        other = 'Down' if o['outcome'] == 'Up' else 'Up'
        markets[o['slug']][other] -= o['shares'] * o['price']
    return cash + sum(min(m.values()) for m in markets.values())


def marked_equity(cash: float, positions: dict) -> float:
    return cash + sum(p.get('mark', p['cost'] / p['shares']) * p['shares'] for p in positions.values())


def protected_floor(risk: dict, day: dict, cfg: dict) -> float:
    floor = max(risk['peak'] * (1 - cfg['drawdown_halt']),
                day['start_equity'] * (1 - cfg['daily_loss_limit']))
    gain = day.get('peak', day['start_equity']) - day['start_equity']
    activation = cfg.get('profit_lock_activation')
    if activation is not None and gain >= day['start_equity'] * activation:
        floor = max(floor, day['start_equity'] + gain * (1 - cfg['profit_lock_giveback']))
    return floor
