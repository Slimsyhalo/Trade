"""Exact research descriptors; bar-close basis is a sampled proxy, not a fill.

No interpolation, orders, signals or parameter optimization. Unknown effective
publication times remain null. Assumed availability cannot certify causal replay.
"""
from decimal import Decimal, localcontext, ROUND_HALF_EVEN

VERSION='derivatives-1'


def amount(value,positive=False):
    result=Decimal(value)
    if not result.is_finite() or result<0 or positive and result==0:
        raise ValueError('Invalid original amount/price')
    return result


def ordered(rows):
    previous=None;symbol=None
    for row in rows:
        stamp=row.get('event_time_ms')
        if type(stamp)is not int or previous is not None and stamp<=previous:
            raise ValueError('Source timestamps must be unique and strictly increasing')
        if not row.get('symbol') or symbol is not None and row['symbol']!=symbol:
            raise ValueError('Mixed/missing source symbol')
        available=row.get('available_at_ms')
        if available is not None and (type(available)is not int or available<stamp):
            raise ValueError('Invalid original effective availability')
        previous=stamp;symbol=row['symbol']
        yield row


def availability(inputs,boundary):
    values=[r.get('available_at_ms') for r in inputs]
    bases=','.join(sorted({r.get('availability_basis','unknown') for r in inputs}))
    return (max(boundary,*values) if all(v is not None for v in values) else None),bases


def sampled_basis(mark_rows,index_rows):
    marks=list(ordered(mark_rows));indexes=list(ordered(index_rows))
    by_time={r['event_time_ms']:r for r in indexes}
    if [r['event_time_ms'] for r in marks]!=[r['event_time_ms'] for r in indexes]:
        raise ValueError('Mark/index times differ; no implicit inner join or gap fill')
    for mark in marks:
        index=by_time[mark['event_time_ms']]
        if mark['symbol']!=index['symbol']:raise ValueError('Cross-symbol basis is invalid')
        start=mark['event_time_ms'];end=mark.get('close_time')
        if mark.get('open_time')!=start or index.get('open_time')!=start or end!=index.get('close_time') or end!=start+59_999:
            raise ValueError('One-minute mark/index boundaries must agree')
        m=amount(mark['close'],True);i=amount(index['close'],True)
        with localcontext() as context:
            context.prec=50;context.rounding=ROUND_HALF_EVEN
            spread=m-i;relative=spread/i
        available,bases=availability((mark,index),end+1)
        yield dict(symbol=mark['symbol'],window_start_ms=start,window_end_ms=end+1,event_time_ms=end,
                   mark_close_original=mark['close'],index_close_original=index['close'],
                   sampled_basis_quote_units=str(spread),sampled_relative_basis=str(relative),
                   relative_basis_numerator=str(spread),relative_basis_denominator=index['close'],
                   available_at_ms=available,input_availability_bases=bases,
                   classification='DERIVED_SAMPLED_BAR_CLOSE_PROXY',strict_causal_replay_certified=False,
                   transform_version=VERSION,decimal_precision=50,decimal_rounding='ROUND_HALF_EVEN')


def open_interest_changes(rows,expected_interval_ms=300_000):
    if type(expected_interval_ms)is not int or expected_interval_ms<=0:raise ValueError('Declared positive cadence required')
    previous=None
    for row in ordered(rows):
        level=amount(row['sum_open_interest']);value=amount(row['sum_open_interest_value'])
        stamp=row['event_time_ms'];interval=stamp-previous['event_time_ms'] if previous else None
        with localcontext() as context:
            context.prec=50
            delta=level-amount(previous['sum_open_interest']) if previous else None
            value_delta=value-amount(previous['sum_open_interest_value']) if previous else None
        available,bases=availability((previous,row) if previous else (row,),stamp)
        contiguous=interval==expected_interval_ms
        yield dict(symbol=row['symbol'],event_time_ms=stamp,previous_observation_ms=previous['event_time_ms'] if previous else None,
                   observation_interval_ms=interval,declared_expected_interval_ms=expected_interval_ms,
                   expected_cadence_matched=contiguous,oi_level_original=row['sum_open_interest'],
                   oi_value_original=row['sum_open_interest_value'],oi_observed_difference_source_units=str(delta) if delta is not None else None,
                   oi_value_observed_difference_source_units=str(value_delta) if value_delta is not None else None,
                   oi_expected_cadence_difference_source_units=str(delta) if contiguous else None,
                   availability_basis='unknown_input_availability' if available is None else 'derived_latest_input',
                   available_at_ms=available,input_availability_bases=bases,
                   unit_policy='Original metrics source units; no contract/base/unit conversion inferred',
                   classification='DERIVED_OBSERVED_LEVEL_DIFFERENCE',strict_causal_replay_certified=False,
                   transform_version=VERSION)
        previous=row
