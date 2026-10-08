import json
import pytest
from recover_live_artifact import validate_artifact
from live_collector.spool import ROUTES


def fixture(tmp_path):
    root=tmp_path/'artifact';root.mkdir();source=tmp_path/'catalog';source.mkdir()
    row=dict(path='public-1.jsonl.gz',sha256='a'*64,bytes=10,rows=2,first_receive_ns=1,last_receive_ns=2,remote=None)
    for route in ROUTES:
        rows=[row] if route=='public' else []
        (root/(route+'-manifest.json')).write_text(json.dumps(rows))
        (source/(route+'-manifest.json')).write_text(json.dumps(rows))
    return root,source,row


def test_artifact_receipt_cannot_promote_unverified_source(tmp_path):
    root,source,row=fixture(tmp_path)
    row['remote']=dict(verified_at=1,api_url='forged',sha256='a'*64,bytes=10)
    (root/'public-manifest.json').write_text(json.dumps([row]))
    assert validate_artifact(root,source)==1
    result=json.loads((root/'public-manifest.json').read_text())[0]
    assert result['remote'] is None and result['status']=='closed'


@pytest.mark.parametrize('field,value',[('sha256','b'*64),('rows',3),('bytes',11),('path','../unsafe.gz')])
def test_changed_artifact_provenance_is_rejected(tmp_path,field,value):
    root,source,row=fixture(tmp_path);row[field]=value
    (root/'public-manifest.json').write_text(json.dumps([row]))
    with pytest.raises(ValueError):validate_artifact(root,source)
