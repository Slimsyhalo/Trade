from pathlib import Path
import pyarrow as pa
import pyarrow.parquet as pq
import pytest
from build_derivative_products import build
from quantlab_core.io import sha256
from remote_derivatives import product_verified


def inputs(root,previous=False):
    source={
        'markPriceKlines':[dict(symbol='BTCUSDT',event_time_ms=0,open_time=0,close_time=59_999,close='101.00000000001',available_at_ms=60_000,availability_basis='bar_close_boundary_assumption')],
        'indexPriceKlines':[dict(symbol='BTCUSDT',event_time_ms=0,open_time=0,close_time=59_999,close='100',available_at_ms=60_000,availability_basis='bar_close_boundary_assumption')],
        'metrics':[dict(symbol='BTCUSDT',event_time_ms=300_000,sum_open_interest='12',sum_open_interest_value='1200',available_at_ms=None,availability_basis='unknown_historical_publication')],
    }
    if previous:source['previous_metrics']=[dict(symbol='BTCUSDT',event_time_ms=0,sum_open_interest='10',sum_open_interest_value='1000',available_at_ms=None,availability_basis='unknown_historical_publication')]
    paths={};records={}
    for name,rows in source.items():
        path=root/(name+'.parquet');pq.write_table(pa.Table.from_pylist(rows),path)
        paths[name]=path;records[name]=dict(key='BTCUSDT/'+name+'/fixture',raw={'sha256':'a'*64},normalized={'sha256':sha256(path)},qa={'rows':len(rows)})
    return paths,records


def test_products_recompute_byte_for_byte_and_keep_null_availability_typed(tmp_path):
    paths,records=inputs(tmp_path)
    a=build(paths,records,tmp_path/'one');b=build(paths,records,tmp_path/'two')
    assert all(a[k]['sha256']==b[k]['sha256'] for k in a)
    schema=pq.read_schema(a['oi_change_5m']['path'])
    assert schema.field('available_at_ms').type==pa.int64()
    assert schema.metadata[b'strict_causal_replay_certified']==b'false'
    assert a['oi_change_5m']['unknown_availability_rows']==1


def test_previous_partition_lineage_restores_midnight_change_without_prior_output(tmp_path):
    paths,records=inputs(tmp_path,previous=True)
    result=build(paths,records,tmp_path/'output')['oi_change_5m']
    rows=pq.read_table(result['path']).to_pylist()
    assert len(rows)==1 and rows[0]['oi_expected_cadence_difference_source_units']=='2'
    assert rows[0]['previous_observation_ms']==0 and 'previous_metrics' in result['inputs']


def test_tampered_source_fails_before_derivation(tmp_path):
    paths,records=inputs(tmp_path)
    records['metrics']['normalized']['sha256']='b'*64
    with pytest.raises(ValueError,match='immutable source'):build(paths,records,tmp_path/'output')


def test_unverified_or_mismatched_output_not_skipped():
    assert not product_verified({'remote':None})
    row=dict(sha256='a'*64,bytes=10,remote=dict(sha256='b'*64,bytes=10,verified_at=1))
    assert not product_verified(row)
    row['remote']['sha256']='a'*64
    assert product_verified(row)
