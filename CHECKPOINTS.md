# Checkpoints — evidence-driven status, 2026-10-08

Source checkpoints preserve progress; they do not approve the full foundation.
For live acquisition counts use main's current reports/historical_execution.json
and manifest. This branch's catalog is an earlier snapshot, not the active writer.

| Checkpoint | Current evidence | Acceptance |
|---|---|---|
| C01 Repository/bootstrap | Code published, locked dependencies, tests | IMPLEMENTED; former write 403 resolved |
| C02 Official discovery | Official contracts, archive probes, observed REST/WS limits | PARTIAL: full-window discovery remains tied to acquisition |
| C03 Storage | 72 stratified probes; 2GB local budget; Releases readback | PARTIAL: entire-window storage not yet demonstrated |
| C04 Historical downloader | Resumable daily acquisition, rate-limit backoff, serialized writer | IMPLEMENTED for scoped sources; long scan running |
| C05 Integrity | Source checksums, local hashes, full asset readbacks, pilot restore | IMPLEMENTED for verified partitions; not all requested data |
| C06 Normalization | Exact decimal strings, typed Parquet/ZSTD; funding source extension tested | IMPLEMENTED for supported schemas |
| C07 QA | 111 tests; source QA, recovery faults, causal guards, adjacent-day replay checks | PARTIAL: full historical QA and long live fault gates pending |
| C08 BTC extraction | Pilot plus incremental remote-backed acquisition | INCOMPLETE: consult current catalog for missing dates |
| C09 ETH extraction | Pilot plus incremental remote-backed acquisition | INCOMPLETE: consult current catalog for missing dates |
| C10 SOL extraction | Pilot plus incremental remote-backed acquisition | INCOMPLETE: consult current catalog for missing dates |
| C11 Derivatives | Mark/index/premium/metrics acquired incrementally; real monthly funding fixtures pass | INCOMPLETE: funding acquisition/restore queued; boundary months unavailable |
| C12 Live | Durable spool, nonblocking remote worker, restart/sequence diagnostics; 29 new fault cases; original 3,990 rows verified | PARTIAL: source checkpoint; real live upload/restore and long recovery validation pending |
| C13 GitHub storage | 18 pilot partitions, 36 assets, full readback and isolated restore PASS; historical checkpoints advancing | IMPLEMENTED for published receipts; full corpus not complete |
| C14 Replay | Streaming Parquet, backward cross-asset joins; 3,428,256 actual aggTrades and 4,320 klines replayed | PARTIAL: isolated branch; funding/OI timing and full coverage unresolved |
| C15 Audit/handoff | Manifest-driven audit extension tested and queued for integration | NOT APPROVED: foundation remains incomplete |

Remote status observed from main report 2026-10-08T13:13:55.246372+00:00: 702 verified historical/pilot partitions.
Historical run 37774209643: in_progress; funding run 37777532680: pending.
See reports/live_recovery_remote_status.json for the captured run/commit observation.
Counts may advance; they are not claims of full date coverage.

Individual trade pilot files remain quarantined for source ID gaps. Funding/OI
publication availability stays unknown; replay cannot silently invent it. The
historical continuation excludes individual trades until their source QA gate is
resolved. Funding's permitted monthly method excludes boundary October months.

Each dataset acceptance requires source integrity, PASS QA, documentation, verified
remote state and scoped restoration evidence. A passing test suite or source commit
does not approve a blocked/incomplete dataset or C15. See REPLAY_CHECKPOINT.md and LIVE_RECOVERY_CHECKPOINT.md.
