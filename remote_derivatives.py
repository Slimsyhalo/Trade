"""Bounded recomputation of every currently ready daily source set.

Source main is an immutable read-only snapshot. Products own a distinct Git
ledger, full remote readbacks and sample restoration. No original reacquisition.
"""
from datetime import date,datetime,timedelta,timezone
import json
import os
from pathlib import Path
import subprocess
import time
import pyarrow.parquet as pq
from build_derivative_products import build,source_identity
from quantlab_core.io import Budget,atomic_json,sha256
from quantlab_core.pipeline import remote_verified
from quantlab_core.remote import GitHubRemote
from quantlab_core.sources import SYMBOLS
from remote_live import commit_checkpoint


def product_verified(row):
    receipt=row.get('remote') or {}
    return bool(receipt.get('verified_at')) and receipt.get('sha256')==row.get('sha256') and receipt.get('bytes')==row.get('bytes')


def main():
    branch=os.environ['DERIVATIVE_LEDGER_BRANCH']
    subprocess.run(['git','fetch','origin','main'],check=True)
    main_sha=subprocess.check_output(['git','rev-parse','origin/main'],text=True).strip()
    records={r['key']:r for r in map(json.loads,subprocess.check_output(['git','show',main_sha+':manifest.jsonl'],text=True).splitlines())}
    manifest=Path('catalog/derivative_manifest.json');report_path=Path('reports/derivative_execution.json')
    products=json.loads(manifest.read_text()) if manifest.exists() else {}
    started=time.monotonic();cpu=time.process_time()
    remote=GitHubRemote('Slimsyhalo/Trade',interval=8,attempts=5,
                       release_body='Research-only derived sampled basis and native-unit Open Interest changes. '
                       'Original Binance source and normalized hashes, transform version, units, assumptions and unknown availability in catalog/derivative_manifest.json. Not executable spread or certified causal replay.')
    report=dict(status='RUNNING',started_at=datetime.now(timezone.utc).isoformat(),source_main_sha=main_sha,
                source_commit_sha=os.environ['CHECKPOINT_SOURCE_SHA'],
                workflow_url='https://github.com/Slimsyhalo/Trade/actions/runs/'+os.environ['GITHUB_RUN_ID'],
                phase_1_accepted=False,C18_accepted=False,strict_causal_replay_certified=False,
                processed_source_sets=0,restorations=[],errors=[],
                scope='Every complete mark/index/metrics daily source set in immutable main snapshot; no original archive redownload')

    def checkpoint():
        report.update(updated_at=datetime.now(timezone.utc).isoformat(),elapsed_seconds=round(time.monotonic()-started,3),
                      process_cpu_seconds=round(time.process_time()-cpu,3),
                      github_read_retries=list(remote.read_retry_events),github_rate_events=list(remote.rate_events),
                      remote_verified_products=sum(product_verified(r) for r in products.values()))
        atomic_json(manifest,products);atomic_json(report_path,report)
        paths=[manifest,report_path]
        if Path('reports/derivative_hosted_tests.txt').exists():paths.append(Path('reports/derivative_hosted_tests.txt'))
        commit_checkpoint(paths,branch,'C18 derivative evidence: '+report['status'])

    checkpoint()
    try:
        days=sorted({r['day'] for r in records.values() if r['dataset']=='metrics' and remote_verified(r)})
        for day in days:
            for symbol in SYMBOLS:
                selected={kind:records.get(f'{symbol}/{kind}/{day}',{}) for kind in ('markPriceKlines','indexPriceKlines','metrics')}
                if not all(remote_verified(r) for r in selected.values()):continue
                yesterday=str(date.fromisoformat(day)-timedelta(days=1))
                previous=records.get(f'{symbol}/metrics/{yesterday}',{})
                if remote_verified(previous):selected['previous_metrics']=previous
                signature,_=source_identity(selected)
                keys={kind:f'{symbol}/{kind}/{day}/{signature}' for kind in ('basis_close_1m','oi_change_5m')}
                if all(product_verified(products.get(k,{})) for k in keys.values()):continue
                if time.monotonic()-started>190*60:
                    report['status']='PAUSED_RUNTIME_LIMIT';checkpoint();return
                source_paths={}
                for kind,record in selected.items():
                    path=Path('data/derivative-sources')/(kind+'-'+record['normalized']['sha256']+'.parquet')
                    if not path.exists():remote.restore(record['normalized']['remote'],path,Budget(Path('data'),2))
                    source_paths[kind]=path
                prefix=Path('data/derived/derivatives')/symbol/day/signature
                # Reconcile an interrupted local build only against its exact remote
                # receipts; never overwrite an unknown original product.
                outputs=build(source_paths,selected,prefix)
                repeated=build(source_paths,selected,prefix/'independent-rebuild')
                for kind,row in outputs.items():
                    if row['sha256']!=repeated[kind]['sha256']:raise ValueError('Independent deterministic rebuild mismatch')
                    row['remote']=remote.put(row['path'],'derived-'+symbol+'-'+kind+'-'+day[:7])
                    row.update(key=keys[kind],symbol=symbol,day=day,state='REMOTE_VERIFIED',
                               quality_state='VALIDATED',storage_state='REMOTE_VERIFIED',
                               source_main_sha=main_sha,deterministic_rebuild='PASS',
                               previous_metrics_available='previous_metrics' in selected)
                    products[row['key']]=row
                    if not any(r['kind']==kind for r in report['restorations']):
                        target=Path('data/restored/derivatives')/(kind+'-'+row['sha256']+'.parquet')
                        remote.restore(row['remote'],target,Budget(Path('data'),2))
                        schema=pq.read_schema(target)
                        if sha256(target)!=row['sha256'] or pq.read_metadata(target).num_rows!=row['rows'] or schema.metadata.get(b'source_identity')!=signature.encode():
                            raise ValueError('Restored derived rows/schema/lineage differ')
                        report['restorations'].append(dict(kind=kind,key=row['key'],state='RESTORED_AND_TESTED',rows=row['rows'],sha256=row['sha256']))
                        target.unlink()
                report.update(processed_source_sets=report['processed_source_sets']+1,last_source_set=symbol+'/'+day)
                checkpoint() # both products read back and their ledger durably pushed before prune
                for path in source_paths.values():path.unlink(missing_ok=True)
                for row in [*outputs.values(),*repeated.values()]:Path(row['path']).unlink(missing_ok=True)
        report['status']='CURRENT_SOURCE_SNAPSHOT_RECOMPUTED';checkpoint()
    except Exception as error:
        report.update(status='BLOCKED',error_type=type(error).__name__,error=str(error),
                      resume_condition='Resolve exact input/output integrity or immutable publication failure; retained local originals remain untouched')
        checkpoint();raise


if __name__=='__main__':main()
