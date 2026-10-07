# Limitations and open gates

1. Only one historical UTC day sampled per implemented dataset/symbol; not two years. The requested inclusive date range has 731 calendar dates. No earlier history downloaded. End day was unfinished at execution time.
2. GitHub write denied (403 integration resource access). No push, remote data, remote restore, or approved checkpoint. Repository user permissions do not imply integration access. Do not request Binance credentials to fix this.
3. Futures REST returned 451 regional restriction. Funding and snapshots unavailable via REST here. No proxy, region switch, alternate domain or credential workaround attempted. Historical public archives and public WS independently responded successfully.
4. Trade-based vs aggregate-based reconstruction is tested separately. Exact equality is required for a PASS; aggregate mismatch is not suppressed as rounding. Never market aggregate-derived subsecond bars as individual tick history.
5. Public archive availability outside probe dates is unknown until discovery. An unavailable sample path is not evidence of entire-history absence. Coarse bookDepth is not full L2; historical bookTicker/liquidation completeness unresolved.
6. Live depth updates exist, but REST snapshots were blocked. Full local book initialization is NOT verified. Live capture is a smoke-tested prototype, not a continuous deployment. Capture gaps and crash recovery still require long-duration fault injection. No ongoing collector is left running.
7. Live receive timestamps are local processing times, not exchange publication or kernel receipt. Clock synchronization/offset calibration is not implemented.
8. Unknown metrics publication timestamps block strict causal replay; metadata guards cannot prove arbitrary external feature code is leak-free. No feature optimization, split selection or OOS inspection performed.
9. Remote adapter has mocked tests only. Authenticated upload retry reconciliation, 2GiB partition splitting, GitHub CI and end-to-end restore still need real verification. GitHub release capacity is not an availability guarantee.
10. CLI and collector serialize with a lock. Internal Pipeline class should not be called concurrently outside CLI. Metadata/logs and environment are outside data budget. Conservative output reservation may reject a partition even if its final compressed size would fit.
11. Current historical QA covers intra-partition ID/interval checks, not all cross-day continuity. Exact duplicate IDs and malformed rows fail; no silent repairs. Source revisions preserve archives; immutable revision metadata retention needs production review.
12. Funding pagination primitive exists but is not integrated as a complete normalized REST pipeline. No full historical liquidation/bookDepth parser. Feature families are extension contracts, not implemented indicators.
13. Account-specific fees, historical fee tier changes, historical spread and latency distributions are not present. No realistic cost-adjusted trading result can be inferred.

14. Individual-trade pilot contains 622/329/117 skipped IDs for BTC/ETH/SOL. Exact matching official minute candles do not explain this; all three partitions stay quarantined until source ID semantics/exclusions are independently established.
