"""Version-bound original-document publication and optional admitted tape replay."""
from datetime import datetime,timezone
import base64
import gzip
import hashlib
import json
import os
from pathlib import Path
import time

import pyarrow.parquet as pq
from acquire_context import discover_all,acquire_release
from build_flow import build
from quantlab_core.io import HTTP,Budget,atomic_json,sha256
from remote_extended import ExpansionRemote,remote_verified
from remote_live import commit_checkpoint


def materialize(record,http,remote):
    raw=Path(record['raw']['path']);normalized=Path(record['normalized']['path']);metadata=record['metadata'];budget=Budget(Path('data'),2)
    if not raw.exists():
        if record['raw'].get('remote'):remote.restore(record['raw']['remote'],raw,budget)
        else:
            response=http.get(metadata['source'])
            try:body=response.content
            finally:response.close()
            if hashlib.sha256(body).hexdigest()!=metadata['source_document_sha256']:
                raise ValueError('Official document changed; preserve prior source version and reconcile separately')
            from acquire_context import compressed_original
            compressed_original(body,raw,budget)
    if not normalized.exists():atomic_json(normalized,metadata)
    for name in ('raw','normalized'):
        item=record[name]
        if sha256(item['path'])!=item['sha256'] or Path(item['path']).stat().st_size!=item['bytes']:raise ValueError('Known context version/hash mismatch')


def flow_from_remote(remote,branch,report):
    """Read an immutable expansion commit; never write its manifest/releases."""
    response=remote.request('GET',remote.base+'/git/ref/heads/codex/c17-archive-expansion')
    source_commit=response.json()['object']['sha'];response.close()
    response=remote.request('GET',remote.base+'/contents/catalog/extended_manifest.json',params={'ref':source_commit})
    payload=response.json();response.close()
    records=json.loads(base64.b64decode(payload['content']))
    certificates=json.loads(Path('catalog/qa_revisions/individual_trades.json').read_text())['certificates']
    flow_manifest=Path('catalog/flow_manifest.json')
    report['flow_source_commit_sha']=source_commit
    report['flow_publications']=json.loads(flow_manifest.read_text()) if flow_manifest.exists() else []
    report['flow_missing_sources']=[]
    for cert in certificates:
        prior=next((r for r in report['flow_publications'] if r['symbol']==cert['symbol'] and r['day']==cert['day']),None)
        if prior and prior.get('storage_state')=='REMOTE_VERIFIED' and prior.get('restoration_state')=='RESTORED_AND_TESTED':continue
        key=cert['symbol']+'/um_individual_trades/'+cert['day'];source=records.get(key)
        if not source or source.get('state')!='VALIDATED' or not remote_verified(source):
            report['flow_missing_sources'].append(key);continue
        target=Path('data/flow_sources')/(cert['symbol']+'-'+source['normalized']['sha256']+'.parquet')
        if not target.exists():remote.restore(source['normalized']['remote'],target,Budget(Path('data'),2))
        adapted=dict(dataset='trades',symbol=source['symbol'],day=source['day'],raw=source['raw'],
                     normalized=dict(source['normalized'],path=str(target)))
        output=Path('data/derived/flow')/source['symbol']/(source['day']+'-tape-flow-1.parquet')
        result=build(adapted,cert,Path('.'),output)
        # Compare deterministic local pilot bytes; disagreement blocks publication.
        expected=next((r for r in json.loads(Path('reports/flow_derivation.json').read_text()) if r['symbol']==source['symbol']),None)
        if not expected or result['normalized']['sha256']!=expected['normalized']['sha256']:raise ValueError('Clean restored-source recomputation differs from pilot')
        result['normalized']['remote']=remote.put(output,'derived-flow-'+source['symbol']+'-'+source['day'][:7])
        result['storage_state']='REMOTE_VERIFIED'
        restore=Path('data/restored/flow')/(source['symbol']+'-'+result['normalized']['sha256']+'.parquet')
        remote.restore(result['normalized']['remote'],restore,Budget(Path('data'),2))
        if pq.read_metadata(restore).num_rows!=result['derived_rows']:raise ValueError('Derived restoration row mismatch')
        result['restoration_state']='RESTORED_AND_TESTED'
        report['flow_publications']=[r for r in report['flow_publications'] if (r['symbol'],r['day'])!=(cert['symbol'],cert['day'])]+[result]
        manifest=Path('catalog/flow_manifest.json');atomic_json(manifest,report['flow_publications'])
        commit_checkpoint([manifest],branch,'C18 derived flow: clean recomputation and restored publication')
        output.unlink();target.unlink();restore.unlink()
    report['flow_status']='REMOTE_RECOMPUTED_RESTORED' if len(report['flow_publications'])==3 else 'WAITING_FOR_INDEPENDENT_SOURCE_PUBLICATION'


