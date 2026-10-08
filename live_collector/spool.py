"""Durable local segments; a single async publisher owns remote mutations.

Raw data is never pruned here, including after a verified upload. A separately
durable remote manifest checkpoint is required before any future pruning policy.
"""
import asyncio
from copy import deepcopy
from datetime import datetime, timezone
import gzip
import json
import os
from pathlib import Path
import time
import uuid
import zlib

from quantlab_core.io import atomic_json, sha256

MAX_RECORD_BYTES = 2_000_000
ROUTES = ('public', 'market', 'snapshots')


def sync_directory(path):
    if os.name == 'posix':
        descriptor = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(descriptor)
        finally:
            os.close(descriptor)


def inspect_segment(path):
    rows = 0
    first = last = None
    with gzip.open(path, 'rb') as source:
        while True:
            line = source.readline(MAX_RECORD_BYTES + 1)
            if not line:
                break
            if len(line) > MAX_RECORD_BYTES or not line.endswith(b'\n'):
                raise ValueError('Oversized/incomplete JSONL record')
            row = json.loads(line)
            if not isinstance(row, dict):
                raise ValueError('Live row envelope must be an object')
            stamp = row.get('receive_timestamp_ns')
            if type(stamp) is not int or stamp <= 0 or not isinstance(row.get('kind'), str) or 'payload' not in row:
                raise ValueError('Invalid live row envelope')
            # Wall-clock regressions are retained; monotonic receipt ordering
            # is not inferred from a machine clock which may be adjusted.
            first = stamp if first is None else first
            last = stamp
            rows += 1
    if not rows:
        raise ValueError('Empty live segment')
    return dict(rows=rows, first_receive_ns=first, last_receive_ns=last)


def receipt_matches(record, receipt):
    return (isinstance(receipt, dict) and receipt.get('sha256') == record['sha256']
            and type(receipt.get('bytes')) is int and receipt['bytes'] == record['bytes']
            and bool(receipt.get('verified_at')) and bool(receipt.get('api_url')))


