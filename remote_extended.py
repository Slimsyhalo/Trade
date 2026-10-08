"""Publish archive expansion on an independent ledger, preserving quarantine.

Bounded batches resume verified records. Raw deletion follows only full readback
AND a successful durable branch checkpoint. Quarantined source files are
preserved remotely for research diagnosis, never counted as validated coverage.
"""
from datetime import date,datetime,timezone
import json
import os
from pathlib import Path
import time

import pyarrow.parquet as pq
from acquire_extended import acquire
from quantlab_core.io import atomic_json,Budget,HTTP
from quantlab_core.remote import GitHubRemote
from quantlab_core.sources import SYMBOLS,START,END,days
from remote_live import commit_checkpoint


MANIFEST=Path('catalog/extended_manifest.json')


class ExpansionRemote(GitHubRemote):
    """Reserve the last 200 repository API requests for the incumbent writer."""
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs);self.remaining=None;self.reset_at=None
    def request(self,*args,**kwargs):
        if self.remaining is not None and self.remaining<200 and self.reset_at and self.reset_at>time.time():
            delay=self.reset_at-time.time()+2
            print('Expansion yields API budget to incumbent writer',flush=True)
            self.wait(delay)
        response=super().request(*args,**kwargs)
        if response.headers.get('X-RateLimit-Remaining') is not None:
            self.remaining=int(response.headers['X-RateLimit-Remaining']);self.reset_at=float(response.headers.get('X-RateLimit-Reset',time.time()+60))
        return response


def remote_verified(record):
    kinds=('raw','normalized','verification_bars') if record.get('verification_bars') else ('raw','normalized')
    for kind in kinds:
        item=record.get(kind,{});r=item.get('remote') or {}
        if not r.get('verified_at') or r.get('sha256')!=item.get('sha256') or r.get('bytes')!=item.get('bytes'):return False
    return True


def jobs(pilot):
    if pilot:
        for symbol in SYMBOLS:
            for kind,day in [('um_bookDepth_summary','2024-10-07'),('um_bookDepth_summary','2026-09-07'),('um_bookDepth_summary','2026-10-07'),('spot_klines_1m','2024-10-07'),('spot_klines_1m','2025-01-01'),('spot_trades','2025-01-01')]:
                yield symbol,kind,date.fromisoformat(day)
            yield symbol,'um_individual_trades',START
    else:
        for day in days(START,END):
            for symbol in SYMBOLS:
                for kind in ('spot_klines_1m','um_bookDepth_summary','spot_trades','um_individual_trades'):
                    yield symbol,kind,day


def preserve_diagnostics(remote,branch):
    """Exact CHECKSUM-identified samples are preserved, not silently revised."""
    report=json.loads(Path('reports/individual_trade_diagnosis.json').read_text())
    manifest_path=Path('catalog/diagnostic_asset_receipts.json')
    receipts=json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    http=HTTP(interval=1);budget=Budget(Path('data'),2)
    for sample in report['samples']:
        for asset in ('raw','verification_bars'):
            original=sample[asset];key=sample['symbol']+'/'+sample['day']+'/'+asset
            if receipts.get(key,{}).get('state')=='REMOTE_VERIFIED':continue
            path=Path(original['path'])
            http.download(original['url'],path,budget,expected=original['sha256'])
            receipt=remote.put(path,'diagnostic-'+sample['symbol']+'-'+sample['day'][:7])
            receipts[key]=dict(state='REMOTE_VERIFIED',source=original,remote=receipt,
                               quality_scope='Official market tape diagnosis; original quarantine decisions retained')
            atomic_json(manifest_path,receipts)
            commit_checkpoint([manifest_path],branch,'C17 preserve exact official diagnostic sources')
            path.unlink() # full readback and durable ledger already succeeded


