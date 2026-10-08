import asyncio
from copy import deepcopy
import gzip
import json
from pathlib import Path
import threading
import time

import pytest
import requests

from live_collector import collector
from live_collector.sequence import SequenceTracker
from live_collector.spool import Sink, inspect_segment, publish_pending
from quantlab_core.io import Budget, sha256


def sink(root, route='market', **options):
    return Sink(root, Budget(root, 0.1), route, **options)


def rows(root, record):
    with gzip.open(root/record['path'], 'rt') as source:
        return [json.loads(line) for line in source]


def receipt(path):
    return dict(sha256=sha256(path), bytes=path.stat().st_size, verified_at=time.time(),
                api_url='https://api.github.com/repos/fixture/releases/assets/1')


class Remote:
    def __init__(self): self.calls = []
    def put(self, path, tag):
        self.calls.append((path.name, tag))
        return receipt(path)


def publish(sinks, remote, **options):
    async def scenario():
        stopped = asyncio.Event(); stopped.set()
        return await publish_pending(sinks, remote, stopped, **options)
    return asyncio.run(scenario())


def test_local_close_precedes_remote_and_keeps_file(tmp_path):
    class Forbidden:
        def put(self, *args): pytest.fail('Sink must not perform remote I/O')
    store = sink(tmp_path, remote=Forbidden())
    store.write('event', {'price': '123.000000000000000001'}); store.close(); store.close()
    record = json.loads(store.manifest_path.read_text())[0]
    assert record['status'] == 'closed' and record['remote'] is None and record['rows'] == 1
    assert (tmp_path/record['path']).exists() and not list(tmp_path.glob('*.part'))
    assert inspect_segment(tmp_path/record['path'])['rows'] == 1
    assert rows(tmp_path, record)[0]['payload']['price'] == '123.000000000000000001'


def test_slow_publication_does_not_block_capture_and_serializes_calls(tmp_path):
    entered = threading.Event(); release = threading.Event()
    store = sink(tmp_path)
    store.write('event', {'n': 1}); store.close()
    class Slow(Remote):
        active = maximum = 0
        def put(self, path, tag):
            self.active += 1; self.maximum = max(self.maximum, self.active)
            if not self.calls:
                entered.set()
                if not release.wait(2): raise TimeoutError('Test synchronization failed')
            result = super().put(path, tag)
            self.active -= 1
            return result
    remote = Slow()
    async def scenario():
        stopped = asyncio.Event()
        task = asyncio.create_task(publish_pending([store], remote, stopped, poll_seconds=0.001))
        try:
            for _ in range(100):
                if entered.is_set(): break
                await asyncio.sleep(0.001)
            assert entered.is_set()
            assert json.loads(store.manifest_path.read_text())[0]['status'] == 'uploading'
            heartbeats = 0
            for _ in range(5):
                await asyncio.sleep(0.001); heartbeats += 1
            store.write('event', {'n': 2}); store.close()
            assert heartbeats == 5 and len(store.records) == 2 and not task.done()
        finally:
            release.set(); stopped.set()
        return await task
    report = asyncio.run(scenario())
    assert report['published_segments'] == 2 and remote.maximum == 1
    assert all(r['status'] == 'remote_verified' and (tmp_path/r['path']).exists() for r in store.records)


def test_failure_preserves_records_and_restart_reconciles_same_names(tmp_path):
    store = sink(tmp_path)
    for n in range(2): store.write('event', {'n': n}); store.close()
    names = [r['path'] for r in store.records]
    class Failure(Remote):
        def put(self, path, tag):
            self.calls.append((path.name, tag))
            raise OSError('Ambiguous upload accepted then connection lost')
    remote = Failure()
    report = publish([store], remote)
    assert report['status'] == 'FAILED' and len(remote.calls) == 1
    assert [r['status'] for r in store.records] == ['upload_failed', 'closed']
    resumed = sink(tmp_path)
    report = publish([resumed], Remote())
    assert report['status'] == 'COMPLETE'
    assert [r['path'] for r in resumed.records] == names
    assert all((tmp_path/name).exists() for name in names)


@pytest.mark.parametrize('field', ['sha256', 'bytes', 'verified_at', 'api_url'])
def test_invalid_remote_receipt_is_not_verified(tmp_path, field):
    store = sink(tmp_path); store.write('event', {}); store.close()
    class Bad(Remote):
        def put(self, path, tag):
            result = receipt(path); result[field] = None; return result
    assert publish([store], Bad())['status'] == 'FAILED'
    assert store.records[0]['status'] == 'upload_failed'
    assert (tmp_path/store.records[0]['path']).exists()


