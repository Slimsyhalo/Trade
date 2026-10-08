# Binance QuantLab — Data Foundation

Phase 1 remains incomplete. Current coverage and remote readback counts are generated from manifest.jsonl in DATA_COVERAGE.md, data_catalog.json and AUDIT_SUMMARY.json. Do not assume a dataset exists unless listed in that catalog.

BTCUSDT, ETHUSDT and SOLUSDT, Binance USD-M perpetual futures. Fixed authorized window: 2024-10-07 through 2026-10-07 UTC. No strategy optimization or orders.

## Verified infrastructure

Public ZIP/checksum downloads, exact decimal normalization, Parquet/ZSTD, bounded storage, versioned manifests, QA, causal replay primitives, GitHub Release readbacks and restoration evidence. Current test results are in QA_REPORT.md and reports/tests.txt.

Official monthly funding archives are supported only for complete months inside the window: November 2024 through September 2026. October boundary archives are refused before download. Funding publication times are unknown and excluded from strict replay. Small official funding fixtures support reproducible tests and are outside the acquisition catalog.

## Execution and checkpoints

The historical writer acquires aggTrades, klines, markPriceKlines, indexPriceKlines, premiumIndexKlines and metrics. The funding checkpoint workflow waits for the same writer lock, tests and integrates its source against latest main, acquires up to 69 permitted monthly funding partitions, then resumes historical work in up to twenty sequential four-hour batches. Completion or QA failure stops further acquisition. Each batch checks out the latest manifest; no parallel writers or restart from zero.

Both original ZIP and Parquet must pass full readback; manifests are committed before local pruning. Actual elapsed time and process CPU time are recorded separately where available.

[Dataset Releases](https://github.com/Slimsyhalo/Trade/releases) · [Actions](https://github.com/Slimsyhalo/Trade/actions)

Individual-trade ID gaps, full L2 reconstruction, liquidation completeness, complete coverage and final C15 remain unresolved. See FOUNDATION_CHECKPOINT.md, REPRODUCIBILITY.md, DATA_SOURCES.md and RESEARCH_HANDOFF.md.
