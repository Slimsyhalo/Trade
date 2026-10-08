from decimal import Decimal
import pytest
from quantlab_core.derivative_features import sampled_basis,open_interest_changes


def bar(price,stamp=0,symbol='BTCUSDT',available=60_000):
    return dict(symbol=symbol,event_time_ms=stamp,open_time=stamp,close_time=stamp+59_999,
                close=price,available_at_ms=available,availability_basis='bar_close_boundary_assumption')


def metric(stamp,level,value='100',available=None):
    return dict(symbol='BTCUSDT',event_time_ms=stamp,sum_open_interest=level,
                sum_open_interest_value=value,available_at_ms=available,
                availability_basis='unknown_historical_publication' if available is None else 'observed_receipt')


def test_basis_is_exact_signed_proxy_and_uses_close_not_open_availability():
    row=list(sampled_basis([bar('99.99999999999999999')],[bar('100')]))[0]
    assert Decimal(row['sampled_basis_quote_units'])==Decimal('-0.00000000000000001')
    assert row['available_at_ms']==60_000 and row['event_time_ms']==59_999
    assert not row['strict_causal_replay_certified']


def test_delayed_or_unknown_publication_survives_derivation():
    assert list(sampled_basis([bar('2',available=120_000)],[bar('1')]))[0]['available_at_ms']==120_000
    assert list(sampled_basis([bar('2',available=None)],[bar('1')]))[0]['available_at_ms'] is None


@pytest.mark.parametrize('marks,indexes',[
    ([bar('2')],[]),([bar('2')],[bar('1',symbol='ETHUSDT')]),
    ([bar('2'),bar('2')],[bar('1'),bar('1')]),([bar('2')],[bar('0')])])
def test_mismatch_duplicate_symbol_or_nonpositive_index_rejected(marks,indexes):
    with pytest.raises(ValueError):list(sampled_basis(marks,indexes))


def test_oi_first_row_and_gap_cannot_fabricate_contiguous_changes():
    rows=list(open_interest_changes([metric(0,'10'),metric(300_000,'9'),metric(900_000,'11')]))
    assert rows[0]['oi_observed_difference_source_units'] is None
    assert rows[1]['oi_expected_cadence_difference_source_units']=='-1'
    assert rows[2]['oi_observed_difference_source_units']=='2'
    assert rows[2]['oi_expected_cadence_difference_source_units'] is None
    assert rows[2]['observation_interval_ms']==600_000
    assert all(r['available_at_ms'] is None for r in rows)


def test_oi_availability_waits_for_delayed_previous_input():
    rows=list(open_interest_changes([metric(0,'10',available=700_000),metric(300_000,'12',available=400_000)]))
    assert rows[1]['available_at_ms']==700_000


def test_bad_oi_level_or_unsorted_time_rejected():
    with pytest.raises(ValueError):list(open_interest_changes([metric(0,'-1')]))
    with pytest.raises(ValueError):list(open_interest_changes([metric(1,'1'),metric(0,'2')]))


def test_oi_exact_source_precision_retained():
    rows=list(open_interest_changes([metric(0,'1.000000000000000001'),metric(300_000,'1.000000000000000002')]))
    assert Decimal(rows[1]['oi_observed_difference_source_units'])==Decimal('0.000000000000000001')
