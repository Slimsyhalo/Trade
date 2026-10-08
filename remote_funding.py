"""Acquire permitted complete funding months and prove remote restoration."""
import json
import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
import yaml
import pyarrow.parquet as pq
from build_audit import build_audit
from quantlab_core.io import atomic_json
from quantlab_core.pipeline import Pipeline, remote_verified
from quantlab_core.remote import GitHubRemote
from quantlab_core.sources import partition_dates


def main():
    root=Path(__file__).resolve().parent
    cfg=yaml.safe_load((root/'config.yaml').read_text())
    pipe=Pipeline(root,cfg); remote=GitHubRemote(cfg['repository'],interval=cfg.get('github_request_interval_seconds',4))
    started=time.monotonic(); cpu_started=time.process_time(); pending=[]
    report={'status':'RUNNING','started_at':datetime.now(timezone.utc).isoformat(),
            'source_checkpoint_sha':os.environ.get('CHECKPOINT_SOURCE_SHA'),
            'processed_partitions':0,'verified_funding_partitions':0,'restores':[],
            'boundary_days_missing':{'2024-10':'2024-10-07 through 2024-10-31','2026-10':'2026-10-01 through 2026-10-07'},
            'notice':'Only complete monthly sources inside authorized bounds. Unknown publication times excluded from strict replay.'}

    def checkpoint():
        report['updated_at']=datetime.now(timezone.utc).isoformat()
        report['elapsed_seconds']=round(time.monotonic()-started,3)
        report['process_cpu_seconds']=round(time.process_time()-cpu_started,3)
        report['github_rate_events']=remote.rate_events
        report['verified_funding_partitions']=sum(remote_verified(r) for r in pipe.records.values() if r['dataset']=='fundingRate')
        atomic_json(root/'reports/funding_execution.json',report)
        build_audit(root)
        subprocess.run(['git','add','-u'],check=True)
        subprocess.run(['git','add','reports/funding_execution.json','reports/validation.json'],check=True)
        if subprocess.run(['git','diff','--cached','--quiet']).returncode:
            subprocess.run(['git','commit','-m','C11 funding checkpoint: verified archives, coverage and restore evidence'],check=True)
            subprocess.run(['git','push','origin','HEAD:main'],check=True)
        for r in pending:
            for kind in ('raw','normalized'): (root/r[kind]['path']).unlink(missing_ok=True)
        pending.clear()

    try:
        checkpoint()
        for symbol in cfg['symbols']:
            for month in partition_dates('fundingRate',cfg['start_date'],cfg['end_date']):
                key=f'{symbol}/fundingRate/{month}'
                if remote_verified(pipe.records.get(key,{})): continue
                r=pipe.sync_one(symbol,'fundingRate',month,remote,False)
                report['processed_partitions']+=1; report['last_partition']=key
                print(json.dumps({'key':key,'status':r.get('status'),'rows':r.get('qa',{}).get('rows')}),flush=True)
                if r.get('status')=='not_published_or_unavailable': continue
                if not remote_verified(r): raise RuntimeError('Funding QA/readback failed: '+key)
                pending.append(r)
                if not any(x['symbol']==symbol for x in report['restores']):
                    target=root/'data/restored'/(symbol+'-funding.parquet')
                    remote.restore(r['normalized']['remote'],target,pipe.budget)
                    rows=pq.read_metadata(target).num_rows
                    if rows!=r['qa']['rows']: raise ValueError('Funding restore row count mismatch')
                    report['restores'].append({'symbol':symbol,'key':key,'status':'PASS','rows':rows,'sha256':r['normalized']['sha256']})
                    target.unlink()
                if report['processed_partitions']==1 or report['processed_partitions']%5==0: checkpoint()
        report['status']='PERMITTED_MONTH_SCAN_FINISHED'
        checkpoint()
    except Exception as exc:
        report['status']='BLOCKED'; report['error']=str(exc)
        checkpoint()
        raise


if __name__=='__main__': main()
