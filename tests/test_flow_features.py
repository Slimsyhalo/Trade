from decimal import Decimal,getcontext,localcontext,ROUND_UP
import json
import pytest
from quantlab_core.flow_features import flow_windows


def event(stamp,price,qty,maker,available=None):
    return dict(event_time_us=stamp,price=price,quantity=qty,is_buyer_maker=maker,available_at_us=available,availability_basis='received' if available is not None else 'unknown')


def test_exact_flow_balance_profile_and_cvd_anchor():
    rows=list(flow_windows([event(1,'10.10','0.1',False,2),event(3,'10.20','0.2',True,4)],initial_cvd='5',anchor='test'))
    row=rows[0]
    assert Decimal(row['total_base_volume'])==Decimal('0.3')
    assert Decimal(row['volume_delta'])==Decimal('-0.1') and Decimal(row['cvd'])==Decimal('4.9')
    assert Decimal(row['vwap_numerator'])==Decimal('3.050')
    assert sum(Decimal(x[1]) for x in json.loads(row['volume_at_price_json']))==Decimal('0.3')
    assert row['available_at_us']==60_000_000


def test_missing_availability_propagates_and_empty_windows_not_fabricated():
    rows=list(flow_windows([event(1,'1','1',False),event(180_000_001,'1','1',True)],anchor='source'))
    assert len(rows)==2 and rows[1]['window_start_us']==180_000_000
    assert all(r['available_at_us'] is None for r in rows)
    assert Decimal(rows[1]['cvd'])==0


def test_future_received_input_delays_output_and_order_invalidates():
    rows=list(flow_windows([event(1,'1','1',False,90_000_000)],anchor='source'))
    assert rows[0]['available_at_us']==90_000_000
    with pytest.raises(ValueError):list(flow_windows([event(2,'1','1',False),event(1,'1','1',False)]))
    with pytest.raises(ValueError):list(flow_windows([event(1,'1','-1',False)]))


def test_yield_does_not_change_callers_decimal_context():
    before=getcontext().prec
    iterator=flow_windows([event(1,'1','1',False),event(60_000_001,'1','1',False)])
    next(iterator)
    assert getcontext().prec==before
    iterator.close()


def test_results_do_not_depend_on_callers_rounding_or_precision():
    inputs=[event(1,'1','1',False),event(2,'2','2',True)]
    expected=list(flow_windows(inputs))
    with localcontext() as context:
        context.prec=6;context.rounding=ROUND_UP
        assert list(flow_windows(inputs))==expected
