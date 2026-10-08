"""Recompute tape features from individually certified, hash-bound partitions."""
import argparse
import json
from pathlib import Path
import time
import pyarrow as pa
import pyarrow.parquet as pq
from quantlab_core.flow_features import flow_windows
from quantlab_core.io import atomic_json,sha256,Budget


def build(record,certificate,source_root,out,seconds=60):
    if record.get('dataset')!='trades' or certificate.get('state')!='VALIDATED':raise ValueError('Admitted individual source required')
    if (certificate['raw_sha256']!=record['raw']['sha256'] or certificate['symbol']!=record['symbol']
            or certificate['day']!=record['day']):raise ValueError('Certificate source binding mismatch')
    source=Path(source_root)/record['normalized']['path']
    if sha256(source)!=record['normalized']['sha256']:raise ValueError('Source Parquet checksum mismatch')
    parquet=pq.ParquetFile(source)
    if parquet.metadata.num_rows!=certificate['independent_bar_evidence']['rows']:raise ValueError('Source rows differ from admission evidence')
    out=Path(out);out.parent.mkdir(parents=True,exist_ok=True)
    if out.exists():raise ValueError('Immutable derived output exists; verify/version before recomputation')
    temp=out.with_suffix('.parquet.part');started=time.monotonic();cpu=time.process_time();rows=0;source_rows=0
    budget=Budget(out.parent,2);writer=None;batch=[]
    def events():
        for b in parquet.iter_batches(batch_size=10000):yield from b.to_pylist()
    def write_batch(batch,writer):
        table=pa.Table.from_pylist(batch)
        if writer is None:
            schema=pa.schema([(f.name,pa.int64() if f.name=='available_at_us' else f.type) for f in table.schema],metadata={b'transform_version':b'tape-flow-1',b'classification':b'DERIVED',b'strict_replay':b'input and window-boundary assumptions require admission'})
            writer=pq.ParquetWriter(temp,schema,compression='zstd')
        table=table.cast(writer.schema);budget.check(table.nbytes*2+1048576);writer.write_table(table)
        return writer
    try:
        for row in flow_windows(events(),seconds,anchor=record['symbol']+'/'+record['day']+' UTC partition start; reset=0'):
            row.update(symbol=record['symbol'],source_parquet_sha256=record['normalized']['sha256'],source_raw_sha256=record['raw']['sha256'],
                       transform_version='tape-flow-1',source_admission_scope=certificate['admitted_scope'])
            rows+=1;source_rows+=row['source_rows'];batch.append(row)
            if len(batch)>=100:writer=write_batch(batch,writer);batch=[]
        if batch:writer=write_batch(batch,writer)
        if writer is not None:writer.close();writer=None
        if not rows or source_rows!=certificate['independent_bar_evidence']['rows']:raise ValueError('Derived source coverage mismatch')
        budget.check();__import__('os').replace(temp,out)
    finally:
        if writer:writer.close()
        temp.unlink(missing_ok=True)
    return dict(state='VALIDATED',classification='DERIVED',transform_version='tape-flow-1',symbol=record['symbol'],day=record['day'],
                source_parquet_sha256=record['normalized']['sha256'],source_raw_sha256=record['raw']['sha256'],
                normalized=dict(path=str(out),sha256=sha256(out),bytes=out.stat().st_size),source_rows=source_rows,derived_rows=rows,
                aggregation_seconds=seconds,elapsed_seconds=round(time.monotonic()-started,3),process_cpu_seconds=round(time.process_time()-cpu,3),
                strict_causal_replay_certified=False,limitations=['Tape-only metrics; no OFI or L2 liquidity inferred','CVD anchor resets explicitly per partition','Window closure/input availability assumptions preserved, no retroactive latency claim'])


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source-root',required=True);p.add_argument('--out-root',default='data/derived/flow');a=p.parse_args()
    manifest={r['key']:r for r in map(json.loads,(Path(a.source_root)/'manifest.jsonl').read_text().splitlines())}
    certificates=json.loads(Path('catalog/qa_revisions/individual_trades.json').read_text())['certificates'];report=[]
    for c in certificates:
        key=c['symbol']+'/trades/'+c['day'];out=Path(a.out_root)/c['symbol']/(c['day']+'-tape-flow-1.parquet')
        result=build(manifest[key],c,a.source_root,out);report.append(result);atomic_json(Path('reports/flow_derivation.json'),report)
        print(json.dumps(result),flush=True)
