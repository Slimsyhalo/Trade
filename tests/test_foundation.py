import io, zipfile, hashlib
from datetime import date
from decimal import Decimal
import pytest
import pyarrow.parquet as pq
from quantlab_core.io import Budget, sha256
from quantlab_core.sources import days, checksum_text, day_ms, funding_pages
from quantlab_core.normalize import normalize
from quantlab_core.research import bars, replay, assert_causal, LeakageError, feature_spec

D=date(2024,10,7); T=day_ms(D)

def zipped(tmp,rows):
    p=tmp/'raw.zip'
    with zipfile.ZipFile(p,'w') as z: z.writestr('data.csv',rows)
    return p

def test_window():
    assert len(list(days('2024-10-07','2026-10-07')))==731
    with pytest.raises(ValueError): list(days('2024-10-06','2024-10-07'))

def test_timestamp(): assert T==1728259200000

def test_checksum(tmp_path):
    p=tmp_path/'x'; p.write_bytes(b'abc'); assert sha256(p)==hashlib.sha256(b'abc').hexdigest()
    assert checksum_text(sha256(p)+'  x','x')==sha256(p)
    with pytest.raises(ValueError): checksum_text(sha256(p)+' y','x')

def test_budget(tmp_path):
    (tmp_path/'x').write_bytes(b'x'*100)
    with pytest.raises(RuntimeError): Budget(tmp_path,0.0000001).check(1)

def test_normalize_precision(tmp_path):
    p=zipped(tmp_path,f'1,123.123456789012345678,0.000000001,1,1,{T},true\n2,124,2,2,2,{T+1},false\n')
    out=tmp_path/'out.parquet'; q=normalize(p,out,'aggTrades','BTCUSDT',D,Budget(tmp_path,0.1))
    assert q['status']=='PASS'; rows=pq.read_table(out).to_pylist()
    assert rows[0]['price']=='123.123456789012345678'
    assert pq.read_metadata(out).row_group(0).column(0).compression=='ZSTD'
    assert sha256(p)==sha256(p)

@pytest.mark.parametrize('rows',[f'1,NaN,2,1,1,{T},true\n',f'1,10,-2,1,1,{T},true\n',f'1,10,2,1,1,{T*1000},true\n','wrong,columns\n'])
def test_invalid_rows(tmp_path,rows):
    with pytest.raises((ValueError,KeyError)): normalize(zipped(tmp_path,rows),tmp_path/'o','aggTrades','BTCUSDT',D,Budget(tmp_path,1))

@pytest.mark.parametrize('ids,field',[( (1,1),'duplicates_found'),((1,3),'id_gaps'),((2,1),'out_of_order')])
def test_qa(tmp_path,ids,field):
    rows=''.join(f'{i},10,2,{i},{i},{T+n},true\n' for n,i in enumerate(ids))
    q=normalize(zipped(tmp_path,rows),tmp_path/'o','aggTrades','BTCUSDT',D,Budget(tmp_path,1))
    assert q['status']=='FAILED' and q[field]>0

def event(ts,price='10',qty='1',maker=False): return dict(event_time_ms=ts,available_at_ms=ts,price=price,quantity=qty,is_buyer_maker=maker,availability_basis='received')

def test_bars():
    result=list(bars([event(T),event(T+1,'11','2',True),event(T+60000,'12')]))
    assert result[0]['volume']==3 and result[0]['quote_volume']==32 and result[0]['available_at_ms']==T+60000
    assert result[0]['taker_buy_base_volume']==1

def test_replay():
    assert [e['event_time_ms'] for e in replay([[event(T),event(T+2)],[event(T+1)]],T+1)]==[T,T+1]
    with pytest.raises(LeakageError): assert_causal(event(T+1),T)

def test_future_bar():
    with pytest.raises(LeakageError): assert_causal(list(bars([event(T)]))[0],T+59999)

@pytest.mark.parametrize('kwargs',[{'centered':True},{'fill':'bfill'},{'offset':-1},{'uses_target':True}])
def test_leakage_specs(kwargs):
    with pytest.raises(LeakageError): feature_spec(**kwargs)

def test_unknown_publication():
    e=event(T); e['available_at_ms']=None
    with pytest.raises(LeakageError): list(replay([[e]],T))

def test_pagination():
    class Response:
        content=b'[]'
        def __init__(self,rows): self.rows=rows
        def json(self): return self.rows
    class Http:
        def __init__(self): self.cursors=[]
        def get(self,url,params):
            self.cursors.append(params['startTime'])
            return Response([{'fundingTime':1},{'fundingTime':3}] if len(self.cursors)==1 else [])
    h=Http(); assert len(list(funding_pages(h,'BTCUSDT',0,10)))==1; assert h.cursors==[0,4]

