import json
from source_foundation import manifest_snapshot


def test_partial_receipts_do_not_break_audit_or_count_as_verified(tmp_path,monkeypatch):
    row=dict(key='BTCUSDT/metrics/2024-12-16',status='PASS',symbol='BTCUSDT',dataset='metrics',
             raw=dict(remote=None),normalized=dict(remote=None))
    monkeypatch.setattr('source_foundation.subprocess.check_output',lambda *a,**kw:json.dumps(row))
    report,_=manifest_snapshot(tmp_path,'sha')
    assert report['remote_verified_partitions']==0 and report['coverage']==[]


def test_monthly_funding_coverage_counts_observed_days_not_file_dates(tmp_path,monkeypatch):
    receipt=dict(verified_at=1,sha256='a'*64,bytes=10)
    row=dict(key='BTCUSDT/fundingRate/2024-11-01',status='PASS',symbol='BTCUSDT',dataset='fundingRate',day='2024-11-01',
             qa=dict(rows=6,observed_days=['2024-11-01','2024-11-02']),
             raw=dict(sha256='a'*64,bytes=10,remote=receipt),normalized=dict(sha256='a'*64,bytes=10,remote=receipt))
    monkeypatch.setattr('source_foundation.subprocess.check_output',lambda *a,**kw:json.dumps(row))
    report,_=manifest_snapshot(tmp_path,'sha')
    assert report['coverage'][0]['coverage_days']==2
    assert report['coverage'][0]['verified_partitions']==1
