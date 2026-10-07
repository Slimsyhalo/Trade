"""Stream CSV ZIP into bounded Parquet row groups; preserve decimal lexemes."""
import csv, io, zipfile, os
from decimal import Decimal
from pathlib import Path
import pyarrow as pa
import pyarrow.parquet as pq
from .sources import BARS, day_ms

FIELDS = {
 'aggTrades': ['agg_trade_id','price','quantity','first_trade_id','last_trade_id','timestamp','is_buyer_maker'],
 'trades': ['trade_id','price','quantity','quote_quantity','timestamp','is_buyer_maker'],
 'klines': ['open_time','open','high','low','close','volume','close_time','quote_volume','number_of_trades','taker_buy_base_volume','taker_buy_quote_volume','ignore'],
 'metrics': ['create_time','symbol','sum_open_interest','sum_open_interest_value','count_toptrader_long_short_ratio','sum_toptrader_long_short_ratio','count_long_short_ratio','sum_taker_long_short_vol_ratio']
}
INTS = {'agg_trade_id','trade_id','first_trade_id','last_trade_id','timestamp','open_time','close_time','number_of_trades'}
NUMERIC = {'price','quantity','quote_quantity','open','high','low','close','volume','quote_volume','taker_buy_base_volume','taker_buy_quote_volume','sum_open_interest','sum_open_interest_value','count_toptrader_long_short_ratio','sum_toptrader_long_short_ratio','count_long_short_ratio','sum_taker_long_short_vol_ratio'}
HEADERS = {'quote_qty':'quote_quantity','agg_trade_id':'agg_trade_id','id':'trade_id','qty':'quantity','time':'timestamp','transact_time':'timestamp','isBuyerMaker':'is_buyer_maker','quoteQty':'quote_quantity','count':'number_of_trades','taker_buy_volume':'taker_buy_base_volume','taker_buy_quote_asset_volume':'taker_buy_quote_volume','quote_asset_volume':'quote_volume'}


def fields_for(dataset): return FIELDS['klines' if dataset in BARS else dataset]


def schema_for(dataset):
    fields = [(k, pa.int64() if k in INTS else pa.bool_() if k == 'is_buyer_maker' else pa.string()) for k in fields_for(dataset)]
    if 'symbol' not in fields_for(dataset): fields.append(('symbol', pa.string()))
    fields.extend([('event_time_ms',pa.int64()),('available_at_ms',pa.int64()),('availability_basis',pa.string())])
    return pa.schema(fields, metadata={b'schema_version':b'1',b'timezone':b'UTC',b'decimals':b'exact source strings'})


