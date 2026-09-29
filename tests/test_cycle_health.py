from types import SimpleNamespace
import pytest
import run
from papertrader import cloud,cycle


@pytest.mark.parametrize('result',[{'mm':'ERROR ValueError: bad tape'},{'error':'timed out'},{'status':'offline'}])
def test_failed_trading_cycle_has_nonzero_exit(monkeypatch,result):
    monkeypatch.setattr(cloud,'cloud_viewer',lambda:False)
    monkeypatch.setattr(cycle,'run_cycle',lambda **kw:result)
    with pytest.raises(SystemExit) as e:
        run.cmd_cycle(SimpleNamespace(trigger='test'))
    assert e.value.code==1


def test_successful_cycle_returns_normally(monkeypatch):
    monkeypatch.setattr(cloud,'cloud_viewer',lambda:False)
    monkeypatch.setattr(cycle,'run_cycle',lambda **kw:{'mm':'no new quotes: cooldown'})
    run.cmd_cycle(SimpleNamespace(trigger='test'))
