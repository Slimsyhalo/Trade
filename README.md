# Binance QuantLab — Complete Research Data Foundation

Phase 1 remains **incomplete**. Research infrastructure only; no strategy optimization, orders or profitability claim. BTCUSDT, ETHUSDT and SOLUSDT; Binance USD-M perpetual futures. Historical authorization: 2024-10-07 through 2026-10-07 inclusive UTC. Later live observations use their actual dates and separate ledgers.

Current primary coverage is generated from `manifest.jsonl` in `DATA_COVERAGE.md`, `data_catalog.json` and `AUDIT_SUMMARY.json`. Acquisition is resumable, SHA-256 verified and pruned only after durable checkpoint publication. Raw ZIPs, exact-decimal Parquet, provenance, QA decisions and remote receipts are retained. A downloaded file is not automatically validated.

The 70-source inventory is in [docs/DATA_SOURCE_INVENTORY.md](docs/DATA_SOURCE_INVENTORY.md) and `catalog/source_inventory.json`. Existing independent acquisition, trade admission, scientific flow transforms, causal replay, context provenance, document restoration and source-version audit modules are integrated. Each source family has separate acceptance conditions; C16–C22 are not yet globally accepted.

[Resumption evidence](docs/RESUMPTION_2026-10-08.md) describes the current fixes, source heads, working budget and workflow ownership. `foundation-resume.yml` continues original history and isolated expansion, and recovers the prior live publication backlog. `live-observation.yml` runs scheduled finite capture sessions. `foundation-observability.yml` publishes fresh counters and workflow states on the independent [operational evidence branch](https://github.com/Slimsyhalo/Trade/tree/codex/foundation-ops). Code/configurations are in Git; immutable hash-named data objects and receipts are in Releases.

Live Actions sessions cannot guarantee 24/7 continuity. Snapshot/OI REST access restrictions, historical full L2, unsampled liquidations, effective historical publication timing, funding boundary days, final historical coverage and global independent restoration remain explicit gaps. Individual market tapes require independent full-minute consistency evidence; original strict ID-gap quarantine decisions remain available. Monthly funding covers only whole authorized months; unknown availability fails strict causal replay.

[Dataset Releases](https://github.com/Slimsyhalo/Trade/releases) · [Actions](https://github.com/Slimsyhalo/Trade/actions) · [Storage plan](reports/storage_capacity_plan.json)
