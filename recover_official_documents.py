"""Preserve the exact legally acquired official documents without re-fetching.

Small immutable bootstrap transfer only. Releases remain canonical storage.
Every container/member is hashed; restoration validates all original documents.
No blocked provider requests, proxy, credential transfer or vintage inference.
"""
from datetime import datetime,timezone
import gzip
import hashlib
import io
import json
import os
from pathlib import Path,PurePosixPath
import subprocess
import zipfile

from quantlab_core.context_events import parse_release
from quantlab_core.io import atomic_json,Budget,sha256
from remote_extended import ExpansionRemote
from remote_live import commit_checkpoint


def verify_container(path,spec,records):
    if Path(path).stat().st_size!=spec['bundle_bytes'] or sha256(path)!=spec['bundle_sha256']:raise ValueError('Bootstrap container hash/size mismatch')
    expected={r['name']:r for r in spec['expected_members']}
    if len(expected)!=len(spec['expected_members']):raise ValueError('Duplicate expected members')
    verified=[]
    with zipfile.ZipFile(path) as archive:
        names=archive.namelist()
        if len(names)!=len(set(names)) or set(names)!=set(expected):raise ValueError('Unexpected/duplicate document bundle members')
        for name in names:
            p=PurePosixPath(name)
            if p.is_absolute() or '..' in p.parts or p.as_posix()!=name:raise ValueError('Unsafe document archive path')
            item=expected[name]
            if archive.getinfo(name).file_size!=item['bytes']:raise ValueError('Archive member size mismatch')
            body=archive.read(name) # includes ZIP CRC check, bounded recorded size
            if hashlib.sha256(body).hexdigest()!=item['sha256']:raise ValueError('Member SHA-256 mismatch')
            if item['kind']=='raw':
                record=records[item['key']];original=gzip.decompress(body);metadata=record['metadata']
                if len(original)!=metadata['source_original_bytes'] or hashlib.sha256(original).hexdigest()!=metadata['source_document_sha256']:raise ValueError('Original HTML differs after restoration')
                parsed=parse_release(original.decode('utf-8',errors='replace'),metadata['kind'],metadata['event_date'])
                if parsed['original_publication_claim_utc']!=metadata['original_publication_claim_utc']:raise ValueError('Restored original publication header differs')
            elif item['kind']=='normalized':
                metadata=json.loads(body)
                if metadata!=records[item['key']]['metadata']:raise ValueError('Restored normalized provenance differs')
                if metadata['historical_effective_availability_utc'] is not None or metadata['strict_historical_replay_eligible']:raise ValueError('Uncertified historical availability was relabeled')
            verified.append(dict(name=name,sha256=item['sha256'],bytes=item['bytes'],state='RESTORED_AND_TESTED'))
    return verified


def assemble(spec,out,budget):
    out=Path(out);out.parent.mkdir(parents=True,exist_ok=True)
    if out.exists():
        if sha256(out)!=spec['bundle_sha256']:raise ValueError('Existing immutable bootstrap differs')
        return
    budget.check(spec['bundle_bytes']);temp=out.with_suffix('.zip.part')
    try:
        with temp.open('xb') as target:
            for part in spec['parts']:
                source=Path(part['path'])
                if sha256(source)!=part['sha256'] or source.stat().st_size!=part['bytes']:raise ValueError('Git handoff part differs')
                target.write(source.read_bytes())
            target.flush();os.fsync(target.fileno())
        if sha256(temp)!=spec['bundle_sha256']:raise ValueError('Assembled bundle differs')
        os.replace(temp,out)
    finally:temp.unlink(missing_ok=True)


def main():
    branch=os.environ['RECOVERY_LEDGER_BRANCH'];spec_path=Path('bootstrap/context-transfer/manifest.json');spec=json.loads(spec_path.read_text())
    manifest=Path('catalog/document_recovery/manifest.json');records=json.loads(manifest.read_text())
    report_path=Path('reports/document_recovery.json');budget=Budget(Path('data'),2)
    source=Path('data/document_recovery/originals.zip');assemble(spec,source,budget)
    preflight=verify_container(source,spec,records)
    remote=ExpansionRemote('Slimsyhalo/Trade',interval=15,attempts=2,release_body=
                          'Exact official BLS and Federal Reserve release documents acquired lawfully from their public archives; immutable original bytes and provenance. Source/member hashes in catalog/document_recovery. Historical vintage/dissemination remains uncertified. Git bootstrap is a small one-off transfer; canonical data are this Release asset.')
    receipt=remote.put(source,'official-research-documents-2024-2026')
    report=dict(status='REMOTE_VERIFIED',source_commit_sha=os.environ['CHECKPOINT_SOURCE_SHA'],
                workflow_url='https://github.com/Slimsyhalo/Trade/actions/runs/'+os.environ['GITHUB_RUN_ID'],
                timestamp_utc=datetime.now(timezone.utc).isoformat(),container=receipt,
                verified_members=len(preflight),official_documents=len(records),historical_vintage_certified=False,
                historical_effective_availability_certified=False,phase_1_accepted=False)
    atomic_json(report_path,report)
    commit_checkpoint([report_path],branch,'C21 exact official-document container: full remote readback')
    # Independent restoration into an absent destination, not the Git bootstrap.
    restored=Path('data/restored/document_recovery/originals.zip')
    remote.restore(receipt,restored,budget)
    verified=verify_container(restored,spec,records)
    for record in records.values():
        record.update(storage_state='REMOTE_VERIFIED',restoration_state='RESTORED_AND_TESTED',
                      container_ref=dict(remote=receipt,raw_member=str(Path(record['raw']['path']).relative_to('data/context')),
                                         normalized_member=str(Path(record['normalized']['path']).relative_to('data/context'))))
    report.update(status='ALL_DOCUMENT_MEMBERS_RESTORED_AND_TESTED',restored_members=verified,
                  completed_at_utc=datetime.now(timezone.utc).isoformat(),
                  notice='All 109 captured documents and their metadata plus five discovery originals independently restored. Does not certify full market foundation or historical original-content vintage.')
    atomic_json(manifest,records);atomic_json(report_path,report)
    commit_checkpoint([manifest,report_path],branch,'C21 restored every official document and metadata member with hashes')
    # Prune transfer working-tree files only after two durable publication receipts.
    # Git history keeps the small transfer; this is no migration of market tapes.
    subprocess.run(['git','rm','--',*[p['path'] for p in spec['parts']]],check=True)
    spec['handoff_status']='RETIRED_AFTER_REMOTE_READBACK_AND_FULL_RESTORE'
    spec['canonical_container']=receipt;atomic_json(spec_path,spec)
    commit_checkpoint([spec_path],branch,'C21 retire small bootstrap transfer after certified release recovery')
    source.unlink();restored.unlink()


if __name__=='__main__':main()
