"""Generate audits from recorded evidence; absent files are not revalidated."""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
import yaml
from quantlab_core.pipeline import Pipeline, remote_verified
from quantlab_core.io import atomic_json


def optional_json(path):
    return json.loads(path.read_text()) if path.exists() else {}


def build_audit(root):
    root=Path(root)
    pipe=Pipeline(root,yaml.safe_load((root/'config.yaml').read_text()))
    catalog=pipe.catalog(); records=list(pipe.records.values())
    good=[r for r in records if r.get('qa',{}).get('status')=='PASS']
    backed=[r for r in records if remote_verified(r)]
    bad=[r for r in records if r.get('qa',{}).get('status')=='FAILED']
    pilot=optional_json(root/'reports/remote_execution.json')
    restore=pilot.get('restore',{'status':'NOT_RUN'})
    checks=pipe.validate()
    tests=(root/'reports/tests.txt').read_text().strip() if (root/'reports/tests.txt').exists() else 'No test evidence recorded'
    symbols={}
    for symbol in pipe.config['symbols']:
        accepted=[r for r in good if r['symbol']==symbol]
        symbols[symbol]={
            'datasets':[r for r in catalog if r['symbol']==symbol],
            'qa_passing_partitions':len(accepted),
            'remote_verified_partitions':sum(remote_verified(r) for r in accepted),
            'aggregate_trades':sum(r['qa']['rows'] for r in accepted if r['dataset']=='aggTrades'),
            'individual_trades':sum(r['qa']['rows'] for r in accepted if r['dataset']=='trades'),
            'bars':sum(r['qa']['rows'] for r in accepted if r['dataset'] in ('klines','markPriceKlines','indexPriceKlines','premiumIndexKlines')),
            'funding_settlements':sum(r['qa']['rows'] for r in accepted if r['dataset']=='fundingRate'),
            'compressed_gb':sum(r['normalized']['bytes'] for r in accepted)/1e9,
            'quality_all_acquired':{k:sum(r.get('qa',{}).get(k,0) for r in records if r['symbol']==symbol) for k in ('duplicates_found','duplicates_removed','id_gaps','interval_gaps','out_of_order','schema_violations')},
            'quarantined_partitions':[r['key'] for r in bad if r['symbol']==symbol]}
    summary={'phase':1,'status':'INCOMPLETE','generated_at':datetime.now(timezone.utc).isoformat(),
             'notice':'DO NOT ASSUME DATA EXISTS UNLESS LISTED IN THE CATALOG.',
             'historical_window':{'start':pipe.config['start_date'],'end_inclusive':pipe.config['end_date']},
             'symbols':symbols,'tests':tests,
             'remote':{'repository':'https://github.com/'+pipe.config['repository'],'verified_partitions':len(backed),'verified_assets':2*len(backed),'restore_test':restore,'verification_basis':'Recorded full readback at verified_at; not a fresh redownload of every asset'},
             'local_validation':{'present_file_checks':sum('integrity_status' in r for r in checks),'present_integrity_failures':[r for r in checks if r.get('integrity_status')=='FAILED'],'remote_not_rechecked':sum(r.get('status')=='REMOTE_NOT_RECHECKED' for r in checks),'missing_local_unbacked_files':sum(r.get('status')=='FAILED' and 'integrity_status' not in r for r in checks)},
             'quarantined_partitions':[r['key'] for r in bad],
             'last_historical_run_report':optional_json(root/'reports/historical_execution.json'),
             'last_funding_run_report':optional_json(root/'reports/funding_execution.json'),
             'limitations':['Full-window coverage incomplete','Individual-trade ID gaps unresolved','Aggregate bars not certified as exact official klines','Historical publication latency unknown for metrics and funding','Boundary funding months excluded because full archives cross authorized limits','Full historical L2 and complete market liquidation coverage not established'],
             'approved_scope':['Initial 18-partition remote pilot and isolated restore'] if pilot.get('status')=='PASS' and restore.get('status')=='PASS' else [],'phase_2_authorized':False}
    atomic_json(root/'AUDIT_SUMMARY.json',summary)
    lines=['# Current data coverage','',f"Generated: {summary['generated_at']}",'',
           'QA days count observed passing dates. Remote days require matching RAW and Parquet readback receipts. Monthly funding coverage counts observed dates, not one day per archive.','',
           '| Symbol | Dataset | First | Last | QA days / expected | Remote days | Rows | QA partitions | Remote partitions |','|---|---|---|---|---:|---:|---:|---:|---:|']
    for r in catalog:
        lines.append(f"| {r['symbol']} | {r['dataset']} | {r['first_available']} | {r['last_available']} | {r['available_days']} / {r['expected_days']} | {r['remote_verified_days']} | {r['rows']:,} | {r['partitions']} | {r['remote_verified_partitions']} |")
    lines+=['','Missing-date lists, failed partitions and remote URLs are in data_catalog.json. Unacquired dates do not imply Binance lacks those dates.','',
            'Funding archives are restricted to complete months inside the window. October 2024 and October 2026 need another permitted source for their in-window dates. No outside-window records were downloaded.']
    (root/'DATA_COVERAGE.md').write_text('\n'.join(lines)+'\n')
    lines=['# Current audit — Phase 1 incomplete','',f"Generated: {summary['generated_at']}",'',f"{len(good)} QA-passing partitions; {len(backed)} verified remote RAW/Parquet pairs; {len(bad)} quarantined partitions.",'',
           '| Symbol | Aggregate trades | Individual trades | Bars | Funding settlements | Remote partitions |','|---|---:|---:|---:|---:|---:|']
    for symbol,r in symbols.items():
        lines.append(f"| {symbol} | {r['aggregate_trades']:,} | {r['individual_trades']:,} | {r['bars']:,} | {r['funding_settlements']:,} | {r['remote_verified_partitions']} |")
    lines+=['',f"Initial restore: {restore.get('status','NOT_RUN')}. Remote counts reflect recorded readbacks; assets were not all downloaded again today.",'','Full-window coverage and final C15 remain incomplete. See DATA_COVERAGE.md and AUDIT_SUMMARY.json.']
    (root/'AUDIT_SUMMARY.md').write_text('\n'.join(lines)+'\n')
    lines=['# Current QA report','',tests,'',f"Manifest: {len(good)} QA-passing, {len(bad)} quarantined, {len(backed)} verified remote partitions.",'',
           'Absent local files after verified pruning are REMOTE_NOT_RECHECKED, never a fresh validation PASS. SHA-256/size/readback times remain in the manifest. Real restoration evidence is in reports/remote_execution.json and reports/funding_execution.json when available.','',
           'Funding schedule checks use one-second QA resolution for observed millisecond jitter. Original calc_time is unchanged; variable intervals use source funding_interval_hours. Publication timestamps remain null and fail strict replay.','',
           'Reconstruction evidence remains in reports/bar_comparison_*.json. Individual-trade bars matched pilot candles but ID-gap QA failed; aggregate bars differed. Archive integrity does not erase either limitation.']
    (root/'QA_REPORT.md').write_text('\n'.join(lines)+'\n')
    return summary


if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--root',default='.')
    report=build_audit(parser.parse_args().root)
    print(json.dumps({'status':report['status'],'verified_remote_partitions':report['remote']['verified_partitions']}))
