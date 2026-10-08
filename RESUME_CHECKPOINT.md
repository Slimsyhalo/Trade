# Resume checkpoint — 2026-10-08

Verified remote HEAD before work: 9ed48e7. The previous job published 502 complete RAW/Parquet pairs, then stopped at BTCUSDT/premiumIndexKlines/2024-11-09 because the remote adapter conflated permissions and rate limits.

Changes: four-second API pacing, rate-header waits, bounded retry of explicitly rejected requests, upload-body rewinding, release/asset metadata caching, rate-event/elapsed-time evidence, and capacity-reviewed aggTrades acquisition. All 38 tests pass. The 72 official archive probes span twelve dates for each symbol and for trades/aggTrades; all returned HTTP 200. These probes do not imply downloaded coverage.

The resumed job checkpoints before local deletion and skips 502 already verified partitions. It acquires aggTrades and the five small datasets within the fixed 2024-10-07 to 2026-10-07 window. It pauses after four hours and can resume from the manifest. Full-window completion is not yet established.

Individual trades remain quarantined; funding, full order-book replay, final audit and C15 are unresolved. No strategy research or trades are performed.
