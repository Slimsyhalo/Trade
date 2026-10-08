# C11 / QA / Replay development checkpoint — 2026-10-08

## Implemented and verified

Official monthly fundingRate source discovered and tested using original BTC/ETH/SOL September 2026 ZIP fixtures. Each source passed its official checksum, typed normalization and 90-settlement QA; timestamps and signed decimal precision are unchanged. Fixtures are small source-test inputs, outside the acquisition catalog.

Permitted downloader scope: 23 whole months per symbol, November 2024 through September 2026. Both October boundary archives are refused before any request. Monthly catalog coverage expands observed dates rather than counting a month file as a single day. Unknown historical publication times remain null and fail strict replay.

Audit generation now derives remote counts from matching ZIP/Parquet receipts, distinguishes absent local files from fresh validation and preserves storage estimates. Aggregate and individual-trade limitations remain visible. QA revisions are retained when interpretation changes.

Bar availability now respects delayed input receipt times; a trade received after its candle closes cannot make that candle available earlier. Unknown input availability fails construction.

## Remote execution

The funding workflow waits for the existing historical writer. Once it acquires that same lock, it copies the tested source onto the latest main, runs the full test suite, then commits code and audit evidence before acquisition. It uploads and fully hashes each RAW and Parquet asset, restores one month per symbol, commits every five partitions, and only then prunes verified local copies. Metadata integrates into main without rewriting historical commits.

Expected funding scan: 69 monthly partitions. After funding, twenty sequential historical batches of at most four hours each resume from main and stop early when the scoped scan finishes or QA blocks it. No parallel writers are used. No successful full scan is claimed before reports/funding_execution.json records its results. Main historical extraction remains in progress. Individual trades, full L2 reconstruction, liquidation completeness and final C15 remain unresolved. This checkpoint does not authorize strategy discovery.

Runtime elapsed_seconds and process_cpu_seconds are measured separately in funding checkpoints. Neither is claimed to measure model thinking time.

Full test evidence: 52 passing tests, including real Binance source-fixture normalization, causal timing, signed-rate precision, monthly window guards, receipt consistency and preservation of storage estimates. A source guard refuses to overwrite concurrent code changes on main.
