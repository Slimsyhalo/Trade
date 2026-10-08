"""Deterministic tape-only research transforms; no orders, signals or fitting."""
from decimal import Decimal,localcontext,ROUND_HALF_EVEN
import json


def flow_windows(events,seconds=60,*,initial_cvd='0',anchor='explicit source start'):
    if type(seconds)is not int or seconds<=0 or not anchor:raise ValueError('Positive timeframe and explicit CVD anchor required')
    width=seconds*1_000_000;previous=None;current=None;cvd=Decimal(initial_cvd)
    if not cvd.is_finite():raise ValueError('Invalid CVD anchor value')
    def finish(window):
        nonlocal cvd
        with localcontext() as context:
            context.prec=50
            context.rounding=ROUND_HALF_EVEN
            if window['buy_volume']+window['sell_volume']!=window['volume']:raise ValueError('Aggressor volume balance failed')
            if sum(window['profile'].values(),Decimal(0))!=window['volume']:raise ValueError('Volume-at-price balance failed')
            delta=window['buy_volume']-window['sell_volume'];cvd+=delta
            return dict(window_start_us=window['start'],window_end_us=window['start']+width,source_rows=window['rows'],
                        buy_base_volume=str(window['buy_volume']),sell_base_volume=str(window['sell_volume']),
                        total_base_volume=str(window['volume']),price_quantity_notional=str(window['notional']),
                        volume_delta=str(delta),cvd=str(cvd),cvd_anchor=anchor,cvd_initial=str(initial_cvd),
                        vwap_numerator=str(window['notional']),vwap_denominator=str(window['volume']),
                        vwap=str(window['notional']/window['volume']),vwap_decimal_precision=50,
                        vwap_rounding='ROUND_HALF_EVEN; exact numerator and denominator retained',
                        volume_at_price_json=json.dumps([[str(price),str(qty)] for price,qty in sorted(window['profile'].items())],separators=(',',':')),
                        available_at_us=max(window['available'],window['start']+width) if window['all_available'] else None,
                        availability_basis='derived_window_boundary_and_input_assumptions' if window['all_available'] else 'unknown_input_availability',
                        input_availability_bases=','.join(sorted(window['bases'])),continuity='No empty-window fabrication; CVD valid only on admitted source scope')
    for event in events:
        ts=event.get('event_time_us')
        if ts is None:
            ts=event.get('event_time_ms')
            if type(ts)is not int:raise ValueError('Integer input timestamp required')
            ts*=1000
        if type(ts)is not int or previous is not None and ts<previous:raise ValueError('Out-of-order or invalid input timestamp')
        previous=ts;start=ts//width*width
        available=event.get('available_at_us')
        if available is None and event.get('available_at_ms') is not None:available=event['available_at_ms']*1000
        if available is not None and (type(available)is not int or available<ts):raise ValueError('Invalid input availability')
        if type(event.get('is_buyer_maker'))is not bool:raise ValueError('Observed maker flag required')
        price=Decimal(event['price']);qty=Decimal(event['quantity'])
        if not price.is_finite() or not qty.is_finite() or price<=0 or qty<=0:raise ValueError('Invalid execution price/quantity')
        if current is None or current['start']!=start:
            if current is not None:yield finish(current)
            current=dict(start=start,rows=0,buy_volume=Decimal(0),sell_volume=Decimal(0),volume=Decimal(0),
                         notional=Decimal(0),profile={},all_available=True,available=0,bases=set())
        with localcontext() as context:
            context.prec=50
            context.rounding=ROUND_HALF_EVEN
            current['rows']+=1;current['volume']+=qty;current['notional']+=price*qty
            current['sell_volume' if event['is_buyer_maker'] else 'buy_volume']+=qty
            current['profile'][price]=current['profile'].get(price,Decimal(0))+qty
            current['all_available'] &= available is not None
            current['available']=max(current['available'],available or 0)
            current['bases'].add(event.get('availability_basis','unknown'))
    if current is not None:yield finish(current)
