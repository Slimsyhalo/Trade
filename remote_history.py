"""Resume bounded historical acquisition after a verified remote pilot.

Each checkpoint is published before pruning. No strategy selection or trading.
"""
import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
import yaml
from quantlab_core.io import atomic_json
from quantlab_core.pipeline import Pipeline
from quantlab_core.remote import GitHubRemote
from quantlab_core.sources import days

DATASETS = ('klines', 'markPriceKlines', 'indexPriceKlines', 'premiumIndexKlines', 'metrics')


def is_verified(record):
    return record.get('qa', {}).get('status') == 'PASS' and all(
        (record.get(kind, {}).get('remote') or {}).get('verified_at')
        for kind in ('raw', 'normalized'))


def main():
    root = Path(__file__).resolve().parent
    pilot = json.loads((root/'reports/remote_execution.json').read_text())
    if pilot.get('status') != 'PASS' or pilot.get('restore', {}).get('status') != 'PASS':
        raise RuntimeError('Real remote restore gate not passed')
    cfg = yaml.safe_load((root/'config.yaml').read_text())
    pipe = Pipeline(root, cfg)
    remote = GitHubRemote(cfg['repository'])
    start = time.monotonic()
    pending = []
    report = {'status': 'RUNNING', 'scope': list(DATASETS), 'processed_this_run': 0,
              'started_at': datetime.now(timezone.utc).isoformat(),
              'notice': 'Small datasets only. Trades/aggTrades bulk awaits stratified capacity review. Phase 1 incomplete.'}

    def checkpoint():
        pipe.catalog()
        report['updated_at'] = datetime.now(timezone.utc).isoformat()
        report['remote_verified_partitions'] = sum(is_verified(r) for r in pipe.records.values())
        atomic_json(root/'reports/historical_execution.json', report)
        subprocess.run(['git', 'add', 'manifest.jsonl', 'data_catalog.json', 'reports/historical_execution.json'], check=True)
        if subprocess.run(['git', 'diff', '--cached', '--quiet']).returncode:
            subprocess.run(['git', 'commit', '-m', 'Checkpoint verified historical data and coverage'], check=True)
            subprocess.run(['git', 'push', 'origin', 'HEAD:main'], check=True)
        for record in pending:
            for kind in ('raw', 'normalized'):
                (root/record[kind]['path']).unlink(missing_ok=True)
        pending.clear()

    try:
        for day in days(cfg['start_date'], cfg['end_date']):
            if day >= datetime.now(timezone.utc).date():
                continue
            for symbol in cfg['symbols']:
                for dataset in DATASETS:
                    key = f'{symbol}/{dataset}/{day}'
                    existing = pipe.records.get(key, {})
                    if is_verified(existing):
                        continue
                    if time.monotonic()-start > 240*60:
                        report['status'] = 'PAUSED_TIME_BUDGET'
                        checkpoint()
                        return
                    record = pipe.sync_one(symbol, dataset, day, remote, False)
                    report['processed_this_run'] += 1
                    report['last_partition'] = key
                    if record.get('status') == 'not_published_or_unavailable':
                        pass
                    elif not is_verified(record):
                        raise RuntimeError(f'QA or remote verification failed: {key}')
                    else:
                        pending.append(record)
                    # <=25 small partitions retained until a durable Git checkpoint.
                    if report['processed_this_run'] % 25 == 0:
                        checkpoint()
        report['status'] = 'SCOPED_SCAN_FINISHED'
        checkpoint()
    except Exception as exc:
        report['status'] = 'BLOCKED'
        report['error'] = str(exc)
        checkpoint()
        raise


if __name__ == '__main__':
    main()
