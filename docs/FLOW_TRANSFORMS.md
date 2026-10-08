# Reproducible tape-derived research variables

`flow_windows` computes observed aggressor buy/sell base volume from the maker
flag, volume delta, explicitly anchored CVD, VWAP and exact volume at price.
It accepts admitted individual executions and retains source row counts.
Missing windows are not fabricated. Input availability uncertainty propagates;
window-close assumptions remain labeled and do not certify strict causal replay.
No tape-based OFI, reconstructed L2, trading orders or optimized signals exist.

Decimal calculations use explicit precision 50 and ROUND_HALF_EVEN independent
of caller context. VWAP preserves its exact numerator and denominator because a
ratio can have a nonterminating decimal expansion. Profiles conserve total base
volume, and buy plus sell volume must equal total volume. CVD's reset/initial
anchor is explicit per partition; concatenating independently reset partitions
is not a continuous CVD series.

`build_flow.py` binds every input to a source SHA and an independent individual
market-tape admission certificate. Actual local reconstruction consumed
9,424,949 executions from the three 2024-10-07 tapes and generated 4,320 minute
rows. Recomputing into separate absent paths produced byte-identical Parquet
hashes for all three assets. Every output minute agrees with official candle
volume, taker buy volume, quote notional and execution count.

Evidence: `reports/flow_derivation.json`, `reports/flow_reproducibility.json`.
The remote context workflow can independently restore admitted Parquet from
an immutable expansion commit, recompute it in a fresh hosted checkout, compare
pilot hashes, publish derived assets and restore them again. Source availability
is a separate gate; it never writes the expansion ledger. Until that execution
is proven, local determinism does not certify remote restoration or full C18
scope. Required book-derived features remain pending synchronized book inputs.
