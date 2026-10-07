> Publication update 2026-10-07: the former GitHub 403 is resolved. The code and 18 passing pilot partitions (36 Release assets) are published; full readback and an isolated restoration passed. See reports/remote_execution.json. The original pilot findings below remain historical evidence; full-window extraction and C15 are still incomplete.

# Quant research handoff — NOT READY FOR STRATEGY DISCOVERY

**DO NOT ASSUME DATA EXISTS UNLESS LISTED IN THE CATALOG.**

Objective: an auditable read-only Binance USD-M perpetual foundation for BTCUSDT, ETHUSDT and SOLUSDT. Requested window 2024-10-07 00:00 UTC through 2026-10-07 end-of-day UTC; no earlier data. The explicit inclusive dates span 731 calendar days. Only pilot data has been acquired; the two-year extraction is not complete.

Start with AUDIT_SUMMARY.json, data_catalog.json, manifest.jsonl, QA_REPORT.md and LIMITATIONS.md. Catalog coverage counts passing local historical partitions, NOT remote backup and NOT full research readiness. All missing partitions are explicit. No optimization, model fitting, signal or profitability claim belongs in this phase.

Location: relative paths are in each manifest record. Remote fields are null until GitHub readback verification. The integration rejected a write to Slimsyhalo/Trade with HTTP 403. No data was pushed. Download the preserved pilot package, then restore GitHub access before production.

Load a partition:
```python
import pyarrow.parquet as pq
from decimal import Decimal
rows = pq.ParquetFile(path).iter_batches(batch_size=10_000)
# Decimal(row['price']) preserves source decimal precision.
```

Bar reconstruction:
```python
from quantlab_core.research import bars
# events must be sorted by event_time_ms / trade ID and contain maker flags.
result = bars(events, seconds=60)  # also 1,5,15,30,180,300,900
```
AggTrades are timestamped aggregates; they cannot recover each original execution time. Inspect reports/bar_comparison_*.json before claiming minute equivalence. Price and volume matching is distinct from trade-count equality. Empty intervals are absent, not fabricated.

Replay: `replay(streams, until_ms=T)` exposes only current events whose availability <= T. Strict mode requires observed received availability. Historical latency assumptions must be explicitly enabled with allow_exchange_assumption=True. Unknown historical publication timing (metrics/OI) is rejected even in that mode. Completed bars become available at close boundary +1ms, never open time. No trade model can claim realistic latency from exchange timestamps alone.

Feature extension protocol: declare inputs, source availability and dependencies; require every dependency available_at <= decision time. Use trailing windows, no centered windows/backfill/negative shifts/targets. Add adversarial tests with future input perturbations. Current guards validate declared metadata; they do NOT magically inspect arbitrary pandas code for leakage. Feature families planned: returns/momentum/volatility, volume/delta/CVD, funding/OI/premium, microstructure, cross-asset lead/lag. They are not optimized or fully implemented.

Cross-asset joins must be backward as-of on availability, with explicit staleness tolerance. Never future-fill SOL/ETH with later BTC observations. Session labels should derive from UTC or IANA America/Argentina/Buenos_Aires. 24/7 extraction is unrestricted by trading hours.

New datasets: add an explicit source contract and dictionary, probe availability and sizes, normalize versioned schema, implement QA and causality policy, generate checksums, upload+restore, then admit to catalog. Unsupported sources must fail rather than silently coerce.

Future research: chronological train/validation/final OOS, freeze and version split before analysis; keep final OOS unexamined during selection. No split has been chosen. Cost model must separately include commission tier effective dates, spread, slippage, funding and latency; account fees and historic executable spreads are currently absent. No future results can assume zero costs.
