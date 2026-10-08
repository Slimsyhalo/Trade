import csv
from datetime import date
import io
import zipfile
import pyarrow.parquet as pq
import pytest
from quantlab_core.extended_archive import normalize_extended
from quantlab_core.io import Budget
from quantlab_core.sources import day_ms


def source(tmp_path,rows):
    path=tmp_path/'source.zip';text=io.StringIO();csv.writer(text).writerows(rows)
    with zipfile.ZipFile(path,'w') as z:z.writestr('source.csv',text.getvalue())
    return path


@pytest.mark.parametrize('day,multiplier',[('2024-12-31',1),('2025-01-01',1000)])
def test_spot_precision_transition_preserves_original_timestamp(tmp_path,day,multiplier):
    stamp=day_ms(date.fromisoformat(day))*multiplier+(123 if multiplier==1000 else 0)
    raw=source(tmp_path,[[1,'100.001','2','200.002',stamp,'False','True']])
    out=tmp_path/'out.parquet'
    qa=normalize_extended(raw,out,'spot_trades','BTCUSDT',day,Budget(tmp_path,1))
    row=pq.read_table(out).to_pylist()[0]
    assert qa['status']=='PASS' and row['timestamp']==stamp
    assert row['event_time_us']==stamp*(1 if multiplier==1000 else 1000)
    assert row['available_at_us'] is None and row['price']=='100.001'


def test_wrong_spot_time_precision_rejected(tmp_path):
    day='2025-01-01';raw=source(tmp_path,[[1,'1','1','1',day_ms(date.fromisoformat(day)),'False','True']])
    with pytest.raises(ValueError,match='precision'):
        normalize_extended(raw,tmp_path/'out.parquet','spot_trades','BTCUSDT',day,Budget(tmp_path,1))


def test_discontinuous_individual_ids_remain_quarantined(tmp_path):
    day='2025-01-01';stamp=day_ms(date.fromisoformat(day))*1000
    raw=source(tmp_path,[[1,'1','1','1',stamp,'False','True'],[3,'1','1','1',stamp+1,'True','True']])
    qa=normalize_extended(raw,tmp_path/'out.parquet','spot_trades','BTCUSDT',day,Budget(tmp_path,1))
    assert qa['state']=='QUARANTINED' and qa['id_discontinuities']==1


def test_percentage_depth_partial_day_not_full_l2(tmp_path):
    raw=source(tmp_path,[['timestamp','percentage','depth','notional'],['2024-10-07 00:00:00','-1','2','200'],['2024-10-07 00:00:30','-1','3','300']])
    qa=normalize_extended(raw,tmp_path/'out.parquet','um_bookDepth_summary','BTCUSDT','2024-10-07',Budget(tmp_path,1))
    assert qa['state']=='QUARANTINED'
    assert not qa['book_reconstruction_eligible']
    assert 'Partial-day boundaries' in ' '.join(qa['review_reasons'])


def test_nonmonotonic_cumulative_bands_require_review(tmp_path):
    raw=source(tmp_path,[['timestamp','percentage','depth','notional'],['2024-10-07 00:00:00','1','3','300'],['2024-10-07 00:00:00','2','2','200']])
    qa=normalize_extended(raw,tmp_path/'out.parquet','um_bookDepth_summary','BTCUSDT','2024-10-07',Budget(tmp_path,1))
    assert qa['state']=='QUARANTINED'
    assert 'Nonmonotonic' in ' '.join(qa['review_reasons'])


def test_missing_spot_minutes_not_silently_filled(tmp_path):
    day='2025-01-01';stamp=day_ms(date.fromisoformat(day))*1000
    raw=source(tmp_path,[[stamp,'2','3','1','2','5',stamp+59_999_999,'10',2,'1','2','0']])
    qa=normalize_extended(raw,tmp_path/'out.parquet','spot_klines_1m','BTCUSDT',day,Budget(tmp_path,1))
    assert qa['missing_minutes']==1439 and qa['state']=='QUARANTINED'
