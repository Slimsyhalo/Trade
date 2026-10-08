# Research data foundation — auditable checkpoint

Phase 1 is **not accepted**. C16–C22 were reconciled against existing C01–C15; none is globally certified. This checkpoint does not modify main or another running writer.

## Immutable observation

Main `c79ad71cdea6e58e1b0d2e00fe52da92fdc2a3c8` contains **1,127 remotely verified partitions** and **235,187,061 aggregate execution rows**, with 62–63 dates per current symbol/dataset out of 731 requested. Full receipt hashes and byte sizes were reconciled; coverage and remaining dates are in `reports/foundation_acceptance_audit.json`. Later main commits may add data.

Expansion `5156dc7e8f1fbfe6f207b62202fd94a16f5f5d41` reports 28 remotely verified partitions, 24 admitted and 4 quarantined, with 34,098,021 admitted records. Quality and storage states are separate. The historical original writer and funding pending workflow were preserved; the expansion writer uses an independent ledger.

Live `58a7763fd86ea2117bd1fce395b696d5c13330cf` reports 27 verified segments and 3,168,344 observations in the current bounded campaign. The earlier 600-second run restored one segment per available route and observed all twelve required symbol/topic streams. This establishes bounded observations, not 24/7 continuity or full L2 reconstruction. REST snapshot/OI failures remain explicit.

Recovery `d23af103f996d62e6c394097ddfb5223fda72d70` restored **223 of 223 members**, including **109 official documents**, from a full-hash-verified 9,074,316-byte Releases container into an absent destination on a clean hosted runner. All original document and normalized metadata hashes passed. The temporary 19 transfer parts were retired only after durable remote receipt and restoration commits. Historical content vintage and effective availability remain uncertified; no revised value is admitted as an original historical observation.

## Trade admission and scientific transforms

The original strict trade QA was retained. All three initial tapes matched official OHLCV, counts and taker quantities in every one of 1,440 minutes; nine additional symbol/date samples tested 18,779,587 executions with 39,026 skipped identifiers. The evidence supports source-market tapes despite global ID discontinuities; their precise cause is undetermined. Structural problems or a missing execution fail the evidence gate. Existing main quarantine records were not overwritten.

Local exact-decimal flow transforms used 9,424,949 executions to reproduce 4,320 minute rows with source hashes and mass conservation. Independent repeated local builds matched byte-for-byte. The separate `flow-cloud-recovery.yml` now requires source restoration on a clean runner, recalculation against pilot output hashes, remote publication and output restoration for BTC/ETH/SOL. Writing the workflow does not certify its result.

## Publication failure and recovery

Context job 113368676125 log records a remote Git rejection `(failed)` at 14:45:15 UTC; the next checkpoint push succeeded at 14:45:17. No external branch divergence was reported. The failed run also observed BLS403 and differing Federal Reserve response bytes. Exact versions were preserved by the certified document recovery workflow, without replacing original bytes or bypassing provider restrictions.

The new checkpoint helper retries the **identical commit** after remote-head readback, only if the expected parent remains. It recognizes a lost success acknowledgement; unreadable refs, authentication failures and external writers stop publication safely. It never forces, rebases or merges. The fix is on this independent branch; active historical/live source code is unchanged during execution.

## Acceptance still open

- 731 dates per selected historical source not yet acquired; campaigns remain active
- All 70 inventoried sources require final capability/cost/schema and acquisition-decision reconciliation
- Historical source-market trade admission established; skipped global ID cause remains undetermined
- Depth summary partial/frozen-band quarantine remains; not a full order book
- REST451 blocks synchronized live L2 snapshots and retention-limited OI acquisition in observed environments
- Finite Actions captures and uncalibrated receive clock do not establish permanent live service
- Official archived documents restored, but historical effective availability and unchanged historical vintage not established
- News, announcements, regulatory/incident timelines, historical contract filters and fees still incomplete
- Flow clean-runner campaign pending; other derived families not yet implemented
- Global independent restoration, fault recovery and final data dictionary incomplete
- Complete dataset size remains unknown; sampled known components already exceed local work budget
- Earlier foreground active time versus external waits was not fully instrumented

## Validation and time evidence

150 tests passed before publication, including regression tests for lost acknowledgement, transient rejection, external writer and unreadable remote. Known foreground acquisition/tool durations and CI elapsed/CPU durations are retained separately. Effective Codex active seconds remain null for uninstrumented earlier intervals; elapsed download time is not reported as model work.

See `catalog/source_inventory.json` (70 entries across seven families), `docs/DATA_SOURCE_INVENTORY.md`, `reports/storage_capacity_plan.json`, immutable evidence heads and the machine-readable acceptance audit. No paid backend, trading strategy or profitability claim was introduced.
