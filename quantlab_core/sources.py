from datetime import date, datetime, timedelta, timezone
import re
START = date(2024, 10, 7)
END = date(2026, 10, 7)
SYMBOLS = ('BTCUSDT', 'ETHUSDT', 'SOLUSDT')
BARS = ('klines', 'markPriceKlines', 'indexPriceKlines', 'premiumIndexKlines')
DATASETS = ('aggTrades', 'trades', *BARS, 'metrics', 'fundingRate', 'bookDepth', 'bookTicker', 'liquidationSnapshot')


def next_month(day):
    return date(day.year+(day.month==12), 1 if day.month==12 else day.month+1, 1)


def period_bounds(dataset, day):
    day=date.fromisoformat(str(day))
    if dataset=='fundingRate':
        finish=next_month(day)
        if day.day!=1 or not START<=day or finish>END+timedelta(days=1):
            raise ValueError('Monthly source would download outside authorized window')
        return day,finish
    next(days(day,day))
    return day,day+timedelta(days=1)


def partition_dates(dataset, start, end):
    start=date.fromisoformat(str(start)); end=date.fromisoformat(str(end))
    next(days(start,end))
    if dataset!='fundingRate':
        yield from days(start,end); return
    month=start.replace(day=1)
    if month<start: month=next_month(month)
    while next_month(month)<=end+timedelta(days=1):
        period_bounds(dataset,month)
        yield month
        month=next_month(month)


def days(start, end):
    start, end = date.fromisoformat(str(start)), date.fromisoformat(str(end))
    if not START <= start <= end <= END: raise ValueError('Outside authorized historical window')
    while start <= end:
        yield start; start += timedelta(days=1)


def archive_url(symbol, dataset, day):
    if symbol not in SYMBOLS or dataset not in DATASETS: raise ValueError('Unsupported symbol/dataset')
    if dataset=='fundingRate':
        day,_=period_bounds(dataset,day)
        return f'https://data.binance.vision/data/futures/um/monthly/fundingRate/{symbol}/{symbol}-fundingRate-{day:%Y-%m}.zip'
    day = next(days(day, day)); interval = '/1m' if dataset in BARS else ''
    label = '1m' if dataset in BARS else dataset
    return f'https://data.binance.vision/data/futures/um/daily/{dataset}/{symbol}{interval}/{symbol}-{label}-{day}.zip'


def day_ms(day):
    return int(datetime.combine(day, datetime.min.time(), timezone.utc).timestamp() * 1000)


def checksum_text(text, filename):
    parts = text.strip().split()
    if len(parts) != 2 or not re.fullmatch('[0-9a-fA-F]{64}', parts[0]) or parts[1].lstrip('*') != filename:
        raise ValueError('Malformed source CHECKSUM or filename mismatch')
    return parts[0].lower()


def funding_pages(http, symbol, start, end):
    """Ascending cursor, inclusive API bounds; no fixed 8-hour assumption."""
    cursor = start
    while cursor < end:
        r = http.get('https://fapi.binance.com/fapi/v1/fundingRate', params=dict(symbol=symbol, startTime=cursor, endTime=end-1, limit=1000))
        rows = r.json()
        if not rows: return
        ts = [int(x['fundingTime']) for x in rows]
        if ts != sorted(set(ts)) or ts[0] < cursor or ts[-1] >= end: raise ValueError('Invalid funding pagination')
        yield r.content, rows
        cursor = ts[-1] + 1
