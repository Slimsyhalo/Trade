# Binance QuantLab — Data Foundation

**Phase 1 incomplete. Remote pilot verified; historical expansion starting.**

BTCUSDT, ETHUSDT and SOLUSDT — Binance USD-M perpetual futures. Authorized window: 2024-10-07 through 2026-10-07 UTC. No trading, strategy optimization or profitability claims.

## Verified results

- 38 local tests pass; the initial remote job also passed its 31-test suite.
- 18 passing pilot partitions were reconstructed, uploaded as 36 immutable hash-named Release assets and fully read back for SHA-256/size verification.
- A restored BTC aggTrades Parquet matched its manifest: 1,459,023 rows.
- The pilot covers 2024-10-07 only. Its 3,428,256 aggregate trades are not two years of history.
- Three individual-trade partitions remain quarantined locally due to ID gaps.

## Current acquisition

The Historical data acquisition workflow scans the authorized range for aggTrades, klines, markPriceKlines, indexPriceKlines, premiumIndexKlines and metrics. It checkpoints every 25 partitions, pushes manifests before pruning, respects the 2 GB data budget and pauses after four hours. It can be resumed through workflow_dispatch. It stops on failed QA or remote verification; unavailable archives are recorded explicitly.

The 72-archive stratified storage review is complete; aggTrades acquisition is enabled. Individual trades still require ID-gap investigation. Funding and full live order-book readiness remain unresolved. A successful pilot is not a complete C15 foundation.

[Release datasets](https://github.com/Slimsyhalo/Trade/releases) · [Actions](https://github.com/Slimsyhalo/Trade/actions)

Current evidence: reports/remote_execution.json, reports/historical_execution.json (when the first historical checkpoint is written), manifest.jsonl and data_catalog.json. Original audit reports describe the initial local pilot; their new publication notices supersede the former GitHub 403 blocker.

**DO NOT ASSUME DATA EXISTS UNLESS LISTED IN THE CATALOG.**

See REPRODUCIBILITY.md and RESEARCH_HANDOFF.md for schemas, restoration and research safeguards.

## Resume checkpoint — 2026-10-08

The previous historical job stopped at 502 verified partitions due to GitHub rate limiting. The resumed client paces API calls, caches release metadata and distinguishes rate-limit waits from permission errors. Tests cover rejected-upload body rewinding and prevent retries of ambiguous mutations. Existing remote partitions are skipped. Current progress is recorded in reports/historical_execution.json.
