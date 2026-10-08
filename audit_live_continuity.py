"""Full-file read-only audit of a captured session; no full-L2 or uptime inference."""
from collections import Counter
from datetime import datetime,timezone
from decimal import Decimal,InvalidOperation
import gzip
import json
from pathlib import Path
import subprocess
import time
from quantlab_core.io import atomic_json,sha256
from quantlab_core.integrity_audit import receipt_valid


def inspect_route(root,records):
    kinds=Counter();streams=Counter();symbols=Counter();diagnostics=Counter();sequence={};examples=[];segments=[]
    previous_receive=None;first=None;last=None;maximum=None;clock_min=None;clock_max=None
    def flag(kind,details):
        diagnostics[kind]+=1
        if len(examples)<25:examples.append(dict(kind=kind,**details))
    for record in sorted(records,key=lambda r:(r['first_receive_ns'],r['path'])):
        if Path(record['path']).name!=record['path']:raise ValueError('Unsafe captured filename')
        if not receipt_valid(record):raise ValueError('Full matching remote receipt required for captured segment')
        path=root/record['path']
        if sha256(path)!=record['sha256'] or path.stat().st_size!=record['bytes']:raise ValueError('Captured segment differs from immutable ledger')
        rows=0;segment_first=None;segment_last=None
        with gzip.open(path,'rt',encoding='utf-8') as source:
            for line in source:
                row=json.loads(line);stamp=row.get('receive_timestamp_ns');kind=row.get('kind');payload=row.get('payload')
                if type(stamp) is not int or stamp<0 or not isinstance(kind,str) or not isinstance(payload,dict):raise ValueError('Invalid captured envelope')
                if segment_first is None:segment_first=stamp
                segment_last=stamp;rows+=1;kinds[kind]+=1
                if first is None:first=stamp
                last=stamp
                if previous_receive is not None and stamp<previous_receive:flag('receive_clock_regression',dict(before_ns=previous_receive,after_ns=stamp))
                previous_receive=stamp;maximum=stamp if maximum is None else max(maximum,stamp)
                if kind!='event':continue
                stream=payload.get('stream');data=payload.get('data')
                if not isinstance(stream,str) or not isinstance(data,dict):flag('malformed_event_envelope',dict(receive_ns=stamp));continue
                streams[stream]+=1;symbol=data.get('s');symbols[str(symbol)]+=1;event=data.get('e')
                exchange_time=data.get('E')
                if type(exchange_time) is int:
                    delta=stamp-exchange_time*1_000_000
                    clock_min=delta if clock_min is None else min(clock_min,delta)
                    clock_max=delta if clock_max is None else max(clock_max,delta)
                if event in ('depthUpdate','aggTrade'):
                    required=('U','u','pu') if event=='depthUpdate' else ('a',)
                    topic='depth' if event=='depthUpdate' else 'aggTrade'
                    base=str(symbol).lower()+'@'+topic
                    allowed=(base,base+'@100ms',base+'@500ms') if event=='depthUpdate' else (base,)
                    if stream not in allowed or any(type(data.get(k)) is not int or data[k]<0 for k in required):
                        flag('malformed_sequence',dict(stream=stream,receive_ns=stamp));continue
                    current=data['u'] if event=='depthUpdate' else data['a']
                    if event=='depthUpdate' and (data['U']>current or data['pu']>current):flag('malformed_sequence',dict(stream=stream,receive_ns=stamp));continue
                    before=sequence.get(stream)
                    if before is not None and current<=before:flag('duplicate_or_old_sequence',dict(stream=stream,previous=before,current=current));continue
                    if before is not None:
                        if event=='depthUpdate' and data['pu']!=before:flag('depth_sequence_gap',dict(stream=stream,previous_u=before,pu=data['pu'],u=current,receive_ns=stamp))
                        if event=='aggTrade' and current!=before+1:flag('aggregate_identifier_gap',dict(stream=stream,previous=before,current=current,receive_ns=stamp))
                    sequence[stream]=current
                elif event=='bookTicker':
                    try:
                        bid,ask,bq,aq=[Decimal(data[k]) for k in ('b','a','B','A')]
                        if any(not x.is_finite() for x in (bid,ask,bq,aq)) or min(bid,ask)<=0 or min(bq,aq)<0:raise ValueError('Invalid displayed quote')
                        if ask<bid:flag('crossed_displayed_quote',dict(stream=stream,receive_ns=stamp,bid=str(bid),ask=str(ask)))
                    except (KeyError,InvalidOperation,ValueError,TypeError):flag('invalid_displayed_quote',dict(stream=stream,receive_ns=stamp))
        if rows!=record['rows'] or segment_first!=record['first_receive_ns'] or segment_last!=record['last_receive_ns']:raise ValueError('Captured rows/receive boundaries differ from immutable ledger')
        segments.append(dict(path=record['path'],sha256=record['sha256'],rows=rows,first_receive_ns=segment_first,last_receive_ns=segment_last,state='READ_AND_TESTED'))
    return dict(segments=len(segments),rows=sum(x['rows'] for x in segments),kinds=dict(kinds),streams=dict(streams),symbols=dict(symbols),
                first_receive_ns=first,last_receive_ns=last,maximum_receive_ns=maximum,
                observed_span_seconds=(maximum-first)/1e9 if first is not None else None,
                sequence_diagnostics=dict(diagnostics),diagnostic_examples=examples,final_sequence_state=sequence,
                recorded_sequence_markers={k:kinds[k] for k in ('sequence_gap','trade_gap','duplicate_or_old','malformed_event')},
                uncalibrated_receive_minus_exchange_E_ns=dict(min=clock_min,max=clock_max,network_latency_certified=False),
                segment_inspections=segments,continuous_operation_certified=False,full_L2_book_certified=False,
                notice='Span is first-to-last recorded receive time, not continuous coverage. Sequence gaps and duplicates are observations, not automatic proof of source loss or reconstructible L2. Cross-reconnect boundaries remain unverified even when identifiers appear continuous. Exchange/local clock difference is not calibrated network latency. Snapshot marker counts do not prove usable depth snapshots.')