def test_book_bridge_and_gap():
    from live_collector.book import OrderBook, BookGap
    b=OrderBook(); b.snapshot({'lastUpdateId':10,'bids':[['9','1']],'asks':[['11','1']]})
    assert b.update({'U':9,'u':11,'pu':8,'b':[['9','0']],'a':[]})
    assert b.valid and '9' not in b.bids
    with pytest.raises(BookGap): b.update({'U':15,'u':16,'pu':14,'b':[],'a':[]})
    assert not b.valid

def test_retry_and_rate_ban(monkeypatch):
    from quantlab_core.io import HTTP
    monkeypatch.setattr('quantlab_core.io.time.sleep',lambda _:None)
    class Response:
        headers={}
        def __init__(self,status): self.status_code=status
        def close(self): pass
        def raise_for_status(self): pass
    class Session:
        def __init__(self,codes): self.codes=iter(codes)
        def get(self,*a,**k): return Response(next(self.codes))
    h=HTTP(0,3); h.session=Session([429,503,200]); assert h.get('unused').status_code==200
    h.session=Session([418])
    with pytest.raises(RuntimeError,match='ban'): h.get('unused')

def test_download_corruption_and_resume(tmp_path):
    from quantlab_core.io import HTTP
    class Response:
        headers={'Content-Length':'3'}
        def __enter__(self): return self
        def __exit__(self,*args): pass
        def iter_content(self,n): yield b'abc'
    h=HTTP(); h.get=lambda *a,**k:Response(); target=tmp_path/'raw'
    with pytest.raises(ValueError): h.download('url',target,Budget(tmp_path,1),'0'*64)
    assert not target.exists() and not list(tmp_path.glob('*.part'))
    digest=hashlib.sha256(b'abc').hexdigest(); h.download('url',target,Budget(tmp_path,1),digest)
    h.get=lambda *a,**k:pytest.fail('Verified resume must not redownload')
    h.download('url',target,Budget(tmp_path,1),digest)

def test_remote_verify_and_restore(tmp_path):
    from quantlab_core.remote import GitHubRemote
    class Response:
        def __enter__(self): return self
        def __exit__(self,*args): pass
        def iter_content(self,n): yield b'abc'
    class Session: headers={}
    r=GitHubRemote('owner/repo',Session()); r.request=lambda *a,**k:Response()
    digest=hashlib.sha256(b'abc').hexdigest(); r.verify('url',digest,3)
    with pytest.raises(ValueError): r.verify('url','0'*64,3)
    r.restore({'api_url':'url','bytes':3,'sha256':digest},tmp_path/'restored',Budget(tmp_path,1))
    assert (tmp_path/'restored').read_bytes()==b'abc'

def test_no_prune_on_remote_failure(tmp_path):
    from quantlab_core.pipeline import Pipeline
    cfg=dict(max_local_storage_gb=1)
    p=Pipeline(tmp_path,cfg)
    for kind in ('raw','normalized'): (tmp_path/kind).write_bytes(b'abc')
    record=dict(key='key',symbol='BTCUSDT',dataset='aggTrades',day='2024-10-07',qa={'status':'PASS'},raw={'path':'raw'},normalized={'path':'normalized'})
    class Remote:
        def put(self,*args): raise ValueError('remote failure')
    with pytest.raises(ValueError): p.upload_record(record,Remote(),True)
    assert (tmp_path/'raw').exists() and (tmp_path/'normalized').exists()

def test_reproducible_parquet(tmp_path):
    p=zipped(tmp_path,f'1,10,2,1,1,{T},true\n')
    for name in ('a','b'): normalize(p,tmp_path/name,'aggTrades','BTCUSDT',D,Budget(tmp_path,1))
    assert sha256(tmp_path/'a')==sha256(tmp_path/'b')

def test_corrupt_zip(tmp_path):
    p=tmp_path/'bad.zip'; p.write_bytes(b'not ZIP')
    with pytest.raises(zipfile.BadZipFile): normalize(p,tmp_path/'out','aggTrades','BTCUSDT',D,Budget(tmp_path,1))

def test_future_funding_and_book():
    for kind in ('funding','depth'):
        with pytest.raises(LeakageError): assert_causal(dict(event_time_ms=T,available_at_ms=T+10,dataset=kind),T)

def test_timestamp_duplicates_not_trade_duplicates(tmp_path):
    p=zipped(tmp_path,f'1,10,1,1,1,{T},true\n2,10,1,2,2,{T},false\n')
    assert normalize(p,tmp_path/'out','aggTrades','BTCUSDT',D,Budget(tmp_path,1))['status']=='PASS'

def test_actual_trades_header(tmp_path):
    raw=zipped(tmp_path,f'id,price,qty,quote_qty,time,is_buyer_maker\n1,10,2,20,{T},true\n')
    qa=normalize(raw,tmp_path/'out','trades','BTCUSDT',D,Budget(tmp_path,1))
    assert qa['status']=='PASS'
