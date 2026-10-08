# C14 replay source checkpoint — 2026-10-08

This checkpoint adds `MarketReplayEngine` and `align_asof`. It is a research
foundation, without strategy selection or simulated execution. C14 remains
partial and C15 remains incomplete.

## Input admission and causal policy

Select exact manifest keys. Each input must have PASS source QA and status,
schema version 1, a matching local Parquet SHA256, byte count, row count and
Arrow schema. Missing local inputs fail and require a separate verified restore.
No download or file deletion occurs. Paths and symlinks must stay within root.
The engine opens one partition per stream and reads batches of at most 10,000
rows (default 1,000), with at most 32 streams. These are logical buffering bounds;
they are not a measured upper bound on PyArrow process memory for arbitrary files.

Streams are merged by `available_at_ms`, retaining exact decimal strings. Unknown
availability, unsupported availability bases, event/availability order regressions,
future events, wrong symbols, partition-window violations and trade-ID discontinuity
within/across adjacent selected days fail. Nonadjacent selected days are explicit
coverage gaps; the engine makes no continuity claim about their missing intervals.

Strict mode accepts only `received`. Historical exchange-time zero-latency and bar
close-boundary assumptions require `allow_exchange_assumption=True`. This opt-in
does not accept unknown funding/OI publication timing. It does not establish
realistic network latency. Caller-supplied availability metadata is not proof that
the historical exchange published a value at that moment.

`align_asof` consumes all observations available at decision time T before producing
the snapshot. Cross-stream ties have deterministic symbol/dataset ordering, without
claiming an exchange-wide sequence. Only backward observations are returned.
Missing and stale symbols return null with a reason. Staleness uses event age,
so delayed old data cannot appear fresh merely because it just arrived. No
interpolation/backfill occurs. Each returned observation is copied. Unknown timing
and unsafe inputs fail. A future record can be buffered internally but is never
returned in an earlier snapshot.

## Usage

Use a local acquisition/restore root containing the manifest and matching files:

```python
from quantlab_core.replay_engine import MarketReplayEngine, align_asof

keys = [f'{s}/klines/2024-10-07' for s in ('BTCUSDT','ETHUSDT','SOLUSDT')]
engine = MarketReplayEngine.from_manifest(
    root, keys, allow_exchange_assumption=True, batch_size=1000)
snapshots = align_asof(
    engine.events(1728345600000), range(1728259200000, 1728345600001, 60000),
    symbols=['BTCUSDT','ETHUSDT','SOLUSDT'], dataset='klines',
    max_age_ms=60000, allow_exchange_assumption=True)
for snapshot in snapshots:
    # Check snapshot['states'] before using observations.
    pass
```

`replay_audit.py --root ROOT --key SYMBOL/DATASET/DAY --until-ms T` emits a
deterministic replay digest and input receipts. Repeat `--key` for each partition.
Historical input requires `--allow-exchange-assumption`. Add the three options
`--decision-start-ms`, `--decision-step-ms`, `--max-age-ms` together to audit a
single-dataset cross-asset join. A failure writes FAILED evidence and exits nonzero;
PASS only describes emitted events in the selected scope.

## Observed evidence

The full suite passed 82 tests. New adversarial cases cover quarantine/integrity,
unknown/unsupported timing, future perturbations, stale late arrivals, equal-time
joins, missing assets, cross-day ID gaps, bounded batches and early resource release.

Actual original pilot inputs (2024-10-07 UTC; no new data acquisition) passed:

| Scope | Emitted rows | Evidence |
|---|---:|---|
| BTC/ETH/SOL aggTrades | 3,428,256 | `reports/replay_aggTrades_real.json` |
| BTC/ETH/SOL official 1m klines | 4,320 | `reports/replay_klines_real.json` |
| 1m cross-asset snapshots | 1,441 decisions | Same klines report; 4,320 available observations and 3 initially missing |

The reports retain each input checksum, declared rows, cutoff, policy and replay
digest. These results do not clear quarantined individual trades, reconstruct
unavailable order books, establish funding/OI causality or prove two-year coverage.

Published on an isolated branch to preserve the active historical writer and queued
funding integration. Main integration must wait for a safe writer boundary. This
checkpoint has not been executed by the queued acquisition workflow.

Implementation reference: Apache Arrow 25.0.1 ParquetFile `iter_batches`,
`schema_arrow` and `close` documentation:
https://arrow.apache.org/docs/python/generated/pyarrow.parquet.ParquetFile.html
