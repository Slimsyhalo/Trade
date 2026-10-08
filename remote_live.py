"""Bounded hosted live observation with its own Git ledger and restore evidence.

No writes to main/historical manifests. Git checkpoints never prune raw segments.
Actions duration is finite; this executable cannot certify permanent capture.
"""
import asyncio
from collections import Counter
from datetime import datetime, timezone
import gzip
import json
import os
from pathlib import Path
import subprocess
import time

import yaml
from live_collector.collector import run
from live_collector.spool import inspect_segment, ROUTES
from quantlab_core.io import atomic_json, Budget
from quantlab_core.remote import GitHubRemote


def summarize(root, destination):
    records=[]
    for route in ROUTES:
        source=root/(route+'-manifest.json')
        rows=json.loads(source.read_text()) if source.exists() else []
        atomic_json(destination/(route+'-manifest.json'),rows)
        records.extend(rows)
    verified=[r for r in records if r.get('status')=='remote_verified']
    return dict(segments=len(records), segment_states=dict(Counter(r.get('status','unknown') for r in records)),
                remote_verified_segments=len(verified), raw_rows=sum(r.get('rows') or 0 for r in verified),
                remote_verified_bytes=sum(r['bytes'] for r in verified),
                earliest_receive_ns=min((r['first_receive_ns'] for r in records if r.get('first_receive_ns')), default=None),
                latest_receive_ns=max((r['last_receive_ns'] for r in records if r.get('last_receive_ns')), default=None))


def push_checkpoint(branch, parent_sha, commit_sha, attempts=5):
    """Retry the identical commit only while the remote retains the expected parent."""
    ref='refs/heads/'+branch
    for attempt in range(attempts):
        result=subprocess.run(['git','push','origin',commit_sha+':'+ref],capture_output=True,text=True)
        if result.returncode==0: return
        # Read back even after a failed transport: the write might have succeeded.
        probe=subprocess.run(['git','ls-remote','origin',ref],capture_output=True,text=True)
        if probe.returncode!=0:
            raise RuntimeError('Cannot verify checkpoint branch head; publication stopped safely')
        if probe.returncode==0:
            remote_sha=probe.stdout.split()[0] if probe.stdout.strip() else None
            if remote_sha==commit_sha: return
            if remote_sha!=parent_sha:
                raise RuntimeError('Checkpoint branch changed externally; publication stopped without overwrite')
        detail=result.stderr.lower()
        if any(x in detail for x in ('authentication failed','permission denied','write access','403','non-fast-forward','fetch first')):
            raise subprocess.CalledProcessError(result.returncode,result.args)
        if attempt+1==attempts:
            raise subprocess.CalledProcessError(result.returncode,result.args)
        time.sleep(min(5*(2**attempt),60))


def commit_checkpoint(paths, branch, message):
    if not branch.startswith('codex/') or branch in ('codex/data-foundation-next',):
        raise ValueError('Live ledger requires an isolated development branch')
    subprocess.run(['git','add','--',*map(str,paths)],check=True)
    changed=subprocess.run(['git','diff','--cached','--quiet']).returncode
    if changed:
        parent_sha=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
        subprocess.run(['git','commit','-m',message],check=True)
        commit_sha=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
        push_checkpoint(branch,parent_sha,commit_sha)
    return subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()


def inspect_events(path):
    kinds=Counter(); events=Counter(); symbols=Counter(); streams=Counter(); markers=[]
    with gzip.open(path,'rt') as source:
        for line in source:
            row=json.loads(line); kinds[row['kind']]+=1
            if row['kind']=='event':
                payload=row['payload']; data=payload.get('data',{})
                events[str(data.get('e','unknown'))]+=1
                symbols[str(data.get('s','unknown'))]+=1
                streams[str(payload.get('stream','unknown'))]+=1
            elif row['kind'] in ('disconnect','snapshot_unavailable','gap','duplicate','connection_start'):
                if len(markers)<100: markers.append(row)
    return dict(kinds=dict(kinds), event_types=dict(events), symbols=dict(symbols), streams=dict(streams), diagnostic_examples=markers)


def observed_streams(restorations, symbols):
    observed={s for r in restorations for s, count in r.get('streams',{}).items() if count>0}
    expected={symbol.lower()+'@'+topic for symbol in symbols
              for topic in ('depth@100ms','bookTicker','aggTrade','markPrice@1s')}
    return dict(required_streams=sorted(expected), missing_streams=sorted(expected-observed),
                status='PASS' if expected<=observed else 'PARTIAL')


