> Publication update 2026-10-07: the former GitHub 403 is resolved. The code and 18 passing pilot partitions (36 Release assets) are published; full readback and an isolated restoration passed. See reports/remote_execution.json. The original pilot findings below remain historical evidence; full-window extraction and C15 are still incomplete.

# Audit summary — Phase 1 incomplete

Outcome: reproducible local pilot, no GitHub publication and no full-window extraction.

| Symbol | Individual trades | Aggregate trades | OHLC rows (all price series) | Passing partitions | Parquet GB |
|---|---:|---:|---:|---:|---:|
| BTCUSDT | 0 | 1,459,023 | 5,760 | 6 | 0.0255 |
| ETHUSDT | 0 | 1,221,050 | 5,760 | 6 | 0.0222 |
| SOLUSDT | 0 | 748,183 | 5,760 | 6 | 0.0130 |

Historical sample day: 2024-10-07 UTC; each covered dataset has 1/731 days (0.1368%). No other dates are implied.

Blocking issues: GitHub integration write access 403; Binance REST regional 451; incomplete history; aggregate-based reconstruction differences; individual-trade source ID gaps. The independently accessible public archive and WS sources were used without attempting to bypass restrictions.

No C01–C15 checkpoint is approved because real remote state and restore cannot be verified. Tests and local partition QA are evidence of the pilot only.

Next actions: authorize the GitHub integration for Trade, publish the reviewed source snapshot, perform a real release upload/download/row-count test, broaden sample estimation, then run incremental historical batches. Resolve trade reconstruction semantics before promoting replay. Deploy live capture only after fault/recovery testing and valid snapshot stitching.

See DATA_COVERAGE.md, QA_REPORT.md, LIMITATIONS.md and RESEARCH_HANDOFF.md for exact scope.

Observed but quarantined: 9,424,949 individual executions (BTC 3,730,708; ETH 3,859,018; SOL 1,835,223). Their 1m bars match every compared official field, but ID-gap QA fails. These rows are excluded from the passing-partition table above and explicitly listed in AUDIT_SUMMARY.json.
