"""Small streamed GET probes: headers only, never bulk download."""
import json
from pathlib import Path
from quantlab_core.io import HTTP, atomic_json
from quantlab_core.sources import archive_url
http=HTTP(interval=0.5,attempts=2); result=[]
for symbol in ('BTCUSDT','ETHUSDT','SOLUSDT'):
 for dataset in ('aggTrades','trades','klines','markPriceKlines','indexPriceKlines','premiumIndexKlines','metrics','bookDepth','bookTicker','liquidationSnapshot'):
  url=archive_url(symbol,dataset,'2024-10-07')
  try:
   with http.get(url,stream=True) as r: row=dict(symbol=symbol,dataset=dataset,day='2024-10-07',status=r.status_code,bytes=int(r.headers.get('Content-Length',0)),url=url)
  except Exception as e: row=dict(symbol=symbol,dataset=dataset,day='2024-10-07',error=str(e),url=url)
  result.append(row); print(json.dumps(row),flush=True)
  atomic_json('reports/source_probes.json',result)
