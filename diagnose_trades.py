"""Official individual-tape ID diagnostics with independent 1m reconstruction.

This report establishes consistency with official market OHLCV, never labels
missing global identifiers as known insurance/ADL events without event evidence.
No original quarantine or main manifest is changed by this diagnostic.
"""
from datetime import date,datetime,timezone
from decimal import Decimal
import csv
import io
import json
from pathlib import Path
import time
import zipfile

from quantlab_core.io import HTTP,Budget,atomic_json
from quantlab_core.sources import archive_url,checksum_text,day_ms,SYMBOLS
from quantlab_core.research import bars,compare_bars


def verified_download(http,budget,symbol,dataset,day,root):
    url=archive_url(symbol,dataset,day);r=http.get(url+'.CHECKSUM')
    try:text=r.text
    finally:r.close()
    digest=checksum_text(text,url.rsplit('/',1)[-1])
    path=root/(symbol+'-'+dataset+'-'+str(day)+'-'+digest[:16]+'.zip')
    http.download(url,path,budget,expected=digest)
    return path,{'url':url,'sha256':digest,'bytes':path.stat().st_size,'path':str(path),'checksum_text':text}


def csv_rows(path):
    with zipfile.ZipFile(path) as z:
        names=z.namelist()
        if len(names)!=1 or not names[0].endswith('.csv'):raise ValueError('Unexpected source ZIP')
        with z.open(names[0]) as f:yield from csv.reader(io.TextIOWrapper(f,encoding='utf-8-sig'))


def diagnose(tape,official,symbol,day):
    day=date.fromisoformat(str(day))
    start=day_ms(day);end=start+86_400_000;stats=dict(rows=0,missing_identifier_count=0,gap_transitions=0,
                                                   duplicate_ids=0,out_of_order=0,gap_examples=[],first_id=None,last_id=None)
    def events():
        previous_id=previous_time=None
        for index,row in enumerate(csv_rows(tape)):
            if index==0 and row[0] in ('id','trade_id'):continue
            if len(row)!=6:raise ValueError('Individual-trade source schema changed')
            ident=int(row[0]);stamp=int(row[4]);price=Decimal(row[1]);quantity=Decimal(row[2]);quote=Decimal(row[3])
            if not start<=stamp<end or not price.is_finite() or price<=0 or not quantity.is_finite() or quantity<0 or not quote.is_finite() or quote<0:raise ValueError('Invalid source trade')
            if row[5].lower() not in ('true','false'):raise ValueError('Invalid maker side')
            if previous_id is not None:
                stats['duplicate_ids']+=ident==previous_id
                stats['out_of_order']+=(ident<previous_id)+(stamp<previous_time)
                gap=max(0,ident-previous_id-1)
                if gap:
                    stats['missing_identifier_count']+=gap;stats['gap_transitions']+=1
                    if len(stats['gap_examples'])<20:stats['gap_examples'].append(dict(before=previous_id,after=ident,time_ms=stamp,skipped=gap))
            stats['rows']+=1;stats['first_id']=ident if stats['first_id'] is None else stats['first_id'];stats['last_id']=ident
            previous_id=ident;previous_time=stamp
            yield dict(price=row[1],quantity=row[2],is_buyer_maker=row[5].lower()=='true',event_time_ms=stamp,
                       available_at_ms=stamp,availability_basis='exchange_time_zero_latency_assumption')
    columns=('open_time','open','high','low','close','volume','close_time','quote_volume','number_of_trades','taker_buy_base_volume','taker_buy_quote_volume','ignore')
    official_rows=[]
    for index,values in enumerate(csv_rows(official)):
        if index==0 and values[0]=='open_time':continue
        if len(values)!=12:raise ValueError('Official bar schema drift')
        row=dict(zip(columns,values));row['open_time']=int(row['open_time']);official_rows.append(row)
    if len(official_rows)!=1440 or len(set(r['open_time'] for r in official_rows))!=1440:raise ValueError('Official verification bars incomplete')
    result=compare_bars(bars(events()),official_rows)
    return dict(symbol=symbol,day=str(day),**stats,bar_comparison_status=result['status'],
                differences=result['differences'][:100],difference_count=len(result['differences']),
                interpretation='SOURCE_TAPE_MATCHES_OFFICIAL_MARKET_BARS' if result['status']=='PASS' and not stats['duplicate_ids'] and not stats['out_of_order'] else 'UNRESOLVED_OR_INCONSISTENT',
                global_identifier_gap_cause='NOT_DETERMINED',
                QA_decision='REVIEW_WITH_SOURCE_SEMANTICS; original quarantine unchanged',
                limitations=['OHLCV consistency does not reveal executions excluded by the source or participant identity',
                             'Source checksums and independent tape/bar agreement do not prove global identifier continuity',
                             'This diagnostic tests historical aggregation, not causal publication/latency availability'])


def main():
    root=Path('data/trade_diagnosis');root.mkdir(parents=True,exist_ok=True)
    budget=Budget(Path('data'),2);http=HTTP(interval=1);started=time.monotonic();cpu=time.process_time()
    report=dict(status='RUNNING',generated_at=datetime.now(timezone.utc).isoformat(),samples=[],
                official_semantics_reference='https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data',
                semantics='Recent trades represent market order-book fills; current documentation excludes insurance-fund and ADL fills. No documented promise of contiguous IDs; specific gaps not attributed without evidence.',
                original_quarantines_released=False)
    for symbol in SYMBOLS:
        for day in (date(2024,12,7),date(2025,6,7),date(2026,9,7)):
            tape,raw=verified_download(http,budget,symbol,'trades',day,root)
            official,bar=verified_download(http,budget,symbol,'klines',day,root)
            result=diagnose(tape,official,symbol,day);result.update(raw=raw,verification_bars=bar)
            report['samples'].append(result);report.update(elapsed_seconds=round(time.monotonic()-started,3),process_cpu_seconds=round(time.process_time()-cpu,3))
            atomic_json(Path('reports/individual_trade_diagnosis.json'),report)
            print(json.dumps({k:result[k] for k in ('symbol','day','rows','missing_identifier_count','interpretation','difference_count')}),flush=True)
    report['status']='BOUNDED_DIAGNOSTIC_FINISHED';atomic_json(Path('reports/individual_trade_diagnosis.json'),report)


if __name__=='__main__':main()
