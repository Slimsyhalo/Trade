"""Generate coverage and pilot audit from observed manifests, never from plans."""
import json, collections, gzip
from pathlib import Path
import yaml
from quantlab_core.pipeline import Pipeline
from quantlab_core.io import atomic_json, sha256
p=Pipeline('.',yaml.safe_load(Path('config.yaml').read_text())); catalog=p.catalog(); validation=p.validate()
records=list(p.records.values()); good=[r for r in records if r.get('qa',{}).get('status')=='PASS']
comparisons={}
for source in ('trades','aggTrades'):
 for symbol in p.config['symbols']:
  path=Path(f'reports/bar_comparison_{source}_{symbol}.json')
  if path.exists():
   report=json.loads(path.read_text()); comparisons[f'{symbol}/{source}']={'status':report['status'],'mismatched_fields':len(report['differences']),'mismatched_minutes':len({x['time'] for x in report['differences']}),'fields':dict(collections.Counter(x['field'] for x in report['differences']))}
live=[]
for path in Path('data/live').glob('*.gz'):
 counts=collections.Counter(); symbols=collections.Counter(); minimum=maximum=None
 for line in gzip.open(path,'rt'):
  row=json.loads(line); counts[row['kind']]+=1
  ts=row['receive_timestamp_ns']; minimum=ts if minimum is None else min(minimum,ts); maximum=ts if maximum is None else max(maximum,ts)
  if row['kind']=='event': symbols[row['payload'].get('data',{}).get('s','unknown')]+=1
 live.append(dict(path=str(path),rows=sum(counts.values()),kinds=dict(counts),symbols=dict(symbols),sha256=sha256(path),bytes=path.stat().st_size,min_receive_ns=minimum,max_receive_ns=maximum))
atomic_json('reports/live_inventory.json',live)
symbols={}
for symbol in p.config['symbols']:
 rows=[r for r in good if r['symbol']==symbol]
 symbols[symbol]={'datasets':[r for r in catalog if r['symbol']==symbol],'trades':sum(r['qa']['rows'] for r in rows if r['dataset']=='trades'),'aggTrades':sum(r['qa']['rows'] for r in rows if r['dataset']=='aggTrades'),'bars':sum(r['qa']['rows'] for r in rows if r['dataset'].endswith('Klines') or r['dataset']=='klines'),'partitions':len(rows),'compressed_gb':sum(r['normalized']['bytes'] for r in rows)/1e9,'quality':{k:sum(r['qa'].get(k,0) for r in rows) for k in ('duplicates_found','duplicates_removed','id_gaps','interval_gaps','out_of_order','schema_violations')},'raw_zip_bytes':sum(r['raw']['bytes'] for r in rows)}
