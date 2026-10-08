# Reproducible derivative research descriptors

C18 remains globally unaccepted. This checkpoint is on `codex/c18-derivatives`, independently of active acquisition writers. No strategy, orders or prediction/optimization is introduced.

## Products

`basis_close_1m` aligns exact one-minute mark/index intervals, preserving original closing-price strings. It stores their signed difference and relative difference with exact numerator/denominator and explicit 50-digit rounding. Observation time is the bar close, never its open. This is a sampled bar-close proxy, not simultaneous executable bid/ask basis. Unequal timestamp sets, duplicate times, cross-symbol joins, unequal boundaries and invalid prices are rejected rather than silently joined/filled.

`oi_change_5m` stores differences between actually observed native-unit Open Interest levels and values, original level strings, both timestamps and interval length. It separately exposes a cadence-matched difference only when the declared 300,000 ms cadence matches. Missing observations are never replaced by zero changes. A restored previous-day metrics partition supplies the midnight transition and is included in source lineage; at the authorized start or without the preceding partition, the first difference stays null. Historical contract/base-unit conversion is not inferred.

Effective availability is no earlier than every contributing input. Unknown historical metrics availability remains null, and assumed bar-close availability is explicitly uncertified. Every product records `strict_causal_replay_certified=false`. Descriptive analysis can use the measured levels, but these files do not certify absence of historical information leakage for trading simulation.

## Provenance and storage

Each input is restored by matching SHA-256/byte receipt from an immutable main manifest snapshot, and Parquet row counts are checked before derivation. Lineage includes original RAW hashes, normalized hashes, source keys, previous-day hashes when present and transform version. Products have explicit typed schemas, UTC milliseconds, exact decimal strings and embedded lineage. The identity is a full SHA-256 over version plus source hashes; changed source versions produce separate keys and filenames.

Every daily set is independently recomputed in another directory and must match byte for byte before publication. GitHub Releases publication includes full readback. One restored output per product family verifies hashes, row counts and embedded lineage. The product catalog is durably committed on the separate branch before disposable input/output copies are removed. Existing original archives and acquisition manifests are never modified.

`remote_derivatives.py` works through every currently ready mark/index/metrics daily set in one immutable main snapshot. It skips only hash/size-matching product receipts, enforces a 190-minute acquisition budget and records runtime/CPU time separately. A bounded result is not full two-year recomputation. Subsequent runs read a fresh main snapshot and process only newly ready or newly versioned sets.

## Actual validation

190 tests pass locally. Three BTCUSDT original normalized partitions for 2024-10-07 were independently restored from Releases with matching hashes and row counts. The actual sources produced 1,440 sampled-basis and 288 OI-change rows. A second full build with fixed schemas/lineage matched byte for byte. All 288 OI output availabilities remained null; basis outputs retain boundary assumptions and their uncertified causal flag. Exact source receipts and output hashes are in `reports/independent_derivative_source_restoration.json` and `reports/C18_derivative_real_probe.json`.

The dedicated hosted workflow starts on this branch publication and performs restoration, repeated recomputation, readback and sampled output restoration for the currently available corpus. Its schedule takes effect only after safe integration onto default `main`; active main writers must first finish or yield their lock. No claim is made that a schedule defined only on a non-default branch is active.
