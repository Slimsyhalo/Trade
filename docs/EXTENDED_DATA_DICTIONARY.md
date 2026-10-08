# Extended scientific storage schemas

Generated from implemented normalizers and a remotely restored hash-bound flow Parquet. Schema evidence does not certify acquired coverage. Original futures field meanings remain in DATA_DICTIONARY.md.

## core_futures

Original timestamps milliseconds, exact numeric lexemes retained. Mark/index OHLC is quote/base price; premium OHLC is signed dimensionless ratio. Placeholder volumes/counts are not executions.

## spot

Original timestamps and source_time_unit retained: milliseconds before 2025-01-01, microseconds from that date. event_time_us is exact normalized UTC; bar-close availability is an assumption.

## percentage_depth

UTC text seconds mapped to integer microseconds; signed cumulative percentage bands are not L2 price levels or synchronized snapshots. Staleness and completeness require separate QA.

## flow

Exact decimal strings; 50 significant-digit HALF_EVEN VWAP with numerator/denominator. Explicit UTC partition CVD reset. Output availability cannot precede window closure or contributing input availability; historical receipt remains uncertified.

## live

JSONL gzip envelope: receive_timestamp_ns integer, kind string, payload original parsed object. E/T exchange milliseconds where present; U/u/pu quote/depth identifiers unchanged. Connection and continuity markers retained; local clock regressions never silently reordered. Raw messages do not certify synchronized L2.

## context

context-1 retains source URL/hash, publication claim, original timezone/DST label and observed acquisition time. Historical effective availability is null and original historical vintage is uncertified. Empty revision lineage does not prove no revisions.

## nullability

Arrow storage nullability is distinct from QA. Unknown availability is retained as null; no zero-filled missing observations or universal continuity rules.

## aggTrades

| Field | Storage type | Unit | Storage nullable |
|---|---|---|---|
| agg_trade_id | int64 | exchange aggregate identifier | True |
| price | string | See dataset-specific semantic policy | True |
| quantity | string | base asset | True |
| first_trade_id | int64 | exchange identifier | True |
| last_trade_id | int64 | exchange identifier | True |
| timestamp | int64 | See dataset-specific semantic policy | True |
| is_buyer_maker | bool | See dataset-specific semantic policy | True |
| symbol | string | See dataset-specific semantic policy | True |
| event_time_ms | int64 | UTC epoch milliseconds | True |
| available_at_ms | int64 | UTC epoch milliseconds; nullable | True |
| availability_basis | string | See dataset-specific semantic policy | True |

## trades

| Field | Storage type | Unit | Storage nullable |
|---|---|---|---|
| trade_id | int64 | exchange source identifier | True |
| price | string | See dataset-specific semantic policy | True |
| quantity | string | base asset | True |
| quote_quantity | string | quote asset | True |
| timestamp | int64 | See dataset-specific semantic policy | True |
| is_buyer_maker | bool | See dataset-specific semantic policy | True |
| symbol | string | See dataset-specific semantic policy | True |
| event_time_ms | int64 | UTC epoch milliseconds | True |
| available_at_ms | int64 | UTC epoch milliseconds; nullable | True |
| availability_basis | string | See dataset-specific semantic policy | True |

## klines

| Field | Storage type | Unit | Storage nullable |
|---|---|---|---|
| open_time | int64 | See dataset-specific semantic policy | True |
| open | string | See dataset-specific semantic policy | True |
| high | string | See dataset-specific semantic policy | True |
| low | string | See dataset-specific semantic policy | True |
| close | string | See dataset-specific semantic policy | True |
| volume | string | base asset | True |
| close_time | int64 | See dataset-specific semantic policy | True |
| quote_volume | string | quote asset | True |
| number_of_trades | int64 | count | True |
| taker_buy_base_volume | string | base asset | True |
| taker_buy_quote_volume | string | quote asset | True |
| ignore | string | See dataset-specific semantic policy | True |
| symbol | string | See dataset-specific semantic policy | True |
| event_time_ms | int64 | UTC epoch milliseconds | True |
| available_at_ms | int64 | UTC epoch milliseconds; nullable | True |
| availability_basis | string | See dataset-specific semantic policy | True |

## metrics

| Field | Storage type | Unit | Storage nullable |
|---|---|---|---|
| create_time | string | See dataset-specific semantic policy | True |
| symbol | string | See dataset-specific semantic policy | True |
| sum_open_interest | string | See dataset-specific semantic policy | True |
| sum_open_interest_value | string | See dataset-specific semantic policy | True |
| count_toptrader_long_short_ratio | string | See dataset-specific semantic policy | True |
| sum_toptrader_long_short_ratio | string | See dataset-specific semantic policy | True |
| count_long_short_ratio | string | See dataset-specific semantic policy | True |
| sum_taker_long_short_vol_ratio | string | See dataset-specific semantic policy | True |
| event_time_ms | int64 | UTC epoch milliseconds | True |
| available_at_ms | int64 | UTC epoch milliseconds; nullable | True |
| availability_basis | string | See dataset-specific semantic policy | True |

