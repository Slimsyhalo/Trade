"""Causal primitives; no strategy/optimization, no automatic gap filling."""
from decimal import Decimal
import heapq

class LeakageError(ValueError): pass

def assert_causal(event, as_of_ms):
    available=event.get('available_at_ms')
    if available is None or available>as_of_ms or event['event_time_ms']>as_of_ms:
        raise LeakageError('Future/unknown availability: QA FAILED')

def replay(streams, until_ms, allow_exchange_assumption=False):
    """Merge iterators by availability. Consumers receive current event only."""
    def checked(stream):
        previous=-1
        for event in stream:
            t=event.get('available_at_ms')
            if t is None: raise LeakageError('Unknown historical publication time')
            if t<previous: raise LeakageError('Stream out of order')
            if not allow_exchange_assumption and event.get('availability_basis')!='received':
                raise LeakageError('Explicit consent required for historical latency assumptions')
            previous=t
            if t>until_ms: break
            assert_causal(event,t)
            yield event
    yield from heapq.merge(*(checked(s) for s in streams), key=lambda e:e['available_at_ms'])

def feature_spec(*, centered=False, fill=None, offset=0, uses_target=False):
    if centered or fill in ('backfill','bfill') or offset<0 or uses_target:
        raise LeakageError('Unsafe feature specification: QA FAILED')
    return {'centered':False,'fill':fill,'offset':offset,'uses_target':False}

def bars(events, seconds=60):
    if seconds not in (1,5,15,30,60,180,300,900): raise ValueError('Unsupported timeframe')
    width=seconds*1000; bar=None; previous=None
    for event in events:
        ts=event['event_time_ms']; price=Decimal(event['price']); qty=Decimal(event['quantity'])
        if previous is not None and ts<previous: raise ValueError('Out of order')
        previous=ts; bucket=ts//width*width
        if bar is None or bucket!=bar['open_time']:
            if bar is not None: yield bar
            bar=dict(open_time=bucket,event_time_ms=bucket,available_at_ms=bucket+width,availability_basis='bar_close_boundary_assumption',open=price,high=price,low=price,close=price,volume=Decimal(0),quote_volume=Decimal(0),taker_buy_base_volume=Decimal(0),taker_buy_quote_volume=Decimal(0),number_of_trades=0)
        bar['high']=max(bar['high'],price); bar['low']=min(bar['low'],price); bar['close']=price
        bar['volume']+=qty; bar['quote_volume']+=price*qty
        if not event['is_buyer_maker']:
            bar['taker_buy_base_volume']+=qty; bar['taker_buy_quote_volume']+=price*qty
        bar['number_of_trades']+=event.get('last_trade_id',0)-event.get('first_trade_id',0)+1
    if bar is not None: yield bar

def compare_bars(reconstructed, official):
    by_time={r['open_time']:r for r in official}; differences=[]
    for bar in reconstructed:
        ref=by_time.pop(bar['open_time'],None)
        if ref is None: differences.append({'time':bar['open_time'],'field':'missing_official'}); continue
        for k in ('open','high','low','close','volume','quote_volume','number_of_trades','taker_buy_base_volume','taker_buy_quote_volume'):
            if Decimal(str(bar[k]))!=Decimal(str(ref[k])): differences.append({'time':bar['open_time'],'field':k,'reconstructed':str(bar[k]),'official':str(ref[k])})
    differences.extend({'time':t,'field':'missing_reconstruction'} for t in by_time)
    return {'status':'PASS' if not differences else 'FAILED','differences':differences}