def main(pilot=False):
    branch=os.environ['EXPANSION_LEDGER_BRANCH'];source_sha=os.environ['CHECKPOINT_SOURCE_SHA']
    started=time.monotonic();cpu=time.process_time();limit=45*60 if pilot else 230*60
    remote=ExpansionRemote('Slimsyhalo/Trade',interval=8,attempts=5,
                       release_body='Binance public archives, attribution Binance; research only under dataset terms in DATA_LICENSE.md. Quarantined assets are not validated coverage. Full hash receipts in catalog/extended_manifest.json.')
    report=dict(status='RUNNING',source_commit_sha=source_sha,started_at=datetime.now(timezone.utc).isoformat(),
                branch=branch,workflow_url='https://github.com/Slimsyhalo/Trade/actions/runs/'+os.environ['GITHUB_RUN_ID'],
                scope='pilot' if pilot else 'authorized two-year selected archives',processed=0,restorations=[],errors=[],
                complete_requested_window_certified=False,phase_1_accepted=False)
    report_path=Path('reports/extended_execution.json')

    def checkpoint():
        records=json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}
        verified=[r for r in records.values() if remote_verified(r)]
        approved=[r for r in verified if r.get('state')=='VALIDATED']
        report.update(updated_at=datetime.now(timezone.utc).isoformat(),elapsed_seconds=round(time.monotonic()-started,3),
                      process_cpu_seconds=round(time.process_time()-cpu,3),github_rate_events=list(remote.rate_events),
                      github_read_retries=list(remote.read_retry_events) if hasattr(remote,'read_retry_events') else None,
                      remote_verified_partitions=len(verified),validated_remote_partitions=len(approved),
                      quarantined_remote_partitions=len(verified)-len(approved),
                      validated_rows=sum(r['qa']['rows'] for r in approved),preserved_rows=sum(r['qa']['rows'] for r in verified),
                      stored_bytes=sum(r[k]['bytes'] for r in verified for k in ('raw','normalized')))
        atomic_json(report_path,report)
        if not MANIFEST.exists():atomic_json(MANIFEST,{})
        commit_checkpoint([MANIFEST,report_path],branch,'C17 archive evidence: '+report['status'])

    checkpoint()
    try:
        if pilot:preserve_diagnostics(remote,branch)
        for symbol,kind,day in jobs(pilot):
            if time.monotonic()-started>=limit:
                report['status']='PAUSED_RUNTIME_LIMIT';break
            key=f'{symbol}/{kind}/{day}'
            records=json.loads(MANIFEST.read_text());old=records.get(key,{})
            if remote_verified(old):continue
            try:
                row=acquire(kind,symbol,day,manifest=MANIFEST,materialize=True,remote=remote)
            except Exception as error:
                # Corruption/auth/budget failures stop this writer. Source absence
                # is recorded and scanning other partitions may continue.
                import requests
                if isinstance(error,requests.HTTPError) and error.response is not None and error.response.status_code==404:
                    report['errors'].append(dict(key=key,cause='Official archive 404',state='UNAVAILABLE',observed_at=datetime.now(timezone.utc).isoformat()))
                    checkpoint();continue
                raise
            for asset in ('raw','normalized'):
                row[asset]['remote']=remote.put(row[asset]['path'],'extended-'+symbol+'-'+kind+'-'+str(day)[:7])
            if row.get('verification_bars'):
                row['verification_bars']['remote']=remote.put(row['verification_bars']['path'],'extended-'+symbol+'-verification-'+str(day)[:7])
            row['storage_state']='REMOTE_VERIFIED';row['quality_state']=row['state']
            records=json.loads(MANIFEST.read_text());records[key]=row;atomic_json(MANIFEST,records)
            if not any(r['kind']==kind for r in report['restorations']):
                target=Path('data/restored/extended')/(symbol+'-'+kind+'-'+str(day)+'.parquet')
                remote.restore(row['normalized']['remote'],target,Budget(Path('data'),2))
                if pq.read_metadata(target).num_rows!=row['qa']['rows']:raise ValueError('Independent archive restoration row mismatch')
                report['restorations'].append(dict(key=key,kind=kind,state='RESTORED_AND_TESTED',quality_state=row['state'],rows=row['qa']['rows'],sha256=row['normalized']['sha256']))
                target.unlink()
            report.update(processed=report['processed']+1,last_partition=key)
            checkpoint() # mutation/readback/ledger all durable before original prune
            for asset in ('raw','normalized'):Path(row[asset]['path']).unlink()
            if row.get('verification_bars'):Path(row['verification_bars']['path']).unlink()
        else:report['status']='SCOPED_SCAN_FINISHED'
        checkpoint()
    except Exception as error:
        report.update(status='BLOCKED',error_type=type(error).__name__,error=str(error),resume_condition='Resolve cause; restore/reconcile hash-named records before restart')
        checkpoint();raise


if __name__=='__main__':main(pilot=os.environ.get('EXPANSION_PILOT','true')=='true')
