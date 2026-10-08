import json, os, time
from pathlib import Path
from datetime import datetime, timezone
import requests
import pyarrow.parquet as pq
from .io import HTTP, Budget, sha256, atomic_json
from .sources import days, archive_url, checksum_text, period_bounds
from .normalize import normalize


def remote_verified(record):
    if record.get('qa',{}).get('status')!='PASS': return False
    for kind in ('raw','normalized'):
        local=record.get(kind,{})
        remote=local.get('remote') or {}
        digest=local.get('sha256')
        if not isinstance(digest,str) or len(digest)!=64 or not isinstance(local.get('bytes'),int) or local['bytes']<=0:
            return False
        if not remote.get('verified_at') or remote.get('sha256')!=local.get('sha256') or remote.get('bytes')!=local.get('bytes'):
            return False
    return True

class Pipeline:
    def __init__(self, root, config):
        self.root=Path(root); self.config=config
        self.budget=Budget(self.root/'data',config['max_local_storage_gb'])
        self.http=HTTP(config.get('request_interval_seconds',1),config.get('max_attempts',5))
        self.manifest_path=self.root/'manifest.jsonl'
        self.records={r['key']:r for r in self.records_list()}
    def records_list(self):
        if not self.manifest_path.exists(): return []
        return [json.loads(line) for line in self.manifest_path.read_text().splitlines() if line]
    def save(self, record):
        # Merge durable records before writing; CLI additionally enforces a single writer.
        self.records.update({r['key']:r for r in self.records_list()})
        previous=self.records.get(record['key'])
        if previous and previous.get('qa')!=record.get('qa') and previous.get('raw',{}).get('sha256'):
            history=self.root/'reports/manifest_qa_revisions.jsonl'
            history.parent.mkdir(parents=True,exist_ok=True)
            with history.open('a') as f: f.write(json.dumps(previous,sort_keys=True)+'\n')
        if previous and previous.get('raw',{}).get('sha256') and previous.get('raw',{}).get('sha256') != record.get('raw',{}).get('sha256'):
            history=self.root/'reports/manifest_revisions.jsonl'
            history.parent.mkdir(parents=True,exist_ok=True)
            with history.open('a') as f: f.write(json.dumps(previous,sort_keys=True)+'\n')
        self.records[record['key']]=record
        tmp=self.manifest_path.with_suffix('.part')
        with tmp.open('w') as f:
            for k in sorted(self.records): f.write(json.dumps(self.records[k],sort_keys=True)+'\n')
            f.flush(); os.fsync(f.fileno())
        os.replace(tmp,self.manifest_path)
    def sync_one(self,symbol,dataset,day,remote=None,prune=False):
        key=f'{symbol}/{dataset}/{day}'; existing=self.records.get(key)
        if existing and existing.get('qa',{}).get('status')=='PASS':
            local_ok=all((self.root/existing[k]['path']).exists() and sha256(self.root/existing[k]['path'])==existing[k]['sha256'] for k in ('raw','normalized'))
            if local_ok:
                if remote: self.upload_record(existing,remote,prune)
                return existing
            if remote and all(existing[k].get('remote') for k in ('raw','normalized')):
                for k in ('raw','normalized'):
                    r=existing[k]['remote']; remote.verify(r['api_url'],r['sha256'],r['bytes'])
                return existing
            # Quarantine corrupted local outputs; retain immutable recorded versions.
            for k in ('raw','normalized'):
                p=self.root/existing[k]['path']
                if p.exists() and sha256(p)!=existing[k]['sha256']: p.rename(p.with_name(p.name+'.corrupt-'+str(time.time_ns())))
        begin,finish=period_bounds(dataset,day)
        url=archive_url(symbol,dataset,day)
        try:
            check=self.http.get(url+'.CHECKSUM').text
        except requests.HTTPError as e:
            status='not_published_or_unavailable' if e.response.status_code==404 else 'request_failed'
            record={'key':key,'symbol':symbol,'dataset':dataset,'day':str(day),'source':url,'status':status,'http_status':e.response.status_code}
            self.save(record); return record
        digest=checksum_text(check,url.rsplit('/',1)[-1]); folder=Path(symbol)/dataset/f'{day:%Y/%m}'
        raw=self.root/'data/raw'/folder/(f'{day.day:02d}-{digest[:16]}.zip')
        self.http.download(url,raw,self.budget,digest)
        # Sidecar is original checksum response, preserved alongside original archive.
        sidecar=raw.with_suffix('.zip.CHECKSUM')
        if not sidecar.exists(): sidecar.write_text(check)
        out=self.root/'data/normalized'/folder/(f'{day.day:02d}-{digest[:16]}.parquet')
        if out.exists():
            if existing and existing.get('qa',{}).get('status')=='PASS' and existing.get('raw',{}).get('sha256')==digest and existing.get('normalized',{}).get('sha256')==sha256(out): return existing
            out.rename(out.with_name(out.name+'.uncommitted-'+str(time.time_ns())))
        try: qa=normalize(raw,out,dataset,symbol,day,self.budget)
        except Exception as e:
            record=dict(key=key,symbol=symbol,dataset=dataset,day=str(day),source=url,status='FAILED',error=str(e),qa={'status':'FAILED'})
            self.save(record); raise
        record=dict(key=key,symbol=symbol,dataset=dataset,day=str(day),source=url,download_timestamp=datetime.now(timezone.utc).isoformat(),schema_version='1',qa=qa,status=qa['status'],source_checksum=check.strip())
        record.update(granularity='month' if dataset=='fundingRate' else 'day',period_start=str(begin),period_end_exclusive=str(finish))
        for kind,path in [('raw',raw),('normalized',out)]:
            record[kind]={'path':str(path.relative_to(self.root)),'sha256':sha256(path),'bytes':path.stat().st_size,'remote':None}
        self.save(record)
        if remote and qa['status']=='PASS': self.upload_record(record,remote,prune)
        return record
    def upload_record(self,record,remote,prune=False):
        if record['qa']['status']!='PASS': raise ValueError('QA failure blocks remote promotion')
        tag=f"data-{record['symbol']}-{record['dataset']}-{record['day'][:7]}"
        for kind in ('raw','normalized'):
            p=self.root/record[kind]['path']
            record[kind]['remote']=remote.put(p,tag); self.save(record)
        if prune:
            # Both files were read back and hash-verified; persisted manifest precedes deletion.
            for kind in ('raw','normalized'): (self.root/record[kind]['path']).unlink()
    def catalog(self):
        expected=[str(d) for d in days(self.config['start_date'],self.config['end_date'])]; result=[]
        for symbol in self.config['symbols']:
            for dataset in self.config['datasets']:
                allrows=[r for r in self.records.values() if r['symbol']==symbol and r['dataset']==dataset]
                good=[r for r in allrows if r.get('qa',{}).get('status')=='PASS']
                present={day for r in good for day in (r['qa'].get('observed_days',[]) if dataset=='fundingRate' else [r['day']])}
                missing=[d for d in expected if d not in present]
                result.append(dict(symbol=symbol,dataset=dataset,first_available=min(present,default=None),last_available=max(present,default=None),first_timestamp=min((r['qa']['min_timestamp'] for r in good),default=None),last_timestamp=max((r['qa']['max_timestamp'] for r in good),default=None),expected_days=len(expected),available_days=len(present),missing_days=len(missing),coverage_percentage=100*len(present)/len(expected),missing_partitions=missing,rows=sum(r['qa']['rows'] for r in good),partitions=len(good),compressed_bytes=sum(r['normalized']['bytes'] for r in good),raw_zip_bytes=sum(r['raw']['bytes'] for r in good),schema_version='1',remote_locations=[r['normalized']['remote'] for r in good if r['normalized']['remote']],qa_status='PARTIAL' if missing else 'PASS',acquired_partitions=len([r for r in allrows if 'normalized' in r]),quarantined_rows=sum(r.get('qa',{}).get('rows',0) for r in allrows if r.get('qa',{}).get('status')=='FAILED'),failed_partitions=[r['key'] for r in allrows if r.get('qa',{}).get('status')=='FAILED']))
                backed=[r for r in good if remote_verified(r)]
                backed_days={day for r in backed for day in (r['qa'].get('observed_days',[]) if dataset=='fundingRate' else [r['day']])}
                result[-1].update(partition_granularity='month' if dataset=='fundingRate' else 'day',remote_verified_partitions=len(backed),remote_verified_days=len(backed_days),remote_coverage_percentage=100*len(backed_days)/len(expected))
        atomic_json(self.root/'data_catalog.json',{'notice':'DO NOT ASSUME DATA EXISTS UNLESS LISTED IN THE CATALOG.','datasets':result})
        return result
    def validate(self):
        checks=[]
        for r in self.records.values():
            if 'normalized' not in r: continue
            for kind in ('raw','normalized'):
                p=self.root/r[kind]['path']
                if not p.exists():
                    checks.append({'key':r['key'],'kind':kind,'status':'REMOTE_NOT_RECHECKED' if r[kind]['remote'] else 'FAILED'}); continue
                ok=sha256(p)==r[kind]['sha256'] and p.stat().st_size==r[kind]['bytes']
                if kind=='normalized': ok=ok and pq.read_metadata(p).num_rows==r['qa']['rows']
                checks.append({'key':r['key'],'kind':kind,'integrity_status':'PASS' if ok else 'FAILED','dataset_qa':r['qa']['status'],'status':'PASS' if ok and r['qa']['status']=='PASS' else 'FAILED'})
        atomic_json(self.root/'reports/validation.json',checks); return checks