def test_orphan_closed_segment_and_interrupted_open_tail(tmp_path):
    store = sink(tmp_path)
    store.sequence_state = {'btcusdt@aggTrade': 10}
    store.write('event', {}); store.close()
    store.manifest_path.unlink()  # crash after durable rename, before ledger commit
    recovered = sink(tmp_path)
    assert recovered.records[0]['recovered'] and recovered.records[0]['status'] == 'closed'
    assert recovered.sequence_state == {}
    partial = tmp_path/'market-9999999999999999999-tail.jsonl.gz.part'
    partial.write_bytes(b'incomplete gzip tail')
    recovered = sink(tmp_path)
    assert recovered.records[-1]['status'] == 'quarantined' and partial.exists()
    assert recovered.sequence_state == {}
    remote = Remote(); publish([recovered], remote)
    assert len(remote.calls) == 1 and all('tail' not in name for name, _ in remote.calls)


@pytest.mark.parametrize('damage', ['hash', 'rows', 'gzip', 'missing'])
def test_recovery_rejects_damaged_local_input(tmp_path, damage):
    store = sink(tmp_path); store.write('event', {}); store.close()
    record = store.records[0]; path = tmp_path/record['path']
    if damage == 'hash': record['sha256'] = '0'*64
    if damage == 'rows': record['rows'] += 1
    if damage == 'gzip':
        path.write_bytes(b'corrupt'); record.update(sha256=sha256(path), bytes=path.stat().st_size)
    if damage == 'missing': path.unlink()
    store._save()
    recovered = sink(tmp_path)
    assert recovered.records[0]['status'] == ('missing_local' if damage == 'missing' else 'quarantined')
    assert not recovered.pending()
    if damage != 'missing': assert path.exists()


def test_interrupted_publication_and_legacy_manifest_migration(tmp_path):
    store = sink(tmp_path); store.write('event', {}); store.close()
    record = store.records[0]
    record['path'] = str(tmp_path/record['path']); record.pop('status')
    store._save()
    resumed = sink(tmp_path)
    assert resumed.records[0]['path'] == Path(record['path']).name
    resumed.begin_upload(resumed.records[0])  # process exits before recording receipt
    assert sink(tmp_path).records[0]['status'] == 'closed'
    assert publish([sink(tmp_path)], Remote())['status'] == 'COMPLETE'


def test_mutation_after_recovery_and_drain_budget(tmp_path):
    store = sink(tmp_path); store.write('event', {}); store.close()
    remote = Remote()
    assert publish([store], remote, drain_seconds=0)['status'] == 'PAUSED_BACKLOG'
    assert not remote.calls and store.records[0]['status'] == 'closed'
    path = tmp_path/store.records[0]['path']; path.write_bytes(b'mutated')
    assert publish([store], remote)['status'] == 'FAILED'
    assert store.records[0]['status'] == 'quarantined' and path.exists() and not remote.calls


def test_budget_exhaustion_never_deletes_pending_segment(tmp_path):
    store = sink(tmp_path); store.write('event', {}); store.close()
    before = list(tmp_path.glob('*.jsonl.gz'))
    store.budget = Budget(tmp_path, 0.000001)
    with pytest.raises(RuntimeError, match='budget exhausted'): store.write('event', {})
    assert before and all(path.exists() for path in before)
    assert store.records[0]['status'] == 'closed'


def message(identifier, *, kind='aggTrade', previous=None, first=None):
    if kind == 'aggTrade':
        data = dict(e=kind, s='BTCUSDT', a=identifier); stream = 'btcusdt@aggTrade'
    else:
        data = dict(e=kind, s='BTCUSDT', U=first if first is not None else identifier,
                    u=identifier, pu=previous); stream = 'btcusdt@depth@100ms'
    return dict(stream=stream, data=data)


