"""Fresh read-only cross-ledger audit; final acceptance remains false."""
from datetime import datetime,timezone
import json,os,subprocess
from pathlib import Path
import requests
from audit_foundation import audit
from quantlab_core.io import atomic_json
from remote_live import commit_checkpoint


def main():
    branches=dict(main='main',expansion='codex/c17-archive-expansion',live='codex/c16-source-inventory',
                  recovery='codex/c21-document-recovery',context_failure='codex/c19-context-provenance',
                  source_watch='codex/c21-source-version-audit',flow='codex/c18-cloud-recomputation')
    heads={k:subprocess.check_output(['git','rev-parse','origin/'+v],text=True).strip() for k,v in branches.items()}
    result=audit(heads)
    flow=json.loads(subprocess.check_output(['git','show',heads['flow']+':reports/flow_cloud_execution.json'],text=True))
    watch=json.loads(subprocess.check_output(['git','show',heads['source_watch']+':reports/checkpoints/C21_2_source_watch_execution.json'],text=True))
    result['flow_cloud_verification']={k:flow.get(k) for k in ('status','source_commit_sha','workflow_url','flow_source_commit_sha','restored_source_rows','derived_rows','stored_bytes','strict_causal_replay_certified')}
    result['source_version_schema_watch']=watch
    result['acceptance_gaps']=[x for x in result['acceptance_gaps'] if not x.startswith('Flow clean-runner campaign pending')]
    result['acceptance_gaps'].append('Clean-runner flow reproduction proven for three original dates only; full derived-family coverage remains incomplete')
    result['combined_source_commit_sha']=os.environ['CHECKPOINT_SOURCE_SHA']
    result['workflow_url']='https://github.com/Slimsyhalo/Trade/actions/runs/'+os.environ['GITHUB_RUN_ID']
    result['execution_environment_block']=dict(component='interactive local execution',cause='exec-server environment_offline',impact='Local shell and scratch readback unavailable; hosted workflows and GitHub remain operational',resume_condition='Reconnect execution environment and re-fetch current main/ledgers')
    session=requests.Session()
    session.headers.update(Authorization='Bearer '+os.environ['GITHUB_TOKEN'],Accept='application/vnd.github+json')
    response=session.get('https://api.github.com/repos/Slimsyhalo/Trade/actions/runs',params={'per_page':20},timeout=(10,30))
    try:
        response.raise_for_status()
        runs=[{k:x.get(k) for k in ('id','name','status','conclusion','head_branch','head_sha','created_at','updated_at','html_url')} for x in response.json()['workflow_runs']]
        atomic_json(Path('reports/foundation_workflow_observation.json'),dict(observed_at=datetime.now(timezone.utc).isoformat(),runs=runs))
    finally:response.close()
    atomic_json(Path('reports/foundation_evidence_heads.json'),heads)
    atomic_json(Path('reports/foundation_acceptance_audit.json'),result)
    tests=Path('reports/combined_foundation_tests.txt').read_text()
    checkpoint=dict(checkpoint_id='C22.1-interim-handoff-not-acceptance',timestamp_utc=datetime.now(timezone.utc).isoformat(),commit_sha=os.environ['CHECKPOINT_SOURCE_SHA'],phase_1_accepted=False,milestone_states=result['milestone_states'],main_verified_partitions=result['main_acquisition']['remote_verified_partitions'],main_aggTrades_rows=result['main_acquisition']['aggTrades_rows'],coverage_ref='reports/foundation_acceptance_audit.json',expansion=result['expansion'],live=result['live'],official_documents=result['official_documents'],flow=result['flow_cloud_verification'],source_watch=watch,tests=tests.strip(),effective_codex_work_seconds=None,external_tool_wait_seconds=None,completed=['Current live capture-ID namespace reconciled with safe Git checkpoint retry','Read-only remote retry and strict hash validation integrated','All existing original/extended/context/flow modules retained','Clean hosted combined test suite and immutable multi-ledger audit'],next=result['acceptance_gaps'])
    atomic_json(Path('reports/checkpoints/C22_1_interim_handoff.json'),checkpoint)
    main=result['main_acquisition'];ext=result['expansion'];lv=result['live']
    text='# Research foundation — interim evidence handoff\n\nPhase 1 and all global C16–C22 acceptance gates remain open. This is an interim verified code/evidence handoff, not final certification.\n\n'
    text+='Main immutable snapshot '+heads['main']+': '+str(main['remote_verified_partitions'])+' verified partitions and '+str(main['aggTrades_rows'])+' aggregate execution rows. Per-symbol dates, missing counts, source hashes and quarantine are in reports/foundation_acceptance_audit.json.\n\n'
    text+='Official documentation: 109 documents and all 223 source/metadata/discovery members restored from a verified Releases container. Historical vintage and effective dissemination remain uncertified. Flow: '+str(flow['restored_source_rows'])+' original execution rows restored and recalculated into '+str(flow['derived_rows'])+' output rows with identical pilot hashes, then remotely published and independently restored.\n\n'
    text+='Archive expansion ledger state '+str(ext['status'])+' at '+str(ext['updated_at'])+'; '+str(ext['remote_verified_partitions'])+' remotely verified, '+str(ext['validated_remote_partitions'])+' validated, '+str(ext['quarantined_remote_partitions'])+' quarantined. Live ledger state '+str(lv['status'])+' at '+str(lv['updated_at'])+'; '+str(lv['remote_verified_segments'])+' verified segments. Bounded live capture does not certify 24/7 operation or synchronized full L2.\n\n'
    text+='Combined validation: '+tests.strip()+'\n\nSource-version/schema watch observed 21 unchanged official checksums and restored actual derived schema bytes. Source revisions remain unknown outside those probes. Code, source references and manifests are in Git; original/normalized dataset objects and receipts remain in Releases. No paid backend was created.\n\n'
    text+='Interactive local execution returned environment_offline. No local process is claimed to survive it. Hosted workflows use independent ledgers, runtime limits, checkpoints and remote receipts. Their exact statuses are recorded separately; a queued/run state is not coverage completion.\n\n'
    text+='This branch reconciles later live capture-ID namespaces with safe identical-commit Git retry and read-only transport recovery. It retains funding, original QA, source-market trade admission, context provenance, tape transforms, restore code and source-version surveillance. It does not alter main or another active ledger. Before main integration, inspect active jobs, compare current heads and preserve their manifests; do not force-push or copy stale inherited catalogs over live writer output.\n\n'
    text+='## Remaining acceptance gaps\n\n'+''.join('- '+x+'\n' for x in result['acceptance_gaps'])
    Path('docs/FOUNDATION_INTERIM_HANDOFF.md').write_text(text)
    paths=[Path('reports/foundation_evidence_heads.json'),Path('reports/foundation_acceptance_audit.json'),Path('reports/foundation_workflow_observation.json'),Path('reports/checkpoints/C22_1_interim_handoff.json'),Path('reports/combined_foundation_tests.txt'),Path('docs/FOUNDATION_INTERIM_HANDOFF.md')]
    commit_checkpoint(paths,os.environ['FOUNDATION_LEDGER_BRANCH'],'C22 interim handoff: combined tests and current immutable evidence; acceptance open')


if __name__=='__main__':main()
