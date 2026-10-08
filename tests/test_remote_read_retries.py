import hashlib
import pytest
import requests
from quantlab_core.remote import GitHubRemote
from quantlab_core.io import Budget


class Response:
    def __init__(self,body=b'abc',failure=False,status=200):
        self.body=body;self.failure=failure;self.status_code=status;self.headers={};self.text='';self.closed=False
    def __enter__(self):return self
    def __exit__(self,*args):self.close()
    def close(self):self.closed=True
    def raise_for_status(self):
        if self.status_code>=400:raise requests.HTTPError('response rejected')
    def iter_content(self,_):
        if self.failure:
            yield b'incomplete'
            raise requests.exceptions.ChunkedEncodingError('incomplete download')
        yield self.body


class Session:
    def __init__(self,items):self.headers={};self.items=iter(items);self.calls=[]
    def request(self,method,url,**kwargs):
        self.calls.append(method);value=next(self.items)
        if isinstance(value,Exception):raise value
        return value


def remote(items):
    session=Session(items);value=GitHubRemote('owner/repo',session,interval=0,attempts=2)
    value.wait=lambda _:None
    return value,session


def test_read_transport_retries_and_preserves_expected_object():
    response=Response();r,s=remote([requests.ConnectionError('closed before response'),response])
    assert r.request('GET','url') is response
    assert s.calls==['GET','GET'] and len(r.read_retry_events)==1


def test_mutation_transport_failure_is_never_blindly_retried():
    r,s=remote([requests.ConnectionError('uncertain upload'),Response()])
    with pytest.raises(requests.ConnectionError):r.request('POST','url')
    assert s.calls==['POST']


def test_interrupted_full_readback_restarts_hash_from_empty():
    partial=Response(failure=True);r,s=remote([partial,Response()])
    r.verify('url',hashlib.sha256(b'abc').hexdigest(),3)
    assert partial.closed and s.calls==['GET','GET']


def test_integrity_mismatch_is_not_retried_or_relaxed():
    r,s=remote([Response(b'wrong'),Response()])
    with pytest.raises(ValueError,match='checksum/size'):r.verify('url',hashlib.sha256(b'abc').hexdigest(),3)
    assert s.calls==['GET']


def test_interrupted_restoration_discards_only_partial_restore(tmp_path):
    r,s=remote([Response(failure=True),Response()])
    destination=tmp_path/'restored.parquet'
    r.restore(dict(bytes=3,sha256=hashlib.sha256(b'abc').hexdigest(),api_url='url'),destination,Budget(tmp_path,1))
    assert destination.read_bytes()==b'abc' and not destination.with_suffix('.parquet.part').exists()
    assert s.calls==['GET','GET']


def test_explicit_server_error_on_read_retries_but_permissions_still_stop():
    response=Response(status=503);r,s=remote([response,Response()])
    assert r.request('GET','url').status_code==200 and response.closed
    denied=Response(status=403);r,s=remote([denied,Response()])
    with pytest.raises(RuntimeError,match='permission denied'):r.request('GET','url')
    assert s.calls==['GET']
