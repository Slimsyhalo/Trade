import gzip
import json
from pathlib import Path
import pytest
from remote_live import observed_streams, inspect_events, summarize, commit_checkpoint


def test_receipt_without_actual_events_cannot_certify_stream_coverage():
    assert observed_streams([{'route':'public','streams':{}}],['BTCUSDT'])['status']=='PARTIAL'
    streams={f'btcusdt@{s}':1 for s in ('depth@100ms','bookTicker','aggTrade','markPrice@1s')}
    assert observed_streams([{'streams':streams}],['BTCUSDT'])['status']=='PASS'
    assert observed_streams([{'streams':streams}],['BTCUSDT','ETHUSDT'])['status']=='PARTIAL'


def test_checkpoint_never_targets_main_or_historical_source_branch():
    for branch in ('main','codex/data-foundation-next'):
        with pytest.raises(ValueError): commit_checkpoint([],branch,'test')


def test_inspection_distinguishes_rest_block_from_market_observation(tmp_path):
    path=tmp_path/'sample.gz'
    rows=[{'kind':'event','payload':{'stream':'btcusdt@depth@100ms','data':{'e':'depthUpdate','s':'BTCUSDT'}}},
          {'kind':'snapshot_unavailable','payload':{'http_status':451}}]
    with gzip.open(path,'wt') as f:
        for r in rows:f.write(json.dumps(r)+'\n')
    observed=inspect_events(path)
    assert observed['event_types']=={'depthUpdate':1}
    assert observed['kinds']['snapshot_unavailable']==1
    assert len(observed['diagnostic_examples'])==1


def test_summary_copies_ledger_and_counts_only_verified_receipts(tmp_path):
    root=tmp_path/'spool';root.mkdir()
    rows=[{'status':'closed','rows':100,'bytes':5,'first_receive_ns':1,'last_receive_ns':2},
          {'status':'remote_verified','rows':2,'bytes':8,'first_receive_ns':3,'last_receive_ns':4}]
    (root/'public-manifest.json').write_text(json.dumps(rows))
    output=tmp_path/'catalog';r=summarize(root,output)
    assert r['raw_rows']==2 and r['remote_verified_segments']==1
    assert json.loads((output/'public-manifest.json').read_text())==rows
