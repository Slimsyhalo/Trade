"""Discover and preserve bounded BLS/FOMC release archives with provenance."""
from datetime import datetime,timezone
import gzip
import hashlib
import json
from pathlib import Path
import time

from quantlab_core.context_events import discover,parse_release
from quantlab_core.io import HTTP,Budget,atomic_json,sha256

INDEXES={k:'https://www.bls.gov/bls/news-release/'+k+'.htm' for k in ('cpi','ppi','empsit','jolts')}
INDEXES['fomc']='https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm'


def compressed_original(body,path,budget):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    compressed=gzip.compress(body,mtime=0)
    if path.exists():
        if path.read_bytes()!=compressed:raise ValueError('Immutable source version changed')
        return
    budget.check(len(compressed));temp=path.with_suffix(path.suffix+'.part')
    with temp.open('xb') as f:
        f.write(compressed);f.flush();__import__('os').fsync(f.fileno())
    __import__('os').replace(temp,path)


def discover_all(http):
    result=[];errors=[];indexes=[]
    for kind,url in INDEXES.items():
        try:
            response=http.get(url)
            try:body=response.content;found=discover(response.text,url,kind)
            finally:response.close()
            digest=hashlib.sha256(body).hexdigest();stamp=datetime.now(timezone.utc).isoformat()
            path=Path('data/context/indexes')/(kind+'-'+digest+'.html.gz');compressed_original(body,path,Budget(Path('data/context'),2))
            indexes.append(dict(kind=kind,url=url,observed_at_utc=stamp,original_sha256=digest,bytes=len(body),raw_gzip=dict(path=str(path),sha256=sha256(path),bytes=path.stat().st_size),discovered_in_window=len(found)))
            result.extend(found)
        except Exception as error:errors.append(dict(kind=kind,url=url,error_type=type(error).__name__,error=str(error),impact='Only this index blocked; other official sources continue',resume_condition='Official access/schema restored; no evasion'))
    atomic_json(Path('catalog/context_discovery.json'),dict(generated_at=datetime.now(timezone.utc).isoformat(),indexes=indexes,candidates=result,errors=errors,
                                                          completeness_certified=False,notice='Current indexes discover archive URLs; current calendars are not as-of historical schedules'))
    return result,errors


def acquire_release(candidate,http):
    url=candidate['url'];response=http.get(url)
    try:
        body=response.content;metadata=parse_release(response.text,candidate['kind'],candidate['release_date'])
        headers={k:response.headers.get(k) for k in ('ETag','Last-Modified','Date','Content-Type')}
    finally:response.close()
    digest=hashlib.sha256(body).hexdigest();stamp=datetime.now(timezone.utc).isoformat()
    root=Path('data/context/releases')/candidate['kind'];raw=root/(candidate['release_date']+'-'+digest+'.html.gz')
    compressed_original(body,raw,Budget(Path('data/context'),2))
    metadata.update(source=url,source_document_sha256=digest,source_original_bytes=len(body),source_response_headers=headers,
                    acquired_at_utc=stamp,observed_document_available_at_utc=stamp,
                    event_id=candidate['kind']+'/'+candidate['release_date'],state='VALIDATED',
                    validation_scope='Release metadata/provenance only; original historical values and causal dissemination not certified',
                    source_terms_ref='catalog/source_inventory.json')
    normalized=root/(candidate['release_date']+'-'+digest+'.context.json')
    if normalized.exists():raise ValueError('Immutable context metadata exists; recover through catalog')
    atomic_json(normalized,metadata)
    return dict(key=metadata['event_id'],state='VALIDATED',historical_replay_eligible=False,metadata=metadata,
                raw=dict(path=str(raw),sha256=sha256(raw),bytes=raw.stat().st_size),
                normalized=dict(path=str(normalized),sha256=sha256(normalized),bytes=normalized.stat().st_size))


def main():
    http=HTTP(interval=1);started=time.monotonic();candidates,errors=discover_all(http)
    manifest=Path('catalog/context_manifest.json');records=json.loads(manifest.read_text()) if manifest.exists() else {}
    for candidate in candidates:
        key=candidate['kind']+'/'+candidate['release_date']
        if key in records:
            for kind in ('raw','normalized'):
                item=records[key][kind]
                if not Path(item['path']).is_file() or sha256(item['path'])!=item['sha256']:
                    raise ValueError('Known local context missing/changed; restore before resuming')
            continue
        try:
            record=acquire_release(candidate,http);records[record['key']]=record
            print(json.dumps(dict(key=record['key'],publication_claim_utc=record['metadata']['original_publication_claim_utc'])),flush=True)
        except Exception as error:errors.append(dict(candidate=candidate,error_type=type(error).__name__,error=str(error)))
        atomic_json(Path('catalog/context_manifest.json'),records)
        atomic_json(Path('reports/context_acquisition.json'),dict(status='RUNNING',acquired_documents=len(records),candidate_count=len(candidates),errors=errors,
                                                               elapsed_seconds=round(time.monotonic()-started,3),historical_value_vintage_certified=False))
    atomic_json(Path('reports/context_acquisition.json'),dict(status='BOUNDED_SOURCE_SCAN_FINISHED',acquired_documents=len(records),candidate_count=len(candidates),errors=errors,
                                                           elapsed_seconds=round(time.monotonic()-started,3),historical_value_vintage_certified=False))


if __name__=='__main__':main()
