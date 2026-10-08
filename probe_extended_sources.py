"""Bounded official archive discovery; HEAD/listing observations are not acquisition."""
from datetime import date, datetime, timezone
import json
from pathlib import Path
import time
import xml.etree.ElementTree as ET

import requests

from quantlab_core.io import atomic_json
from quantlab_core.sources import START, END, SYMBOLS, archive_url


def spot_url(symbol, dataset, day, interval='1m'):
    if symbol not in SYMBOLS or dataset not in ('trades','aggTrades','klines') or not START <= day <= END:
        raise ValueError('Unsupported/out-of-window spot request')
    folder = f'/{interval}' if dataset == 'klines' else ''
    label = interval if dataset == 'klines' else dataset
    return f'https://data.binance.vision/data/spot/daily/{dataset}/{symbol}{folder}/{symbol}-{label}-{day}.zip'


def listed_window(session, dataset, symbol):
    prefix = f'data/futures/um/daily/{dataset}/{symbol}/'
    params = {'list-type':2, 'prefix':prefix, 'start-after':prefix+f'{symbol}-{dataset}-{START}'}
    result, pages = [], 0
    endpoint = 'https://s3-ap-northeast-1.amazonaws.com/data.binance.vision'
    while True:
        time.sleep(1)
        response = session.get(endpoint, params=params, timeout=(15,45))
        response.raise_for_status()
        root = ET.fromstring(response.content)
        ns = {'s':'http://s3.amazonaws.com/doc/2006-03-01/'}
        pages += 1
        beyond = False
        for item in root.findall('s:Contents', ns):
            key = item.findtext('s:Key', namespaces=ns)
            name = key.rsplit('/',1)[-1]
            if not name.endswith('.zip'):
                continue
            day = date.fromisoformat(name[len(symbol)+len(dataset)+2:-4])
            if day > END:
                beyond = True; break
            if START <= day <= END:
                result.append(dict(key=key, day=str(day), bytes=int(item.findtext('s:Size',namespaces=ns)),
                                   last_modified=item.findtext('s:LastModified',namespaces=ns)))
        if beyond or root.findtext('s:IsTruncated',namespaces=ns) != 'true':
            return dict(dataset=dataset, symbol=symbol, listed_files=result, pages=pages,
                        status='LISTING_SCANNED', endpoint=endpoint, params_prefix=prefix)
        token = root.findtext('s:NextContinuationToken', namespaces=ns)
        if not token or pages >= 4:
            raise ValueError('Listing could not establish bounded-window result')
        params = {'list-type':2, 'prefix':prefix, 'continuation-token':token}


def main():
    session = requests.Session()
    observations = []
    dates = (date(2024,10,7), date(2025,4,7), date(2026,4,7), END)
    for symbol in SYMBOLS:
        for dataset in ('bookDepth','bookTicker','liquidationSnapshot'):
            for day in dates:
                url = archive_url(symbol,dataset,day)
                time.sleep(1)
                response = session.head(url, timeout=(15,45))
                record = dict(market='um',symbol=symbol,dataset=dataset,day=str(day),url=url,
                              http_status=response.status_code,bytes=int(response.headers.get('Content-Length',0)),
                              observed_at=datetime.now(timezone.utc).isoformat())
                observations.append(record); print(json.dumps(record),flush=True)
                response.close()
    for symbol in SYMBOLS:
        for dataset in ('klines','trades','aggTrades'):
            for day in (START,date(2025,1,1),END):
                url = spot_url(symbol,dataset,day)
                time.sleep(1)
                response = session.head(url,timeout=(15,45))
                record = dict(market='spot',symbol=symbol,dataset=dataset,day=str(day),url=url,
                              http_status=response.status_code,bytes=int(response.headers.get('Content-Length',0)),
                              observed_at=datetime.now(timezone.utc).isoformat())
                observations.append(record); print(json.dumps(record),flush=True)
                response.close()
    listings = []
    for symbol in SYMBOLS:
        for dataset in ('bookTicker','liquidationSnapshot'):
            try:
                record = listed_window(session,dataset,symbol)
            except Exception as error:
                record = dict(symbol=symbol,dataset=dataset,status='LISTING_NOT_ESTABLISHED',error=str(error))
            listings.append(record)
            print(json.dumps({k:v for k,v in record.items() if k!='listed_files'},sort_keys=True),flush=True)
    atomic_json(Path('reports/extended_source_probes.json'),
                dict(generated_at=datetime.now(timezone.utc).isoformat(),head_probes=observations,listings=listings,
                     notice='HEAD/listing evidence only; 404 on one date does not prove historical impossibility'))


if __name__ == '__main__': main()
