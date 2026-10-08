# Historical acquisition expansion

The isolated expansion branch retains the incumbent core writer and funding
workflow unchanged. Selected sources add spot executions, spot 1m OHLCV,
percentage-depth summaries and evidence-certified USD-M individual market
executions. The 731-day inclusive window is enforced before source URL creation.
Spot original timestamps retain milliseconds before 2025 and microseconds from
2025-01-01; new normalized schemas use exact microseconds and decimal strings.

Initial actual local samples cover three symbols: three bookDepth dates and two
spot-candle dates per symbol. Nine partitions validate (86,400 depth rows and
8,640 spot bars); six depth partitions remain quarantined for frozen bands or
partial-day boundaries. The 2026-10-07 depth source ends near 02:49 UTC. The
2026-09-07 source shows some exact depth/notional pairs unchanged for hours.
These are observed review conditions, not proven causes or repaired data.
Snapshots change from ten bands in 2024 to twelve in the 2026 samples; this is
preserved source structure, never converted into full price-level depth.

The workflow publishes a bounded source pilot, then resumes serialized batches
from its own manifest. One publisher uploads raw ZIPs and reproducible Parquet,
verifies full SHA-256/size readback, stores a durable Git receipt, and only then
prunes local inputs. Quarantine quality remains separate from verified storage.
Verification bars for individual trades are independently hashed and published.
Per-source sample restoration downloads into absent paths and validates hashes,
schema metadata and row counts. Dataset state is not promoted merely by upload.

GitHub API requests are paced at fifteen seconds; expansion yields when the
observed repository budget drops below 200 requests, reserving capacity for the
incumbent writer. Server-supplied reset/rate waits are observable and resumable.
Batch runtime is bounded; new batches skip matching verified partitions.
Failures preserve files; 404s are recorded per source, not universal absence.
No paid backend is purchased. The finite matrix is a resumable campaign, not a
guarantee of completion: gaps, blocked sources and remaining scope must be
audited independently after execution.

Actual operational evidence lives in `reports/extended_execution.json` and
`catalog/extended_manifest.json`. Local QA samples alone are not remote verified.
The acceptance status of C17/C21/Phase 1 remains open.
