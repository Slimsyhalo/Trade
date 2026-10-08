"""Read-only public capture with durable spooling and serialized publication.

No book validity is claimed without an official snapshot bridge. Every received
message is retained, including duplicates. Disconnects/restarts remain explicit.
"""
import argparse
import asyncio
from collections import Counter
import json
from pathlib import Path
import random
import time

import requests
import websockets
import yaml

from quantlab_core.io import Budget, HTTP, atomic_json
from quantlab_core.sources import SYMBOLS
from .sequence import SequenceTracker
from .spool import Sink, publish_pending


async def capture(route, symbols, sink, deadline):
    suffixes = ['bookTicker', 'depth@100ms'] if route == 'public' else ['aggTrade', 'markPrice@1s', 'forceOrder']
    streams = '/'.join(symbol.lower()+'@'+topic for symbol in symbols for topic in suffixes)
    url = 'wss://fstream.binance.com/'+route+'/stream?streams='+streams
    tracker = SequenceTracker(sink.sequence_state)
    attempt = 0
    while time.monotonic() < deadline:
        try:
            async with websockets.connect(url, open_timeout=20, ping_interval=20, max_queue=1024) as socket:
                sink.write('connection_start', dict(route=route, continuity='new_connection_unverified',
                                                   previous_sequence_checkpoint=tracker.last.copy(), book_valid=False))
                attempt = 0
                async for message in socket:
                    if time.monotonic() >= deadline:
                        break
                    try:
                        envelope = json.loads(message)
                        if not isinstance(envelope, dict):
                            raise ValueError('Combined message must be an object')
                    except (ValueError, TypeError) as error:
                        sink.write('malformed_message', dict(raw=message.decode('utf-8', errors='replace') if isinstance(message, bytes) else message,
                                                             error=str(error)))
                        continue
                    markers = tracker.observe(envelope)
                    sink.sequence_state = tracker.last.copy()
                    # Preserve RAW even if sequence analysis calls it a duplicate.
                    sink.write('event', envelope)
                    for kind, payload in markers:
                        sink.write(kind, payload)
                # A clean close before deadline also means interrupted coverage.
                if time.monotonic() < deadline:
                    sink.write('disconnect', dict(error='Remote stream ended', unrecoverable_gap_possible=True, book_valid=False))
                    attempt += 1
        except asyncio.CancelledError:
            sink.write('capture_stop', dict(reason='deadline_or_cancellation', continuity='stopped', book_valid=False))
            raise
        except (OSError, TimeoutError, websockets.exceptions.WebSocketException) as error:
            sink.write('disconnect', dict(error=str(error), unrecoverable_gap_possible=True, book_valid=False))
            attempt += 1
        finally:
            sink.close()
        if attempt and time.monotonic() < deadline:
            await asyncio.sleep(min(max(0, deadline-time.monotonic()), min(30, 2**min(attempt, 5))+random.random()))


def fetch_snapshot(http, endpoint, params):
    response = http.get('https://fapi.binance.com/fapi/v1/'+endpoint, params=params)
    try:
        return response.json()
    finally:
        response.close()


async def snapshots(symbols, sink, deadline):
    http = HTTP(interval=1)
    try:
        while time.monotonic() < deadline:
            for symbol in symbols:
                for endpoint, params in [('openInterest', {'symbol': symbol}), ('depth', {'symbol': symbol, 'limit': 1000})]:
                    if time.monotonic() >= deadline:
                        return
                    try:
                        payload = await asyncio.to_thread(fetch_snapshot, http, endpoint, params)
                        sink.write(endpoint+'_snapshot', dict(symbol=symbol, data=payload))
                    except requests.HTTPError as error:
                        status = error.response.status_code if error.response is not None else None
                        if error.response is not None:
                            error.response.close()
                        if status in (403, 451):
                            sink.write('snapshot_unavailable', dict(symbol=symbol, endpoint=endpoint,
                                       http_status=status, reason='Official REST access blocked; polling stopped', book_valid=False))
                            return
                        sink.write('snapshot_error', dict(symbol=symbol, endpoint=endpoint, http_status=status, error=str(error)))
                    except (requests.RequestException, ValueError) as error:
                        sink.write('snapshot_error', dict(symbol=symbol, endpoint=endpoint, error=str(error)))
            await asyncio.sleep(min(30, max(0, deadline-time.monotonic())))
    finally:
        sink.close()


