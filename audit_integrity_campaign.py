"""Independent bounded restore campaign; owns evidence, never acquisition ledgers."""
from datetime import datetime,timezone
import argparse
import json
import os
from pathlib import Path
import subprocess
import time
import zipfile
import requests
import pyarrow.parquet as pq
from quantlab_core.integrity_audit import audit_ledgers,sample_plan
from quantlab_core.io import Budget,atomic_json,sha256
from quantlab_core.remote import GitHubRemote
from remote_live import commit_checkpoint

BRANCHES=dict(main='main',expansion='codex/c17-archive-expansion',derived='codex/c18-derivatives')


def at(sha,path):return subprocess.check_output(['git','show',sha+':'+path],text=True)


def snapshot():
    subprocess.run(['git','fetch','origin'],check=True)
    heads={k:subprocess.check_output(['git','rev-parse','origin/'+v],text=True).strip() for k,v in BRANCHES.items()}
    ledgers=dict(main=[json.loads(x) for x in at(heads['main'],'manifest.jsonl').splitlines()],
                 expansion=list(json.loads(at(heads['expansion'],'catalog/extended_manifest.json')).values()),
                 derived=list(json.loads(at(heads['derived'],'catalog/derivative_manifest.json')).values()))
    inventory=json.loads(at(heads['main'],'catalog/source_inventory.json'))
    return heads,ledgers,inventory


def inspect_file(path,item):
    if sha256(path)!=item['sha256'] or path.stat().st_size!=item['bytes']:raise ValueError('Restored content differs from source receipt')
    if item['object_kind'] in ('raw','verification_bars'):
        # Read every compressed member to EOF: CRC checked, no extraction or unbounded memory.
        with zipfile.ZipFile(path) as z:
            if not z.infolist():raise ValueError('Empty original archive')
            members=[]
            for member in z.infolist():
                if member.is_dir():continue
                if not member.filename.endswith('.csv'):raise ValueError('Unexpected original archive member')
                count=0
                with z.open(member) as stream:
                    while block:=stream.read(1024*1024):count+=len(block)
                if count!=member.file_size:raise ValueError('Original member size differs')
                members.append(dict(name=member.filename,bytes=count,crc32=f'{member.CRC:08x}'))
        return dict(format='zip',members=members,crc_check='PASS')
    parquet=pq.ParquetFile(path);schema=parquet.schema_arrow
    if parquet.metadata.num_rows!=item['expected_rows']:raise ValueError('Restored Parquet row count differs')
    if item.get('source_identity') and (schema.metadata or {}).get(b'source_identity')!=item['source_identity'].encode():
        raise ValueError('Restored derivative source identity differs')
    time_name=next((k for k in ('event_time_ms','event_time_us') if k in schema.names),None)
    if time_name is None:raise ValueError('Scientific Parquet missing explicit event time')
    unit='ms' if time_name.endswith('_ms') else 'us'
    availability_name='available_at_'+unit
    columns=[time_name]+([availability_name] if availability_name in schema.names else [])
    count=0;previous=None;first=None;last=None;unknown=0;boundary_violations=0
    for batch in parquet.iter_batches(batch_size=65536,columns=columns):
        data=batch.to_pydict();count+=batch.num_rows
        for index,timestamp in enumerate(data[time_name]):
            if type(timestamp) is not int:raise ValueError('Missing/noninteger event timestamp')
            if previous is not None and timestamp<previous:raise ValueError('Restored event order regresses')
            if first is None:first=timestamp
            previous=last=timestamp
            if availability_name in data:
                available=data[availability_name][index]
                if available is None:unknown+=1
                elif available<timestamp:boundary_violations+=1
    if count!=item['expected_rows']:raise ValueError('Parquet full timestamp scan count differs')
    if boundary_violations:raise ValueError('Availability precedes observation')
    return dict(format='parquet',rows=count,first_event=first,last_event=last,event_unit=unit,
                unknown_availability_rows=unknown if availability_name in columns else None,
                timestamp_order='NONDECREASING',availability_not_before_event='PASS' if availability_name in columns else 'NOT_ASSESSED',
                fields=[dict(name=f.name,type=str(f.type),nullable=f.nullable) for f in schema],
                arrow_metadata={k.decode():v.decode() for k,v in (schema.metadata or {}).items()},
                strict_causal_replay_certified=False)


def receipt_identity(item):return item['ledger']+'/'+item['partition_key']+'/'+item['object_kind']+'/'+item['sha256']