def test_sequence_checkpoint_duplicate_and_gap_semantics():
    tracker = SequenceTracker({'btcusdt@aggTrade': 10, 'btcusdt@depth@100ms': 20})
    assert tracker.observe(message(10))[0][0] == 'duplicate_or_old'
    assert tracker.observe(message(13))[0][0] == 'trade_gap'
    assert tracker.observe(message(20, kind='depthUpdate', previous=19))[0][0] == 'duplicate_or_old'
    assert tracker.observe(message(22, kind='depthUpdate', previous=20, first=21)) == []
    assert tracker.observe(message(25, kind='depthUpdate', previous=23, first=24))[0][0] == 'sequence_gap'
    resumed = SequenceTracker(tracker.last)
    assert resumed.observe(message(13))[0][0] == 'duplicate_or_old'
    assert resumed.observe(message(14)) == []


@pytest.mark.parametrize('change', ['symbol', 'type', 'range', 'envelope'])
def test_malformed_event_does_not_advance_sequence(change):
    tracker = SequenceTracker({'btcusdt@depth@100ms': 20})
    envelope = message(22, kind='depthUpdate', previous=20)
    if change == 'symbol': envelope['data']['s'] = 'ETHUSDT'
    if change == 'type': envelope['data']['u'] = True
    if change == 'range': envelope['data']['U'] = 23
    if change == 'envelope': envelope = {}
    assert tracker.observe(envelope)[0][0] == 'malformed_event'
    assert tracker.last == {'btcusdt@depth@100ms': 20}


def test_capture_retains_duplicate_raw_and_cursor_across_reconnect(tmp_path, monkeypatch):
    store = sink(tmp_path)
    store.sequence_state = {'btcusdt@aggTrade': 10}
    batches = [[message(10), message(11)], [message(11), message(13)]]
    class Socket:
        def __init__(self, batch): self.batch = iter(batch)
        async def __aenter__(self): return self
        async def __aexit__(self, *args): return False
        def __aiter__(self): return self
        async def __anext__(self):
            try: return json.dumps(next(self.batch))
            except StopIteration: raise StopAsyncIteration
    connections = 0
    def connect(*args, **kwargs):
        nonlocal connections
        connections += 1
        if batches: return Socket(batches.pop(0))
        raise RuntimeError('Test completed after reconnect')
    async def immediate(_): pass
    monkeypatch.setattr(collector.websockets, 'connect', connect)
    monkeypatch.setattr(collector.asyncio, 'sleep', immediate)
    with pytest.raises(RuntimeError, match='Test completed'):
        asyncio.run(collector.capture('market', ['BTCUSDT'], store, time.monotonic()+100))
    allrows = [row for record in store.records for row in rows(tmp_path, record)]
    assert sum(row['kind'] == 'event' for row in allrows) == 4
    assert sum(row['kind'] == 'duplicate_or_old' for row in allrows) == 2
    assert sum(row['kind'] == 'trade_gap' for row in allrows) == 1
    assert connections == 3 and sink(tmp_path).sequence_state['btcusdt@aggTrade'] == 13


def test_regional_rest_block_stops_polling(tmp_path, monkeypatch):
    store = sink(tmp_path, 'snapshots')
    calls = []
    def blocked(*args):
        calls.append(args)
        response = requests.Response(); response.status_code = 451
        response._content_consumed = True
        raise requests.HTTPError('Regional restriction', response=response)
    monkeypatch.setattr(collector, 'fetch_snapshot', blocked)
    asyncio.run(collector.snapshots(['BTCUSDT','ETHUSDT','SOLUSDT'], store, time.monotonic()+100))
    assert len(calls) == 1
    data = rows(tmp_path, store.records[0])
    assert data[0]['kind'] == 'snapshot_unavailable' and data[0]['payload']['http_status'] == 451


def test_run_capture_failure_closes_every_sink_and_writes_failed_report(tmp_path, monkeypatch):
    async def fail(route, symbols, store, deadline):
        store.write('event', {'route': route})
        if route == 'market': raise ValueError('Injected capture failure')
        await asyncio.sleep(10)
    async def snapshot(symbols, store, deadline):
        store.write('snapshot_error', {})
        await asyncio.sleep(10)
    monkeypatch.setattr(collector, 'capture', fail)
    monkeypatch.setattr(collector, 'snapshots', snapshot)
    with pytest.raises(ExceptionGroup):
        asyncio.run(collector.run(dict(symbols=['BTCUSDT'], max_local_storage_gb=0.1), 1, root=tmp_path))
    assert json.loads((tmp_path/'session-report.json').read_text())['status'] == 'FAILED'
    assert not list(tmp_path.glob('*.jsonl.gz.part'))
    assert len(list(tmp_path.glob('*.jsonl.gz'))) == 3


