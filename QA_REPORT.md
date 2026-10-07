> Publication update 2026-10-07: the former GitHub 403 is resolved. The code and 18 passing pilot partitions (36 Release assets) are published; full readback and an isolated restoration passed. See reports/remote_execution.json. The original pilot findings below remain historical evidence; full-window extraction and C15 are still incomplete.

# QA report

## Local tests

...............................                                          [100%]
31 passed in 0.21s

## Actual data validation

42 RAW/Parquet file checks; 36 PASS. Integrity checks pass separately from dataset QA; individual trades with ID gaps fail promotion. Validated SHA256, bytes and Parquet row counts. All promoted partitions passed within-day source/schema/ID/interval checks. Source schema discovery initially rejected the trades header quote_qty; explicit alias added and regression-tested before accepting data.

## Reconstruction

| Dataset | Result | Mismatched minutes | Mismatched fields |
|---|---|---:|---:|
| BTCUSDT/trades | PASS | 0 | 0 |
| ETHUSDT/trades | PASS | 0 | 0 |
| SOLUSDT/trades | PASS | 0 | 0 |
| BTCUSDT/aggTrades | FAILED | 354 | 1279 |
| ETHUSDT/aggTrades | FAILED | 203 | 710 |
| SOLUSDT/aggTrades | FAILED | 90 | 384 |

A reconstruction FAILED is distinct from a source integrity PASS. Aggregate-derived bars are not certified as exact. All discrepancies retained in reports/bar_comparison_*.json. Synthetic tests do not establish arbitrary feature code or production system correctness.

## Remote acceptance

NOT RUN / BLOCKED: GitHub 403. Mock upload/restore integrity tests are not counted as a real restore. No checkpoint approved.

## Live

Observed market/public events; REST snapshots returned 451. Full L2 reconstruction not certified. See reports/live_inventory.json.

## Individual-trade quarantine

Original checksums and all reconstructed official 1m bars match for the sampled date, but intra-day ID gaps remain: BTCUSDT 622; ETHUSDT 329; SOLUSDT 117. All three individual-trade partitions remain FAILED and are excluded from passing coverage. Source exclusions or identifier semantics are possible explanations, not established facts. Do not silently discard or fill missing IDs. The raw and normalized files are retained for audit.
