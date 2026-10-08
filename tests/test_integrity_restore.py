import zipfile
import pyarrow as pa
import pyarrow.parquet as pq
import pytest
from audit_integrity_campaign import inspect_file
from quantlab_core.io import sha256


def item(path,kind='normalized',rows=2):return dict(sha256=sha256(path),bytes=path.stat().st_size,object_kind=kind,expected_rows=rows)


def test_actual_zip_crc_read(tmp_path):
    p=tmp_path/'a.zip'
    with zipfile.ZipFile(p,'w') as z:z.writestr('a.csv','time,qty\n1,2\n')
    assert inspect_file(p,item(p,'raw'))['crc_check']=='PASS'


def test_schema_count_and_unknown_availability(tmp_path):
    p=tmp_path/'a.parquet';pq.write_table(pa.table(dict(event_time_ms=[1,2],available_at_ms=pa.array([None,None],type=pa.int64()))),p)
    result=inspect_file(p,item(p));assert result['unknown_availability_rows']==2
    with pytest.raises(ValueError,match='row count'):inspect_file(p,item(p,rows=3))


def test_availability_and_timestamp_errors(tmp_path):
    p=tmp_path/'a.parquet'
    for timestamps,available,reason in [([2,1],[3,3],'regresses'),([1,2],[0,3],'precedes')]:
        pq.write_table(pa.table(dict(event_time_ms=timestamps,available_at_ms=available)),p)
        with pytest.raises(ValueError,match=reason):inspect_file(p,item(p))


def test_bad_derivative_lineage(tmp_path):
    p=tmp_path/'a.parquet';pq.write_table(pa.table(dict(event_time_ms=[1,2])),p)
    i=item(p);i['source_identity']='a'*64
    with pytest.raises(ValueError,match='identity'):inspect_file(p,i)
