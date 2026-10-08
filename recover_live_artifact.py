"""Recover a failed bounded capture without opening a new market connection.

Artifact input must match every segment in the immutable Git capture ledger.
Only pending segments are published; old receipts remain explicitly inherited.
Recovery uses a separate ledger and never rewrites the original failed evidence.
"""
import asyncio
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import time

from live_collector.spool import Sink, ROUTES, inspect_segment, publish_pending, receipt_matches
from quantlab_core.io import Budget, atomic_json
from quantlab_core.remote import GitHubRemote
from remote_live import commit_checkpoint, summarize, inspect_events

CAPTURE='37795816483-1'
SOURCE_RUN=37795816483
ARTIFACT_ID=11565318990


def validate_artifact(root, source_catalog):
    total=0
    for route in ROUTES:
        original=json.loads((source_catalog/(route+'-manifest.json')).read_text())
        supplied=json.loads((root/(route+'-manifest.json')).read_text())
        expected={r['path']:r for r in original}
        if len(expected)!=len(original) or len(supplied)!=len(original):
            raise ValueError('Artifact segment count differs from durable source ledger')
        seen=set()
        for row in supplied:
            name=row['path']
            if Path(name).name!=name or name in seen or name not in expected:
                raise ValueError('Unknown/duplicate/unsafe artifact segment')
            seen.add(name)
            for field in ('sha256','bytes','rows','first_receive_ns','last_receive_ns'):
                if row.get(field)!=expected[name].get(field):
                    raise ValueError('Artifact provenance differs from durable source ledger')
            # Restore receipt authority from Git, not from mutable artifact metadata.
            row['remote']=expected[name].get('remote')
            row['status']='remote_verified' if receipt_matches(row,row['remote']) else 'closed'
        atomic_json(root/(route+'-manifest.json'),supplied)
        total+=len(supplied)
    return total


async def main():
    branch=os.environ['RECOVERY_LEDGER_BRANCH']
    root=Path(os.environ.get('LIVE_ARTIFACT_ROOT','data/recovery-artifact'))/'data/live'/CAPTURE
    destination=Path('catalog/live_recovery')/CAPTURE
    report_path=Path('reports/live_recovery')/(CAPTURE+'.json')
    started=time.monotonic(); cpu=time.process_time()
    report=dict(schema_version=1,status='RUNNING',source_capture_id=CAPTURE,
                source_run_id=SOURCE_RUN,source_artifact_id=ARTIFACT_ID,
                original_capture_state='BLOCKED_PUBLICATION_BACKLOG_WITH_VALID_LOCAL_INTEGRITY',
                source_commit_sha=os.environ['CHECKPOINT_SOURCE_SHA'],
                workflow_url='https://github.com/Slimsyhalo/Trade/actions/runs/'+os.environ['GITHUB_RUN_ID'],
                started_at=datetime.now(timezone.utc).isoformat(),
                restorations=[],new_market_connections=0,continuous_operation_certified=False,
                full_L2_book_certified=False,phase_1_accepted=False)
    remote=GitHubRemote('Slimsyhalo/Trade',interval=4,attempts=5)

    def checkpoint():
        report.update(updated_at=datetime.now(timezone.utc).isoformat(),
                      elapsed_seconds=round(time.monotonic()-started,3),process_cpu_seconds=round(time.process_time()-cpu,3),
                      github_read_retries=list(remote.read_retry_events),github_rate_events=list(remote.rate_events),
                      **summarize(root,destination))
        atomic_json(report_path,report)
        commit_checkpoint([destination,report_path],branch,'C20 artifact recovery: '+report['status'])

    try:
        report['provenance_checked_segments']=validate_artifact(root,Path('catalog/live')/CAPTURE)
        sinks=[Sink(root,Budget(Path('data'),2),route) for route in ROUTES]
        if any(r['status'] in ('quarantined','missing_local') for s in sinks for r in s.records):
            raise ValueError('Artifact contains missing/corrupt source segments; preserve evidence')
        report['inherited_verified_segments']=sum(r['status']=='remote_verified' for s in sinks for r in s.records)
        report['pending_segments_before']=sum(len(s.pending()) for s in sinks)
        checkpoint()
        stopped=asyncio.Event();stopped.set()
        task=asyncio.create_task(publish_pending(sinks,remote,stopped,drain_seconds=3600))
        while not task.done():
            await asyncio.wait([task],timeout=60)
            await asyncio.to_thread(checkpoint)
        report['publication']=await task
        if report['publication']['status']!='COMPLETE':
            raise RuntimeError('Artifact publication remains incomplete; preserve local originals')
        for sink in sinks:
            row=next((r for r in sink.records if r['status']=='remote_verified'),None)
            if row is None:continue
            target=Path('data/restored/live-recovery')/(sink.route+'-'+row['sha256']+'.jsonl.gz')
            await asyncio.to_thread(remote.restore,row['remote'],target,Budget(Path('data'),2))
            inspection=inspect_segment(target)
            if inspection['rows']!=row['rows']:raise ValueError('Restored source row count mismatch')
            report['restorations'].append(dict(route=sink.route,state='RESTORED_AND_TESTED',
                                              sha256=row['sha256'],bytes=row['bytes'],**inspection,**inspect_events(target)))
            target.unlink()
        report['status']='ALL_CAPTURE_SEGMENTS_REMOTE_VERIFIED_WITH_SAMPLE_RESTORATION'
    except Exception as error:
        report.update(status='BLOCKED',error_type=type(error).__name__,error=str(error),
                      resume_condition='Resolve exact provenance/integrity/publication failure; originals retained')
        raise
    finally:
        await asyncio.to_thread(checkpoint)


if __name__=='__main__':asyncio.run(main())
