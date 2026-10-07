# Binance QuantLab — Data Foundation pilot

**Status: INCOMPLETE / BLOCKED. No strategy, orders or profitability claims.**

BTCUSDT · ETHUSDT · SOLUSDT, Binance USD-M perpetual. Authorized historical bounds: 2024-10-07 through 2026-10-07 UTC inclusive. Only sampled data listed in `data_catalog.json` exists; the two-year extraction has not run.

Implemented and tested locally: public archive download/checksums, explicit schemas, Parquet/ZSTD, exact decimal precision, disk budget, resumable manifests, partition QA, causal replay primitives, bar reconstruction, current routed WebSocket capture and GitHub release adapter (mock-tested).

**Publication update (2026-10-07):** GitHub connector write access is verified. Code publication is in progress; datasets are not yet remotely verified. The local shell has no GitHub write credential. **REST blocker:** Binance Futures returns HTTP 451 from this environment. Archive downloads and public WebSockets work.

Read in order:
1. AUDIT_SUMMARY.md / AUDIT_SUMMARY.json — actual results and unresolved gates.
2. DATA_COVERAGE.md / data_catalog.json — downloaded coverage and every missing partition.
3. QA_REPORT.md — tests, hashes and reconstruction discrepancies.
4. REPRODUCIBILITY.md — install, sync, validate, upload and restore.
5. RESEARCH_HANDOFF.md — interpretation and safeguards for the next researcher.

```bash
python bootstrap.py
.venv/bin/python -m pytest -q
.venv/bin/python quantlab.py status
.venv/bin/python quantlab.py validate
```

Data files are excluded from ordinary Git. Original ZIPs stay unmodified. Remote deletion of local originals is disabled until successful full readback verification. No Binance keys are used. No capital-connected capability exists.

This pilot is not an approved C15 foundation. Complete the checkpoint gates in CHECKPOINTS.md before moving to Phase 2.