def test_crash_between_segment_rename_and_manifest_commit(tmp_path, monkeypatch):
    store = sink(tmp_path); store.write('event', {})
    from live_collector import spool
    real = spool.atomic_json
    def fail(*args): raise OSError('Injected manifest commit failure')
    monkeypatch.setattr(spool, 'atomic_json', fail)
    with pytest.raises(OSError, match='commit failure'): store.close()
    assert not store.manifest_path.exists() and len(list(tmp_path.glob('*.jsonl.gz'))) == 1
    monkeypatch.setattr(spool, 'atomic_json', real)
    recovered = sink(tmp_path)
    assert recovered.records[0]['status'] == 'closed' and recovered.records[0]['recovered']


def test_cancelled_upload_keeps_input_and_recoverable_state(tmp_path):
    store = sink(tmp_path); store.write('event', {}); store.close()
    entered = threading.Event(); release = threading.Event(); completed = threading.Event()
    class Delayed(Remote):
        def put(self, path, tag):
            entered.set()
            if not release.wait(2): raise TimeoutError('Test synchronization failed')
            result = super().put(path, tag); completed.set(); return result
    async def scenario():
        stopped = asyncio.Event()
        task = asyncio.create_task(publish_pending([store], Delayed(), stopped))
        try:
            for _ in range(100):
                if entered.is_set(): break
                await asyncio.sleep(0.001)
            assert entered.is_set()
            task.cancel()
            with pytest.raises(asyncio.CancelledError): await task
            assert store.records[0]['status'] == 'upload_failed'
        finally:
            release.set()
        for _ in range(100):
            if completed.is_set(): break
            await asyncio.sleep(0.001)
        assert completed.is_set()
    asyncio.run(scenario())
    assert (tmp_path/store.records[0]['path']).exists()
    assert sink(tmp_path).records[0]['status'] == 'closed'


def test_nonobject_gzip_envelope_is_quarantined(tmp_path):
    path = tmp_path/'market-nonobject.jsonl.gz'
    with gzip.open(path, 'wt') as target: target.write('[]\n')
    store = sink(tmp_path)
    assert store.records[0]['status'] == 'quarantined' and path.exists()


def test_run_local_success_and_publication_failure_reports(tmp_path, monkeypatch):
    async def capture(route, symbols, store, deadline):
        store.write('event', {'route': route})
    async def snapshots(symbols, store, deadline):
        store.write('snapshot_unavailable', {'http_status': 451})
    monkeypatch.setattr(collector, 'capture', capture)
    monkeypatch.setattr(collector, 'snapshots', snapshots)
    cfg = dict(symbols=['BTCUSDT'], max_local_storage_gb=0.1)
    local = tmp_path/'local'
    report = asyncio.run(collector.run(cfg, 1, root=local))
    assert report['status'] == 'CAPTURE_FINISHED' and report['publication']['status'] == 'LOCAL_ONLY'
    assert report['integrity_status'] == 'PASS'
    class Failed(Remote):
        def put(self, *args): raise ValueError('Injected remote failure')
    root = tmp_path/'remote'
    with pytest.raises(RuntimeError, match='publication incomplete'):
        asyncio.run(collector.run(cfg, 1, Failed(), root=root))
    report = json.loads((root/'session-report.json').read_text())
    assert report['status'] == 'FAILED' and report['publication']['status'] == 'FAILED'
    assert len(list(root.glob('*.jsonl.gz'))) == 3


@pytest.mark.parametrize('failure', ['bridge', 'sequence'])
def test_order_book_cannot_become_valid_after_gap_without_new_snapshot(failure):
    from live_collector.book import OrderBook, BookGap
    book = OrderBook()
    snapshot = dict(lastUpdateId=10, bids=[['9','1']], asks=[['11','1']])
    book.snapshot(snapshot)
    if failure == 'sequence':
        book.update(dict(U=9, u=11, pu=8, b=[], a=[]))
        bad = dict(U=13, u=14, pu=12, b=[], a=[])
    else:
        bad = dict(U=12, u=13, pu=11, b=[], a=[])
    with pytest.raises(BookGap): book.update(bad)
    assert not book.valid and book.last is None
    with pytest.raises(BookGap, match='Snapshot required'):
        book.update(dict(U=9, u=11, pu=8, b=[], a=[]))
    book.snapshot(snapshot)
    assert book.update(dict(U=9, u=11, pu=8, b=[], a=[])) and book.valid
