"""Observe current Git ledgers and workflows without writing any source ledger."""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import requests
from quantlab_core.io import atomic_json
from source_foundation import manifest_snapshot
from remote_live import commit_checkpoint


def at(sha,path):
    return json.loads(subprocess.check_output(['git','show',sha+':'+path],text=True))


def main():
    branches=dict(main='main',expansion='codex/c17-archive-expansion',
                  live='codex/live-observations',recovery='codex/live-artifact-recovery',
                  derivatives='codex/c18-derivatives',integrity='codex/c21-integrity-audit',
                  candidate_probe='codex/live-buffered-probe')
    subprocess.run(['git','fetch','origin'],check=True)
    heads={k:subprocess.check_output(['git','rev-parse','origin/'+v],text=True).strip() for k,v in branches.items()}
    primary,_=manifest_snapshot(Path('.'),heads['main'])
    expansion=at(heads['expansion'],'reports/extended_execution.json')
    paths=subprocess.check_output(['git','ls-tree','-r','--name-only',heads['live'],'--','reports/live_execution'],text=True).splitlines()
    captures=[at(heads['live'],p) for p in paths if p.endswith('.json')]
    capture=max(captures,key=lambda r:r.get('started_at',''),default={})
    recovery_path='reports/live_recovery/37795816483-1.json'
    exists=subprocess.run(['git','cat-file','-e',heads['recovery']+':'+recovery_path],capture_output=True).returncode==0
    recovery=at(heads['recovery'],recovery_path) if exists else dict(status='NOT_YET_RECORDED')
    def optional(sha,path):
        exists=subprocess.run(['git','cat-file','-e',sha+':'+path],capture_output=True).returncode==0
        return at(sha,path) if exists else dict(status='NOT_YET_RECORDED')
    derivatives=optional(heads['derivatives'],'reports/derivative_execution.json')
    integrity=optional(heads['integrity'],'reports/integrity/execution.json')
    probe_paths=subprocess.check_output(['git','ls-tree','-r','--name-only',heads['candidate_probe'],'--','reports/live_execution'],text=True).splitlines()
    probes=[at(heads['candidate_probe'],p) for p in probe_paths if p.endswith('.json')]
    probes=[p for p in probes if p.get('ledger_branch')=='codex/live-buffered-probe']
    candidate=max(probes,key=lambda r:r.get('started_at',''),default=dict(status='NOT_YET_RECORDED'))
    headers={'Authorization':'Bearer '+os.environ['GITHUB_TOKEN'],'Accept':'application/vnd.github+json'}
    with requests.get('https://api.github.com/repos/Slimsyhalo/Trade/actions/runs',
                      headers=headers,params={'per_page':30},timeout=(15,30)) as response:
        response.raise_for_status()
        runs=[{k:r.get(k) for k in ('id','name','status','conclusion','head_branch','head_sha','created_at','updated_at','html_url')}
              for r in response.json()['workflow_runs']]
    report=dict(schema_version=1,observed_at=datetime.now(timezone.utc).isoformat(),evidence_commits=heads,
                source_commit_sha=os.environ['CHECKPOINT_SOURCE_SHA'],phase_1_accepted=False,
                main_acquisition=primary,expansion=expansion,latest_bounded_capture=capture,
                original_capture_recovery=recovery,derivative_recomputation=derivatives,independent_integrity=integrity,
                candidate_buffered_probe=candidate,workflows=runs,
                notice='Inherited receipts are prior full readback evidence, not a fresh audit of every remote object. '
                       'Independent ledgers remain distinct; records/bytes are not naively summed across overlapping tapes. '
                       'Scheduled Actions may delay/drop runs and cannot guarantee 24/7 coverage.')
    destination=Path('reports/operations/current.json');atomic_json(destination,report)
    text='# Current research foundation operations\n\nObserved UTC: '+report['observed_at']+'. Phase 1 remains incomplete.\n\n'
    text+='| Component | Evidence head | State | Preserved / verified scope |\n|---|---|---|---|\n'
    text+='| Main archives | '+heads['main']+' | Immutable observation | '+str(primary['remote_verified_partitions'])+' remotely verified partitions; '+str(primary['aggTrades_rows'])+' aggTrades rows |\n'
    text+='| Expansion | '+heads['expansion']+' | '+str(expansion.get('status'))+' | '+str(expansion.get('remote_verified_partitions'))+' partitions; '+str(expansion.get('validated_remote_partitions'))+' validated |\n'
    text+='| Latest live capture | '+heads['live']+' | '+str(capture.get('status','NOT_YET_RECORDED'))+' | '+str(capture.get('remote_verified_segments',0))+' segments |\n'
    text+='| Original live recovery | '+heads['recovery']+' | '+str(recovery.get('status'))+' | '+str(recovery.get('remote_verified_segments',0))+' segments |\n'
    text+='| Derivative products | '+heads['derivatives']+' | '+str(derivatives.get('status'))+' | '+str(derivatives.get('remote_verified_products',0))+' products |\n'
    text+='| Independent restoration | '+heads['integrity']+' | '+str(integrity.get('status'))+' | '+str(integrity.get('completed_plan_objects',0))+'/'+str(integrity.get('planned_objects',0))+' sampled objects |\n'
    text+='| Candidate buffered live probe | '+heads['candidate_probe']+' | '+str(candidate.get('status'))+' | '+str(candidate.get('remote_verified_segments',0))+' separate probe segments; no rollout inferred |\n\n'
    text+='These are separate scopes. Bounded observations, partial historical coverage and sampled restoration do not certify final acceptance, historical full L2 or continuous live operation. Full counters, dates, errors and workflow URLs are in `reports/operations/current.json`.\n'
    doc=Path('docs/CURRENT_OPERATIONS.md');doc.write_text(text)
    commit_checkpoint([destination,doc],os.environ['OPS_LEDGER_BRANCH'],'Research foundation operational evidence')


if __name__=='__main__':main()
