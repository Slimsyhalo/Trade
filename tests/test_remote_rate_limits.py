import io
import pytest
from quantlab_core.remote import GitHubRemote


class Response:
    def __init__(self,status,headers=None,text=''):
        self.status_code=status; self.headers=headers or {}; self.text=text
    def close(self): pass
    def raise_for_status(self):
        if self.status_code>=400: raise RuntimeError(str(self.status_code))


class Session:
    def __init__(self,responses):
        self.headers={}; self.responses=iter(responses); self.calls=0; self.bodies=[]
    def request(self,*args,**kwargs):
        self.calls+=1
        if 'data' in kwargs: self.bodies.append(kwargs['data'].read())
        return next(self.responses)


def test_primary_limit_waits_until_reset():
    r=Response(403,{'X-RateLimit-Remaining':'0','X-RateLimit-Reset':'200'})
    assert GitHubRemote.rate_delay(r,0,now=100)==102


def test_secondary_limit_and_permission_are_distinguished():
    assert GitHubRemote.rate_delay(Response(403,text='secondary rate limit'),1)==120
    assert GitHubRemote.rate_delay(Response(429,{'Retry-After':'7'}),0)==7
    assert GitHubRemote.rate_delay(Response(403,text='Resource not accessible by integration'),0) is None


def test_rejected_upload_retry_rewinds_body():
    session=Session([Response(429,{'Retry-After':'1'}),Response(200)])
    remote=GitHubRemote('owner/repo',session,interval=0)
    waits=[]; remote.wait=waits.append
    remote.request('POST','url',data=io.BytesIO(b'original bytes'))
    assert session.bodies==[b'original bytes',b'original bytes']
    assert any(x>=1 for x in waits)


def test_permission_denial_not_retried():
    session=Session([Response(403,text='Resource not accessible by integration')])
    remote=GitHubRemote('owner/repo',session,interval=0)
    with pytest.raises(RuntimeError,match='permission denied'): remote.request('GET','url')
    assert session.calls==1


def test_ambiguous_mutation_not_retried():
    class Broken(Session):
        def request(self,*args,**kwargs):
            self.calls+=1; raise OSError('connection lost after send')
    session=Broken([]); remote=GitHubRemote('owner/repo',session,interval=0)
    with pytest.raises(OSError): remote.request('POST','url')
    assert session.calls==1
