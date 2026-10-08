"""Independent clean-runner recalculation of admitted execution-tape features."""
from datetime import datetime, timezone
import os
from pathlib import Path
import time
from quantlab_core.io import atomic_json
from remote_context import flow_from_remote
from remote_extended import ExpansionRemote
from remote_live import commit_checkpoint


def main():
    branch=os.environ['FLOW_LEDGER_BRANCH']; report_path=Path('reports/flow_cloud_execution.json')
    started=time.monotonic(); cpu=time.process_time()
    report=dict(status='RUNNING',source_commit_sha=os.environ['CHECKPOINT_SOURCE_SHA'],
                workflow_url='https://github.com/Slimsyhalo/Trade/actions/runs/'+os.environ['GITHUB_RUN_ID'],
                started_at=datetime.now(timezone.utc).isoformat(),ledger_branch=branch,
                phase_1_accepted=False,global_C18_accepted=False,strict_causal_replay_certified=False,
                scope='Three admitted official individual-trade partitions, 2024-10-07; no source reacquisition',
                limitations=['A three-partition reproducibility test does not certify two-year feature coverage',
                             'Full L2 and order-event metrics remain unavailable without synchronized snapshots',
                             'Historical effective input availability remains unknown'])
    remote=ExpansionRemote('Slimsyhalo/Trade',interval=15,attempts=2,release_body=
                          'Derived scientific execution-tape measurements. Original Binance source hashes, exact-minute admission certificates, transform version and restore evidence in catalog/flow_manifest.json. Research dataset terms apply; no trading strategy or profitability claim.')
    def checkpoint():
        report.update(updated_at=datetime.now(timezone.utc).isoformat(),
                      elapsed_seconds=round(time.monotonic()-started,3),process_cpu_seconds=round(time.process_time()-cpu,3),
                      github_rate_events=list(remote.rate_events))
        atomic_json(report_path,report)
        paths=[report_path]
        if Path('catalog/flow_manifest.json').exists(): paths.append(Path('catalog/flow_manifest.json'))
        commit_checkpoint(paths,branch,'C18 clean-runner feature verification: '+report['status'])
    checkpoint()
    try:
        flow_from_remote(remote,branch,report)
        report['status']=report['flow_status']
        report['restored_source_rows']=sum(x['source_rows'] for x in report['flow_publications'])
        report['derived_rows']=sum(x['derived_rows'] for x in report['flow_publications'])
        report['stored_bytes']=sum(x['normalized']['bytes'] for x in report['flow_publications'])
    except Exception as error:
        report.update(status='BLOCKED',error_type=type(error).__name__,error=str(error),
                      resume_condition='Original admitted source, deterministic recomputation and remote integrity must all pass')
        raise
    finally: checkpoint()


if __name__=='__main__':main()
