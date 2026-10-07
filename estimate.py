"""Explicit sample-based planning; no false two-year coverage claim."""
import json
from pathlib import Path
r=json.loads(Path('reports/source_probes.json').read_text())
lines=['# Storage estimate','', 'Pre-bulk estimate based on streamed Content-Length probes of 2024-10-07 only. This is a one-day extrapolation, NOT a capacity guarantee. Downloading all history is blocked until remote storage works. Plan 3x this baseline for activity variation; obtain at least 12 stratified monthly samples before production bulk approval.','', '731 inclusive calendar dates are requested. The end date is still in progress at this audit. Exact endpoints are authoritative; no earlier history is requested.','', '| Symbol | Dataset | Sample ZIP bytes | RAW ZIP baseline GB (731d) | Normalized uncompressed | Parquet ZSTD | Remote |','|---|---|---:|---:|---|---|---|']
for x in r:
 size=x.get('bytes'); estimate=f'{size*731/1e9:.3f}' if size else 'unknown'
 lines.append(f"| {x['symbol']} | {x['dataset']} | {size or 'unavailable at sample date'} | {estimate} | unmeasured | unmeasured | RAW + Parquet; unmeasured |")
lines+=['','No invented compression ratios. Pilot measurements will be appended. aggTrades are prioritized; individual trades retain finer event timing and are not exactly reconstructible from aggTrades. Do not silently label them redundant. bookDepth is a coarse summary and must not be used as full L2 history.']
Path('STORAGE_ESTIMATE.md').write_text('\n'.join(lines)+'\n')
