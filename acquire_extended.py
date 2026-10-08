"""Bounded samples and resumable, separately manifested archive expansion."""
from datetime import date,datetime,timezone
import argparse
import json
from pathlib import Path

from probe_extended_sources import spot_url
from quantlab_core.extended_archive import normalize_extended
from quantlab_core.io import HTTP,Budget,atomic_json,sha256
from quantlab_core.sources import archive_url,checksum_text,SYMBOLS
from quantlab_core.normalize import normalize
from quantlab_core.trade_admission import admit_individual_tape


def acquire(kind,symbol,day,root=Path('data/extended'),manifest=Path('catalog/extended_manifest.json'),*,materialize=False,remote=None):
    if kind not in ('spot_trades','spot_klines_1m','um_bookDepth_summary','um_individual_trades'):raise ValueError('Unsupported source')
    day=date.fromisoformat(str(day));dataset='bookDepth' if kind=='um_bookDepth_summary' else 'trades' if kind in ('spot_trades','um_individual_trades') else 'klines'
    url=archive_url(symbol,dataset,day) if kind.startswith('um_') else spot_url(symbol,dataset,day)
    records=json.loads(manifest.read_text()) if manifest.exists() else {}
    key=f'{symbol}/{kind}/{day}';existing=records.get(key)
    if existing and existing.get('state') in ('VALIDATED','QUARANTINED','REMOTE_VERIFIED'):
        # Verify retained local files before skipping; archived-only remote records are
        # handled by the publisher/restore layer, never silently regenerated here.
        budget=Budget(root,2)
        if materialize:
            # Recover the exact source version recorded by the ledger, not a
            # newly revised version at the same public URL. Wrong SHA stops.
            raw=Path(existing['raw']['path']);out=Path(existing['normalized']['path'])
            if not raw.exists():
                receipt=existing['raw'].get('remote')
                if receipt and remote:remote.restore(receipt,raw,budget)
                else:HTTP(interval=1).download(existing['source'],raw,budget,expected=existing['raw']['sha256'])
            if not out.exists():
                receipt=existing['normalized'].get('remote')
                if receipt and remote:remote.restore(receipt,out,budget)
                elif kind=='um_individual_trades':normalize(raw,out,'trades',symbol,day,budget)
                else:normalize_extended(raw,out,kind,symbol,day,budget)
            evidence=existing.get('verification_bars')
            if evidence:
                path=Path(evidence['path'])
                if not path.exists():
                    receipt=evidence.get('remote')
                    if receipt and remote:remote.restore(receipt,path,budget)
                    else:HTTP(interval=1).download(evidence['source'],path,budget,expected=evidence['sha256'])
        assets=('raw','normalized','verification_bars') if existing.get('verification_bars') else ('raw','normalized')
        for asset in assets:
            p=Path(existing[asset]['path'])
            if (not p.is_file() or sha256(p)!=existing[asset]['sha256']
                    or p.stat().st_size!=existing[asset]['bytes']):
                raise ValueError('Existing local acquisition missing/changed; restore first')
        return existing
    http=HTTP(interval=1);budget=Budget(root,2)
    response=http.get(url+'.CHECKSUM')
    try: checksum=response.text
    finally:response.close()
    digest=checksum_text(checksum,url.rsplit('/',1)[-1])
    raw=root/'raw'/symbol/kind/(str(day)+'-'+digest[:16]+'.zip')
    out=root/'normalized'/symbol/kind/(str(day)+'-'+digest[:16]+'.parquet')
    record=dict(key=key,kind=kind,symbol=symbol,day=str(day),source=url,source_checksum=checksum,
                downloaded_at=datetime.now(timezone.utc).isoformat(),state='ACQUIRED',qa=None,
                raw={'path':str(raw),'sha256':digest},source_terms_ref='DATA_LICENSE.md',schema_version='extended-1')
    http.download(url,raw,budget,expected=digest);record['raw']['bytes']=raw.stat().st_size
    records[key]=record;atomic_json(manifest,records)
    try:
        if out.exists():raise ValueError('Interrupted normalized output retained; explicit reconciliation needed')
        if kind=='um_individual_trades':
            original=normalize(raw,out,'trades',symbol,day,budget)
            bar_url=archive_url(symbol,'klines',day);response=http.get(bar_url+'.CHECKSUM')
            try:bar_checksum=response.text
            finally:response.close()
            bar_digest=checksum_text(bar_checksum,bar_url.rsplit('/',1)[-1])
            bar_path=root/'verification'/symbol/(str(day)+'-'+bar_digest[:16]+'.zip')
            http.download(bar_url,bar_path,budget,expected=bar_digest)
            admission=admit_individual_tape(raw,bar_path,symbol,day,original)
            record.update(admission=admission,verification_bars=dict(path=str(bar_path),sha256=bar_digest,bytes=bar_path.stat().st_size,source=bar_url,source_checksum=bar_checksum),schema_version='1')
            qa=dict(original,state=admission['state'],status='PASS' if admission['state']=='VALIDATED' else 'FAILED',
                    id_continuity_policy='Not required for official market tape only when independent full-minute consistency certificate passes; original ID gaps retained')
        else:qa=normalize_extended(raw,out,kind,symbol,day,budget)
        record.update(qa=qa,state=qa['state'],normalized=dict(path=str(out),sha256=sha256(out),bytes=out.stat().st_size))
    except Exception as error:
        record.update(state='QUARANTINED',error_type=type(error).__name__,error=str(error))
        raise
    finally:
        records[key]=record;atomic_json(manifest,records)
    return record


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--kind',required=True,choices=['spot_trades','spot_klines_1m','um_bookDepth_summary','um_individual_trades']);p.add_argument('--symbol',required=True,choices=SYMBOLS);p.add_argument('--day',required=True)
    a=p.parse_args();r=acquire(a.kind,a.symbol,a.day);print(json.dumps(r))
