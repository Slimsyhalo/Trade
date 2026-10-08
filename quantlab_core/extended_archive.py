"""Separate spot/percentage-depth schemas with exact source time precision.

No historical tape ID guarantee is assumed. Monotonic unique IDs are structural
QA; discontinuities are recorded and keep individual tapes quarantined pending
cross-source completeness evidence. Percentage-depth is never admitted as L2.
"""
import csv
from datetime import date, datetime, timezone
from decimal import Decimal
import io
import os
from pathlib import Path
import statistics
import zipfile

import pyarrow as pa
import pyarrow.parquet as pq
from .normalize import FIELDS
from .sources import day_ms, period_bounds

KINDS=('spot_trades','spot_klines_1m','um_bookDepth_summary')


def fields_for(kind):
    if kind=='spot_trades': return ['trade_id','price','quantity','quote_quantity','timestamp','is_buyer_maker','is_best_match']
    if kind=='spot_klines_1m': return FIELDS['klines']
    if kind=='um_bookDepth_summary': return ['timestamp','percentage','depth','notional']
    raise ValueError('Unsupported extended dataset')


def schema_for(kind):
    ints={'trade_id','open_time','close_time','number_of_trades'}
    if kind=='spot_trades': ints.add('timestamp')
    fields=[(f,pa.int64() if f in ints else pa.bool_() if f in ('is_buyer_maker','is_best_match') else pa.string()) for f in fields_for(kind)]
    fields.extend([('symbol',pa.string()),('source_time_unit',pa.string()),('event_time_us',pa.int64()),
                   ('available_at_us',pa.int64()),('availability_basis',pa.string())])
    return pa.schema(fields,metadata={b'schema_version':b'extended-1',b'timezone':b'UTC',
                                     b'decimals':b'exact source strings',b'book_semantics':b'percentage summaries are not L2'})


