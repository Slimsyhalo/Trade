"""GitHub Releases: immutable hash-named assets and full readback verification.
GITHUB_TOKEN is read only from the environment; never written to files or logs.
"""
import os, hashlib, time
from pathlib import Path
import requests
from .io import sha256

class GitHubRemote:
    def __init__(self, repository, session=None):
        token = os.environ.get('GITHUB_TOKEN')
        if not token and session is None: raise RuntimeError('GitHub write authentication unavailable; keep local data')
        self.session=session or requests.Session(); self.repository=repository
        self.session.headers.update({'Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28'})
        if token: self.session.headers['Authorization']='Bearer '+token
        self.base='https://api.github.com/repos/'+repository
    def request(self, method, url, **kwargs):
        # Mutations never blindly retried: caller reconciles by immutable asset name.
        r=self.session.request(method,url,timeout=(15,120),**kwargs)
        if r.status_code in (403,429):
            raise RuntimeError('GitHub permission/rate limit blocked; preserve local files and resume later')
        r.raise_for_status(); return r
    def release(self, tag):
        r=self.session.get(self.base+'/releases/tags/'+tag,timeout=30)
        if r.status_code==404:
            return self.request('POST',self.base+'/releases',json={'tag_name':tag,'name':tag,'body':'Immutable public market-data partitions. Verify against manifest.','prerelease':True}).json()
        r.raise_for_status(); return r.json()
    def verify(self, url, expected, size):
        h=hashlib.sha256(); count=0
        with self.request('GET',url,headers={'Accept':'application/octet-stream'},stream=True) as r:
            for chunk in r.iter_content(1024*1024): h.update(chunk); count+=len(chunk)
        if h.hexdigest()!=expected or count!=size: raise ValueError('Remote checksum/size mismatch')
    def put(self, path, tag):
        path=Path(path); digest=sha256(path); size=path.stat().st_size
        if size>=2*1024**3: raise ValueError('Asset exceeds GitHub limit; split partition first')
        rel=self.release(tag); name=digest+'-'+path.name
        assets=[]; page=1
        while True:
            batch=self.request('GET',rel['assets_url'],params={'per_page':100,'page':page}).json(); assets+=batch
            if len(batch)<100: break
            page+=1
        matches=[x for x in assets if x['name']==name]
        if matches: asset=matches[0]
        else:
            if len(assets)>=1000: raise RuntimeError('Release asset limit reached')
            with path.open('rb') as f:
                asset=self.request('POST',rel['upload_url'].split('{')[0],params={'name':name},headers={'Content-Type':'application/octet-stream'},data=f).json()
        self.verify(asset['url'],digest,size)
        return {'asset_id':asset['id'],'api_url':asset['url'],'url':asset['browser_download_url'],'sha256':digest,'bytes':size,'verified_at':time.time()}
    def restore(self, record, path, budget):
        path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
        if path.exists(): raise ValueError('Restore destination must be isolated/absent')
        temp=path.with_suffix(path.suffix+'.part'); budget.check(record['bytes'])
        try:
            with self.request('GET',record['api_url'],headers={'Accept':'application/octet-stream'},stream=True) as r, temp.open('wb') as f:
                for chunk in r.iter_content(1024*1024): budget.check(len(chunk)); f.write(chunk); f.flush()
            if sha256(temp)!=record['sha256'] or temp.stat().st_size!=record['bytes']: raise ValueError('Restoration checksum failed')
            os.replace(temp,path)
        finally:
            if temp.exists(): temp.unlink()