async def run(cfg, seconds, remote=None, *, root=Path('data/live'), drain_seconds=30):
    if type(seconds) is not int or seconds <= 0:
        raise ValueError('Positive integer capture duration required')
    if not cfg.get('symbols') or len(set(cfg['symbols'])) != len(cfg['symbols']) or any(s not in SYMBOLS for s in cfg['symbols']):
        raise ValueError('Select distinct supported public-market symbols')
    root = Path(root).resolve()
    budget = Budget(root.parent, cfg['max_local_storage_gb'])
    sinks = [Sink(root, budget, route) for route in ('public', 'market', 'snapshots')]
    started = time.monotonic()
    deadline = started + seconds
    stopped = asyncio.Event()
    publisher = asyncio.create_task(publish_pending(sinks, remote, stopped, drain_seconds=drain_seconds)) if remote else None
    error = None
    try:
        async with asyncio.timeout(seconds+1):
            async with asyncio.TaskGroup() as tasks:
                tasks.create_task(capture('public', cfg['symbols'], sinks[0], deadline))
                tasks.create_task(capture('market', cfg['symbols'], sinks[1], deadline))
                tasks.create_task(snapshots(cfg['symbols'], sinks[2], deadline))
    except TimeoutError:
        pass
    except Exception as caught:
        error = caught
    finally:
        for sink in sinks:
            try:
                sink.close()
            except Exception as caught:
                if error is None:
                    error = caught
        stopped.set()
        publication = await publisher if publisher else dict(status='LOCAL_ONLY', published_segments=0,
                                                             pending_segments=sum(len(s.pending()) for s in sinks))
    states = Counter(record.get('status', 'unknown') for sink in sinks for record in sink.records)
    integrity = 'FAILED' if states['quarantined'] or states['missing_local'] else 'PASS'
    report = dict(status='FAILED' if error is not None or integrity == 'FAILED' or publication['status'] in ('FAILED', 'PAUSED_BACKLOG') else 'CAPTURE_FINISHED',
                  integrity_status=integrity,
                  elapsed_seconds=round(time.monotonic()-started, 3), requested_capture_seconds=seconds,
                  publication=publication, segment_states=dict(states),
                  retained_bytes=sum(r.get('bytes', 0) for s in sinks for r in s.records),
                  notice='Includes existing spool; no continuous coverage or valid L2 book claim; no pruning',
                  error=str(error) if error is not None else None)
    atomic_json(root/'session-report.json', report)
    if error is not None:
        raise error
    if report['status'] == 'FAILED':
        raise RuntimeError('Live integrity/publication incomplete; preserve spool and reconcile before resuming')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seconds', type=int, default=60)
    parser.add_argument('--remote', action='store_true')
    parser.add_argument('--drain-seconds', type=int, default=30)
    args = parser.parse_args()
    if args.drain_seconds < 0:
        parser.error('--drain-seconds must be nonnegative')
    cfg = yaml.safe_load(Path('config.yaml').read_text())
    remote = None
    if args.remote:
        from quantlab_core.remote import GitHubRemote
        remote = GitHubRemote(cfg['repository'], interval=cfg.get('github_request_interval_seconds', 4))
    from quantlab_core.lock import writer_lock
    with writer_lock(Path('.pipeline.lock')):
        print(json.dumps(asyncio.run(run(cfg, args.seconds, remote, drain_seconds=args.drain_seconds))))
