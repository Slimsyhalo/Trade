"""Deterministic daily products from exact remotely restored source Parquet."""
import hashlib
import json
from pathlib import Path
import pyarrow as pa
import pyarrow.parquet as pq
from quantlab_core.derivative_features import sampled_basis,open_interest_changes,VERSION
from quantlab_core.io import sha256

INTS={'window_start_ms','window_end_ms','event_time_ms','available_at_ms','decimal_precision',
      'previous_observation_ms','observation_interval_ms','declared_expected_interval_ms'}
BOOLS={'strict_causal_replay_certified','expected_cadence_matched'}


def source_identity(records):
    provenance={k:dict(key=r['key'],raw_sha256=r['raw']['sha256'],normalized_sha256=r['normalized']['sha256'])
                for k,r in sorted(records.items())}
    signature=hashlib.sha256(json.dumps(dict(version=VERSION,inputs=provenance),sort_keys=True,separators=(',',':')).encode()).hexdigest()
    return signature,provenance


def build(paths,records,destination):
    data={}
    for name,path in paths.items():
        if sha256(path)!=records[name]['normalized']['sha256']:raise ValueError('Restored input differs from immutable source identity')
        rows=pq.read_table(path).to_pylist()
        if len(rows)!=records[name]['qa']['rows']:raise ValueError('Restored source row count mismatch')
        data[name]=rows
    basis=list(sampled_basis(data['markPriceKlines'],data['indexPriceKlines']))
    previous=data.get('previous_metrics',[])
    metrics=([previous[-1]] if previous else [])+data['metrics']
    oi=list(open_interest_changes(metrics))
    if previous:oi=oi[1:] # derive the midnight transition, retain no prior-day output
    signature,provenance=source_identity(records)
    destination=Path(destination);destination.mkdir(parents=True,exist_ok=True)
    results={}
    for kind,rows in [('basis_close_1m',basis),('oi_change_5m',oi)]:
        if not rows:raise ValueError('No derivative rows; cannot publish empty success')
        fields=[(name,pa.int64() if name in INTS else pa.bool_() if name in BOOLS else pa.string()) for name in rows[0]]
        schema=pa.schema(fields,metadata={b'transform_version':VERSION.encode(),b'source_identity':signature.encode(),
                        b'inputs':json.dumps(provenance,sort_keys=True,separators=(',',':')).encode(),
                        b'timezone':b'UTC',b'strict_causal_replay_certified':b'false'})
        path=destination/(kind+'-'+signature+'.parquet')
        if path.exists():raise ValueError('Immutable derived output already exists; explicit reconciliation required')
        pq.write_table(pa.Table.from_pylist(rows,schema=schema),path,compression='zstd',compression_level=6)
        results[kind]=dict(path=str(path),sha256=sha256(path),bytes=path.stat().st_size,rows=len(rows),
                           source_identity=signature,inputs=provenance,
                           unknown_availability_rows=sum(r['available_at_ms'] is None for r in rows),
                           classification='DERIVED',strict_causal_replay_certified=False,transform_version=VERSION)
    return results