class Sink:
    def __init__(self, root, budget, route, remote=None, *, max_bytes=8_000_000, max_seconds=60):
        if route not in ROUTES:
            raise ValueError('Unsupported live route')
        if max_bytes <= 0 or max_seconds <= 0:
            raise ValueError('Positive segment limits required')
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.budget, self.route, self.remote = budget, route, remote
        self.max_bytes, self.max_seconds = max_bytes, max_seconds
        self.manifest_path = self.root / (route + '-manifest.json')
        self.records = json.loads(self.manifest_path.read_text()) if self.manifest_path.exists() else []
        self.f = self.raw = self.path = None
        self.count = 0
        self.started = 0
        self.first_receive_ns = self.last_receive_ns = None
        self.sequence_state = {}
        self._recover()

    def _save(self):
        atomic_json(self.manifest_path, self.records)
        sync_directory(self.root)

    def local_path(self, record):
        path = Path(record['path'])
        # Old manifests recorded absolute or cwd-relative data/live paths.
        candidate = path.resolve() if path.is_absolute() or len(path.parts) > 1 else (self.root / path).resolve()
        if candidate.parent != self.root or not candidate.name.startswith(self.route + '-'):
            raise ValueError('Live manifest path escapes its route/root')
        return candidate

    def _recover(self):
        known = set()
        for record in self.records:
            path = self.local_path(record)
            if path.name in known:
                raise ValueError('Duplicate live manifest path')
            known.add(path.name)
            record['path'] = path.name
            if record.get('status') == 'quarantined':
                self.sequence_state = {}
                continue
            if not path.is_file():
                record.update(status='missing_local', last_error='Local segment absent; no restoration performed')
                self.sequence_state = {}
                continue
            try:
                if sha256(path) != record['sha256'] or path.stat().st_size != record['bytes']:
                    raise ValueError('Live checksum/size mismatch')
                observed = inspect_segment(path)
                if observed['rows'] != record['rows']:
                    raise ValueError('Live row count mismatch')
                record.update(observed, integrity_status='PASS')
                record['status'] = 'remote_verified' if receipt_matches(record, record.get('remote')) else 'closed'
                if record.get('sequence_state') is not None:
                    self.sequence_state = deepcopy(record['sequence_state'])
                else:
                    self.sequence_state = {}
            except (ValueError, KeyError, OSError, EOFError, zlib.error) as error:
                record.update(status='quarantined', integrity_status='FAILED', last_error=str(error))
                self.sequence_state = {}
        for path in sorted(self.root.glob(self.route + '-*.jsonl.gz*')):
            if path.name in known or not (path.name.endswith('.jsonl.gz') or path.name.endswith('.jsonl.gz.part')):
                continue
            if path.resolve().parent != self.root:
                raise ValueError('Orphan live segment escapes root')
            record = dict(path=path.name, sha256=sha256(path), bytes=path.stat().st_size,
                          remote=None, recovered=True, sequence_state=None,
                          continuity='unknown_after_recovery')
            try:
                if path.name.endswith('.part'):
                    raise ValueError('Interrupted open segment retained without promotion')
                record.update(inspect_segment(path), integrity_status='PASS', status='closed')
                self._set_tag(record)
            except (ValueError, OSError, EOFError, zlib.error) as error:
                record.update(rows=None, status='quarantined', integrity_status='FAILED', last_error=str(error))
            self.records.append(record)
            # An orphan tail has no committed cursor; never carry an older
            # checkpoint forward as if every received event were represented.
            self.sequence_state = {}
        if self.records:
            self._save()

    def _set_tag(self, record):
        stamp = record.get('last_receive_ns') or time.time_ns()
        hour = datetime.fromtimestamp(stamp / 1e9, timezone.utc).strftime('%Y-%m-%d-%H')
        record.setdefault('tag', f'live-{self.route}-{hour}')

    def write(self, kind, payload):
        now = time.time_ns()
        data = (json.dumps(dict(receive_timestamp_ns=now, kind=kind, payload=payload),
                           separators=(',', ':')) + '\n').encode()
        if len(data) > MAX_RECORD_BYTES:
            raise ValueError('Live row exceeds declared envelope limit')
        self.budget.check(len(data) + 65536)
        if self.f is None:
            name = f'{self.route}-{now}-{uuid.uuid4().hex}.jsonl.gz.part'
            self.path = self.root / name
            self.raw = self.path.open('xb')
            self.f = gzip.GzipFile(fileobj=self.raw, mode='wb', filename='', mtime=0)
            self.count = 0
            self.started = time.monotonic()
            self.first_receive_ns = now
        self.f.write(data)
        self.f.flush()
        self.raw.flush()
        self.count += 1
        self.last_receive_ns = now
        if self.path.stat().st_size >= self.max_bytes or time.monotonic()-self.started >= self.max_seconds:
            self.close()

    def close(self):
        if self.f is None:
            return
        path = self.path
        try:
            self.f.close()
            self.raw.flush()
            os.fsync(self.raw.fileno())
        finally:
            self.raw.close()
            self.f = self.raw = None
        final = path.with_suffix('')
        os.replace(path, final)
        sync_directory(self.root)
        record = dict(path=final.name, sha256=sha256(final), bytes=final.stat().st_size,
                      rows=self.count, remote=None, status='closed', integrity_status='PASS',
                      first_receive_ns=self.first_receive_ns, last_receive_ns=self.last_receive_ns,
                      sequence_state=deepcopy(self.sequence_state), continuity='requires_connection_and_gap_markers')
        self._set_tag(record)
        self.records.append(record)
        self._save()

    def pending(self):
        return [r for r in self.records if r.get('status') in ('closed', 'upload_failed')]

    def begin_upload(self, record):
        path = self.local_path(record)
        if not path.is_file() or sha256(path) != record['sha256'] or path.stat().st_size != record['bytes']:
            record.update(status='quarantined', integrity_status='FAILED', last_error='Input changed before upload')
            self._save()
            raise ValueError(record['last_error'])
        self._set_tag(record)
        record.update(status='uploading', upload_attempts=record.get('upload_attempts', 0)+1)
        self._save()
        return path

    def verified(self, record, receipt):
        if not receipt_matches(record, receipt):
            raise ValueError('Remote receipt does not prove matching readback')
        record.update(remote=receipt, status='remote_verified', last_error=None)
        self._save()

    def failed(self, record, error):
        if record.get('status') != 'quarantined':
            record.update(status='upload_failed', last_error=str(error), remote=None)
        self._save()


async def publish_pending(sinks, remote, stopped, *, poll_seconds=0.1, drain_seconds=30):
    """One remote call at a time; stopped capture gets a bounded new-work drain.

    An in-flight remote request is allowed to finish, including its own network
    timeout/rate-limit policy. Cancelling a Python thread does not abort that I/O.
    Ambiguous failures are not retried within this session. Restart uses immutable
    asset-name reconciliation in GitHubRemote.put. No files are deleted.
    """
    published = 0
    drain_deadline = None
    while True:
        if stopped.is_set() and drain_deadline is None:
            drain_deadline = time.monotonic() + drain_seconds
        pending = [(sink, record) for sink in sinks for record in sink.pending()]
        if not pending:
            if stopped.is_set():
                return dict(status='COMPLETE', published_segments=published, pending_segments=0)
            await asyncio.sleep(poll_seconds)
            continue
        if drain_deadline is not None and time.monotonic() >= drain_deadline:
            return dict(status='PAUSED_BACKLOG', published_segments=published, pending_segments=len(pending))
        sink, record = min(pending, key=lambda item: (item[1].get('last_receive_ns', 0), item[1]['path']))
        try:
            path = sink.begin_upload(record)
            receipt = await asyncio.to_thread(remote.put, path, record['tag'])
            sink.verified(record, receipt)
            published += 1
        except asyncio.CancelledError:
            # Keep the immutable input. A following process reconciles a remote
            # asset which may have been accepted before cancellation.
            sink.failed(record, 'Publisher cancelled; reconcile immutable asset before resuming')
            raise
        except Exception as error:
            sink.failed(record, error)
            return dict(status='FAILED', error=str(error), published_segments=published,
                        pending_segments=sum(len(s.pending()) for s in sinks))
