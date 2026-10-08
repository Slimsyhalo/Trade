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
from build_audit import build_audit

DATASETS = ('aggTrades', 'klines', 'markPriceKlines', 'indexPriceKlines', 'premiumIndexKlines', 'metrics')


def validate_storage_review(root):
    probes=json.loads((root/'reports/stratified_storage_probe.json').read_text())
    for symbol in ('BTCUSDT','ETHUSDT','SOLUSDT'):
        sample=[r for r in probes if r['symbol']==symbol and r['dataset']=='aggTrades']
        if len(sample)!=12 or any(r.get('status')!=200 or r.get('bytes',0)<=0 for r in sample):
            raise RuntimeError('Stratified aggTrades storage review is incomplete')


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
    validate_storage_review(root)
    pipe = Pipeline(root, cfg)
    remote = GitHubRemote(cfg['repository'],interval=cfg.get('github_request_interval_seconds',4))
    start = time.monotonic()
    cpu_start=time.process_time()
    pending = []
    report = {'status': 'RUNNING', 'scope': list(DATASETS), 'processed_this_run': 0,
              'started_at': datetime.now(timezone.utc).isoformat(),
              'notice': 'AggTrades capacity reviewed across 12 dates/symbol. Individual trades remain quarantined for ID gaps. Phase 1 incomplete.'}

    def checkpoint():
        pipe.catalog()
        report['updated_at'] = datetime.now(timezone.utc).isoformat()
        report['remote_verified_partitions'] = sum(is_verified(r) for r in pipe.records.values())
        report['elapsed_seconds'] = round(time.monotonic()-start,2)
        report['process_cpu_seconds'] = round(time.process_time()-cpu_start,2)
        report['github_rate_events'] = remote.rate_events
        atomic_json(root/'reports/historical_execution.json', report)
        build_audit(root)
        subprocess.run(['git', 'add', 'manifest.jsonl', 'data_catalog.json', 'reports/historical_execution.json','AUDIT_SUMMARY.json','AUDIT_SUMMARY.md','DATA_COVERAGE.md','QA_REPORT.md','reports/validation.json'], check=True)
        if subprocess.run(['git', 'diff', '--cached', '--quiet']).returncode:
            subprocess.run(['git', 'commit', '-m', 'Checkpoint verified historical data and coverage'], check=True)
            subprocess.run(['git', 'push', 'origin', 'HEAD:main'], check=True)
        for record in pending:
            for kind in ('raw', 'normalized'):
                (root/record[kind]['path']).unlink(missing_ok=True)
        pending.clear()

    try:
        checkpoint()
        for day in days(cfg['start_date'], cfg['end_date']):
            if day >= datetime.now(timezone.utc).date():
                continue
            for symbol in cfg['symbols']:
                for dataset in DATASETS:
                    key = f'{symbol}/{dataset}/{day}'
                    existing = pipe.records.get(key, {})
                    if is_verified(existing):
                        continue
                    # A 404 is an observed absence, not downloaded coverage.
                    # Retry missing archives once per new run, not repeatedly within it.
                    if time.monotonic()-start > 240*60:
                        report['status'] = 'PAUSED_TIME_BUDGET'
                        checkpoint()
                        return
                    record = pipe.sync_one(symbol, dataset, day, remote, False)
                    report['processed_this_run'] += 1
                    report['last_partition'] = key
                    print(json.dumps({'partition':key,'status':record.get('status'),'rows':record.get('qa',{}).get('rows')}),flush=True)
                    if record.get('status') == 'not_published_or_unavailable':
                        pass
                    elif not is_verified(record):
                        raise RuntimeError(f'QA or remote verification failed: {key}')
                    else:
                        pending.append(record)
                    # Commit before pruning; keep large partitions well within budget.
                    pending_bytes=sum(r[k]['bytes'] for r in pending for k in ('raw','normalized'))
                    if report['processed_this_run']==1 or report['processed_this_run'] % 25 == 0 or pending_bytes>250_000_000:
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
