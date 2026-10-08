import gzip
import hashlib
import json
import zipfile
import pytest
from quantlab_core.context_events import parse_release
from quantlab_core.io import sha256
from recover_official_documents import verify_container


def fixture(tmp_path,known_availability=False):
    original=b'embargoed until 8:30 a.m. (ET) Thursday, October 10, 2024'
    metadata=parse_release(original.decode(),'cpi','2024-10-10')
    metadata.update(source_original_bytes=len(original),source_document_sha256=hashlib.sha256(original).hexdigest())
    if known_availability:metadata['historical_effective_availability_utc']='2024-10-10T12:30:00Z'
    contents={'releases/cpi/original.html.gz':gzip.compress(original,mtime=0),'releases/cpi/provenance.context.json':json.dumps(metadata).encode()}
    path=tmp_path/'originals.zip'
    with zipfile.ZipFile(path,'w') as z:
        for name,body in contents.items():z.writestr(name,body)
    spec=dict(bundle_bytes=path.stat().st_size,bundle_sha256=sha256(path),expected_members=[
        dict(name=name,sha256=hashlib.sha256(body).hexdigest(),bytes=len(body),kind='raw' if name.endswith('.gz') else 'normalized',key='cpi/2024-10-10') for name,body in contents.items()])
    return path,spec,{'cpi/2024-10-10':{'metadata':metadata}}


def test_exact_document_and_provenance_all_restored(tmp_path):
    path,spec,records=fixture(tmp_path)
    result=verify_container(path,spec,records)
    assert len(result)==2 and all(x['state']=='RESTORED_AND_TESTED' for x in result)


def test_container_or_member_corruption_stops_recovery(tmp_path):
    path,spec,records=fixture(tmp_path)
    spec['expected_members'][0]['sha256']='0'*64
    with pytest.raises(ValueError,match='SHA-256'):verify_container(path,spec,records)
    spec['bundle_sha256']='0'*64
    with pytest.raises(ValueError,match='container'):verify_container(path,spec,records)


def test_restoration_does_not_certify_unknown_historical_availability(tmp_path):
    path,spec,records=fixture(tmp_path,known_availability=True)
    with pytest.raises(ValueError,match='availability'):verify_container(path,spec,records)
