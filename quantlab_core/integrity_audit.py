"""Read-only scientific coverage accounting; inherited receipts are not fresh restores."""
from collections import Counter, defaultdict
from datetime import date, timedelta
import re
import hashlib
import json

CORE = {'aggTrades':'um_aggTrades','trades':'um_trades','klines':'um_klines_1m',
        'markPriceKlines':'um_mark_price','indexPriceKlines':'um_index_price',
        'premiumIndexKlines':'um_premium_index','metrics':'um_metrics','fundingRate':'um_funding_settled'}
EXTENDED = {'um_individual_trades':'um_trades','spot_trades':'spot_trades',
            'spot_klines_1m':'spot_klines_1m','um_bookDepth_summary':'um_bookDepth_summary'}
DERIVED = {'basis_close_1m':'perpetual_basis','oi_change_5m':'oi_changes'}


def calendar(start,end):
    first=date.fromisoformat(start);last=date.fromisoformat(end)
    if last<first:raise ValueError('Reversed coverage window')
    return [str(first+timedelta(days=i)) for i in range((last-first).days+1)]


def ranges(days):
    ordered=sorted(set(days));result=[]
    for day in ordered:
        if result and date.fromisoformat(day)==date.fromisoformat(result[-1]['end'])+timedelta(days=1):
            result[-1]['end']=day;result[-1]['days']+=1
        else:result.append(dict(start=day,end=day,days=1))
    return result


def receipt_valid(obj, repository='Slimsyhalo/Trade'):
    if not isinstance(obj,dict):return False
    remote=obj.get('remote') or {};digest=obj.get('sha256');size=obj.get('bytes')
    return (isinstance(digest,str) and re.fullmatch(r'[0-9a-f]{64}',digest) is not None
            and type(size) is int and size>0 and isinstance(remote,dict)
            and type(remote.get('asset_id')) is int and remote['asset_id']>0
            and remote.get('api_url')==f'https://api.github.com/repos/{repository}/releases/assets/{remote["asset_id"]}'
            and isinstance(remote.get('verified_at'),(int,float)) and not isinstance(remote.get('verified_at'),bool)
            and remote['verified_at']>0 and remote.get('sha256')==digest and remote.get('bytes')==size)


def admitted(row,ledger):
    if ledger=='derived':return row.get('quality_state')=='VALIDATED' and row.get('deterministic_rebuild')=='PASS'
    if row.get('qa',{}).get('status')!='PASS':return False
    if ledger=='expansion' and row.get('kind')=='um_individual_trades':
        a=row.get('admission') or {};b=a.get('independent_bar_evidence') or {}
        return (a.get('state')=='VALIDATED' and a.get('raw_sha256')==row.get('raw',{}).get('sha256')
                and a.get('verification_bars_sha256')==row.get('verification_bars',{}).get('sha256')
                and b.get('bar_comparison_status')=='PASS' and b.get('difference_count')==0
                and a.get('symbol')==row.get('symbol') and a.get('day')==row.get('day'))
    return True


def objects(row,ledger):
    if ledger=='derived':return {'product':row}
    names=['raw','normalized']
    if ledger=='expansion' and row.get('kind')=='um_individual_trades':names.append('verification_bars')
    return {kind:row.get(kind) or {} for kind in names}


def dates_for(row):
    # Monthly observation membership, never inferred from the filename or bounds.
    if row.get('dataset')=='fundingRate':return row.get('qa',{}).get('observed_days',[])
    return [row.get('day')]


