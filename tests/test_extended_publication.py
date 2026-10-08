from datetime import date
import json
from pathlib import Path
import shutil
import pyarrow as pa
import pyarrow.parquet as pq
import pytest
import remote_extended as module
from quantlab_core.io import sha256


def setup(tmp_path,monkeypatch,fail_checkpoint):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv('EXPANSION_LEDGER_BRANCH','codex/test')
    monkeypatch.setenv('CHECKPOINT_SOURCE_SHA','source')
    monkeypatch.setenv('GITHUB_RUN_ID','1')
    raw=tmp_path/'raw.zip';raw.write_bytes(b'quarantined source remains immutable')
    norm=tmp_path/'normalized.parquet';pq.write_table(pa.table({'value':[1]}),norm)
    row=dict(key='BTCUSDT/um_bookDepth_summary/2024-10-07',state='QUARANTINED',qa={'rows':1},
             raw={'path':str(raw),'sha256':sha256(raw),'bytes':raw.stat().st_size},
             normalized={'path':str(norm),'sha256':sha256(norm),'bytes':norm.stat().st_size})
    class Remote:
        rate_events=[]
        def __init__(self,*a,**kw):pass
        def put(self,path,tag):return dict(verified_at=1,sha256=sha256(path),bytes=Path(path).stat().st_size,api_url=str(path))
        def restore(self,record,path,budget):
            path.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(record['api_url'],path)
    monkeypatch.setattr(module,'ExpansionRemote',Remote)
    monkeypatch.setattr(module,'jobs',lambda pilot:iter([('BTCUSDT','um_bookDepth_summary',date(2024,10,7))]))
    monkeypatch.setattr(module,'acquire',lambda *a,**kw:row)
    monkeypatch.setattr(module,'preserve_diagnostics',lambda *a:None)
    calls=[]
    def checkpoint(*args):
        calls.append(args)
        if fail_checkpoint and len(calls)>1:raise RuntimeError('Git push rejected')
    monkeypatch.setattr(module,'commit_checkpoint',checkpoint)
    return raw,norm


def test_git_checkpoint_failure_retains_original_assets(tmp_path,monkeypatch):
    raw,norm=setup(tmp_path,monkeypatch,True)
    with pytest.raises(RuntimeError,match='Git push rejected'):module.main(pilot=True)
    assert raw.is_file() and norm.is_file()


def test_remote_verification_preserves_quality_quarantine(tmp_path,monkeypatch):
    raw,norm=setup(tmp_path,monkeypatch,False);module.main(pilot=True)
    row=next(iter(json.loads(Path('catalog/extended_manifest.json').read_text()).values()))
    assert row['state']=='QUARANTINED' and row['storage_state']=='REMOTE_VERIFIED'
    report=json.loads(Path('reports/extended_execution.json').read_text())
    assert report['validated_remote_partitions']==0 and report['quarantined_remote_partitions']==1
    assert not raw.exists() and not norm.exists()