## fundingRate

| Field | Storage type | Unit | Storage nullable |
|---|---|---|---|
| calc_time | int64 | See dataset-specific semantic policy | True |
| funding_interval_hours | int64 | See dataset-specific semantic policy | True |
| last_funding_rate | string | See dataset-specific semantic policy | True |
| symbol | string | See dataset-specific semantic policy | True |
| event_time_ms | int64 | UTC epoch milliseconds | True |
| available_at_ms | int64 | UTC epoch milliseconds; nullable | True |
| availability_basis | string | See dataset-specific semantic policy | True |

## spot_trades

| Field | Storage type | Unit | Storage nullable |
|---|---|---|---|
| trade_id | int64 | exchange source identifier | True |
| price | string | See dataset-specific semantic policy | True |
| quantity | string | base asset | True |
| quote_quantity | string | quote asset | True |
| timestamp | int64 | See dataset-specific semantic policy | True |
| is_buyer_maker | bool | See dataset-specific semantic policy | True |
| is_best_match | bool | See dataset-specific semantic policy | True |
| symbol | string | See dataset-specific semantic policy | True |
| source_time_unit | string | See dataset-specific semantic policy | True |
| event_time_us | int64 | UTC epoch microseconds | True |
| available_at_us | int64 | UTC epoch microseconds; nullable | True |
| availability_basis | string | See dataset-specific semantic policy | True |

## spot_klines_1m

| Field | Storage type | Unit | Storage nullable |
|---|---|---|---|
| open_time | int64 | See dataset-specific semantic policy | True |
| open | string | See dataset-specific semantic policy | True |
| high | string | See dataset-specific semantic policy | True |
| low | string | See dataset-specific semantic policy | True |
| close | string | See dataset-specific semantic policy | True |
| volume | string | base asset | True |
| close_time | int64 | See dataset-specific semantic policy | True |
| quote_volume | string | quote asset | True |
| number_of_trades | int64 | count | True |
| taker_buy_base_volume | string | base asset | True |
| taker_buy_quote_volume | string | quote asset | True |
| ignore | string | See dataset-specific semantic policy | True |
| symbol | string | See dataset-specific semantic policy | True |
| source_time_unit | string | See dataset-specific semantic policy | True |
| event_time_us | int64 | UTC epoch microseconds | True |
| available_at_us | int64 | UTC epoch microseconds; nullable | True |
| availability_basis | string | See dataset-specific semantic policy | True |

## um_bookDepth_summary

| Field | Storage type | Unit | Storage nullable |
|---|---|---|---|
| timestamp | string | See dataset-specific semantic policy | True |
| percentage | string | signed percentage distance band; not a price level | True |
| depth | string | cumulative base asset quantity at percentage band | True |
| notional | string | cumulative quote notional at percentage band | True |
| symbol | string | See dataset-specific semantic policy | True |
| source_time_unit | string | See dataset-specific semantic policy | True |
| event_time_us | int64 | UTC epoch microseconds | True |
| available_at_us | int64 | UTC epoch microseconds; nullable | True |
| availability_basis | string | See dataset-specific semantic policy | True |

## tape-flow-1

| Field | Storage type | Unit | Storage nullable |
|---|---|---|---|
| window_start_us | int64 | UTC epoch microseconds | True |
| window_end_us | int64 | UTC epoch microseconds | True |
| source_rows | int64 | count | True |
| buy_base_volume | string | base asset | True |
| sell_base_volume | string | base asset | True |
| total_base_volume | string | base asset | True |
| price_quantity_notional | string | quote asset | True |
| volume_delta | string | base asset | True |
| cvd | string | base asset from explicit anchor | True |
| cvd_anchor | string | See dataset-specific semantic policy | True |
| cvd_initial | string | base asset | True |
| vwap_numerator | string | quote asset | True |
| vwap_denominator | string | base asset | True |
| vwap | string | quote per base asset | True |
| vwap_decimal_precision | int64 | decimal significant digits | True |
| vwap_rounding | string | See dataset-specific semantic policy | True |
| volume_at_price_json | string | ordered [exact price string, base quantity string] pairs | True |
| available_at_us | int64 | UTC epoch microseconds; nullable | True |
| availability_basis | string | See dataset-specific semantic policy | True |
| input_availability_bases | string | See dataset-specific semantic policy | True |
| continuity | string | See dataset-specific semantic policy | True |
| symbol | string | See dataset-specific semantic policy | True |
| source_parquet_sha256 | string | See dataset-specific semantic policy | True |
| source_raw_sha256 | string | See dataset-specific semantic policy | True |
| transform_version | string | See dataset-specific semantic policy | True |
| source_admission_scope | string | See dataset-specific semantic policy | True |

