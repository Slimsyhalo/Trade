from copy import deepcopy
from datetime import date
import json

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from quantlab_core.io import sha256
from quantlab_core.normalize import schema_for
from quantlab_core.research import LeakageError
from quantlab_core.replay_engine import MarketReplayEngine, ReplayIntegrityError, align_asof
from quantlab_core.sources import day_ms
from replay_audit import audit


D = date(2024, 10, 7)
T = day_ms(D)


def event(ts=T, *, symbol='BTCUSDT', identifier=1, available=None, basis='received'):
    return dict(agg_trade_id=identifier, price='123.123456789012345678', quantity='0.001',
                first_trade_id=identifier, last_trade_id=identifier, timestamp=ts,
                is_buyer_maker=False, symbol=symbol, event_time_ms=ts,
                available_at_ms=ts if available is None else available, availability_basis=basis)


def partition(root, events, *, day=D, schema=None):
    symbol = events[0]['symbol']
    path = root / f'{symbol}-{day}.parquet'
    pq.write_table(pa.Table.from_pylist(events, schema=schema or schema_for('aggTrades')),
                   path, row_group_size=2, compression='zstd')
    return dict(key=f'{symbol}/aggTrades/{day}', symbol=symbol, dataset='aggTrades',
                day=str(day), schema_version='1', status='PASS',
                qa={'status': 'PASS', 'rows': len(events)},
                normalized={'path': path.name, 'sha256': sha256(path), 'bytes': path.stat().st_size})


def aligned_event(ts, symbol='BTCUSDT', **options):
    return dict(event(ts, symbol=symbol, **options), dataset='aggTrades')


def test_merge_precision_cutoff_deterministic_ties(tmp_path):
    btc = partition(tmp_path, [event(identifier=1), event(T+2, identifier=2)])
    eth = partition(tmp_path, [event(symbol='ETHUSDT')])
    engine = MarketReplayEngine(tmp_path, [eth, btc], batch_size=1)
    rows = list(engine.events(T+1))
    assert [row['symbol'] for row in rows] == ['BTCUSDT', 'ETHUSDT']
    assert rows[0]['price'] == '123.123456789012345678'
    assert rows[0]['dataset'] == 'aggTrades' and rows[0]['partition_key'] == btc['key']
    assert audit(engine, T+2)['replay_sha256'] == audit(engine, T+2)['replay_sha256']


def test_strict_assumptions_unknown_and_unrecognized(tmp_path):
    row = event(basis='exchange_time_zero_latency_assumption')
    record = partition(tmp_path, [row])
    with pytest.raises(LeakageError):
        list(MarketReplayEngine(tmp_path, [record]).events(T))
    assert len(list(MarketReplayEngine(tmp_path, [record], allow_exchange_assumption=True).events(T))) == 1
    for available, basis in ((None, 'unknown_historical_publication'), (T, 'made_up')):
        row.update(available_at_ms=available, availability_basis=basis)
        record = partition(tmp_path, [row])
        with pytest.raises(LeakageError):
            list(MarketReplayEngine(tmp_path, [record], allow_exchange_assumption=True).events(T))


@pytest.mark.parametrize('change', ['qa', 'status', 'version', 'digest', 'traversal', 'duplicate'])
def test_manifest_admission(tmp_path, change):
    record = partition(tmp_path, [event()])
    records = [record]
    if change == 'qa': record['qa']['status'] = 'FAILED'
    if change == 'status': record['status'] = 'FAILED'
    if change == 'version': record['schema_version'] = '2'
    if change == 'digest': record['normalized']['sha256'] = 'z' * 64
    if change == 'traversal': record['normalized']['path'] = '../elsewhere.parquet'
    if change == 'duplicate': records.append(deepcopy(record))
    with pytest.raises(ReplayIntegrityError): MarketReplayEngine(tmp_path, records)


@pytest.mark.parametrize('change', ['checksum', 'size', 'rows', 'absent', 'schema', 'symbol', 'outside'])
def test_input_integrity(tmp_path, change):
    rows = [event()]
    if change == 'outside': rows = [event(T-1)]
    if change == 'symbol': rows = [event(symbol='ETHUSDT')]
    schema = schema_for('aggTrades').remove_metadata() if change == 'schema' else None
    record = partition(tmp_path, rows, schema=schema)
    if change == 'symbol': record.update(symbol='BTCUSDT', key=f'BTCUSDT/aggTrades/{D}')
    if change == 'checksum': record['normalized']['sha256'] = '0' * 64
    if change == 'size': record['normalized']['bytes'] += 1
    if change == 'rows': record['qa']['rows'] += 1
    if change == 'absent': (tmp_path / record['normalized']['path']).unlink()
    with pytest.raises(ReplayIntegrityError):
        list(MarketReplayEngine(tmp_path, [record]).events(T))


def test_symlink_escape(tmp_path):
    record = partition(tmp_path, [event()])
    (tmp_path / 'escape').symlink_to(tmp_path.parent, target_is_directory=True)
    record['normalized']['path'] = 'escape/out.parquet'
    with pytest.raises(ReplayIntegrityError): MarketReplayEngine(tmp_path, [record])


