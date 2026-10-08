"""Read-only, bounded-batch replay of explicitly selected immutable partitions."""
from collections import defaultdict
from copy import deepcopy
from datetime import date
import hashlib
import heapq
import json
from pathlib import Path
import re

import pyarrow.parquet as pq

from .normalize import schema_for
from .research import LeakageError, assert_causal
from .sources import day_ms, period_bounds


ASSUMPTIONS = frozenset((
    'exchange_time_zero_latency_assumption', 'bar_close_boundary_assumption',
))


class ReplayIntegrityError(ValueError):
    """A selected input cannot be admitted to research replay."""


def _integer(value, name):
    if type(value) is not int or value < 0:
        raise ValueError(f'{name} must be a nonnegative integer')
    return value


def _availability(event, allow_exchange_assumption):
    available = event.get('available_at_ms')
    if available is None:
        raise LeakageError('Unknown historical publication time')
    _integer(available, 'available_at_ms')
    _integer(event.get('event_time_ms'), 'event_time_ms')
    basis = event.get('availability_basis')
    if basis != 'received' and not (
        allow_exchange_assumption and basis in ASSUMPTIONS
    ):
        raise LeakageError('Unapproved availability basis; historical assumptions require explicit opt-in')
    assert_causal(event, available)
    return available


class MarketReplayEngine:
    """Merge selected local Parquets by availability without loading entire tables.

    Records must be selected explicitly. No download, QA bypass, pruning, gap fill,
    execution model or strategy is performed. Missing local files require a
    separately verified restoration. The manifest describes coverage, not a
    guarantee that unselected dates exist.
    """

    def __init__(self, root, records, *, batch_size=1000,
                 allow_exchange_assumption=False):
        if type(batch_size) is not int or not 1 <= batch_size <= 10000:
            raise ValueError('batch_size must be between 1 and 10000')
        self.root = Path(root).resolve()
        self.batch_size = batch_size
        self.allow_exchange_assumption = allow_exchange_assumption
        self.records = deepcopy(list(records))
        if not self.records:
            raise ValueError('Select at least one manifest partition')
        self.groups = defaultdict(list)
        keys = set()
        for record in self.records:
            if record.get('qa', {}).get('status') != 'PASS' or record.get('status') != 'PASS':
                raise ReplayIntegrityError('Quarantined/nonpassing partition cannot enter replay')
            if record.get('schema_version') != '1':
                raise ReplayIntegrityError('Unsupported manifest schema version')
            symbol, dataset = record['symbol'], record['dataset']
            day = date.fromisoformat(record['day'])
            begin, end = period_bounds(dataset, day)
            key = f'{symbol}/{dataset}/{day}'
            if record.get('key') != key or key in keys:
                raise ReplayIntegrityError('Duplicate/inconsistent partition key')
            keys.add(key)
            normalized = record.get('normalized', {})
            digest = normalized.get('sha256')
            if not isinstance(digest, str) or not re.fullmatch('[0-9a-f]{64}', digest):
                raise ReplayIntegrityError('Missing/invalid normalized checksum')
            if _integer(normalized.get('bytes'), 'normalized bytes') == 0:
                raise ReplayIntegrityError('Empty normalized input')
            if _integer(record['qa'].get('rows'), 'QA rows') == 0:
                raise ReplayIntegrityError('Empty QA partition')
            path = Path(normalized.get('path', ''))
            if not path.parts or path.is_absolute() or '..' in path.parts:
                raise ReplayIntegrityError('Normalized path must stay inside replay root')
            resolved = (self.root / path).resolve()
            if not resolved.is_relative_to(self.root):
                raise ReplayIntegrityError('Normalized path escapes replay root')
            self.groups[(symbol, dataset)].append((begin, end, record, resolved))
        if len(self.groups) > 32:
            raise ValueError('At most 32 simultaneous streams are supported')
        self.coverage_gaps = []
        for (symbol, dataset), partitions in sorted(self.groups.items()):
            partitions.sort(key=lambda item: item[0])
            for left, right in zip(partitions, partitions[1:]):
                if left[1] > right[0]:
                    raise ReplayIntegrityError('Overlapping selected partitions')
                if left[1] < right[0]:
                    self.coverage_gaps.append(dict(
                        symbol=symbol, dataset=dataset, start=str(left[1]),
                        end_exclusive=str(right[0]), days=(right[0]-left[1]).days,
                        reason='Interval not selected; no continuity claim'))

    @classmethod
    def from_manifest(cls, root, keys, **options):
        keys = list(keys)
        if not keys or len(set(keys)) != len(keys):
            raise ValueError('Select distinct manifest keys')
        records = {}
        with (Path(root) / 'manifest.jsonl').open() as source:
            for line in source:
                if not line.strip():
                    continue
                record = json.loads(line)
                key = record['key']
                if key in records:
                    raise ReplayIntegrityError('Duplicate manifest key')
                records[key] = record
        missing = set(keys) - records.keys()
        if missing:
            raise ReplayIntegrityError(f'Missing manifest keys: {sorted(missing)}')
        return cls(root, (records[key] for key in keys), **options)

    def _stream(self, partitions, until_ms):
        previous_available = previous_time = previous_id = previous_end = None
        for begin, end, record, path in partitions:
            # No future partition is needed when its earliest event is beyond cutoff.
            if day_ms(begin) > until_ms:
                return
            if not path.is_file():
                raise ReplayIntegrityError(f'Restore verified local input first: {record["key"]}')
            with path.open('rb') as source:
                digest = hashlib.sha256()
                size = 0
                for chunk in iter(lambda: source.read(1024 * 1024), b''):
                    digest.update(chunk)
                    size += len(chunk)
                receipt = record['normalized']
                if size != receipt['bytes'] or digest.hexdigest() != receipt['sha256']:
                    raise ReplayIntegrityError(f'Input checksum/size mismatch: {record["key"]}')
                source.seek(0)
                parquet = pq.ParquetFile(source, pre_buffer=False)
                try:
                    dataset = record['dataset']
                    if not parquet.schema_arrow.equals(schema_for(dataset), check_metadata=True):
                        raise ReplayIntegrityError(f'Parquet schema drift: {record["key"]}')
                    if parquet.metadata.num_rows != record['qa']['rows']:
                        raise ReplayIntegrityError(f'Parquet row count mismatch: {record["key"]}')
                    if previous_end != begin:
                        # A missing selected day is a coverage gap, not proof of lost IDs.
                        previous_id = None
                    id_field = 'agg_trade_id' if dataset == 'aggTrades' else 'trade_id' if dataset == 'trades' else None
                    for batch in parquet.iter_batches(batch_size=self.batch_size, use_threads=False):
                        for event in batch.to_pylist():
                            if event['symbol'] != record['symbol']:
                                raise ReplayIntegrityError('Parquet symbol mismatch')
                            ts = event['event_time_ms']
                            _integer(ts, 'event_time_ms')
                            if not day_ms(begin) <= ts < day_ms(end):
                                raise ReplayIntegrityError('Event outside declared partition')
                            available = _availability(event, self.allow_exchange_assumption)
                            if previous_available is not None and available < previous_available:
                                raise LeakageError('Availability order regression')
                            if previous_time is not None and ts < previous_time:
                                raise ReplayIntegrityError('Event time order regression')
                            if id_field:
                                identifier = _integer(event[id_field], id_field)
                                if previous_id is not None and identifier != previous_id + 1:
                                    raise ReplayIntegrityError('Trade ID discontinuity within/across adjacent partitions')
                                previous_id = identifier
                            previous_time, previous_available = ts, available
                            if available > until_ms:
                                return
                            yield dict(event, dataset=dataset, partition_key=record['key'])
                    previous_end = end
                finally:
                    parquet.close()

    def events(self, until_ms):
        """Deterministic ties: symbol/dataset stream order, then original row order.

        Tied events are not evidence of an exchange-wide ordering. Consumers that
        decide at T should process every event available at T before deciding.
        """
        _integer(until_ms, 'until_ms')
        streams = [self._stream(self.groups[key], until_ms) for key in sorted(self.groups)]
        try:
            yield from heapq.merge(*streams, key=lambda event: event['available_at_ms'])
        finally:
            for stream in streams:
                stream.close()