def audit_ledgers(ledgers,inventory,start='2024-10-07',end='2026-10-07',symbols=('BTCUSDT','ETHUSDT','SOLUSDT')):
    expected=set(calendar(start,end));groups=defaultdict(list);issues=[];unique={};counts=Counter()
    core_by_key={r['key']:r for r in ledgers.get('main',[])}
    for ledger,rows in ledgers.items():
        mapping={'main':CORE,'expansion':EXTENDED,'derived':DERIVED}.get(ledger,{})
        seen=set()
        for row in rows:
            key=row.get('key');kind=row.get('dataset') or row.get('kind') or (key.split('/')[1] if key and ledger=='derived' else None)
            ident=mapping.get(kind)
            if key in seen:raise ValueError('Duplicate partition key within immutable ledger: '+str(key))
            seen.add(key)
            if ident is None:
                issues.append(dict(ledger=ledger,key=key,reason='UNMAPPED_SOURCE'));continue
            obj=objects(row,ledger);storage=all(receipt_valid(x) for x in obj.values())
            quality=admitted(row,ledger);lineage=True
            if ledger=='derived':
                for source in row.get('inputs',{}).values():
                    current=core_by_key.get(source.get('key'),{})
                    if current.get('raw',{}).get('sha256')!=source.get('raw_sha256') or current.get('normalized',{}).get('sha256')!=source.get('normalized_sha256'):
                        lineage=False
                if not row.get('inputs'):lineage=False
                signature=hashlib.sha256(json.dumps(dict(version=row.get('transform_version'),inputs=row.get('inputs',{})),sort_keys=True,separators=(',',':')).encode()).hexdigest()
                if signature!=row.get('source_identity') or not str(key).endswith('/'+signature):lineage=False
                if not lineage:issues.append(dict(ledger=ledger,key=key,reason='SOURCE_VERSION_DIFFERENT_OR_NOT_IN_CURRENT_SNAPSHOT',source_main_sha=row.get('source_main_sha')))
            quarantine=(row.get('quality_state')=='QUARANTINED' or row.get('qa',{}).get('status') in ('FAIL','FAILED') or row.get('state')=='QUARANTINED')
            state='QUARANTINED' if quarantine else 'REMOTE_VERIFIED' if storage and quality and lineage else 'VALIDATED' if quality else 'ACQUIRED' if row.get('raw') else 'UNAVAILABLE' if row.get('http_status')==404 else 'NOT_VALIDATED'
            counts[state]+=1
            valid_dates=[]
            for day in dates_for(row):
                try:date.fromisoformat(day)
                except (TypeError,ValueError):issues.append(dict(ledger=ledger,key=key,reason='INVALID_OBSERVATION_DATE'));continue
                if day not in expected:issues.append(dict(ledger=ledger,key=key,reason='OUTSIDE_AUTHORIZED_WINDOW',day=day))
                else:valid_dates.append(day)
            if row.get('qa',{}).get('status')=='PASS' and not quality:issues.append(dict(ledger=ledger,key=key,reason='QA_PASS_WITHOUT_SOURCE_ADMISSION_CERTIFICATE'))
            if quality and not storage:issues.append(dict(ledger=ledger,key=key,reason='ADMITTED_WITHOUT_ALL_MATCHING_RECEIPTS'))
            for kind,value in obj.items():
                if receipt_valid(value):
                    digest=value['sha256']
                    if digest in unique and unique[digest]!=value['bytes']:raise ValueError('Same SHA-256 with inconsistent recorded size')
                    unique[digest]=value['bytes']
            groups[ident,row.get('symbol')].append(dict(ledger=ledger,row=row,state=state,storage=storage,quality=quality,lineage=lineage,dates=valid_dates))
    coverage=[]
    for ident in sorted(set(CORE.values())|set(EXTENDED.values())|set(DERIVED.values())):
        for symbol in symbols:
            entries=groups[ident,symbol];good=[x for x in entries if x['state']=='REMOTE_VERIFIED']
            covered=set(d for x in good for d in x['dates'])
            byday=defaultdict(set)
            for x in good:
                digest=(x['row'].get('raw') or x['row']).get('sha256')
                for day in x['dates']:byday[day].add(digest)
            conflicts=sorted(d for d,v in byday.items() if len(v)>1)
            coverage.append(dict(source_id=ident,symbol=symbol,expected_days=len(expected),admitted_remote_days=len(covered),
                                 first_admitted_day=min(covered,default=None),last_admitted_day=max(covered,default=None),
                                 covered_ranges=ranges(covered),missing_ranges=ranges(expected-covered),
                                 quarantined_days=ranges(d for x in entries if x['state']=='QUARANTINED' for d in x['dates']),
                                 partition_states=dict(Counter(x['state'] for x in entries)),
                                 conflicting_admitted_versions=conflicts,complete_calendar_membership=len(covered)==len(expected) and not conflicts,
                                 scientific_completeness_certified=False))
    mapped={x['source_id'] for x in coverage};inventory_rows=[]
    for row in inventory['datasets']:
        inventory_rows.append(dict(source_id=row['id'],family=row['family'],classification=row['classification'],selected=row['selected'],
                                   evidence_scope='PARTITION_LEDGER_AUDITED' if row['id'] in mapped else 'NOT_ASSESSED_BY_PARTITION_AUDIT',
                                   complete_requested_window_certified=False))
    return dict(schema_version='integrity-coverage-1',requested_window=dict(start=start,end_inclusive=end,days=len(expected),timezone='UTC'),
                phase_1_accepted=False,global_C21_accepted=False,milestone_states={f'C{i}':'NOT_ACCEPTED' for i in range(16,23)},
                partition_states=dict(counts),coverage=coverage,inventory_scope=inventory_rows,issues=issues,
                unique_receipt_objects=len(unique),unique_receipt_bytes=sum(unique.values()),
                notice='Coverage is membership of QA-admitted partitions with matching inherited full-readback receipts. No fresh remote-object check, lossless source guarantee, strict causal availability, continuous live service or global acceptance inferred. Original and derived records are never summed as executions. Monthly funding uses observed_days only. Legacy quarantines remain separate from source-tape admission. Missing dates are NOT_ACQUIRED, not proven source unavailability.')


def sample_plan(ledgers):
    """First/last admitted partition per ledger/source/symbol; deterministic, source-version bound."""
    groups=defaultdict(list)
    for ledger,rows in ledgers.items():
        for row in rows:
            if not admitted(row,ledger) or not all(receipt_valid(x) for x in objects(row,ledger).values()):continue
            kind=row.get('dataset') or row.get('kind') or row['key'].split('/')[1]
            groups[ledger,kind,row['symbol']].append(row)
    plan=[]
    for group,rows in sorted(groups.items()):
        ordered=sorted(rows,key=lambda r:(r['day'],r['key']))
        selected={r['key']:r for r in (ordered[0],ordered[-1])}
        for row in selected.values():
            for kind,value in objects(row,group[0]).items():
                plan.append(dict(ledger=group[0],dataset=group[1],symbol=group[2],partition_key=row['key'],object_kind=kind,
                                 sha256=value['sha256'],bytes=value['bytes'],remote=value['remote'],
                                 expected_rows=row.get('rows') if group[0]=='derived' else row.get('qa',{}).get('rows') if kind=='normalized' else None,
                                 source_identity=row.get('source_identity') if group[0]=='derived' else None))
    return plan
