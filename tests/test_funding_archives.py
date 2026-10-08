import io
import json
import zipfile
from datetime import date, timedelta
from pathlib import Path
import pytest
import pyarrow.parquet as pq
from quantlab_core.io import Budget
from quantlab_core.normalize import normalize
from quantlab_core.sources import archive_url, partition_dates, period_bounds, day_ms
from quantlab_core.pipeline import Pipeline
from quantlab_core.research import replay, LeakageError


def archive(tmp_path, text):
    raw=tmp_path/'source.zip'
    with zipfile.ZipFile(raw,'w') as z: z.writestr('funding.csv',text)
    return raw


def month_rows(begin=date(2024,11,1),interval=8):
    _,finish=period_bounds('fundingRate',begin)
    return [(t,interval,'-0.0001000000123') for t in range(day_ms(begin),day_ms(finish),interval*3600000)]


def write_rows(tmp_path,rows):
    return archive(tmp_path,'calc_time,funding_interval_hours,last_funding_rate\n'+''.join(f'{t},{h},{r}\n' for t,h,r in rows))


def test_only_complete_months_inside_authorized_window():
    months=list(partition_dates('fundingRate','2024-10-07','2026-10-07'))
    assert len(months)==23
    assert months[0]==date(2024,11,1) and months[-1]==date(2026,9,1)
    for d in (date(2024,10,1),date(2026,10,1),date(2024,11,2)):
        with pytest.raises(ValueError): archive_url('BTCUSDT','fundingRate',d)
    assert '/monthly/fundingRate/' in archive_url('BTCUSDT','fundingRate',months[0])


def test_signed_precision_and_unknown_publication(tmp_path):
    out=tmp_path/'month.parquet'
    qa=normalize(write_rows(tmp_path,month_rows()),out,'fundingRate','BTCUSDT',date(2024,11,1),Budget(tmp_path,1))
    assert qa['status']=='PASS' and qa['rows']==90 and len(qa['observed_days'])==30
    event=pq.read_table(out).to_pylist()[0]
    assert event['last_funding_rate']=='-0.0001000000123'
    assert event['available_at_ms'] is None
    with pytest.raises(LeakageError): list(replay([[event]],event['event_time_ms']))


def test_variable_funding_intervals(tmp_path):
    rows=month_rows()
    # The source declares the elapsed interval for each settlement, not a
    # hardcoded three-settlements/day rule.
    t,h,r=rows[1]
    rows.insert(1,(t-4*3600000,4,r))
    rows[2]=(t,4,r)
    qa=normalize(write_rows(tmp_path,rows),tmp_path/'out','fundingRate','BTCUSDT',date(2024,11,1),Budget(tmp_path,1))
    assert qa['status']=='PASS'


def test_settlement_jitter_is_preserved_and_disclosed(tmp_path):
    rows=[(t+n%7,h,r) for n,(t,h,r) in enumerate(month_rows())]
    out=tmp_path/'out'
    qa=normalize(write_rows(tmp_path,rows),out,'fundingRate','BTCUSDT',date(2024,11,1),Budget(tmp_path,1))
    assert qa['status']=='PASS' and qa['funding_schedule_precision_ms']==1000
    assert qa['max_subsecond_offset_ms']==6
    assert [r['calc_time'] for r in pq.read_table(out).to_pylist()]==[r[0] for r in rows]


def test_missing_settlement_fails_quality(tmp_path):
    rows=month_rows(); rows.pop(10)
    qa=normalize(write_rows(tmp_path,rows),tmp_path/'out','fundingRate','BTCUSDT',date(2024,11,1),Budget(tmp_path,1))
    assert qa['status']=='FAILED' and qa['interval_gaps']==1


def test_monthly_archive_cannot_contain_an_outside_record(tmp_path):
    rows=month_rows(); rows[0]=(day_ms(date(2024,10,31)),8,'0.01')
    with pytest.raises(ValueError,match='outside partition'):
        normalize(write_rows(tmp_path,rows),tmp_path/'out','fundingRate','BTCUSDT',date(2024,11,1),Budget(tmp_path,1))


def test_catalog_counts_observed_days_not_month_files(tmp_path):
    cfg={'symbols':['BTCUSDT'],'datasets':['fundingRate'],'start_date':'2024-10-07','end_date':'2026-10-07','max_local_storage_gb':1}
    pipeline=Pipeline(tmp_path,cfg)
    r={'key':'BTCUSDT/fundingRate/2024-11-01','symbol':'BTCUSDT','dataset':'fundingRate','day':'2024-11-01','qa':{'status':'PASS','rows':90,'min_timestamp':day_ms(date(2024,11,1)),'max_timestamp':day_ms(date(2024,11,30)),'observed_days':[str(date(2024,11,1)+timedelta(days=n)) for n in range(30)]},'raw':{'bytes':10},'normalized':{'bytes':20,'remote':None}}
    pipeline.save(r)
    result=pipeline.catalog()[0]
    assert result['partitions']==1 and result['available_days']==30
    assert result['first_available']=='2024-11-01' and result['last_available']=='2024-11-30'
    assert result['missing_days']==701


@pytest.mark.parametrize('symbol',['BTCUSDT','ETHUSDT','SOLUSDT'])
def test_official_september_funding_fixture(tmp_path,symbol):
    from quantlab_core.io import sha256
    folder=Path(__file__).parent/'fixtures/funding'
    entry=next(r for r in json.loads((folder/'manifest.json').read_text()) if r['symbol']==symbol)
    raw=folder/Path(entry['path']).name
    assert sha256(raw)==entry['sha256']==entry['source_checksum'].split()[0]
    qa=normalize(raw,tmp_path/'out','fundingRate',symbol,date(2026,9,1),Budget(tmp_path,1))
    assert qa['status']=='PASS' and qa['rows']==90 and len(qa['observed_days'])==30
