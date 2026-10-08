"""Hosted source-version probes and schema evidence from a restored derived file."""
from datetime import datetime,timezone
import json,os,subprocess,time
from pathlib import Path
import pyarrow.parquet as pq
from audit_source_versions import run_audit
from source_foundation import manifest_snapshot
from quantlab_core.io import atomic_json,Budget
from quantlab_core.normalize import FIELDS,schema_for
from quantlab_core.extended_archive import schema_for as extended_schema
from remote_extended import ExpansionRemote
from remote_live import commit_checkpoint

UNITS=dict(event_time_ms='UTC epoch milliseconds',available_at_ms='UTC epoch milliseconds; nullable',event_time_us='UTC epoch microseconds',available_at_us='UTC epoch microseconds; nullable',window_start_us='UTC epoch microseconds',window_end_us='UTC epoch microseconds',receive_timestamp_ns='local Unix UTC nanoseconds; uncalibrated application receipt',trade_id='exchange source identifier',agg_trade_id='exchange aggregate identifier',first_trade_id='exchange identifier',last_trade_id='exchange identifier',quantity='base asset',volume='base asset',depth='cumulative base asset quantity at percentage band',notional='cumulative quote notional at percentage band',percentage='signed percentage distance band; not a price level',quote_quantity='quote asset',quote_volume='quote asset',taker_buy_base_volume='base asset',taker_buy_quote_volume='quote asset',number_of_trades='count',source_rows='count',buy_base_volume='base asset',sell_base_volume='base asset',total_base_volume='base asset',volume_delta='base asset',cvd='base asset from explicit anchor',cvd_initial='base asset',price_quantity_notional='quote asset',vwap_numerator='quote asset',vwap_denominator='base asset',vwap='quote per base asset',vwap_decimal_precision='decimal significant digits',volume_at_price_json='ordered [exact price string, base quantity string] pairs')
POLICIES={
    'core_futures':'Original timestamps milliseconds, exact numeric lexemes retained. Mark/index OHLC is quote/base price; premium OHLC is signed dimensionless ratio. Placeholder volumes/counts are not executions.',
    'spot':'Original timestamps and source_time_unit retained: milliseconds before 2025-01-01, microseconds from that date. event_time_us is exact normalized UTC; bar-close availability is an assumption.',
    'percentage_depth':'UTC text seconds mapped to integer microseconds; signed cumulative percentage bands are not L2 price levels or synchronized snapshots. Staleness and completeness require separate QA.',
    'flow':'Exact decimal strings; 50 significant-digit HALF_EVEN VWAP with numerator/denominator. Explicit UTC partition CVD reset. Output availability cannot precede window closure or contributing input availability; historical receipt remains uncertified.',
    'live':'JSONL gzip envelope: receive_timestamp_ns integer, kind string, payload original parsed object. E/T exchange milliseconds where present; U/u/pu quote/depth identifiers unchanged. Connection and continuity markers retained; local clock regressions never silently reordered. Raw messages do not certify synchronized L2.',
    'context':'context-1 retains source URL/hash, publication claim, original timezone/DST label and observed acquisition time. Historical effective availability is null and original historical vintage is uncertified. Empty revision lineage does not prove no revisions.',
    'nullability':'Arrow storage nullability is distinct from QA. Unknown availability is retained as null; no zero-filled missing observations or universal continuity rules.'}


def entry(schema):
    return dict(fields=[dict(name=f.name,storage_type=str(f.type),storage_nullable=f.nullable,
                              unit=UNITS.get(f.name,'See dataset-specific semantic policy'),
                              qa_null_policy='unknown availability retained; never zero-filled' if f.name.startswith('available_at') else 'See source/transform admission policy') for f in schema],
                arrow_metadata={k.decode():v.decode() for k,v in (schema.metadata or {}).items()})


