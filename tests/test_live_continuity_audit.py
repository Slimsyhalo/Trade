import gzip,json
from audit_live_continuity import inspect_route
from quantlab_core.io import sha256
import pytest


def segment(root,name,rows):
    p=root/name
    with gzip.open(p,'wt') as f:
        for row in rows:f.write(json.dumps(row)+'\n')
    d=sha256(p);b=p.stat().st_size
    return dict(path=name,rows=len(rows),sha256=d,bytes=b,first_receive_ns=rows[0]['receive_timestamp_ns'],last_receive_ns=rows[-1]['receive_timestamp_ns'],remote=dict(sha256=d,bytes=b,verified_at=1,asset_id=1,api_url='https://api.github.com/repos/Slimsyhalo/Trade/releases/assets/1'))


def depth(stamp,u,pu):return dict(receive_timestamp_ns=stamp,kind='event',payload=dict(stream='btcusdt@depth@100ms',data=dict(s='BTCUSDT',e='depthUpdate',U=u,u=u,pu=pu)))


def test_gap_across_rotated_segments_and_clock_regression(tmp_path):
    a=segment(tmp_path,'a.gz',[depth(10,1,0),depth(20,2,1)])
    b=segment(tmp_path,'b.gz',[depth(21,4,3),depth(19,4,3)])
    r=inspect_route(tmp_path,[b,a]);assert r['rows']==4
    assert r['sequence_diagnostics']==dict(depth_sequence_gap=1,receive_clock_regression=1,duplicate_or_old_sequence=1)
    assert r['full_L2_book_certified'] is False


def test_reconnect_and_snapshot_unavailability_do_not_certify_service(tmp_path):
    rows=[dict(receive_timestamp_ns=1,kind='connection_start',payload={}),dict(receive_timestamp_ns=2,kind='snapshot_unavailable',payload=dict(http_status=451))]
    r=inspect_route(tmp_path,[segment(tmp_path,'a.gz',rows)])
    assert r['kinds']['snapshot_unavailable']==1 and r['continuous_operation_certified'] is False


def test_unknown_member_or_boundary_fails(tmp_path):
    r=segment(tmp_path,'a.gz',[depth(1,1,0)]);r['first_receive_ns']=2
    with pytest.raises(ValueError,match='boundaries'):inspect_route(tmp_path,[r])
    r['path']='../a.gz'
    with pytest.raises(ValueError,match='Unsafe'):inspect_route(tmp_path,[r])


def test_book_ticker_anomalies_are_observed_not_hidden(tmp_path):
    row=dict(receive_timestamp_ns=1,kind='event',payload=dict(stream='btcusdt@bookTicker',data=dict(e='bookTicker',s='BTCUSDT',b='2',a='1',B='0',A='1',E=1)))
    r=inspect_route(tmp_path,[segment(tmp_path,'a.gz',[row])]);assert r['sequence_diagnostics']['crossed_displayed_quote']==1
    assert not r['uncalibrated_receive_minus_exchange_E_ns']['network_latency_certified']
