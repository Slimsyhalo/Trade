from datetime import date
import json
from pathlib import Path

import pytest
import acquire_extended as module
from quantlab_core.io import sha256
from remote_extended import remote_verified


def archived(tmp_path):
    assets={}
    payloads={}
    for kind,data in [('raw',b'original tape'),('normalized',b'original parquet'),('verification_bars',b'official bars')]:
        digest=__import__('hashlib').sha256(data).hexdigest()
        payloads[digest]=data
        assets[kind]=dict(path=str(tmp_path/kind),sha256=digest,bytes=len(data),
                          remote=dict(sha256=digest,bytes=len(data),verified_at=1,api_url='fixture'))
    row=dict(key='BTCUSDT/um_individual_trades/2024-10-07',state='VALIDATED',source='fixture',**assets)
    manifest=tmp_path/'manifest.json';manifest.write_text(json.dumps({row['key']:row}))
    return row,manifest,payloads


def test_resume_restores_exact_bar_certificate_as_well_as_tape(tmp_path):
    row,manifest,payloads=archived(tmp_path)
    calls=[]
    class Remote:
        def restore(self,receipt,path,budget):
            calls.append(receipt['sha256']);path.write_bytes(payloads[receipt['sha256']])
    result=module.acquire('um_individual_trades','BTCUSDT',date(2024,10,7),
                          root=tmp_path,manifest=manifest,materialize=True,remote=Remote())
    assert len(calls)==3 and result==row
    assert remote_verified(result)


def test_resume_changed_bar_certificate_fails_closed(tmp_path):
    row,manifest,payloads=archived(tmp_path)
    class Remote:
        def restore(self,receipt,path,budget):
            path.write_bytes(b'changed' if path.name=='verification_bars' else payloads[receipt['sha256']])
    with pytest.raises(ValueError,match='missing/changed'):
        module.acquire('um_individual_trades','BTCUSDT',date(2024,10,7),
                       root=tmp_path,manifest=manifest,materialize=True,remote=Remote())


def test_tape_receipts_without_verified_bar_evidence_not_skipped(tmp_path):
    row,_,_=archived(tmp_path)
    assert remote_verified(row)
    row['verification_bars']['remote']=None
    assert not remote_verified(row)