def normalize_extended(raw,out,kind,symbol,day,budget):
    day=date.fromisoformat(str(day)); begin,end=period_bounds('trades',day)
    start_us,end_us=day_ms(begin)*1000,day_ms(end)*1000
    unit='us' if day>=date(2025,1,1) else 'ms'
    multiplier=1 if unit=='us' else 1000
    fields=fields_for(kind); schema=schema_for(kind)
    out=Path(out);out.parent.mkdir(parents=True,exist_ok=True);temp=out.with_suffix('.parquet.part')
    if out.exists(): raise ValueError('Immutable normalized output exists')
    qa=dict(state='VALIDATED',status='PASS',rows=0,duplicates=0,out_of_order=0,id_discontinuities=0,
            missing_minutes=0,source_time_unit=unit if kind!='um_bookDepth_summary' else 'UTC_text_seconds',
            first_event_us=None,last_event_us=None,source_kind=kind,book_reconstruction_eligible=False,
            assumptions=[],review_reasons=[])
    previous=previous_id=None;batch=[];timestamps=[];minute_set=set();current_group=None;group={}
    frozen={};max_frozen={};bands=set();group_count=0;first_band_set=None

    def finish_group():
        nonlocal group_count,first_band_set
        if not group:return
        group_count+=1
        if first_band_set is None:first_band_set=set(group)
        elif set(group)!=first_band_set:qa['review_reasons'].append('Percentage band set changed within partition; missing band or source-version change requires review')
        bands.update(group)
        for sign in (-1,1):
            side=sorted(((abs(p),pair) for p,pair in group.items() if p*sign>0))
            if any(side[i][1][j]>side[i+1][1][j] for i in range(len(side)-1) for j in (0,1)):
                qa['review_reasons'].append('Nonmonotonic cumulative depth/notional bands')
        for band,pair in group.items():
            old=frozen.get(band)
            first=old[1] if old and old[0]==pair else current_group
            frozen[band]=(pair,first)
            max_frozen[str(band)]=max(max_frozen.get(str(band),0),(current_group-first)//1_000_000)

    try:
        with zipfile.ZipFile(raw) as archive:
            members=archive.infolist()
            if len(members)!=1 or not members[0].filename.endswith('.csv'):raise ValueError('Unexpected ZIP members')
            with archive.open(members[0]) as source,pq.ParquetWriter(temp,schema,compression='zstd',compression_level=6) as writer:
                for index,values in enumerate(csv.reader(io.TextIOWrapper(source,encoding='utf-8-sig',newline=''))):
                    if index==0 and kind=='um_bookDepth_summary':
                        if values!=fields:raise ValueError('bookDepth schema drift')
                        continue
                    if index==0 and values and values[0] in ('id','trade_id','open_time'):
                        raise ValueError('Unexpected spot header; source schema review required')
                    if len(values)!=len(fields):raise ValueError('Extended source schema drift')
                    row=dict(zip(fields,values))
                    for f in fields:
                        t=schema.field(f).type
                        if t==pa.int64():row[f]=int(row[f])
                        elif t==pa.bool_():
                            if row[f].lower() not in ('true','false'):raise ValueError('Invalid boolean')
                            row[f]=row[f].lower()=='true'
                        elif f not in ('timestamp','ignore'):
                            number=Decimal(row[f])
                            if not number.is_finite() or (f!='percentage' and number<0):raise ValueError('Invalid amount')
                            if f in ('price','open','high','low','close') and number<=0:raise ValueError('Nonpositive price')
                    if kind=='um_bookDepth_summary':
                        dt=datetime.fromisoformat(row['timestamp'])
                        if dt.tzinfo is not None:raise ValueError('Unexpected timestamp timezone; source contract is UTC text')
                        ts=int(dt.replace(tzinfo=timezone.utc).timestamp())*1_000_000
                        available=None;basis='unknown_historical_publication'
                        band=Decimal(row['percentage'])
                        if not -100<band<100 or band==0:raise ValueError('Invalid percentage band')
                        if current_group!=ts:
                            finish_group(); group={};current_group=ts;timestamps.append(ts)
                        if band in group:qa['duplicates']+=1
                        group[band]=(Decimal(row['depth']),Decimal(row['notional']))
                    elif kind=='spot_trades':
                        ts=row['timestamp']*multiplier;available=None;basis='unknown_historical_publication'
                        key=row['trade_id']
                        if previous_id is not None:
                            qa['duplicates']+=key==previous_id
                            qa['out_of_order']+=key<previous_id
                            qa['id_discontinuities']+=max(0,key-previous_id-1)
                        previous_id=key
                    else:
                        ts=row['open_time']*multiplier
                        minute_set.add(ts)
                        available=(row['close_time']+1)*multiplier;basis='bar_close_boundary_assumption'
                        if ts%60_000_000 or available!=ts+60_000_000:raise ValueError('Wrong spot minute precision/boundaries')
                        if not Decimal(row['low'])<=min(Decimal(row['open']),Decimal(row['close']))<=max(Decimal(row['open']),Decimal(row['close']))<=Decimal(row['high']):raise ValueError('Impossible OHLC')
                        if Decimal(row['taker_buy_base_volume'])>Decimal(row['volume']) or Decimal(row['taker_buy_quote_volume'])>Decimal(row['quote_volume']):raise ValueError('Taker volume exceeds total')
                        if previous is not None:qa['duplicates']+=ts==previous
                    if not start_us<=ts<end_us:raise ValueError('Timestamp outside authorized partition or wrong precision')
                    if previous is not None:qa['out_of_order']+=ts<previous
                    previous=ts
                    row.update(symbol=symbol,source_time_unit=qa['source_time_unit'],event_time_us=ts,
                               available_at_us=available,availability_basis=basis)
                    qa['first_event_us']=ts if qa['first_event_us'] is None else min(qa['first_event_us'],ts)
                    qa['last_event_us']=ts if qa['last_event_us'] is None else max(qa['last_event_us'],ts)
                    batch.append(row);qa['rows']+=1
                    if len(batch)>=10_000:
                        table=pa.Table.from_pylist(batch,schema=schema);budget.check(table.nbytes*2+1048576);writer.write_table(table);batch=[]
                finish_group()
                if batch:
                    table=pa.Table.from_pylist(batch,schema=schema);budget.check(table.nbytes*2+1048576);writer.write_table(table)
        if kind=='spot_klines_1m':qa['missing_minutes']=1440-len(minute_set)
        if kind=='um_bookDepth_summary':
            diffs=[b-a for a,b in zip(timestamps,timestamps[1:]) if b>a]
            median=statistics.median(diffs) if diffs else None
            qa.update(snapshot_groups=group_count,observed_percentage_bands=sorted(map(str,bands)),
                      median_observed_cadence_us=median,largest_observed_gap_us=max(diffs) if diffs else None,
                      max_identical_band_seconds=max_frozen)
            qa['assumptions'].append('Boundary review threshold = twice observed median cadence; not an exchange continuity guarantee')
            if median is None or timestamps[0]-start_us>2*median or end_us-timestamps[-1]>2*median:
                qa['review_reasons'].append('Partial-day boundaries relative to observed cadence')
            if median and max(diffs)>2*median:
                qa['review_reasons'].append('Internal snapshot gap above twice observed median cadence; source continuity not certified')
            if any(v>=3600 for v in max_frozen.values()):
                qa['review_reasons'].append('Unchanged depth/notional band for at least one hour; investigate source staleness, no automatic gap fill')
        if not qa['rows'] or any(qa[k] for k in ('duplicates','out_of_order','id_discontinuities','missing_minutes')) or qa['review_reasons']:
            qa.update(state='QUARANTINED',status='FAILED')
        qa['review_reasons']=sorted(set(qa['review_reasons']))
        budget.check();os.replace(temp,out)
        return qa
    finally:
        temp.unlink(missing_ok=True)
