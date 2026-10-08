#!/usr/bin/env python3
"""Read-only integrity/sequence inspection of an explicitly inventoried live pilot."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import gzip
import json
from pathlib import Path
import time

from live_collector.sequence import SequenceTracker
from live_collector.spool import inspect_segment
from quantlab_core.io import atomic_json, sha256


def validate(root, inventory):
    root = Path(root).resolve()
    started, cpu_started = time.monotonic(), time.process_time()
    result = []
    names = set()
    trackers = {}
    for expected in inventory:
        name = Path(expected['path']).name
        if name in names:
            raise ValueError('Duplicate inventory input')
        names.add(name)
        path = (root/name).resolve()
        if path.parent != root or not path.is_file():
            raise ValueError('Selected live input missing/outside root')
        digest, size = sha256(path), path.stat().st_size
        if digest != expected['sha256'] or size != expected['bytes']:
            raise ValueError('Original live inventory checksum/size mismatch')
        observed = inspect_segment(path)
        if observed['rows'] != expected['rows']:
            raise ValueError('Original live inventory row count mismatch')
        route = name.split('-', 1)[0]
        tracker = trackers.setdefault(route, SequenceTracker())
        kinds, diagnostics = Counter(), Counter()
        with gzip.open(path, 'rt') as source:
            for line in source:
                row = json.loads(line)
                kinds[row['kind']] += 1
                if row['kind'] == 'event':
                    if not isinstance(row['payload'], dict):
                        diagnostics['malformed_event'] += 1
                    else:
                        diagnostics.update(kind for kind, _ in tracker.observe(row['payload']))
        result.append(dict(path=name, sha256=digest, bytes=size, **observed,
                           kinds=dict(kinds), sequence_diagnostics=dict(diagnostics),
                           final_observed_sequence=tracker.last.copy(), integrity_status='PASS'))
    if not result:
        raise ValueError('Select inventoried live inputs')
    return dict(status='PASS', scope='Retained original live pilot input integrity and observed sequence diagnostics only',
                generated_at=datetime.now(timezone.utc).isoformat(), segments=result,
                rows=sum(item['rows'] for item in result), bytes=sum(item['bytes'] for item in result),
                wall_seconds=round(time.monotonic()-started, 6),
                process_cpu_seconds=round(time.process_time()-cpu_started, 6),
                limitations=['No new live capture or new remote upload in this validation',
                             'Original collector may have discarded duplicate/old events; inspection cannot recover them',
                             'No valid full L2 book claim; original REST snapshots were blocked',
                             'Short pilot does not establish continuous/long-duration recovery'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--inventory', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=Path('reports/live_pilot_integrity.json'))
    args = parser.parse_args()
    try:
        report = validate(args.root, json.loads(args.inventory.read_text()))
    except Exception as error:
        atomic_json(args.output, dict(status='FAILED', error_type=type(error).__name__, error=str(error)))
        raise
    atomic_json(args.output, report)
    print(json.dumps({key: report[key] for key in ('status', 'rows', 'bytes', 'wall_seconds', 'process_cpu_seconds')}))


if __name__ == '__main__':
    main()