def document(audit,report):
    lines=['# Independent coverage and restoration audit','','Observed UTC: '+audit['observed_at']+'. Phase 1 and global C21 remain **NOT_ACCEPTED**.','',
           'Immutable source heads: '+', '.join(k+' `'+v+'`' for k,v in audit['evidence_commits'].items())+'.','',
           '| Source | Symbol | Admitted remote days / requested | Quarantined partitions | Missing date ranges |',
           '|---|---|---:|---:|---|']
    for r in audit['coverage']:
        gaps='; '.join(x['start']+'..'+x['end'] for x in r['missing_ranges'])
        lines.append(f"| {r['source_id']} | {r['symbol']} | {r['admitted_remote_days']}/{r['expected_days']} | {r['partition_states'].get('QUARANTINED',0)} | {gaps} |")
    lines+=['','Fresh restoration campaign state: **'+report['status']+'**. Planned source-bound samples: '+str(report['planned_objects'])+
            '; completed this immutable plan: '+str(report['completed_plan_objects'])+'; lifetime restored objects: '+str(report['lifetime_restored_objects'])+'.','',
            'First and last admitted partitions of each source/symbol/ledger are sampled. Every original ZIP member is read to EOF for CRC integrity; Parquet rows, schema lineage, event ordering and availability boundaries are scanned. Outputs are only pruned after an audit checkpoint is pushed. This is sampled restoration, not verification of every object or source completeness. Historical publication timing remains uncertified.','',audit['notice'],'',
            'Inventory sources without a compatible partition ledger are explicitly NOT_ASSESSED_BY_PARTITION_AUDIT; their original documentary/live evidence is not replaced. Schedule on this non-default audit branch is inactive until integration with the default branch at a safe writer boundary.']
    return '\n'.join(lines)+'\n'


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--minutes',type=float,default=45)
    parser.add_argument('--max-objects',type=int);parser.add_argument('--local',action='store_true');args=parser.parse_args()
    started=time.monotonic();cpu=time.process_time();heads,ledgers,inventory=snapshot()
    audit=audit_ledgers(ledgers,inventory);audit.update(observed_at=datetime.now(timezone.utc).isoformat(),evidence_commits=heads)
    audit_path=Path('reports/integrity/coverage.json');plan_path=Path('reports/integrity/restore_plan.json')
    receipt_path=Path('catalog/integrity_restore_receipts.json');report_path=Path('reports/integrity/execution.json');doc=Path('docs/INTEGRITY_COVERAGE_AUDIT.md')
    receipts=json.loads(receipt_path.read_text()) if receipt_path.exists() else {}
    plan=sample_plan(ledgers)
    for item in plan:item['source_ledger_sha']=heads[item['ledger']]
    atomic_json(audit_path,audit);atomic_json(plan_path,plan)
    report=dict(schema_version=1,status='RUNNING',started_at=datetime.now(timezone.utc).isoformat(),evidence_commits=heads,
                source_commit_sha=os.environ.get('CHECKPOINT_SOURCE_SHA',subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()),
                workflow_url='https://github.com/Slimsyhalo/Trade/actions/runs/'+os.environ.get('GITHUB_RUN_ID','local'),
                planned_objects=len(plan),planned_bytes=sum(x['bytes'] for x in plan),errors=[],phase_1_accepted=False,global_C21_accepted=False,
                audit_code_files_sha256={p:sha256(Path(p)) for p in ('audit_integrity_campaign.py','quantlab_core/integrity_audit.py')},
                strict_causal_replay_certified=False,scope='Immutable source ledgers; deterministic earliest/latest stratified samples only')
    remote=GitHubRemote('Slimsyhalo/Trade',session=requests.Session() if args.local else None,interval=4,attempts=5)
    def checkpoint():
        report.update(updated_at=datetime.now(timezone.utc).isoformat(),elapsed_seconds=round(time.monotonic()-started,3),process_cpu_seconds=round(time.process_time()-cpu,3),
                      completed_plan_objects=sum(receipt_identity(x) in receipts for x in plan),lifetime_restored_objects=len(receipts),
                      completed_plan_bytes=sum(x['bytes'] for x in plan if receipt_identity(x) in receipts),
                      github_read_retries=remote.read_retry_events,github_rate_events=remote.rate_events,effective_codex_work_seconds=None)
        atomic_json(receipt_path,receipts);atomic_json(report_path,report);doc.parent.mkdir(exist_ok=True);doc.write_text(document(audit,report))
        if not args.local:
            paths=[audit_path,plan_path,receipt_path,report_path,doc]
            test=Path('reports/integrity/hosted_tests.txt')
            if test.exists():paths.append(test)
            commit_checkpoint(paths,os.environ['INTEGRITY_LEDGER_BRANCH'],'C21 immutable coverage and actual independent restoration: '+report['status'])
    checkpoint();processed=0
    for item in plan:
        identity=receipt_identity(item)
        if identity in receipts:continue
        if time.monotonic()-started>=args.minutes*60 or (args.max_objects is not None and processed>=args.max_objects):
            report['status']='PAUSED_BOUNDED_RUN';checkpoint();return
        path=Path('data/integrity-restores')/(item['sha256']+('.zip' if item['object_kind'] in ('raw','verification_bars') else '.parquet'))
        try:
            if path.exists():raise ValueError('Retained restore requires explicit reconciliation; no overwrite')
            remote.restore(item['remote'],path,Budget(Path('data/integrity-restores'),2))
            inspection=inspect_file(path,item)
            receipts[identity]=dict(state='RESTORED_AND_TESTED',restored_at=datetime.now(timezone.utc).isoformat(),source=item,inspection=inspection,
                                    audit_code_sha=report['source_commit_sha'])
            processed+=1;report['last_restored']=identity;checkpoint()
            path.unlink() # only disposable audit copy; source remote objects unchanged
        except Exception as error:
            report.update(status='BLOCKED',error_type=type(error).__name__,error=str(error),affected_object=identity,
                          resume_condition='Resolve exact restoration/inspection failure; retained evidence and source ledgers are unchanged')
            checkpoint();raise
    report['status']='SAMPLED_RESTORATION_PLAN_COMPLETE';checkpoint()


if __name__=='__main__':main()