async def main(seconds=600):
    branch=os.environ['LIVE_LEDGER_BRANCH']; run_id=os.environ['GITHUB_RUN_ID']
    source_sha=os.environ['CHECKPOINT_SOURCE_SHA']; cfg=yaml.safe_load(Path('config.yaml').read_text())
    cfg.update(live_segment_seconds=300, live_segment_bytes=32_000_000)
    root=Path('data/live')/run_id; destination=Path('catalog/live')/run_id
    report_path=Path('reports/live_execution')/(run_id+'.json')
    started=time.monotonic(); cpu=time.process_time()
    report=dict(schema_version=1, status='RUNNING', run_id=run_id, source_commit_sha=source_sha,
                workflow_url='https://github.com/'+cfg['repository']+'/actions/runs/'+run_id,
                started_at=datetime.now(timezone.utc).isoformat(), requested_capture_seconds=seconds,
                raw_format='gzip JSONL, original messages plus receive timestamps/diagnostics',
                capture_scope='Actual live dates only; outside historical request window stored separately',
                continuous_operation_certified=False, full_L2_book_certified=False,
                ledger_branch=branch, restorations=[], limitations=[
                    'Hosted job finite; no 24/7 operation or automatic next-run coverage guarantee',
                    'New run starts a new connection; downtime cannot be recovered by this collector',
                    'Depth and OI snapshot REST restrictions recorded, never circumvented',
                    'forceOrder feed may be sampled; not all historical liquidations',
                    'Clock calibration absent; receive timestamp is application receipt, not kernel/network latency',
                    'No local raw pruning; pending files require immutable-name reconciliation after failure'])
    remote=GitHubRemote(cfg['repository'], interval=15, attempts=2, release_body=
                       'Binance public market-data live observations; research only. '
                       'Attribution: Binance. Dataset terms and source provenance: '
                       'https://github.com/Slimsyhalo/Trade/blob/codex/c16-source-inventory/DATA_LICENSE.md . '
                       'Verify SHA-256, size, receipt and continuity against catalog/live. '
                       'No continuous coverage or full L2 book certification.')

    def checkpoint():
        report.update(updated_at=datetime.now(timezone.utc).isoformat(),
                      elapsed_seconds=round(time.monotonic()-started,3), process_cpu_seconds=round(time.process_time()-cpu,3),
                      github_rate_events=list(remote.rate_events), **summarize(root,destination))
        atomic_json(report_path,report)
        # The workflow is the sole writer to this branch during this bounded run.
        commit_checkpoint([destination,report_path],branch,'C20 live evidence: '+report['status']+' '+run_id)

    checkpoint()
    task=asyncio.create_task(run(cfg,seconds,remote,root=root,drain_seconds=600))
    try:
        while not task.done():
            done,_=await asyncio.wait([task],timeout=60)
            await asyncio.to_thread(checkpoint)
        report['capture_report']=await task
        # Restore one independently read-back segment from each available route.
        # Never use the original local segment as the restoration input.
        for route in ROUTES:
            ledger=destination/(route+'-manifest.json')
            records=json.loads(ledger.read_text())
            row=next((r for r in records if r.get('status')=='remote_verified'),None)
            if not row: continue
            target=Path('data/restored')/run_id/(route+'-'+row['sha256']+'.jsonl.gz')
            await asyncio.to_thread(remote.restore,row['remote'],target,Budget(Path('data'),2))
            inspection=inspect_segment(target)
            if inspection['rows']!=row['rows']: raise ValueError('Restored live row count differs')
            report['restorations'].append(dict(route=route,sha256=row['sha256'],bytes=row['bytes'],
                                              state='RESTORED_AND_TESTED', **inspection, **inspect_events(target)))
            # This is a verified disposable restoration, never original acquisition.
            target.unlink()
        report['observed_stream_coverage']=observed_streams(report['restorations'],cfg['symbols'])
        report.update(status='BOUNDED_CAPTURE_RESTORED' if report['observed_stream_coverage']['status']=='PASS' else 'PARTIAL_CAPTURE_RESTORED',
                      last_success_at=datetime.now(timezone.utc).isoformat())
    except Exception as error:
        report.update(status='BLOCKED',error_type=type(error).__name__,error=str(error))
        if not task.done(): task.cancel()
        await asyncio.gather(task,return_exceptions=True)
        raise
    finally:
        await asyncio.to_thread(checkpoint)


if __name__=='__main__': asyncio.run(main())
