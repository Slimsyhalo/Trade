"""Bounded live capture with route isolation, disk budget and loss markers.
Depth events are retained; book reconstruction requires snapshot bridge validation.
Disconnected periods are never represented as uninterrupted data.
"""
import argparse, asyncio, gzip, json, time, uuid, random
from datetime import datetime, timezone
from pathlib import Path
import yaml
import websockets
from quantlab_core.io import Budget, HTTP, atomic_json, sha256
from quantlab_core.sources import SYMBOLS

class Sink:
    def __init__(self,root,budget,route,remote=None):
        self.root=Path(root); self.root.mkdir(parents=True,exist_ok=True); self.budget=budget; self.route=route; self.remote=remote
        self.f=None; self.path=None; self.count=0; self.started=0; self.records=json.loads((self.root/(route+'-manifest.json')).read_text()) if (self.root/(route+'-manifest.json')).exists() else []
    def write(self,kind,payload):
        if self.f is None:
            self.path=self.root/f'{self.route}-{time.time_ns()}-{uuid.uuid4().hex}.jsonl.gz'
            self.f=gzip.open(self.path,'wb'); self.count=0; self.started=time.monotonic()
        now=time.time_ns(); data=(json.dumps({'receive_timestamp_ns':now,'kind':kind,'payload':payload},separators=(',',':'))+'\n').encode()
        self.budget.check(len(data)+65536); self.f.write(data); self.f.flush(); self.count+=1
        if self.path.stat().st_size>=8_000_000 or time.monotonic()-self.started>=60: self.close()
    def close(self):
        if self.f is None: return
        self.f.close(); self.f=None
        record=dict(path=str(self.path),sha256=sha256(self.path),bytes=self.path.stat().st_size,rows=self.count,remote=None)
        if self.remote: record['remote']=self.remote.put(self.path,'live-'+datetime.now(timezone.utc).strftime('%Y-%m-%d'))
        self.records.append(record); atomic_json(self.root/(self.route+'-manifest.json'),self.records)

async def capture(route,symbols,sink,deadline):
    suffixes=['bookTicker','depth@100ms'] if route=='public' else ['aggTrade','markPrice@1s','forceOrder']
    streams='/'.join(s.lower()+'@'+x for s in symbols for x in suffixes)
    url='wss://fstream.binance.com/'+route+'/stream?streams='+streams
    attempt=0
    while time.monotonic()<deadline:
        try:
            async with websockets.connect(url,open_timeout=20,ping_interval=20,max_queue=1024) as ws:
                sink.write('connection_start',{'route':route,'continuity':'new_segment'})
                last={}; attempt=0
                async for msg in ws:
                    obj=json.loads(msg); data=obj.get('data',{}); stream=obj.get('stream','unknown'); kind=data.get('e')
                    if kind=='depthUpdate':
                        previous=last.get(stream)
                        if previous is not None and data['pu']!=previous: sink.write('sequence_gap',{'stream':stream,'previous_u':previous,'pu':data['pu'],'book_valid':False})
                        if previous is not None and data['u']<=previous:
                            sink.write('duplicate_or_old',{'stream':stream,'u':data['u']}); continue
                        last[stream]=data['u']
                    elif kind=='aggTrade':
                        previous=last.get(stream)
                        if previous is not None and data['a']<=previous:
                            sink.write('duplicate_or_old',{'stream':stream,'id':data['a']}); continue
                        if previous is not None and data['a']!=previous+1: sink.write('trade_gap',{'stream':stream,'previous':previous,'id':data['a']})
                        last[stream]=data['a']
                    sink.write('event',obj)
                    if time.monotonic()>=deadline: break
        except (OSError,TimeoutError,websockets.exceptions.WebSocketException) as e:
            sink.write('disconnect',{'error':str(e),'unrecoverable_gap_possible':True}); attempt+=1
            await asyncio.sleep(min(30,2**min(attempt,5))+random.random())
        finally: sink.close()

async def snapshots(symbols,sink,deadline):
    http=HTTP(interval=1)
    while time.monotonic()<deadline:
        for symbol in symbols:
            for endpoint,params in [('openInterest',{'symbol':symbol}),('depth',{'symbol':symbol,'limit':1000})]:
                try:
                    r=await asyncio.to_thread(http.get,'https://fapi.binance.com/fapi/v1/'+endpoint,params=params)
                    sink.write(endpoint+'_snapshot',r.json())
                except Exception as e: sink.write('snapshot_error',{'symbol':symbol,'endpoint':endpoint,'error':str(e)})
        await asyncio.sleep(min(30,max(0,deadline-time.monotonic())))
    sink.close()

async def run(cfg,seconds,remote=None):
    root=Path('data/live'); budget=Budget('data',cfg['max_local_storage_gb']); deadline=time.monotonic()+seconds
    sinks=[Sink(root,budget,r,remote) for r in ('public','market','snapshots')]
    try:
        async with asyncio.timeout(seconds+1):
            await asyncio.gather(capture('public',cfg['symbols'],sinks[0],deadline),capture('market',cfg['symbols'],sinks[1],deadline),snapshots(cfg['symbols'],sinks[2],deadline))
    except TimeoutError: pass
    finally:
        for sink in sinks: sink.close()

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--seconds',type=int,default=60); p.add_argument('--remote',action='store_true'); a=p.parse_args()
    cfg=yaml.safe_load(Path('config.yaml').read_text()); remote=None
    if a.remote:
        from quantlab_core.remote import GitHubRemote
        remote=GitHubRemote(cfg['repository'])
    from quantlab_core.lock import writer_lock
    with writer_lock(Path('.pipeline.lock')):
        asyncio.run(run(cfg,a.seconds,remote))
