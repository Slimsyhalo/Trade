# Data dictionary — schema v1

Source numbers remain exact strings; no ingestion rounding. Integer IDs/timestamps are int64, maker flag bool. Historical timestamps are milliseconds UTC, not Spot microseconds. All source fields are non-null under accepted schema. Source column aliases are explicit in normalize.py.

## aggTrades

| Field | Parquet type | Unit | Meaning | Precision / timezone | Nullable | Transformation |
|---|---|---|---|---|---|---|
| agg_trade_id | int64 | identifier | Exchange aggregate identifier | original lexical precision | no | integer parse |
| price | string | USDT | Executed price | original lexical precision | no | none |
| quantity | string | base asset | Executed base quantity | original lexical precision | no | none |
| first_trade_id | int64 | identifier | First underlying trade ID | original lexical precision | no | integer parse |
| last_trade_id | int64 | identifier | Last underlying trade ID; range is not guaranteed to represent recoverable event timestamps | original lexical precision | no | integer parse |
| timestamp | int64 | epoch ms | Exchange transaction timestamp | integer ms UTC | no | integer parse |
| is_buyer_maker | bool | text/flag | True: buyer passive, SELL aggressor; False: BUY aggressor | original lexical precision | no | bool parse |

Source: Binance daily aggTrades CSV.

## trades

| Field | Parquet type | Unit | Meaning | Precision / timezone | Nullable | Transformation |
|---|---|---|---|---|---|---|
| trade_id | int64 | identifier | Individual execution identifier | original lexical precision | no | integer parse |
| price | string | USDT | Executed price | original lexical precision | no | none |
| quantity | string | base asset | Executed base quantity | original lexical precision | no | none |
| quote_quantity | string | USDT | Source quote quantity | original lexical precision | no | none |
| timestamp | int64 | epoch ms | Exchange transaction timestamp | integer ms UTC | no | integer parse |
| is_buyer_maker | bool | text/flag | True: buyer passive, SELL aggressor; False: BUY aggressor | original lexical precision | no | bool parse |

Source: Binance daily trades CSV.

## klines

| Field | Parquet type | Unit | Meaning | Precision / timezone | Nullable | Transformation |
|---|---|---|---|---|---|---|
| open_time | int64 | epoch ms | Bar opening boundary | integer ms UTC | no | integer parse |
| open | string | USDT | First price in interval | original lexical precision | no | none |
| high | string | USDT | Highest price in interval | original lexical precision | no | none |
| low | string | USDT | Lowest price in interval | original lexical precision | no | none |
| close | string | USDT | Last price in interval | original lexical precision | no | none |
| volume | string | base asset | Base volume | original lexical precision | no | none |
| close_time | int64 | epoch ms | Last millisecond of interval | integer ms UTC | no | integer parse |
| quote_volume | string | USDT | Quote volume | original lexical precision | no | none |
| number_of_trades | int64 | count | Source execution count | original lexical precision | no | integer parse |
| taker_buy_base_volume | string | base asset | Aggressive buy base volume | original lexical precision | no | none |
| taker_buy_quote_volume | string | USDT | Aggressive buy quote volume | original lexical precision | no | none |
| ignore | string | text/flag | Source placeholder preserved; do not use as feature | original lexical precision | no | none |

Source: Binance daily klines CSV.

## metrics

| Field | Parquet type | Unit | Meaning | Precision / timezone | Nullable | Transformation |
|---|---|---|---|---|---|---|
| create_time | string | text/flag | Source UTC metrics timestamp | original lexical precision | no | none |
| symbol | string | text/flag | USD-M perpetual symbol | original lexical precision | no | none |
| sum_open_interest | string | base asset | Original OI base quantity level | original lexical precision | no | none |
| sum_open_interest_value | string | USDT | Original OI quote notional level | original lexical precision | no | none |
| count_toptrader_long_short_ratio | string | ratio | Top-trader account long/short ratio | original lexical precision | no | none |
| sum_toptrader_long_short_ratio | string | ratio | Top-trader position long/short ratio | original lexical precision | no | none |
| count_long_short_ratio | string | ratio | Account long/short ratio | original lexical precision | no | none |
| sum_taker_long_short_vol_ratio | string | ratio | Taker buy/sell volume ratio | original lexical precision | no | none |

Source: Binance daily metrics CSV.

## fundingRate

| Field | Parquet type | Unit | Meaning | Precision / timezone | Nullable | Transformation |
|---|---|---|---|---|---|---|
| calc_time | int64 | UTC epoch ms | Original funding settlement calculation time; millisecond jitter preserved | original lexical precision | no | integer parse |
| funding_interval_hours | int64 | hours | Source-declared funding interval; do not assume eight hours | original lexical precision | no | integer parse |
| last_funding_rate | string | signed dimensionless rate | Settled signed funding rate; not a predicted future rate | original lexical precision | no | none |

Source: Binance daily fundingRate CSV.

## Mark / index / premium candles

Use the kline envelope. Mark/index OHLC units are USDT; premium OHLC are signed dimensionless ratios. Volume/count placeholders are retained but have no trade-volume meaning.

## Added fields

| Field | Type | Unit / timezone | Nullable | Meaning / transformation |
|---|---|---|---|---|
| symbol | string | identifier | no | Partition symbol, validated for metrics |
| event_time_ms | int64 | UTC epoch ms | no | Original trade time, bar open, or parsed UTC metrics create_time |
| available_at_ms | int64 | UTC epoch ms | yes | Trade exchange time assumption; bar close+1; metrics null because historical publication unknown |
| availability_basis | string | policy label | no | Must be inspected before replay; not an observation of network latency |

## Live envelopes

receive_timestamp_ns: int64 local Unix UTC nanoseconds captured when message is written; not guaranteed kernel receipt time. kind: string event/control type. payload: untouched parsed JSON object; nested exchange E/T/U/u/pu/a/nq fields remain available. JSON.gz is raw capture; it is NOT normalized or admitted into the historical catalog. Connection_start/disconnect/sequence_gap/trade_gap are explicit continuity markers. Snapshot failures are errors, not snapshots.

## Funding monthly archive policy

Original calc_time is retained exactly. Funding schedule gap checks compare second-resolution timestamps and disclose funding_schedule_precision_ms=1000 and max_subsecond_offset_ms. last_funding_rate is a signed exact decimal lexeme. Historical publication time is unknown: available_at_ms=null, excluded from strict replay. RAW monthly archives are downloaded only when every date lies inside the authorized window.