@pytest.mark.parametrize('kind', ['arrival_regression', 'time_regression', 'future_event', 'id_gap'])
def test_ordering_and_causality(tmp_path, kind):
    rows = [event(available=T+2), event(T+1, identifier=2, available=T+3)]
    if kind == 'arrival_regression': rows[1]['available_at_ms'] = T+1
    if kind == 'time_regression': rows[1]['event_time_ms'] = T-1
    if kind == 'future_event': rows[1]['available_at_ms'] = T
    if kind == 'id_gap': rows[1]['agg_trade_id'] = 3
    record = partition(tmp_path, rows)
    with pytest.raises((ReplayIntegrityError, LeakageError)):
        list(MarketReplayEngine(tmp_path, [record]).events(T+10))


def test_adjacent_day_id_gap_and_missing_day(tmp_path):
    first = partition(tmp_path, [event(T+86399999)])
    second = partition(tmp_path, [event(T+86400000, identifier=3)], day=date(2024,10,8))
    with pytest.raises(ReplayIntegrityError, match='discontinuity'):
        list(MarketReplayEngine(tmp_path, [second, first]).events(T+86400000))
    later = partition(tmp_path, [event(T+172800000, identifier=9)], day=date(2024,10,9))
    engine = MarketReplayEngine(tmp_path, [first, later])
    assert len(list(engine.events(T+172800000))) == 2
    assert engine.coverage_gaps[0]['days'] == 1
    assert engine.coverage_gaps[0]['start'] == '2024-10-08'


def test_asof_ties_future_staleness_and_snapshot_copy():
    rows = [aligned_event(T, available=T+10), aligned_event(T+1, 'ETHUSDT', available=T+10),
            aligned_event(T+20, available=T+20, identifier=2)]
    snapshots = list(align_asof(rows, [T+9,T+10,T+19,T+20,T+31],
                              symbols=['BTCUSDT','ETHUSDT','SOLUSDT'], dataset='aggTrades', max_age_ms=10))
    assert snapshots[0]['states'] == dict(BTCUSDT='missing', ETHUSDT='missing', SOLUSDT='missing')
    assert snapshots[1]['states']['BTCUSDT'] == snapshots[1]['states']['ETHUSDT'] == 'available'
    assert snapshots[2]['observations']['BTCUSDT'] is None
    assert snapshots[3]['observations']['BTCUSDT']['agg_trade_id'] == 2
    assert snapshots[4]['states']['BTCUSDT'] == 'stale'
    snapshots[1]['observations']['BTCUSDT']['price'] = 'modified'
    assert rows[0]['price'] != 'modified'


def test_future_perturbation_cannot_change_earlier_snapshot():
    def snapshot(future_price):
        rows = [aligned_event(T), dict(aligned_event(T+100), price=future_price)]
        return list(align_asof(rows, [T+50], symbols=['BTCUSDT'], dataset='aggTrades', max_age_ms=100))[0]
    assert snapshot('1') == snapshot('9999999')


@pytest.mark.parametrize('kind', ['regression', 'future_event', 'wrong_dataset', 'decision_order', 'unknown'])
def test_asof_rejects_unsafe_inputs(kind):
    rows = [aligned_event(T), aligned_event(T+1)]
    decisions = [T,T+10]
    if kind == 'regression': rows.reverse()
    if kind == 'future_event': rows[1]['available_at_ms'] = T
    if kind == 'wrong_dataset': rows[1]['dataset'] = 'fundingRate'
    if kind == 'decision_order': decisions = [T,T]
    if kind == 'unknown': rows[1]['available_at_ms'] = None
    with pytest.raises((ValueError, LeakageError)):
        list(align_asof(rows, decisions, symbols=['BTCUSDT'], dataset='aggTrades', max_age_ms=100))


def test_resource_release_and_batch_bound(tmp_path, monkeypatch):
    record = partition(tmp_path, [event(T+i, identifier=i+1) for i in range(5)])
    real = pq.ParquetFile
    opened = []
    class Tracked:
        def __init__(self, *args, **kwargs):
            self.actual = real(*args, **kwargs); self.closed = False; opened.append(self)
        def __getattr__(self, name): return getattr(self.actual, name)
        def iter_batches(self, **kwargs):
            for batch in self.actual.iter_batches(**kwargs):
                assert batch.num_rows <= 1
                yield batch
        def close(self): self.actual.close(); self.closed = True
    monkeypatch.setattr('quantlab_core.replay_engine.pq.ParquetFile', Tracked)
    iterator = MarketReplayEngine(tmp_path, [record], batch_size=1).events(T+10)
    next(iterator); iterator.close()
    assert opened and all(p.closed for p in opened)


def test_manifest_selection_and_audit_tail(tmp_path):
    record = partition(tmp_path, [event(), event(T+9, identifier=2)])
    (tmp_path/'manifest.jsonl').write_text(json.dumps(record)+'\n')
    engine = MarketReplayEngine.from_manifest(tmp_path, [record['key']])
    report = audit(engine, T+9, decision_start_ms=T, decision_step_ms=5, max_age_ms=10)
    assert report['emitted_rows'] == 2 and report['asof']['decisions'] == 3
    assert report['last_available_at_ms'] == T+9
    with pytest.raises(ReplayIntegrityError): MarketReplayEngine.from_manifest(tmp_path, ['missing'])
    (tmp_path/'manifest.jsonl').write_text((json.dumps(record)+'\n')*2)
    with pytest.raises(ReplayIntegrityError): MarketReplayEngine.from_manifest(tmp_path, [record['key']])
