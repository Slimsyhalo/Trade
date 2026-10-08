"""Persistence-only replay of real payloads; not new market observations."""
import gzip,json,subprocess,time,types,tempfile
from pathlib import Path
from quantlab_core.io import Budget,atomic_json,sha256
from live_collector.spool import Sink


def run(path,output,count=10000):
    source_sha='0edc1bc1bc5b9830487c060c78778c1d323e8954'
    reference=types.ModuleType('reference_spool')
    exec(compile(subprocess.check_output(['git','show',source_sha+':live_collector/spool.py'],text=True),'reference_spool','exec'),reference.__dict__)
    entries=[]
    with gzip.open(path,'rt') as f:
        for line in f:
            row=json.loads(line)
            if row['kind']=='event':entries.append((row['kind'],row['payload'],row['receive_timestamp_ns'],{}))
            if len(entries)>=count:break
    results={}
    with tempfile.TemporaryDirectory(prefix='quantlab-batch-benchmark-') as folder:
        for kind,implementation in [('original',reference.Sink),('batched',Sink)]:
            root=Path(folder)/kind;store=implementation(root,Budget(root,1),'public',max_bytes=100_000_000,max_seconds=3600)
            before=time.monotonic();cpu=time.process_time()
            if kind=='original':
                for event,payload,_,_ in entries:store.write(event,payload)
            else:
                for begin in range(0,len(entries),128):store.write_batch(entries[begin:begin+128])
            store.close();elapsed=time.monotonic()-before;cpu=time.process_time()-cpu
            observed=[]
            for record in store.records:
                with gzip.open(root/record['path'],'rt') as stream:observed.extend(json.loads(x)['payload'] for x in stream)
            if observed!=[x[1] for x in entries]:raise ValueError('Persistence benchmark lost/reordered payloads')
            results[kind]=dict(rows=len(observed),elapsed_seconds=elapsed,process_cpu_seconds=cpu,compressed_bytes=sum(x['bytes'] for x in store.records),payload_preservation='PASS')
    report=dict(classification='PERSISTENCE_ONLY_REPLAY_NOT_LIVE_CONTINUITY',source_original_spool_sha=source_sha,
                source_segment_sha256=sha256(Path(path)),source_code_files_sha256={p:sha256(Path(p)) for p in ('benchmark_live_batching.py','live_collector/spool.py')},
                results=results,elapsed_speed_ratio=results['original']['elapsed_seconds']/results['batched']['elapsed_seconds'],
                C20_accepted=False,network_improvement_certified=False,
                limitations='One local workload of actual payloads. Original receipt timestamps regenerated; batched timestamps preserved. Different gzip policy and flush frequency change bytes. No inference of network throughput, permanent service, kernel latency or root cause of past disconnects. Temporary benchmark copies removed; originals unchanged.')
    atomic_json(output,report);return report


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();run(args.source,args.output)