summary={'phase':'1','status':'INCOMPLETE_BLOCKED','historical_window':{'start':'2024-10-07T00:00:00Z','end_exclusive':'2026-10-08T00:00:00Z','inclusive_calendar_days':731},'symbols':symbols,'tests':Path('reports/tests.txt').read_text(),'local_file_validation':{'checked':len(validation),'passed':sum(x['status']=='PASS' for x in validation),'integrity_passed':sum(x.get('integrity_status')=='PASS' for x in validation)},'bar_reconstruction':comparisons,'live':live,'remote':{'repository':'https://github.com/Slimsyhalo/Trade','uploaded_partitions':0,'restore_test':'NOT_RUN_BLOCKED','error':'HTTP 403 Resource not accessible by integration'},'rest':{'status':451,'reason':'Regional restriction; no bypass attempted'},'quarantined_data':[r for r in records if r.get('qa',{}).get('status')=='FAILED'],'available_data':'Only passing manifest/catalog entries and separately inventoried live smoke captures','unavailable_data':['Remaining historical days','Funding history','Full reconstructible historical L2','Verified complete liquidation history','GitHub copies','REST depth/OI snapshots'],'approved_checkpoints':[]}
atomic_json('AUDIT_SUMMARY.json',summary)
lines=['# Data coverage — pilot only','','Coverage means downloaded and locally QA-passing daily partitions; remote coverage is 0%. Null remote locations are intentional.','', '| Symbol | Dataset | First | Last | Expected days | Available | Missing | Coverage | Rows |','|---|---|---|---|---:|---:|---:|---:|---:|']
for r in catalog: lines.append(f"| {r['symbol']} | {r['dataset']} | {r['first_available']} | {r['last_available']} | {r['expected_days']} | {r['available_days']} | {r['missing_days']} | {r['coverage_percentage']:.4f}% | {r['rows']:,} |")
lines+=['','Full missing-day lists are in data_catalog.json. first_available refers to first acquired passing partition, not an assertion about earliest source availability. Unprobed dates are missing locally, not necessarily missing at Binance. The end day was still in progress.']
Path('DATA_COVERAGE.md').write_text('\n'.join(lines)+'\n')
qa=['# QA report','','## Local tests','',summary['tests'].strip(),'','## Actual data validation','',f"{len(validation)} RAW/Parquet file checks; {summary['local_file_validation']['passed']} PASS. Integrity checks pass separately from dataset QA; individual trades with ID gaps fail promotion. Validated SHA256, bytes and Parquet row counts. All promoted partitions passed within-day source/schema/ID/interval checks. Source schema discovery initially rejected the trades header quote_qty; explicit alias added and regression-tested before accepting data.",'','## Reconstruction','', '| Dataset | Result | Mismatched minutes | Mismatched fields |','|---|---|---:|---:|']
for key,value in comparisons.items(): qa.append(f"| {key} | {value['status']} | {value['mismatched_minutes']} | {value['mismatched_fields']} |")
qa+=['','A reconstruction FAILED is distinct from a source integrity PASS. Aggregate-derived bars are not certified as exact. All discrepancies retained in reports/bar_comparison_*.json. Synthetic tests do not establish arbitrary feature code or production system correctness.','', '## Remote acceptance','','NOT RUN / BLOCKED: GitHub 403. Mock upload/restore integrity tests are not counted as a real restore. No checkpoint approved.','', '## Live','','Observed market/public events; REST snapshots returned 451. Full L2 reconstruction not certified. See reports/live_inventory.json.']
Path('QA_REPORT.md').write_text('\n'.join(qa)+'\n')
audit=['# Audit summary — Phase 1 incomplete','','Outcome: reproducible local pilot, no GitHub publication and no full-window extraction.','', '| Symbol | Individual trades | Aggregate trades | OHLC rows (all price series) | Passing partitions | Parquet GB |','|---|---:|---:|---:|---:|---:|']
for symbol,r in symbols.items(): audit.append(f"| {symbol} | {r['trades']:,} | {r['aggTrades']:,} | {r['bars']:,} | {r['partitions']} | {r['compressed_gb']:.4f} |")
audit+=['','Historical sample day: 2024-10-07 UTC; each covered dataset has 1/731 days (0.1368%). No other dates are implied.','', 'Blocking issues: GitHub integration write access 403; Binance REST regional 451; incomplete history; aggregate-based reconstruction differences; individual-trade source ID gaps. The independently accessible public archive and WS sources were used without attempting to bypass restrictions.','', 'No C01–C15 checkpoint is approved because real remote state and restore cannot be verified. Tests and local partition QA are evidence of the pilot only.','', 'Next actions: authorize the GitHub integration for Trade, publish the reviewed source snapshot, perform a real release upload/download/row-count test, broaden sample estimation, then run incremental historical batches. Resolve trade reconstruction semantics before promoting replay. Deploy live capture only after fault/recovery testing and valid snapshot stitching.','', 'See DATA_COVERAGE.md, QA_REPORT.md, LIMITATIONS.md and RESEARCH_HANDOFF.md for exact scope.']
Path('AUDIT_SUMMARY.md').write_text('\n'.join(audit)+'\n')
# Append measured pilot compression; no fabricated normalized expansion factors.
import zipfile
estimate=Path('STORAGE_ESTIMATE.md').read_text().split('## Measured pilot')[0]
estimate+='\n## Measured pilot\n\n| Symbol | Dataset | Raw CSV bytes | Original ZIP bytes | Uncompressed Arrow bytes | Parquet ZSTD bytes | Remote needed ZIP+Parquet |\n|---|---|---:|---:|---:|---:|---:|\n'
import pyarrow.parquet as pq
for r in records:
 if 'raw' not in r or 'normalized' not in r: continue
 raw=Path(r['raw']['path']); normalized=Path(r['normalized']['path'])
 with zipfile.ZipFile(raw) as z: csvsize=sum(m.file_size for m in z.infolist())
 arrowbytes=sum(batch.nbytes for batch in pq.ParquetFile(normalized).iter_batches())
 estimate+=f"| {r['symbol']} | {r['dataset']} | {csvsize} | {r['raw']['bytes']} | {arrowbytes} | {r['normalized']['bytes']} | {r['raw']['bytes']+r['normalized']['bytes']} |\n"
Path('STORAGE_ESTIMATE.md').write_text(estimate)
print(json.dumps({'partitions':len(good),'rows':sum(r['qa']['rows'] for r in good),'remote_uploaded':0,'comparisons':comparisons},indent=2))
