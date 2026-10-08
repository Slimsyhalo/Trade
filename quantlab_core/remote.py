"""GitHub Releases: immutable hash-named assets and full readback verification.
GITHUB_TOKEN is read only from the environment; never written to files or logs.
"""
import os, hashlib, time, random
from pathlib import Path
import requests
from .io import sha256

class GitHubRemote:
    def __init__(self, repository, session=None, interval=4.0, attempts=5, release_body=None):
        token = os.environ.get('GITHUB_TOKEN')
        if not token and session is None: raise RuntimeError('GitHub write authentication unavailable; keep local data')
        self.session=session or requests.Session(); self.repository=repository
        self.session.headers.update({'Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28'})
        if token: self.session.headers['Authorization']='Bearer '+token
        self.base='https://api.github.com/repos/'+repository
        self.interval=interval; self.attempts=attempts; self.last_request=0
        self.releases={}; self.assets={}; self.rate_events=[]; self.read_retry_events=[]
        self.release_body=release_body or 'Immutable public market-data partitions. Verify against manifest.'
    @staticmethod
    def rate_delay(response, attempt, now=None):
        now=time.time() if now is None else now
        headers=response.headers
        if headers.get('X-RateLimit-Remaining')=='0':
            return max(1, float(headers.get('X-RateLimit-Reset',now+60))-now+2)
        if headers.get('Retry-After'):
            return max(1, float(headers['Retry-After']))
        if response.status_code==429 or 'rate limit' in response.text.lower():
            return 60*(2**attempt)
        return None
    @staticmethod
    def wait(seconds):
        # Emit observable progress; long server waits are split into <=60s sleeps.
        while seconds>0:
            step=min(60,seconds); time.sleep(step); seconds-=step
    def request(self, method, url, **kwargs):
        # Read-only transport failures may retry. Ambiguous mutations propagate
        # unchanged for immutable-name reconciliation; never blindly repeat POST.
        for attempt in range(self.attempts):
            self.wait(max(0,self.interval-(time.monotonic()-self.last_request)))
            self.last_request=time.monotonic()
            body=kwargs.get('data'); position=body.tell() if hasattr(body,'tell') else None
            try:
                r=self.session.request(method,url,timeout=(15,120),**kwargs)
            except (requests.ConnectionError, requests.Timeout) as error:
                if method.upper() not in ('GET','HEAD') or attempt+1==self.attempts: raise
                delay=min(5*(2**attempt),60)
                self.read_retry_events.append(dict(scope='request',method=method.upper(),error_type=type(error).__name__,attempt=attempt+1,delay_seconds=delay))
                self.wait(delay); continue
            if method.upper() in ('GET','HEAD') and r.status_code>=500:
                status=r.status_code
                if attempt+1==self.attempts:
                    try: r.raise_for_status()
                    finally: r.close()
                r.close(); delay=min(5*(2**attempt),60)
                self.read_retry_events.append(dict(scope='request',method=method.upper(),http_status=status,attempt=attempt+1,delay_seconds=delay))
                self.wait(delay); continue
            if r.status_code in (403,429):
                delay=self.rate_delay(r,attempt)
                if delay is None:
                    r.close(); raise RuntimeError('GitHub permission denied (not rate limiting); retain local files')
                self.rate_events.append({'status':r.status_code,'delay_seconds':delay,'attempt':attempt+1})
                print(f'GitHub rate limit: waiting {delay:.0f}s before retry {attempt+1}',flush=True)
                r.close()
                if attempt+1==self.attempts: raise RuntimeError('GitHub rate-limit retry budget exhausted; retain local files')
                if position is not None: body.seek(position)
                self.wait(delay+random.random()); continue
            if r.status_code==404: return r
            r.raise_for_status(); return r
    def release(self, tag):
        if tag in self.releases: return self.releases[tag]
        r=self.request('GET',self.base+'/releases/tags/'+tag)
        if r.status_code==404:
            r=self.request('POST',self.base+'/releases',json={'tag_name':tag,'name':tag,'body':self.release_body,'prerelease':True})
        r.raise_for_status(); self.releases[tag]=r.json(); return self.releases[tag]
    def verify(self, url, expected, size):
        for attempt in range(self.attempts):
            h=hashlib.sha256(); count=0
            try:
                with self.request('GET',url,headers={'Accept':'application/octet-stream'},stream=True) as r:
                    for chunk in r.iter_content(1024*1024): h.update(chunk); count+=len(chunk)
            except (requests.ConnectionError,requests.Timeout,requests.exceptions.ChunkedEncodingError) as error:
                if attempt+1==self.attempts: raise
                delay=min(5*(2**attempt),60)
                self.read_retry_events.append(dict(scope='full_readback',error_type=type(error).__name__,attempt=attempt+1,delay_seconds=delay))
                self.wait(delay); continue
            if h.hexdigest()!=expected or count!=size: raise ValueError('Remote checksum/size mismatch')
            return
    def put(self, path, tag):
        path=Path(path); digest=sha256(path); size=path.stat().st_size
        if size>=2*1024**3: raise ValueError('Asset exceeds GitHub limit; split partition first')
        rel=self.release(tag); name=digest+'-'+path.name
        if tag not in self.assets:
            assets=[]; page=1
            while True:
                batch=self.request('GET',rel['assets_url'],params={'per_page':100,'page':page}).json(); assets+=batch
                if len(batch)<100: break
                page+=1
            self.assets[tag]=assets
        assets=self.assets[tag]
        matches=[x for x in assets if x['name']==name]
        if matches: asset=matches[0]
        else:
            if len(assets)>=1000: raise RuntimeError('Release asset limit reached')
            with path.open('rb') as f:
                asset=self.request('POST',rel['upload_url'].split('{')[0],params={'name':name},headers={'Content-Type':'application/octet-stream'},data=f).json()
            assets.append(asset)
        self.verify(asset['url'],digest,size)
        return {'asset_id':asset['id'],'api_url':asset['url'],'url':asset['browser_download_url'],'sha256':digest,'bytes':size,'verified_at':time.time()}
    def restore(self, record, path, budget):
        path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
        if path.exists(): raise ValueError('Restore destination must be isolated/absent')
        temp=path.with_suffix(path.suffix+'.part'); budget.check(record['bytes'])
        try:
            for attempt in range(self.attempts):
                try:
                    with self.request('GET',record['api_url'],headers={'Accept':'application/octet-stream'},stream=True) as r, temp.open('wb') as f:
                        for chunk in r.iter_content(1024*1024): budget.check(len(chunk)); f.write(chunk); f.flush()
                except (requests.ConnectionError,requests.Timeout,requests.exceptions.ChunkedEncodingError) as error:
                    temp.unlink(missing_ok=True)
                    if attempt+1==self.attempts: raise
                    delay=min(5*(2**attempt),60)
                    self.read_retry_events.append(dict(scope='restoration',error_type=type(error).__name__,attempt=attempt+1,delay_seconds=delay))
                    self.wait(delay); continue
                if sha256(temp)!=record['sha256'] or temp.stat().st_size!=record['bytes']: raise ValueError('Restoration checksum failed')
                os.replace(temp,path); return
        finally:
            if temp.exists(): temp.unlink()