def main():
    branch=os.environ['CONTEXT_LEDGER_BRANCH'];http=HTTP(interval=1)
    remote=ExpansionRemote('Slimsyhalo/Trade',interval=15,attempts=2,release_body=
                          'Official BLS/Federal Reserve release documents and research metadata; original source URLs, publication claims and SHA-256 in catalog/context_manifest.json. Historical availability/content vintage remains explicitly uncertified; no revised values substituted.')
    manifest=Path('catalog/context_manifest.json');records=json.loads(manifest.read_text()) if manifest.exists() else {}
    report_path=Path('reports/context_execution.json');started=time.monotonic();cpu=time.process_time()
    report=dict(status='RUNNING',source_commit_sha=os.environ['CHECKPOINT_SOURCE_SHA'],
                workflow_url='https://github.com/Slimsyhalo/Trade/actions/runs/'+os.environ['GITHUB_RUN_ID'],
                started_at=datetime.now(timezone.utc).isoformat(),errors=[],restorations=[],phase_1_accepted=False,
                historical_effective_availability_certified=False,historical_value_vintage_certified=False)
    candidates,discovery_errors=discover_all(http);report['errors'].extend(discovery_errors)
    report['candidate_count']=len(candidates)

    def checkpoint():
        verified=[r for r in records.values() if remote_verified(r)]
        report.update(updated_at=datetime.now(timezone.utc).isoformat(),elapsed_seconds=round(time.monotonic()-started,3),
                      process_cpu_seconds=round(time.process_time()-cpu,3),remote_verified_documents=len(verified),
                      remote_verified_bytes=sum(r[k]['bytes'] for r in verified for k in ('raw','normalized')),
                      github_rate_events=list(remote.rate_events))
        atomic_json(manifest,records);atomic_json(report_path,report)
        commit_checkpoint([manifest,report_path,Path('catalog/context_discovery.json')],branch,'C19 official document evidence: '+report['status'])

    checkpoint()
    try:
        discovery=Path('catalog/context_discovery.json');index_catalog=json.loads(discovery.read_text())
        for index in index_catalog['indexes']:
            item=index['raw_gzip'];item['remote']=remote.put(item['path'],'context-discovery-'+index['kind'])
            atomic_json(discovery,index_catalog)
            commit_checkpoint([discovery],branch,'C19 preserved official archive discovery source')
            Path(item['path']).unlink()
        for candidate in candidates:
            if time.monotonic()-started>230*60:
                report['status']='PAUSED_RUNTIME_LIMIT';break
            key=candidate['kind']+'/'+candidate['release_date'];record=records.get(key)
            if record and remote_verified(record):continue
            try:
                if record:materialize(record,http,remote)
                else:record=acquire_release(candidate,http)
            except Exception as error:
                report['errors'].append(dict(key=key,cause=str(error),error_type=type(error).__name__,impact='Affected document only; original version/availability not inferred'))
                checkpoint();continue
            for kind in ('raw','normalized'):record[kind]['remote']=remote.put(record[kind]['path'],'context-'+candidate['kind']+'-'+candidate['release_date'][:7])
            record['storage_state']='REMOTE_VERIFIED';records[key]=record
            if not any(x['kind']==candidate['kind'] for x in report['restorations']):
                target=Path('data/restored/context')/(key.replace('/','-')+'.html.gz')
                remote.restore(record['raw']['remote'],target,Budget(Path('data'),2))
                body=gzip.decompress(target.read_bytes())
                if hashlib.sha256(body).hexdigest()!=record['metadata']['source_document_sha256']:raise ValueError('Restored original HTML differs')
                report['restorations'].append(dict(key=key,kind=candidate['kind'],state='RESTORED_AND_TESTED',original_document_sha256=record['metadata']['source_document_sha256']))
                target.unlink()
            checkpoint()
            for kind in ('raw','normalized'):Path(record[kind]['path']).unlink()
        else:report['status']='DISCOVERED_SOURCE_SCAN_FINISHED'
        checkpoint()
        try:flow_from_remote(remote,branch,report)
        except Exception as error:
            report.update(flow_status='BLOCKED_COMPONENT_ONLY',flow_error=str(error),flow_resume_condition='Verified admitted source and deterministic recomputation/restoration required')
        checkpoint()
    except Exception as error:
        report.update(status='BLOCKED',error_type=type(error).__name__,error=str(error),resume_condition='Resolve exact source version, storage integrity or publication failure; retained local files first')
        checkpoint();raise


if __name__=='__main__':main()
