"""Observe every latest core group and initial individual tapes, without downloads."""
from collections import Counter
from datetime import datetime,timezone
import argparse,json,subprocess,time
from pathlib import Path
from quantlab_core.io import HTTP,atomic_json
from quantlab_core.source_versions import observe_version


def select_records(main_sha,expansion_sha):
    core=[json.loads(x) for x in subprocess.check_output(['git','show',main_sha+':manifest.jsonl'],text=True).splitlines()]
    latest={r['key']:r for r in core};groups={}
    for r in latest.values():
        if r.get('status')!='PASS':continue
        key=(r['symbol'],r['dataset'])
        if key not in groups or r['day']>groups[key]['day']:groups[key]=r
    extension=json.loads(subprocess.check_output(['git','show',expansion_sha+':catalog/extended_manifest.json'],text=True))
    for symbol in ('BTCUSDT','ETHUSDT','SOLUSDT'):
        r=extension.get(symbol+'/um_individual_trades/2024-10-07')
        if r:
            r=dict(r);r['source']=r.get('source') or r.get('source_url')
            if not r['source']:raise ValueError('Missing explicit official individual-tape source URL')
            groups[symbol,'initial_individual_trade']=r
    return list(groups.values())


def run_audit(main_sha,expansion_sha,output):
    started=time.monotonic();http=HTTP(interval=.5,attempts=2)
    records=select_records(main_sha,expansion_sha)
    report=dict(schema_version=1,scope='Latest admitted date of each core group, plus original three admitted individual tapes; sampled source-version watch only',
                evidence_commits=dict(main=main_sha,expansion=expansion_sha),started_at=datetime.now(timezone.utc).isoformat(),
                phase_1_accepted=False,full_source_revision_history_certified=False,observations=[])
    for record in records:
        report['observations'].append(observe_version(record,http));atomic_json(output,report)
    report.update(states=dict(Counter(x['state'] for x in report['observations'])),elapsed_seconds=round(time.monotonic()-started,3),
                  observed_at=datetime.now(timezone.utc).isoformat())
    atomic_json(output,report)
    return report


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--main-sha',required=True);p.add_argument('--expansion-sha',required=True);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();report=run_audit(args.main_sha,args.expansion_sha,args.output)
    print(json.dumps({k:v for k,v in report.items() if k!='observations'},indent=2))
