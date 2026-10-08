import csv
from datetime import date
import io
import zipfile
from quantlab_core.io import Budget
from quantlab_core.normalize import normalize
from quantlab_core.sources import day_ms
from quantlab_core.trade_admission import admit_individual_tape


def zip_rows(path,rows):
    text=io.StringIO();csv.writer(text).writerows(rows)
    with zipfile.ZipFile(path,'w') as z:z.writestr('data.csv',text.getvalue())


def fixture(tmp_path,missing=False):
    start=day_ms(date(2024,10,7));tape=tmp_path/'trades.zip';official=tmp_path/'official.zip'
    trades=[];bars=[]
    for i in range(1440):
        stamp=start+i*60000
        trades.append([i+1+(i>0),'1','1','1',stamp,'false'])
        bars.append([stamp,'1','1','1','1','1',stamp+59999,'1',1,'1','1','0'])
    if missing:trades.pop(10)
    zip_rows(tape,trades);zip_rows(official,bars)
    qa=normalize(tape,tmp_path/'tape.parquet','trades','BTCUSDT',date(2024,10,7),Budget(tmp_path,1))
    return tape,official,qa


def test_global_id_gap_admitted_only_with_full_market_consistency(tmp_path):
    tape,official,qa=fixture(tmp_path)
    assert qa['status']=='FAILED' and qa['id_gaps']==1
    decision=admit_individual_tape(tape,official,'BTCUSDT','2024-10-07',qa)
    assert decision['state']=='VALIDATED'
    assert decision['original_strict_qa']['status']=='FAILED'
    assert not decision['global_identifier_continuity_certified']
    assert decision['cause_of_specific_global_id_gaps']=='NOT_DETERMINED'


def test_real_missing_market_trade_remains_quarantined(tmp_path):
    tape,official,qa=fixture(tmp_path,missing=True)
    decision=admit_individual_tape(tape,official,'BTCUSDT','2024-10-07',qa)
    assert decision['state']=='QUARANTINED'
    assert decision['independent_bar_evidence']['difference_count']>0


def test_schema_failure_cannot_be_relaxed_by_bar_consistency(tmp_path):
    tape,official,qa=fixture(tmp_path);qa['schema_violations']=1
    assert admit_individual_tape(tape,official,'BTCUSDT','2024-10-07',qa)['state']=='QUARANTINED'
