# Independent coverage and restoration audit

Observed UTC: 2026-10-08T19:33:55.129384+00:00. Phase 1 and global C21 remain **NOT_ACCEPTED**.

Immutable source heads: main `a4ab5406a199a02590c5c35c943af538e3750fd8`, expansion `f71bca8c84951e6658136308fe937e7bed0903b6`, derived `7c9d5561d3019df4b1c53bfaccce63ed40319bfb`.

| Source | Symbol | Admitted remote days / requested | Quarantined partitions | Missing date ranges |
|---|---|---:|---:|---|
| oi_changes | BTCUSDT | 12/731 | 0 | 2024-10-19..2026-10-07 |
| oi_changes | ETHUSDT | 11/731 | 0 | 2024-10-18..2026-10-07 |
| oi_changes | SOLUSDT | 11/731 | 0 | 2024-10-18..2026-10-07 |
| perpetual_basis | BTCUSDT | 12/731 | 0 | 2024-10-19..2026-10-07 |
| perpetual_basis | ETHUSDT | 11/731 | 0 | 2024-10-18..2026-10-07 |
| perpetual_basis | SOLUSDT | 11/731 | 0 | 2024-10-18..2026-10-07 |
| spot_klines_1m | BTCUSDT | 9/731 | 0 | 2024-10-15..2024-12-31; 2025-01-02..2026-10-07 |
| spot_klines_1m | ETHUSDT | 9/731 | 0 | 2024-10-15..2024-12-31; 2025-01-02..2026-10-07 |
| spot_klines_1m | SOLUSDT | 9/731 | 0 | 2024-10-15..2024-12-31; 2025-01-02..2026-10-07 |
| spot_trades | BTCUSDT | 9/731 | 0 | 2024-10-15..2024-12-31; 2025-01-02..2026-10-07 |
| spot_trades | ETHUSDT | 9/731 | 0 | 2024-10-15..2024-12-31; 2025-01-02..2026-10-07 |
| spot_trades | SOLUSDT | 8/731 | 0 | 2024-10-14..2024-12-31; 2025-01-02..2026-10-07 |
| um_aggTrades | BTCUSDT | 80/731 | 0 | 2024-12-26..2026-10-07 |
| um_aggTrades | ETHUSDT | 79/731 | 0 | 2024-12-25..2026-10-07 |
| um_aggTrades | SOLUSDT | 79/731 | 0 | 2024-12-25..2026-10-07 |
| um_bookDepth_summary | BTCUSDT | 8/731 | 2 | 2024-10-15..2026-10-07 |
| um_bookDepth_summary | ETHUSDT | 8/731 | 2 | 2024-10-15..2026-10-07 |
| um_bookDepth_summary | SOLUSDT | 8/731 | 2 | 2024-10-15..2026-10-07 |
| um_funding_settled | BTCUSDT | 699/731 | 0 | 2024-10-07..2024-10-31; 2026-10-01..2026-10-07 |
| um_funding_settled | ETHUSDT | 699/731 | 0 | 2024-10-07..2024-10-31; 2026-10-01..2026-10-07 |
| um_funding_settled | SOLUSDT | 699/731 | 0 | 2024-10-07..2024-10-31; 2026-10-01..2026-10-07 |
| um_index_price | BTCUSDT | 80/731 | 0 | 2024-12-26..2026-10-07 |
| um_index_price | ETHUSDT | 79/731 | 0 | 2024-12-25..2026-10-07 |
| um_index_price | SOLUSDT | 79/731 | 0 | 2024-12-25..2026-10-07 |
| um_klines_1m | BTCUSDT | 80/731 | 0 | 2024-12-26..2026-10-07 |
| um_klines_1m | ETHUSDT | 79/731 | 0 | 2024-12-25..2026-10-07 |
| um_klines_1m | SOLUSDT | 79/731 | 0 | 2024-12-25..2026-10-07 |
| um_mark_price | BTCUSDT | 80/731 | 0 | 2024-12-26..2026-10-07 |
| um_mark_price | ETHUSDT | 79/731 | 0 | 2024-12-25..2026-10-07 |
| um_mark_price | SOLUSDT | 79/731 | 0 | 2024-12-25..2026-10-07 |
| um_metrics | BTCUSDT | 79/731 | 0 | 2024-12-25..2026-10-07 |
| um_metrics | ETHUSDT | 79/731 | 0 | 2024-12-25..2026-10-07 |
| um_metrics | SOLUSDT | 79/731 | 0 | 2024-12-25..2026-10-07 |
| um_premium_index | BTCUSDT | 80/731 | 0 | 2024-12-26..2026-10-07 |
| um_premium_index | ETHUSDT | 79/731 | 0 | 2024-12-25..2026-10-07 |
| um_premium_index | SOLUSDT | 79/731 | 0 | 2024-12-25..2026-10-07 |
| um_trades | BTCUSDT | 6/731 | 3 | 2024-10-11..2024-10-11; 2024-10-14..2026-10-07 |
| um_trades | ETHUSDT | 7/731 | 2 | 2024-10-11..2024-10-11; 2024-10-15..2026-10-07 |
| um_trades | SOLUSDT | 6/731 | 2 | 2024-10-11..2024-10-11; 2024-10-14..2026-10-07 |

Fresh restoration campaign state: **RUNNING**. Planned source-bound samples: 150; completed this immutable plan: 68; lifetime restored objects: 68.

First and last admitted partitions of each source/symbol/ledger are sampled. Every original ZIP member is read to EOF for CRC integrity; Parquet rows, schema lineage, event ordering and availability boundaries are scanned. Outputs are only pruned after an audit checkpoint is pushed. This is sampled restoration, not verification of every object or source completeness. Historical publication timing remains uncertified.

Coverage is membership of QA-admitted partitions with matching inherited full-readback receipts. No fresh remote-object check, lossless source guarantee, strict causal availability, continuous live service or global acceptance inferred. Original and derived records are never summed as executions. Monthly funding uses observed_days only. Legacy quarantines remain separate from source-tape admission. Missing dates are NOT_ACQUIRED, not proven source unavailability.

Inventory sources without a compatible partition ledger are explicitly NOT_ASSESSED_BY_PARTITION_AUDIT; their original documentary/live evidence is not replaced. Schedule on this non-default audit branch is inactive until integration with the default branch at a safe writer boundary.
