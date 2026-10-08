from copy import deepcopy
from pathlib import Path
import pytest
from source_foundation import inventory, validate_inventory
from probe_extended_sources import spot_url
from quantlab_core.sources import START, END

ROOT=Path(__file__).resolve().parents[1]

def test_discovery_never_certifies_acquired_window():
    spec=inventory(ROOT)
    assert not spec['phase_1_accepted']
    assert all(not r['historical_bounds']['complete_requested_window_certified'] for r in spec['datasets'])
    spec['datasets'][0]['historical_bounds']['complete_requested_window_certified']=True
    with pytest.raises(ValueError): validate_inventory(spec)

def test_depth_metrics_cannot_depend_on_trade_tape_only():
    spec=inventory(ROOT); rows={r['id']:r for r in spec['datasets']}
    for metric in ('order_flow_imbalance','book_liquidity_imbalance'):
        assert set(rows[metric]['dependencies'])=={'um_depth_updates_live','um_depth_snapshot_live'}
    assert rows['absorption_pressure']['kind']=='ESTIMATE'
    assert rows['um_trades']['implementation']=='core_quarantined'

def test_absent_archive_is_not_absent_commercial_history():
    rows={r['id']:r for r in inventory(ROOT)['datasets']}
    assert rows['um_bookTicker_archive']['classification']=='UNAVAILABLE'
    assert rows['historical_l2_tardis']['classification']=='PROVIDER_RESTRICTED'

def test_invalid_derivation_or_classification_rejected():
    spec=inventory(ROOT)
    bad=deepcopy(spec); bad['datasets'][-1]['dependencies']=['invented_input']
    with pytest.raises(ValueError): validate_inventory(bad)
    bad=deepcopy(spec); bad['datasets'][0]['classification']='ACQUIRED'
    with pytest.raises(ValueError): validate_inventory(bad)

def test_spot_bounds_and_precision_are_explicit():
    assert '/spot/daily/trades/' in spot_url('BTCUSDT','trades',START)
    assert str(END) in spot_url('SOLUSDT','klines',END)
    with pytest.raises(ValueError): spot_url('BTCUSDT','trades',START.replace(year=2023))
    rows={r['id']:r for r in inventory(ROOT)['datasets']}
    assert 'microseconds' in rows['spot_trades']['units']