def normalize(raw, out, dataset, symbol, day, budget):
    fields = fields_for(dataset); schema = schema_for(dataset)
    out = Path(out); temp = out.with_suffix('.parquet.part'); out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists(): raise RuntimeError('Normalized output exists; validate or version it')
    qa = dict(rows=0,duplicates_found=0,duplicates_removed=0,deduplication_reason='No silent removal; duplicates fail QA',id_gaps=0,interval_gaps=0,out_of_order=0,malformed_rows=0,schema_violations=0,status='PASS')
    previous_ts = previous_id = None; seen = set(); batch = []; first = last = None
    start = day_ms(day); end = start + 86400000
    try:
        with zipfile.ZipFile(raw) as z:
            members = z.infolist()
            if len(members) != 1 or not members[0].filename.endswith('.csv'): raise ValueError('Unexpected ZIP members')
            # ZipFile checks CRC while reading; no extraction to disk.
            with z.open(members[0]) as f, pq.ParquetWriter(temp, schema, compression='zstd', compression_level=6) as writer:
                for n, values in enumerate(csv.reader(io.TextIOWrapper(f, encoding='utf-8-sig', newline=''))):
                    if n == 0 and values and (values[0] in fields or values[0] in HEADERS):
                        mapped = [HEADERS.get(v,v) for v in values]
                        if mapped != fields: raise ValueError(f'Schema drift: {values}')
                        continue
                    if len(values) != len(fields): raise ValueError(f'Schema drift: {len(values)} fields expected {len(fields)}')
                    row = dict(zip(fields,values))
                    for k,v in list(row.items()):
                        if k in INTS: row[k] = int(v)
                        elif k == 'is_buyer_maker':
                            if v.lower() not in ('true','false'): raise ValueError('Invalid boolean')
                            row[k] = v.lower() == 'true'
                        elif k in NUMERIC:
                            d = Decimal(v)
                            if not d.is_finite(): raise ValueError('Nonfinite numeric')
                            if dataset != 'premiumIndexKlines' and d < 0: raise ValueError('Negative amount/price')
                            if k in ('price','open','high','low','close') and dataset != 'premiumIndexKlines' and d <= 0: raise ValueError('Nonpositive price')
                    if dataset == 'metrics':
                        from datetime import datetime, timezone
                        ts = int(datetime.fromisoformat(row['create_time']).replace(tzinfo=timezone.utc).timestamp()*1000)
                        if row['symbol'] != symbol: raise ValueError('Symbol mismatch')
                        # Publication time is unknown: keep null to block strict replay.
                        available = None; basis = 'unknown_historical_publication'
                    elif dataset in BARS:
                        ts = row['open_time']; available = row['close_time'] + 1; basis = 'bar_close_boundary_assumption'
                        if ts % 60000 or row['close_time'] != ts+59999: raise ValueError('Invalid minute boundaries')
                        if not Decimal(row['low']) <= min(Decimal(row['open']),Decimal(row['close'])) <= max(Decimal(row['open']),Decimal(row['close'])) <= Decimal(row['high']): raise ValueError('Impossible OHLC')
                    else:
                        ts = row['timestamp']; available = ts; basis = 'exchange_time_zero_latency_assumption'
                    if not start <= ts < end: raise ValueError('Timestamp outside partition or wrong precision')
                    if previous_ts is not None:
                        qa['out_of_order'] += ts < previous_ts
                        if dataset in BARS: qa['interval_gaps'] += max(0,(ts-previous_ts)//60000-1)
                    key = row.get('agg_trade_id',row.get('trade_id',ts))
                    if key in seen: qa['duplicates_found'] += 1
                    # Trades are required strictly ascending; bounded memory avoids an ID set.
                    if dataset in ('trades','aggTrades'):
                        if previous_id is not None:
                            qa['duplicates_found'] += key == previous_id
                            qa['out_of_order'] += key < previous_id
                            qa['id_gaps'] += max(0,key-previous_id-1)
                        if dataset == 'aggTrades' and row['last_trade_id'] < row['first_trade_id']: raise ValueError('Invalid trade ID range')
                        previous_id = key
                    else: seen.add(key)
                    row.update(symbol=symbol,event_time_ms=ts,available_at_ms=available,availability_basis=basis)
                    first = ts if first is None else min(first,ts); last = ts if last is None else max(last,ts)
                    batch.append(row); qa['rows'] += 1; previous_ts = ts
                    if len(batch) == 10000:
                        table = pa.Table.from_pylist(batch,schema=schema); budget.check(table.nbytes*2+1048576); writer.write_table(table); batch=[]
                if batch:
                    table=pa.Table.from_pylist(batch,schema=schema); budget.check(table.nbytes*2+1048576); writer.write_table(table)
        if dataset in BARS:
            qa['interval_gaps'] += (first-start)//60000 + (end-60000-last)//60000 if first is not None else 1440
        if not qa['rows'] or any(qa[k] for k in ('duplicates_found','id_gaps','interval_gaps','out_of_order')): qa['status']='FAILED'
        qa.update(min_timestamp=first,max_timestamp=last)
        budget.check(); os.replace(temp,out)
        return qa
    finally:
        if temp.exists(): temp.unlink()
