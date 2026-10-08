# Individual market-tape QA decision

The original validator treats every skipped identifier as missing executions.
Binance's archive README identifies `/fapi/v1/trades` as the individual-trade
source. The current recent-trades documentation describes order-book market
fills, excludes insurance-fund/ADL transactions and does not guarantee global
identifier continuity. Documentation of exclusions is not evidence that any
specific missing ID belongs to those event types.

Additional official CHECKSUM-verified samples cover BTCUSDT, ETHUSDT and SOLUSDT
on 2024-12-07, 2025-06-07 and 2026-09-07. They contain 18,779,587 rows and 39,026
skipped identifiers. All nine reproduce every field of all 1,440 official minute
bars exactly: OHLC, base/quote volume, execution count and taker buy base/quote
volume. The original three 2024-10-07 tapes also reproduce official bars exactly.
Evidence: `reports/individual_trade_diagnosis.json` and
`catalog/qa_revisions/individual_trades.json`.

Decision: ID discontinuities remain recorded diagnostics. An individual market
tape can be admitted only with unique ascending identifiers, ordered in-range
timestamps, valid schema/amounts, source hashes and exact full-day official-bar
consistency. Missing executions, malformed data or conflicting bars keep the
tape quarantined. The original strict QA is retained in every certificate.
`quantlab_core/trade_admission.py` implements this separate evidence gate;
the incumbent validator and active main manifest remain preserved until safe
integration. The expanded acquisition pipeline applies the gate partition by
partition and stores independent verification bars remotely.

This certifies the official market-tape scope, not all global identifier event
types, hidden executions or participant identities. Specific gap causes remain
undetermined. Historical latency/publication assumptions remain separate from
data completeness. Passing this gate does not authorize strict causal replay
with unknown availability or any trading strategy.

Regression cases admit a skipped ID with exact full-minute consistency, reject
a truly missing market trade and retain schema failures despite bar agreement.

Sources:
https://github.com/binance/binance-public-data and
https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data .
