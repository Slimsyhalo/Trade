# Architecture and implementation boundary

Single-writer CLI -> public archive downloader -> source SHA256 -> immutable ZIP -> streaming normalization -> fail-closed partition QA -> Parquet/ZSTD -> manifest -> optional GitHub release upload -> full-byte remote verification -> optional prune.

`quantlab_core/io.py`: pacing, retries, atomic metadata, source integrity, budget.
`quantlab_core/sources.py`: allowlisted symbols/datasets, fixed authorized window, funding pagination primitive.
`quantlab_core/normalize.py`: explicit version-1 schemas, exact decimal strings, bounded 10k-row batches, timestamps and QA.
`quantlab_core/pipeline.py`: checkpoint manifests, deterministic paths, catalog, corruption quarantine, resume.
`quantlab_core/remote.py`: release adapter and restore. Real acceptance remains blocked.
`quantlab_core/research.py`: causal guards, availability-ordered replay, exact Decimal bar calculations.
`live_collector/`: separate public/market streams, periodic REST snapshots, raw JSON.gz rotation, sequence/loss markers and optional upload. Collector prototype: not an always-on managed service.

Layers: raw original archives; normalized typed Parquet; derived reproducible calculations. Archive decimal values remain strings to preserve their entire lexical precision; analytical callers must explicitly cast to Decimal or a justified decimal Arrow scale. No float conversion at ingestion. UTC int64 milliseconds for historical Futures, receive int64 nanoseconds for live.

State is one atomic JSONL manifest with one entry per symbol/dataset/day, plus history of source revisions. CLI OS advisory lock prevents simultaneous writers. Corrupted files are retained under quarantine names and redownloaded; budget failure stops work without deleting unverified files. Resume trusts local verified hashes or re-verifies remote assets when remote mode is enabled.

Trade ID checks currently run within partitions. Cross-partition boundary validation is an outstanding production gate. Metrics with unknown publication time have nullable available_at_ms; strict replay rejects them. Historical trade exchange-time availability requires explicit assumption acceptance. Do not treat this as historical receive time.

Pending production work: broad discovery and source-specific backfills, funding ingestion integration, historical bookDepth parser, coordinated live disk reservations, robust process-crash live segment recovery, synchronized live snapshot/delta stitching, cross-day QA, partition splitting, remote integration/restore and GitHub CI. No claim of C01-C15 completion.
