import gzip,json,time,asyncio
import pytest
from live_collector.spool import Sink
from quantlab_core.io import Budget
from live_collector import collector


def rows(root,store):
    return [json.loads(line) for r in store.records for line in gzip.open(root/r['path'],'rt')]


def test_batch_keeps_original_receipt_and_rotation_cursor(tmp_path):
    store=Sink(tmp_path,Budget(tmp_path,1),'market',max_bytes=1)
    store.write_batch([('event',{'n':1},100,{'btcusdt@aggTrade':1}),('event',{'n':2},101,{'btcusdt@aggTrade':2})]);store.close()
    assert [r['receive_timestamp_ns'] for r in rows(tmp_path,store)]==[100,101]
    assert [r['sequence_state']['btcusdt@aggTrade'] for r in store.records]==[1,2]


def test_batch_validates_every_envelope_before_writing(tmp_path):
    store=Sink(tmp_path,Budget(tmp_path,1),'market')
    with pytest.raises(ValueError):store.write_batch([('event',{},1,{}),('event',{},None,{})])
    assert list(tmp_path.glob('*.gz*'))==[]
    with pytest.raises(ValueError):store.write_batch([('event',{},1,{})]*257)


def test_shared_budget_scanned_once_per_bounded_batch(tmp_path):
    class CountBudget(Budget):
        calls=0
        def check(self,extra=0):self.calls+=1;return super().check(extra)
    budget=CountBudget(tmp_path,1);store=Sink(tmp_path,budget,'market')
    store.write_batch([('event',dict(p='1.0000000000000000001'),i+1,{}) for i in range(128)]);store.close()
    assert budget.calls==1 and len(rows(tmp_path,store))==128


def test_failure_does_not_replay_ambiguous_buffer_in_finally(tmp_path,monkeypatch):
    store=Sink(tmp_path,Budget(tmp_path,1),'market');calls=[]
    original=store.write_batch
    def fail(entries):
        if entries[0][0]!='event':return original(entries)
        calls.append(entries);raise OSError('Ambiguous disk write')
    store.write_batch=fail
    class Socket:
        async def __aenter__(self):return self
        async def __aexit__(self,*a):return False
        def __aiter__(self):return self
        async def __anext__(self):
            if hasattr(self,'done'):raise StopAsyncIteration
            self.done=True
            return json.dumps(dict(stream='btcusdt@aggTrade',data=dict(e='aggTrade',s='BTCUSDT',a=1)))
    monkeypatch.setattr(collector.websockets,'connect',lambda *a,**kw:Socket())
    with pytest.raises(collector.BatchPersistenceError):asyncio.run(collector.capture('market',['BTCUSDT'],store,time.monotonic()+100))
    assert len(calls)==1 and store.unconfirmed_buffer_rows==1


def test_probe_release_namespace_cannot_overlap_default(tmp_path):
    store=Sink(tmp_path,Budget(tmp_path,1),'market',release_prefix='live-probe-buffered')
    store.write('event',{});store.close()
    assert store.records[0]['tag'].startswith('live-probe-buffered-market-')
    with pytest.raises(ValueError):Sink(tmp_path,Budget(tmp_path,1),'market',release_prefix='../x')