def run(root,ledger_sha,capture_id,output):
    started=time.monotonic();cpu=time.process_time();routes={}
    for route in ('public','market','snapshots'):
        path=f'catalog/live_recovery/{capture_id}/{route}-manifest.json'
        records=json.loads(subprocess.check_output(['git','show',ledger_sha+':'+path],text=True))
        routes[route]=inspect_route(Path(root),records)
    report=dict(schema_version='live-continuity-audit-1',status='FULL_CAPTURE_FILES_READ_AND_TESTED',
                observed_at=datetime.now(timezone.utc).isoformat(),source_ledger_sha=ledger_sha,capture_id=capture_id,
                source_code_files_sha256={'audit_live_continuity.py':sha256(Path(__file__))},
                source_artifact_id=11565318990,source_run_id=37795816483,
                all_captured_segments=len([s for r in routes.values() for s in r['segment_inspections']]),
                all_captured_rows=sum(r['rows'] for r in routes.values()),routes=routes,
                elapsed_seconds=round(time.monotonic()-started,3),process_cpu_seconds=round(time.process_time()-cpu,3),
                effective_codex_work_seconds=None,phase_1_accepted=False,C20_accepted=False,
                continuous_operation_certified=False,full_L2_book_certified=False,
                restoration_scope='Existing preserved original failed-run artifact; each segment hash/bytes bound to completed immutable recovery ledger. No fresh remote download of every segment inferred.')
    atomic_json(output,report);return report


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--ledger-sha',required=True)
    p.add_argument('--capture-id',default='37795816483-1');p.add_argument('--output',type=Path,required=True)
    args=p.parse_args();run(args.root,args.ledger_sha,args.capture_id,args.output)
