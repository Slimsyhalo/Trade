import subprocess
import pytest
import remote_live


def simulate(monkeypatch, outcomes):
    calls=[];pending=iter(outcomes)
    def run(args, **kwargs):
        calls.append(args)
        code,out,err=next(pending)
        return subprocess.CompletedProcess(args,code,out,err)
    monkeypatch.setattr(remote_live.subprocess,'run',run)
    monkeypatch.setattr(remote_live.time,'sleep',lambda _:None)
    return calls


def test_transient_rejection_retries_identical_commit_without_force(monkeypatch):
    calls=simulate(monkeypatch,[(1,'','remote rejected (failed)'),(0,'parent\trefs/heads/codex/test\n',''),(0,'','')])
    remote_live.push_checkpoint('codex/test','parent','new')
    assert calls[0]==calls[2]
    assert all('--force' not in c for c in calls)


def test_external_writer_stops_without_second_push(monkeypatch):
    calls=simulate(monkeypatch,[(1,'','remote rejected'),(0,'someone_else\trefs/heads/codex/test\n','')])
    with pytest.raises(RuntimeError,match='changed externally'):
        remote_live.push_checkpoint('codex/test','parent','new')
    assert len(calls)==2


def test_lost_acknowledgement_recognizes_already_published_commit(monkeypatch):
    calls=simulate(monkeypatch,[(1,'','transport closed'),(0,'new\trefs/heads/codex/test\n','')])
    remote_live.push_checkpoint('codex/test','parent','new')
    assert len(calls)==2


def test_unreadable_remote_stops_safely(monkeypatch):
    simulate(monkeypatch,[(1,'','remote rejected'),(1,'','network unavailable')])
    with pytest.raises(RuntimeError,match='Cannot verify'):
        remote_live.push_checkpoint('codex/test','parent','new')
