import json
from pathlib import Path
import yaml
from build_audit import build_audit
from quantlab_core.pipeline import Pipeline, remote_verified
from quantlab_core.research import bars, assert_causal, LeakageError
import pytest


def sample_record():
    r={'key':'BTCUSDT/aggTrades/2024-10-07','symbol':'BTCUSDT','dataset':'aggTrades','day':'2024-10-07',
       'qa':{'status':'PASS','rows':2,'min_timestamp':1728259200000,'max_timestamp':1728259200001}}
    for kind in ('raw','normalized'):
        r[kind]={'path':'data/'+kind,'sha256':'a'*64,'bytes':10,
                 'remote':{'verified_at':1,'sha256':'a'*64,'bytes':10,'url':'https://example.invalid/asset'}}
    return r


def test_audit_uses_real_receipts_and_retains_storage_estimate(tmp_path):
    cfg={'symbols':['BTCUSDT'],'datasets':['aggTrades'],'start_date':'2024-10-07','end_date':'2026-10-07','max_local_storage_gb':1,'repository':'owner/repo'}
    (tmp_path/'config.yaml').write_text(yaml.safe_dump(cfg))
    (tmp_path/'STORAGE_ESTIMATE.md').write_text('stratified observations must survive')
    r=sample_record(); Pipeline(tmp_path,cfg).save(r)
    summary=build_audit(tmp_path)
    assert summary['remote']['verified_partitions']==1
    assert summary['local_validation']['present_file_checks']==0
    assert summary['local_validation']['remote_not_rechecked']==2
    assert summary['status']=='INCOMPLETE'
    assert (tmp_path/'STORAGE_ESTIMATE.md').read_text()=='stratified observations must survive'
    r['raw']['remote']['sha256']='b'*64
    Pipeline(tmp_path,cfg).save(r)
    assert build_audit(tmp_path)['remote']['verified_partitions']==0


def test_malformed_remote_metadata_is_not_verified():
    r=sample_record(); assert remote_verified(r)
    del r['raw']['sha256']; del r['raw']['remote']['sha256']
    assert not remote_verified(r)


def test_delayed_trade_cannot_make_bar_available_before_receipt():
    trade={'event_time_ms':1000,'available_at_ms':125000,'price':'1','quantity':'2','is_buyer_maker':False}
    bar=list(bars([trade],seconds=60))[0]
    assert bar['available_at_ms']==125000
    with pytest.raises(LeakageError): assert_causal(bar,124999)
    assert_causal(bar,125000)


def test_unknown_trade_availability_fails_bar_construction():
    with pytest.raises(LeakageError): list(bars([{'event_time_ms':0,'available_at_ms':None}]))