def main():
    started=time.monotonic();cpu=time.process_time()
    branch=os.environ['SOURCE_AUDIT_BRANCH']
    heads={k:subprocess.check_output(['git','rev-parse','origin/'+v],text=True).strip() for k,v in (
        ('main','main'),('expansion','codex/c17-archive-expansion'))}
    report_path=Path('reports/source_version_observations.json')
    probe=run_audit(heads['main'],heads['expansion'],report_path)
    source_sha='4247fbf96f931eee9106415bd50977c3f0b908f3'
    flow=json.loads(subprocess.check_output(['git','show',source_sha+':catalog/flow_manifest.json'],text=True))
    row=next(x for x in flow if x['symbol']=='BTCUSDT')
    if row['storage_state']!='REMOTE_VERIFIED' or row['restoration_state']!='RESTORED_AND_TESTED':
        raise ValueError('Restored derived schema evidence required')
    remote=ExpansionRemote('Slimsyhalo/Trade',interval=15,attempts=2)
    target=Path('data/restored/schema')/(row['normalized']['sha256']+'.parquet')
    remote.restore(row['normalized']['remote'],target,Budget(Path('data'),2))
    schema=pq.read_schema(target)
    if pq.read_metadata(target).num_rows!=1440:raise ValueError('Schema source row count differs')
    registry=dict(schema_version='research-schema-registry-1',classification='SCHEMA_EVIDENCE_NOT_COVERAGE_CERTIFICATE',timezone='UTC; original publisher timezone/DST retained',schemas={},semantic_policies=POLICIES)
    for dataset in FIELDS:registry['schemas'][dataset]=entry(schema_for(dataset))
    for dataset in ('spot_trades','spot_klines_1m','um_bookDepth_summary'):registry['schemas'][dataset]=entry(extended_schema(dataset))
    registry['schemas']['tape-flow-1']=entry(schema)
    registry['flow_schema_evidence']=dict(source_commit_sha=source_sha,derived_parquet_sha256=row['normalized']['sha256'],derived_rows=1440,restore_state='RESTORED_AND_TESTED')
    atomic_json(Path('catalog/schema_registry.json'),registry)
    lines=['# Extended scientific storage schemas','','Generated from implemented normalizers and a remotely restored hash-bound flow Parquet. Schema evidence does not certify acquired coverage. Original futures field meanings remain in DATA_DICTIONARY.md.','']
    for kind,policy in POLICIES.items():lines.extend(['## '+kind,'',policy,''])
    for kind,value in registry['schemas'].items():
        lines.extend(['## '+kind,'','| Field | Storage type | Unit | Storage nullable |','|---|---|---|---|'])
        for field in value['fields']:lines.append('| '+field['name']+' | '+field['storage_type']+' | '+field['unit']+' | '+str(field['storage_nullable'])+' |')
        lines.append('')
    dictionary=Path('docs/EXTENDED_DATA_DICTIONARY.md');dictionary.write_text('\n'.join(lines)+'\n')
    snapshot,_=manifest_snapshot(Path('.'),heads['main']);atomic_json(Path('reports/source_watch_main_snapshot.json'),snapshot)
    status='SAMPLED_SOURCE_VERSIONS_UNCHANGED_SCHEMA_RESTORED' if probe['states']=={'UNCHANGED_AT_OBSERVATION':21} else 'SOURCE_WATCH_ALERT_REVIEW_REQUIRED'
    evidence=dict(status=status,source_commit_sha=os.environ['CHECKPOINT_SOURCE_SHA'],workflow_url='https://github.com/Slimsyhalo/Trade/actions/runs/'+os.environ['GITHUB_RUN_ID'],timestamp_utc=datetime.now(timezone.utc).isoformat(),evidence_commits=heads,source_probes=len(probe['observations']),source_states=probe['states'],schema_dataset_types=len(registry['schemas']),schema_restore=registry['flow_schema_evidence'],main_verified_partitions=snapshot['remote_verified_partitions'],main_aggTrades_rows=snapshot['aggTrades_rows'],elapsed_seconds=round(time.monotonic()-started,3),process_cpu_seconds=round(time.process_time()-cpu,3),effective_codex_work_seconds=None,phase_1_accepted=False,global_C21_accepted=False)
    checkpoint=Path('reports/checkpoints/C21_2_source_watch_execution.json');atomic_json(checkpoint,evidence)
    paths=[report_path,Path('catalog/schema_registry.json'),dictionary,Path('reports/source_watch_main_snapshot.json'),checkpoint]
    commit_checkpoint(paths,branch,'C21 source-version watch and actual restored schema evidence: '+status)
    # Disposable restore only; original remote data are unchanged.
    target.unlink()


if __name__=='__main__':main()
