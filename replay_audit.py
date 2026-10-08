#!/usr/bin/env python3
"""Audit selected replay inputs; no strategy, execution or profitability output."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

from quantlab_core.io import atomic_json
from quantlab_core.replay_engine import MarketReplayEngine, align_asof


def audit(engine, until_ms, *, decision_start_ms=None, decision_step_ms=None,
          max_age_ms=None):
    counts = Counter()
    digest = hashlib.sha256()
    first = last = None

    def observed():
        nonlocal first, last
        iterator = engine.events(until_ms)
        try:
            for event in iterator:
                key = f'{event["symbol"]}/{event["dataset"]}'
                counts[key] += 1
                first = event['available_at_ms'] if first is None else first
                last = event['available_at_ms']
                digest.update(json.dumps(event, sort_keys=True, separators=(',', ':')).encode() + b'\n')
                yield event
        finally:
            iterator.close()

    snapshots = Counter()
    alignment = None
    if decision_start_ms is not None:
        if type(decision_step_ms) is not int or decision_step_ms <= 0:
            raise ValueError('Positive decision step required')
        if type(decision_start_ms) is not int or not 0 <= decision_start_ms <= until_ms:
            raise ValueError('Decision start must be within cutoff')
        datasets = {record['dataset'] for record in engine.records}
        if len(datasets) != 1:
            raise ValueError('As-of audit requires exactly one selected dataset')
        decisions = range(decision_start_ms, until_ms + 1, decision_step_ms)
        # Include the cutoff even when it is not aligned to the step, so every
        # emitted replay event is audited, rather than leaving an unconsumed tail.
        from itertools import chain
        if (until_ms - decision_start_ms) % decision_step_ms:
            decisions = chain(decisions, [until_ms])
        for snapshot in align_asof(
            observed(), decisions, symbols=sorted({r['symbol'] for r in engine.records}),
            dataset=next(iter(datasets)), max_age_ms=max_age_ms,
            allow_exchange_assumption=engine.allow_exchange_assumption,
        ):
            snapshots['decisions'] += 1
            snapshots.update(snapshot['states'].values())
        alignment = dict(snapshots, max_age_ms=max_age_ms,
                         age_basis='event_time_ms', equal_time_policy='consume_all_before_decision')
    else:
        for _ in observed():
            pass
    return {
        'status': 'PASS', 'generated_at': datetime.now(timezone.utc).isoformat(),
        'scope': 'Selected local inputs and events available through cutoff only; not C15 approval',
        'until_ms': until_ms, 'batch_size': engine.batch_size,
        'allow_exchange_assumption': engine.allow_exchange_assumption,
        'selected_coverage_gaps': engine.coverage_gaps,
        'selected_inputs': [dict(key=r['key'], normalized_sha256=r['normalized']['sha256'],
                                 declared_rows=r['qa']['rows']) for r in engine.records],
        'emitted_rows': sum(counts.values()), 'rows_by_stream': dict(sorted(counts.items())),
        'first_available_at_ms': first, 'last_available_at_ms': last,
        'replay_sha256': digest.hexdigest(), 'asof': alignment,
        'limitations': ['No inferred availability for funding/OI',
                        'No full-window coverage claim', 'No simulated trades or costs',
                        'Historical timestamps do not establish received latency'],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument('--key', action='append', required=True)
    parser.add_argument('--until-ms', type=int, required=True)
    parser.add_argument('--batch-size', type=int, default=1000)
    parser.add_argument('--allow-exchange-assumption', action='store_true')
    parser.add_argument('--decision-start-ms', type=int)
    parser.add_argument('--decision-step-ms', type=int)
    parser.add_argument('--max-age-ms', type=int)
    parser.add_argument('--output', type=Path, default=Path('reports/replay_audit.json'))
    args = parser.parse_args()
    alignment_options = (args.decision_start_ms, args.decision_step_ms, args.max_age_ms)
    if any(v is not None for v in alignment_options) and not all(v is not None for v in alignment_options):
        parser.error('As-of audit requires decision start, decision step and max age together')
    output = args.output if args.output.is_absolute() else args.root / args.output
    try:
        engine = MarketReplayEngine.from_manifest(
            args.root, args.key, batch_size=args.batch_size,
            allow_exchange_assumption=args.allow_exchange_assumption,
        )
        report = audit(engine, args.until_ms, decision_start_ms=args.decision_start_ms,
                       decision_step_ms=args.decision_step_ms, max_age_ms=args.max_age_ms)
    except Exception as error:
        atomic_json(output, {'status': 'FAILED', 'error_type': type(error).__name__,
                             'error': str(error), 'selected_keys': args.key,
                             'until_ms': args.until_ms})
        raise
    atomic_json(output, report)
    print(json.dumps({'status': report['status'], 'emitted_rows': report['emitted_rows'],
                      'replay_sha256': report['replay_sha256'], 'asof': report['asof']}))


if __name__ == '__main__':
    main()
