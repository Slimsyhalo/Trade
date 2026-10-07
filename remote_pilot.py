"""Bounded reconstruction/upload of the existing passing pilot on GitHub Actions."""
import json
import subprocess
from datetime import date, datetime, timezone
from pathlib import Path
import yaml
import pyarrow.parquet as pq
from quantlab_core.pipeline import Pipeline
from quantlab_core.remote import GitHubRemote
from quantlab_core.io import atomic_json


def publish_metadata():
    subprocess.run(['git', 'add', 'manifest.jsonl', 'data_catalog.json', 'reports/remote_execution.json'], check=True)
    if subprocess.run(['git', 'diff', '--cached', '--quiet']).returncode:
        subprocess.run(['git', 'commit', '-m', 'Record verified pilot release assets and restore evidence'], check=True)
        subprocess.run(['git', 'push', 'origin', 'HEAD:main'], check=True)


def main():
    root = Path(__file__).resolve().parent
    pipeline = Pipeline(root, yaml.safe_load((root/'config.yaml').read_text()))
    remote = GitHubRemote(pipeline.config['repository'])
    passing = [r for r in pipeline.records.values() if r.get('qa', {}).get('status') == 'PASS']
    if len(passing) != 18 or any(r['day'] != '2024-10-07' for r in passing):
        raise RuntimeError('This bounded job only handles the original 18-partition pilot')
    report = {'status': 'RUNNING', 'verified_partitions': [], 'restore': None,
              'started_at': datetime.now(timezone.utc).isoformat()}
    for previous in passing:
        record = pipeline.sync_one(previous['symbol'], previous['dataset'], date.fromisoformat(previous['day']), remote, False)
        if record.get('qa', {}).get('status') != 'PASS':
            raise RuntimeError('Dataset QA failed; retain local files')
        if report['restore'] is None:
            target = root/'data/restored/pilot.parquet'
            remote.restore(record['normalized']['remote'], target, pipeline.budget)
            rows = pq.read_metadata(target).num_rows
            if rows != record['qa']['rows']:
                raise ValueError('Restored row count differs from manifest')
            report['restore'] = {'status': 'PASS', 'key': record['key'], 'rows': rows,
                                 'sha256': record['normalized']['sha256']}
            target.unlink()
        report['verified_partitions'].append(record['key'])
        pipeline.catalog()
        atomic_json(root/'reports/remote_execution.json', report)
        publish_metadata()
        # Both full readbacks passed and manifest is now durable in remote Git.
        for kind in ('raw', 'normalized'):
            (root/record[kind]['path']).unlink(missing_ok=True)
    report['status'] = 'PASS'
    report['finished_at'] = datetime.now(timezone.utc).isoformat()
    atomic_json(root/'reports/remote_execution.json', report)
    publish_metadata()


if __name__ == '__main__':
    main()
