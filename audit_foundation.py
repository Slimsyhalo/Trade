"""Immutable multi-ledger evidence audit. Never rewrites acquisition manifests."""
from collections import Counter
from datetime import datetime,timezone
import json
from pathlib import Path
import subprocess
from source_foundation import manifest_snapshot
from quantlab_core.io import atomic_json


def read_at(sha,path):
    return json.loads(subprocess.check_output(['git','show',sha+':'+path],text=True))


def audit(heads):
    main,_=manifest_snapshot(Path('.'),heads['main'])
    ext=read_at(heads['expansion'],'reports/extended_execution.json')
    live=read_at(heads['live'],'reports/live_execution/37795816483-1.json')
    recovery=read_at(heads['recovery'],'reports/document_recovery.json')
    inventory=read_at(heads['recovery'],'catalog/source_inventory.json')
    return dict(schema_version=1,observed_at=datetime.now(timezone.utc).isoformat(),evidence_commits=heads,
                phase_1_accepted=False,main_acquisition=main,
                inventory=dict(datasets=len(inventory['datasets']),families=dict(Counter(x['family'] for x in inventory['datasets'])),
                               classifications=dict(Counter(x['classification'] for x in inventory['datasets'])),C16_accepted=False),
                expansion={k:ext.get(k) for k in ('status','updated_at','workflow_url','remote_verified_partitions','validated_remote_partitions','quarantined_remote_partitions','validated_rows','preserved_rows','stored_bytes','errors')},
                live={k:live.get(k) for k in ('status','updated_at','workflow_url','capture_id','requested_capture_seconds','remote_verified_segments','raw_rows','remote_verified_bytes','continuous_operation_certified','full_L2_book_certified')},
                official_documents={k:recovery.get(k) for k in ('status','timestamp_utc','workflow_url','container','verified_members','official_documents','historical_vintage_certified','historical_effective_availability_certified')},
                acceptance_gaps=[
                    '731 dates per selected historical source not yet acquired; campaigns remain active',
                    'All 70 inventoried sources require final capability/cost/schema and acquisition-decision reconciliation',
                    'Historical source-market trade admission established; skipped global ID cause remains undetermined',
                    'Depth summary partial/frozen-band quarantine remains; not a full order book',
                    'REST451 blocks synchronized live L2 snapshots and retention-limited OI acquisition in observed environments',
                    'Finite Actions captures and uncalibrated receive clock do not establish permanent live service',
                    'Official archived documents restored, but historical effective availability and unchanged historical vintage not established',
                    'News, announcements, regulatory/incident timelines, historical contract filters and fees still incomplete',
                    'Flow clean-runner campaign pending; other derived families not yet implemented',
                    'Global independent restoration, fault recovery and final data dictionary incomplete',
                    'Complete dataset size remains unknown; sampled known components already exceed local work budget',
                    'Earlier foreground active time versus external waits was not fully instrumented'],
                milestone_states={x:'NOT_ACCEPTED' for x in ('C16','C17','C18','C19','C20','C21','C22')},
                reproducibility='git show each immutable evidence commit/path; main counters computed by source_foundation.manifest_snapshot; no live branch inferred complete')


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--heads',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();atomic_json(args.output,audit(json.loads(args.heads.read_text())))