def align_asof(events, decision_times, *, symbols, dataset, max_age_ms,
               allow_exchange_assumption=False):
    """Backward availability join; missing/stale observations stay explicit.

    All ties at T are consumed before a snapshot at T. Age is measured from the
    source event time, so an old event arriving late cannot masquerade as fresh.
    Each snapshot is copied. One future event may be buffered internally and is
    never exposed. This function does not resample, interpolate or backfill.
    """
    _integer(max_age_ms, 'max_age_ms')
    symbols = tuple(symbols)
    if not symbols or len(set(symbols)) != len(symbols):
        raise ValueError('Select distinct symbols')
    latest = {}
    previous_available = previous_decision = None
    iterator = iter(events)

    def next_event():
        nonlocal previous_available
        event = next(iterator, None)
        if event is None:
            return None
        available = _availability(event, allow_exchange_assumption)
        if previous_available is not None and available < previous_available:
            raise LeakageError('As-of input availability order regression')
        previous_available = available
        if event.get('symbol') not in symbols or event.get('dataset') != dataset:
            raise ValueError('As-of input contains an unselected symbol/dataset')
        return event

    pending = None
    started = False
    try:
        for decision in decision_times:
            _integer(decision, 'decision time')
            if previous_decision is not None and decision <= previous_decision:
                raise ValueError('Decision times must be strictly increasing')
            previous_decision = decision
            if not started:
                pending = next_event()
                started = True
            while pending is not None and pending['available_at_ms'] <= decision:
                latest[pending['symbol']] = dict(pending)
                pending = next_event()
            observations, states = {}, {}
            for symbol in symbols:
                event = latest.get(symbol)
                if event is None:
                    observations[symbol], states[symbol] = None, 'missing'
                elif decision - event['event_time_ms'] > max_age_ms:
                    observations[symbol], states[symbol] = None, 'stale'
                else:
                    assert_causal(event, decision)
                    observations[symbol], states[symbol] = dict(event), 'available'
            yield {'as_of_ms': decision, 'observations': observations, 'states': states}
    finally:
        close = getattr(iterator, 'close', None)
        if close:
            close()
