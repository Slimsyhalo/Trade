#!/usr/bin/env python3
import argparse, json, sys
from pathlib import Path
from datetime import date, datetime, timezone
import yaml
from quantlab_core.pipeline import Pipeline
from quantlab_core.sources import days, archive_url, DATASETS
from quantlab_core.io import atomic_json

def main():
    p=argparse.ArgumentParser(description='Read-only Binance QuantLab; no trading')
    p.add_argument('command',choices=['discover','sync','validate','status','upload','restore'])
    p.add_argument('--config',default='config.yaml'); p.add_argument('--symbol'); p.add_argument('--dataset')
    p.add_argument('--start'); p.add_argument('--end'); p.add_argument('--max-local-storage-gb',type=float)
    p.add_argument('--limit',type=int,default=1,help='Max partitions per invocation; explicit batch size prevents blind downloads')
    p.add_argument('--remote',action='store_true'); p.add_argument('--prune',action='store_true'); p.add_argument('--key')
    args=p.parse_args(); root=Path(args.config).resolve().parent; cfg=yaml.safe_load(Path(args.config).read_text())
    if args.max_local_storage_gb is not None: cfg['max_local_storage_gb']=args.max_local_storage_gb
    pipeline=Pipeline(root,cfg)
    if args.command=='status': print(json.dumps(pipeline.catalog(),indent=2)); return
    if args.command=='validate':
        checks=pipeline.validate(); print(json.dumps(checks,indent=2))
        if not checks or any(c['status']!='PASS' for c in checks): sys.exit(1)
        return
    if args.prune and not args.remote: p.error('--prune requires --remote')
    remote=None
    if args.remote or args.command in ('upload','restore'):
        from quantlab_core.remote import GitHubRemote
        remote=GitHubRemote(cfg['repository'])
    if args.command=='upload':
        for r in list(pipeline.records.values()):
            if r.get('qa',{}).get('status')=='PASS': pipeline.upload_record(r,remote,args.prune)
        pipeline.catalog(); return
    if args.command=='restore':
        if not args.key: p.error('--key required')
        import pyarrow.parquet as pq
        r=pipeline.records[args.key]; record=r['normalized'].get('remote')
        if not record: raise RuntimeError('Partition has no verified remote copy')
        target=root/'data/restored'/Path(r['normalized']['path']).name
        remote.restore(record,target,pipeline.budget)
        if pq.read_metadata(target).num_rows!=r['qa']['rows']: raise ValueError('Restore row count mismatch')
        atomic_json(root/'reports/restore.json',{'key':args.key,'status':'PASS','sha256':record['sha256'],'rows':r['qa']['rows']}); return
    if args.limit<1: p.error('--limit must be positive')
    symbols=[args.symbol] if args.symbol else cfg['symbols']; datasets=[args.dataset] if args.dataset else cfg['datasets']
    count=0; probes=[]
    for symbol in symbols:
        for dataset in datasets:
            for day in days(args.start or cfg['start_date'],args.end or cfg['end_date']):
                if args.command=='discover':
                    url=archive_url(symbol,dataset,day)
                    try:
                        with pipeline.http.get(url,stream=True) as r:
                            probe={'symbol':symbol,'dataset':dataset,'day':str(day),'url':url,'status':r.status_code,'compressed_bytes':int(r.headers.get('Content-Length',0))}
                    except Exception as e: probe={'symbol':symbol,'dataset':dataset,'day':str(day),'error':str(e)}
                    probes.append(probe); print(json.dumps(probe),flush=True)
                else:
                    if day>=datetime.now(timezone.utc).date():
                        print(json.dumps({'day':str(day),'status':'not_closed_utc_day'}),flush=True); continue
                    r=pipeline.sync_one(symbol,dataset,day,remote,args.prune)
                    print(json.dumps({'key':r['key'],'status':r['status'],'rows':r.get('qa',{}).get('rows')}),flush=True)
                count+=1
                if count>=args.limit:
                    if probes: atomic_json(root/'reports/discovery.json',probes)
                    pipeline.catalog(); return
    if probes: atomic_json(root/'reports/discovery.json',probes)
    pipeline.catalog()

if __name__=='__main__':
    from quantlab_core.lock import writer_lock
    with writer_lock(Path(__file__).resolve().parent / '.pipeline.lock'): main()
