# Research data source inventory

Research only. Phase 1 remains open. Availability classifications do not certify acquired coverage.

Generated reproducibly: `python source_foundation.py --main-sha 61b571698c36a128fc366bc0ca2dadec416e7a06`.

Requested historical window: 2024-10-07 through 2026-10-07 inclusive UTC, BTCUSDT / ETHUSDT / SOLUSDT. Live observations use their actual later capture timestamps and a separate ledger.

Official archive probes and bounded bucket listings: `reports/extended_source_probes.json`. Archive spot timestamps change from milliseconds to microseconds on 2025-01-01; retain original precision. Empty historical bookTicker/liquidation prefixes establish absence from this official archive window only. Commercial L2 providers remain alternatives.

Exact provider bounds, licensing, quotas and limitations are retained in the structured inventory. Null bounds mean not established. External release values require original-release provenance and revision lineage; current revised series and current calendars cannot substitute.

| Dataset | Family | Kind | Availability | Priority | Implementation |
|---|---|---|---|---:|---|
| um_trades | operations | ORIGINAL | HISTORICAL_AVAILABLE | 1 | core_quarantined |
| um_aggTrades | operations | ORIGINAL | HISTORICAL_AVAILABLE | 1 | core_running |
| um_klines_1m | operations | ORIGINAL | HISTORICAL_AVAILABLE | 1 | core_running |
| um_mark_price | derivatives | ORIGINAL | HISTORICAL_AVAILABLE | 1 | core_running |
| um_index_price | derivatives | ORIGINAL | HISTORICAL_AVAILABLE | 1 | core_running |
| um_premium_index | derivatives | ORIGINAL | HISTORICAL_AVAILABLE | 1 | core_running |
| um_metrics | derivatives | ORIGINAL | HISTORICAL_AVAILABLE | 1 | core_running |
| um_funding_settled | derivatives | ORIGINAL | PARTIALLY_AVAILABLE | 1 | funding_queued |
| um_funding_rules | execution | ORIGINAL | PARTIALLY_AVAILABLE | 1 | rest_blocked |
| um_bookDepth_summary | order_book | ORIGINAL | HISTORICAL_AVAILABLE | 1 | parser_pending |
| um_bookTicker_archive | order_book | ORIGINAL | UNAVAILABLE | 1 | official_window_listing_empty |
| um_liquidation_archive | derivatives | ORIGINAL | UNAVAILABLE | 1 | official_window_listing_empty |
| um_depth_updates_live | order_book | ORIGINAL | LIVE_ONLY | 0 | source_fault_tested |
| um_bookTicker_live | order_book | ORIGINAL | LIVE_ONLY | 0 | source_fault_tested |
| um_liquidations_live | derivatives | ORIGINAL | LIVE_ONLY | 0 | source_fault_tested |
| um_aggTrades_live | operations | ORIGINAL | LIVE_ONLY | 0 | source_fault_tested |
| um_mark_funding_live | derivatives | ORIGINAL | LIVE_ONLY | 0 | source_fault_tested |
| um_depth_snapshot_live | order_book | ORIGINAL | LIVE_ONLY | 0 | rest_blocked |
| um_open_interest_live | derivatives | ORIGINAL | LIVE_ONLY | 0 | rest_blocked |
| um_basis_rest | derivatives | ORIGINAL | PARTIALLY_AVAILABLE | 2 | rest_blocked |
| um_taker_buy_sell_rest | derivatives | ORIGINAL | PARTIALLY_AVAILABLE | 2 | rest_blocked |
| um_position_ratios_rest | derivatives | ORIGINAL | PARTIALLY_AVAILABLE | 2 | rest_blocked |
| spot_trades | related_markets | ORIGINAL | HISTORICAL_AVAILABLE | 2 | parser_pending |
| spot_aggTrades | related_markets | ORIGINAL | HISTORICAL_AVAILABLE | 3 | discovery_running |
| spot_klines_1m | related_markets | ORIGINAL | HISTORICAL_AVAILABLE | 2 | parser_pending |
| spot_klines_1s | related_markets | ORIGINAL | HISTORICAL_AVAILABLE | 3 | evaluated |
| coinbase_btc_eth_sol | related_markets | ORIGINAL | PARTIALLY_AVAILABLE | 3 | evaluated |
| crypto_market_cap | related_markets | ORIGINAL | PARTIALLY_AVAILABLE | 3 | probe_pending |
| crypto_global_dominance | related_markets | ORIGINAL | PROVIDER_RESTRICTED | 3 | provider_gate |
| macro_calendar | external_context | ORIGINAL | HISTORICAL_AVAILABLE | 1 | parser_pending |
| macro_cpi | external_context | ORIGINAL | HISTORICAL_AVAILABLE | 1 | parser_pending |
| macro_ppi | external_context | ORIGINAL | HISTORICAL_AVAILABLE | 1 | parser_pending |
| macro_nfp_employment | external_context | ORIGINAL | HISTORICAL_AVAILABLE | 1 | parser_pending |
| macro_jolts | external_context | ORIGINAL | HISTORICAL_AVAILABLE | 2 | parser_pending |
| fomc_calendar_statements | external_context | ORIGINAL | HISTORICAL_AVAILABLE | 1 | parser_pending |
| fomc_minutes_sep | external_context | ORIGINAL | HISTORICAL_AVAILABLE | 2 | parser_pending |
| ecb_decisions | external_context | ORIGINAL | HISTORICAL_AVAILABLE | 2 | parser_pending |
| macro_vintages | external_context | ORIGINAL | PARTIALLY_AVAILABLE | 2 | credential_gate |
| financial_crypto_news_metadata | external_context | ORIGINAL | PARTIALLY_AVAILABLE | 2 | parser_pending |
| news_original_text | external_context | ORIGINAL | PROVIDER_RESTRICTED | 3 | provider_gate |
| regulatory_events | external_context | ORIGINAL | PARTIALLY_AVAILABLE | 2 | parser_pending |
| binance_announcements | external_context | ORIGINAL | PARTIALLY_AVAILABLE | 1 | discovery_pending |
| market_incidents | external_context | ORIGINAL | PARTIALLY_AVAILABLE | 1 | discovery_pending |
| vix_daily | related_markets | ORIGINAL | PARTIALLY_AVAILABLE | 3 | licensing_gate |
| historical_l2_tardis | order_book | ORIGINAL | PROVIDER_RESTRICTED | 1 | provider_gate |
| historical_l2_kaiko | order_book | ORIGINAL | PROVIDER_RESTRICTED | 2 | provider_gate |
| execution_contract_filters | execution | ORIGINAL | PARTIALLY_AVAILABLE | 0 | rest_blocked |
| execution_fees_public | execution | ORIGINAL | PARTIALLY_AVAILABLE | 1 | documentation_pending |
| execution_fees_account | execution | ORIGINAL | NOT_APPLICABLE | 3 | scope_excluded |
| execution_latency_observed | execution | ORIGINAL | LIVE_ONLY | 0 | partial_clock_unknown |
| full_l3_participant_orders | order_book | ORIGINAL | NOT_APPLICABLE | 3 | scope_excluded |
| insurance_adl_context | derivatives | ORIGINAL | PARTIALLY_AVAILABLE | 3 | evaluated |
| continuous_contract_klines | operations | ORIGINAL | HISTORICAL_AVAILABLE | 3 | scope_evaluated |
| trade_aggressor_side | microstructure | DERIVED | DERIVABLE | 2 | contract_defined_not_certified |
| buy_sell_volume_delta | microstructure | DERIVED | DERIVABLE | 2 | contract_defined_not_certified |
| cvd | microstructure | DERIVED | DERIVABLE | 2 | contract_defined_not_certified |
| vwap | microstructure | DERIVED | DERIVABLE | 2 | contract_defined_not_certified |
| volume_at_price_profile | microstructure | DERIVED | DERIVABLE | 2 | contract_defined_not_certified |
| temporal_aggregations | operations | DERIVED | DERIVABLE | 2 | contract_defined_not_certified |
| best_quote_spread | order_book | DERIVED | DERIVABLE | 2 | contract_defined_not_certified |
| book_liquidity_imbalance | microstructure | DERIVED | DERIVABLE | 2 | contract_defined_not_certified |
| order_flow_imbalance | microstructure | DERIVED | DERIVABLE | 2 | contract_defined_not_certified |
| liquidity_walls | microstructure | ESTIMATE | DERIVABLE | 2 | contract_defined_not_certified |
| absorption_pressure | microstructure | ESTIMATE | DERIVABLE | 2 | contract_defined_not_certified |
| oi_changes | derivatives | DERIVED | DERIVABLE | 2 | contract_defined_not_certified |
| perpetual_basis | derivatives | DERIVED | DERIVABLE | 2 | contract_defined_not_certified |
| futures_spot_spread | related_markets | DERIVED | DERIVABLE | 2 | contract_defined_not_certified |
| cross_asset_volatility_correlation | related_markets | DERIVED | DERIVABLE | 2 | contract_defined_not_certified |
| regime_descriptors | related_markets | ESTIMATE | DERIVABLE | 2 | contract_defined_not_certified |
| execution_cost_scenarios | execution | ESTIMATE | DERIVABLE | 2 | contract_defined_not_certified |

## um_trades

Source checksums and structural QA; ID gaps unresolved, retain quarantine and cross-dataset evidence

Resolution: tick. Schema: id,price,qty,quote_qty,time,is_buyer_maker. Units: base units; USDT; ms UTC.

Temporal availability: Original source timestamps retained; publication latency unknown unless explicitly observed.

Source: https://github.com/binance/binance-public-data.

## um_aggTrades

Not a lossless substitute for individual executions; RPI tags/normal quantity differ between archive and live

Resolution: aggregate_tick. Schema: agg_trade_id,price,quantity,first_trade_id,last_trade_id,timestamp,is_buyer_maker. Units: base units; USDT; ms UTC.

Temporal availability: Original source timestamps retained; publication latency unknown unless explicitly observed.

Source: https://github.com/binance/binance-public-data.

## um_klines_1m

Full-minute original observations; no fabricated empty bars

Resolution: 1m. Schema: OHLCV,quote_volume,trade_count,taker_buy_volume. Units: USDT; base; UTC ms.

Temporal availability: Original source timestamps retained; publication latency unknown unless explicitly observed.

Source: https://github.com/binance/binance-public-data.

## um_mark_price

Placeholder volume is not traded volume

Resolution: 1m. Schema: mark OHLC. Units: USDT; UTC ms.

Temporal availability: Original source timestamps retained; publication latency unknown unless explicitly observed.

Source: https://github.com/binance/binance-public-data.

## um_index_price

Composite reference index; constituents/changes require separate snapshots

Resolution: 1m. Schema: index OHLC. Units: USDT; UTC ms.

Temporal availability: Original source timestamps retained; publication latency unknown unless explicitly observed.

Source: https://github.com/binance/binance-public-data.

## um_premium_index

Negative premium valid; not a dollar price

Resolution: 1m. Schema: premium OHLC. Units: signed dimensionless ratio; UTC ms.

Temporal availability: Original source timestamps retained; publication latency unknown unless explicitly observed.

Source: https://github.com/binance/binance-public-data.

## um_metrics

Historical publication delay unknown; timestamp labeling and cross-day QA require investigation

Resolution: 5m. Schema: OI level/value; top account/position/global ratios; taker long-short ratio. Units: base units; USDT; ratios; UTC text.

Temporal availability: Original source timestamps retained; publication latency unknown unless explicitly observed.

Source: https://github.com/binance/binance-public-data.

## um_funding_settled

23 complete permitted months; 32 boundary days missing; settled value not a forward forecast

Resolution: variable_interval. Schema: calc_time,funding_interval_hours,last_funding_rate. Units: signed rate; interval hours; UTC ms.

Temporal availability: Original source timestamps retained; publication latency unknown unless explicitly observed.

Source: https://github.com/binance/binance-public-data.

## um_funding_rules

Current fundingInfo plus dated announcements; no universal historical rule log

Resolution: change_event. Schema: caps,floors,fundingIntervalHours. Units: rates; hours.

Temporal availability: Keep exchange timestamp and received timestamp; no historical availability inference.

Source: https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data.

## um_bookDepth_summary

Coarse liquidity bands are not individual price levels, full L2 or OFI; source anomalies must be audited

Resolution: coarse_snapshots. Schema: timestamp,percentage,depth,notional. Units: relative percent bands; base depth; USDT notional.

Temporal availability: Original source timestamps retained; publication latency unknown unless explicitly observed.

Source: https://github.com/binance/binance-public-data.

## um_bookTicker_archive

No files listed in the advertised official archive prefix inside the authorized window for all three symbols. Scope: this archive only; paid historical providers remain separately inventoried.

Resolution: quote_tick. Schema: update_id,bid,ask,bid_qty,ask_qty,time. Units: USDT; base; source UTC time.

Temporal availability: Original source timestamps retained; publication latency unknown unless explicitly observed.

Source: https://github.com/binance/binance-public-data.

## um_liquidation_archive

No files listed in the advertised official archive prefix inside the authorized window for all three symbols. Scope: this archive only; paid historical providers remain separately inventoried.

Resolution: liquidation_event. Schema: source liquidationSnapshot schema not yet established. Units: source quantities and times.

Temporal availability: Original source timestamps retained; publication latency unknown unless explicitly observed.

Source: https://github.com/binance/binance-public-data.

## um_depth_updates_live

Snapshot bridge required; gap/reconnect invalidates book; raw deltas preserved

Resolution: 100ms_updates. Schema: U,u,pu,bids,asks,E,T. Units: price levels USDT; base quantity; UTC ms and receive ns.

Temporal availability: Exchange ms and local receive ns; local clock calibration still required.

Source: https://developers.binance.com/en/docs/products/derivatives-trading-usds-futures/websocket-market-streams/Important-WebSocket-Change-Notice.

## um_bookTicker_live

Public top of book excludes hidden/RPI liquidity; historical free source not established

Resolution: quote_event. Schema: u,b,B,a,A,E,T. Units: USDT; base; exchange ms and receive ns.

Temporal availability: Exchange ms and local receive ns; local clock calibration still required.

Source: https://developers.binance.com/en/docs/products/derivatives-trading-usds-futures/websocket-market-streams/Important-WebSocket-Change-Notice.

## um_liquidations_live

Stream may publish snapshots rather than every liquidation; validate semantics before intensity metrics

Resolution: snapshot_stream. Schema: forceOrder payload. Units: side; price; quantity; exchange and receive time.

Temporal availability: Exchange ms and local receive ns; local clock calibration still required.

Source: https://developers.binance.com/en/docs/products/derivatives-trading-usds-futures/websocket-market-streams/Important-WebSocket-Change-Notice.

## um_aggTrades_live

Extra live fields retained; not falsely described as individual tick executions

Resolution: aggregate_event. Schema: a,p,q,f,l,T,m,nq when provided. Units: USDT; base; ms/ns.

Temporal availability: Exchange ms and local receive ns; local clock calibration still required.

Source: https://developers.binance.com/en/docs/products/derivatives-trading-usds-futures/websocket-market-streams/Important-WebSocket-Change-Notice.

## um_mark_funding_live

Estimated future settlement/funding distinct from later settled rates

Resolution: 1s. Schema: mark,index,settle_estimate,funding,next_funding_time. Units: USDT; rate; UTC times.

Temporal availability: Exchange ms and local receive ns; local clock calibration still required.

Source: https://developers.binance.com/en/docs/products/derivatives-trading-usds-futures/websocket-market-streams/Important-WebSocket-Change-Notice.

## um_depth_snapshot_live

REST 451 here; no evasion; valid book requires snapshot bridging

Resolution: poll_and_gap_recovery. Schema: lastUpdateId,bids,asks. Units: USDT; base quantities.

Temporal availability: Keep exchange timestamp and received timestamp; no historical availability inference.

Source: https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data.

## um_open_interest_live

Record polling availability; sampling is not continuous position/order observability

Resolution: polling. Schema: symbol,openInterest,time. Units: contract base units; UTC ms.

Temporal availability: Keep exchange timestamp and received timestamp; no historical availability inference.

Source: https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data.

## um_basis_rest

Latest 30 days; not a two-year endpoint; current REST region restriction

Resolution: 5m_or_coarser. Schema: futuresPrice,indexPrice,basis,basisRate. Units: USDT; ratio; UTC ms.

Temporal availability: Keep exchange timestamp and received timestamp; no historical availability inference.

Source: https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data.

## um_taker_buy_sell_rest

Latest 30 days; archive metrics ratio is not raw buy and sell volume separately

Resolution: 5m_or_coarser. Schema: buyVol,sellVol,buySellRatio. Units: base quantities; ratio; UTC ms.

Temporal availability: Keep exchange timestamp and received timestamp; no historical availability inference.

Source: https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data.

## um_position_ratios_rest

Latest 30 days; archive mappings must be verified before claiming equivalence

Resolution: 5m_or_coarser. Schema: top/global account and position ratios. Units: dimensionless ratios.

Temporal availability: Keep exchange timestamp and received timestamp; no historical availability inference.

Source: https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data.

## spot_trades

Preserve source precision; USD-M schema cannot silently parse spot timestamps/extra fields

Resolution: tick. Schema: id,price,qty,quoteQty,time,isBuyerMaker,isBestMatch. Units: USDT/base; ms before 2025, microseconds from 2025.

Temporal availability: Original source timestamps retained; publication latency unknown unless explicitly observed.

Source: https://github.com/binance/binance-public-data.

## spot_aggTrades

Evaluate incremental research value after individual spot trades; no indiscriminate duplicate campaign

Resolution: aggregate_tick. Schema: id,price,qty,first,last,time,maker,best_match. Units: USDT/base; ms/us transition.

Temporal availability: Original source timestamps retained; publication latency unknown unless explicitly observed.

Source: https://github.com/binance/binance-public-data.

## spot_klines_1m

Official cross-check of spot trades and futures-spot comparisons

Resolution: 1m. Schema: 12-field OHLCV. Units: USDT/base; source ms/us precision.

Temporal availability: Original source timestamps retained; publication latency unknown unless explicitly observed.

Source: https://github.com/binance/binance-public-data.

## spot_klines_1s

Available spot interval; prioritize ticks plus 1m verification; never import 1s assumption into futures REST

Resolution: 1s. Schema: 12-field OHLCV. Units: USDT/base; source ms/us precision.

Temporal availability: Original source timestamps retained; publication latency unknown unless explicitly observed.

Source: https://github.com/binance/binance-public-data.

## coinbase_btc_eth_sol

BTC-USD/ETH-USD/SOL-USD extra venue context; retention, product dates and incremental utility not certified

Resolution: candle_or_tick. Schema: product_id,time,OHLCV/trade fields. Units: USD/base; source timestamps.

Temporal availability: Exchange candle times plus received time; missing intervals must not be fabricated.

Source: https://docs.cdp.coinbase.com/exchange/reference/exchangerestapi_getproductcandles.

## crypto_market_cap

Community coverage and supply methodology differ by asset; does not guarantee entire crypto universe

Resolution: 1d. Schema: asset,time,CapMrktCurUSD and price metrics where offered. Units: USD; daily UTC.

Temporal availability: Daily metric time and retrieval time; provider methodology/revisions and publication delay required.

Source: https://gitbook-docs.coinmetrics.io/packages/coin-metrics-community-data.

## crypto_global_dominance

Full two-year free historical access/redistribution not established; no subscription authorized

Resolution: provider_dependent. Schema: global market cap,dominance,coin market cap. Units: USD; percent; provider times.

Temporal availability: Aggregated provider timestamps and revisions; not executable exchange ticks.

Source: https://docs.coingecko.com/reference/coins-id-market-chart-range.

## macro_calendar

Calendars can change; retrieve original releases, not schedule alone as realized event evidence

Resolution: release_event. Schema: scheduled date,time,event,reference period,calendar revision. Units: America/New_York to UTC.

Temporal availability: Release header time America/New_York with DST; original release and revisions kept separately.

Source: https://www.bls.gov/bls/newsrels.htm.

## macro_cpi

Original archived release differs from current revised time series

Resolution: monthly_release. Schema: original headline/core CPI release and revision metadata. Units: index levels; MoM/YoY percentages; release UTC.

Temporal availability: Release header time America/New_York with DST; original release and revisions kept separately.

Source: https://www.bls.gov/bls/newsrels.htm.

## macro_ppi

Revisions and rescheduled releases must be retained

Resolution: monthly_release. Schema: original PPI release and revisions. Units: index/percent; publication UTC.

Temporal availability: Release header time America/New_York with DST; original release and revisions kept separately.

Source: https://www.bls.gov/bls/newsrels.htm.

## macro_nfp_employment

Payroll benchmark revisions and previous-month corrections cannot replace initial values

Resolution: monthly_release. Schema: payrolls,unemployment,wages,initial and revised values. Units: persons; percent; earnings; UTC publication.

Temporal availability: Release header time America/New_York with DST; original release and revisions kept separately.

Source: https://www.bls.gov/bls/newsrels.htm.

## macro_jolts

Release embargo time and revision lineage required

Resolution: monthly_release. Schema: vacancies,hires,separations,initial/revised values. Units: persons/rates; release time.

Temporal availability: Release header time America/New_York with DST; original release and revisions kept separately.

Source: https://www.bls.gov/bls/newsrels.htm.

## fomc_calendar_statements

Statement, minutes and press conference are separate availability events

Resolution: meeting_release. Schema: meeting dates,statement,target range,release time. Units: percent policy rates; America/New_York.

Temporal availability: Original publication header and IANA America/New_York; scheduled time is not effective received time.

Source: https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm.

## fomc_minutes_sep

Minutes are published after meeting; forecasts are not later realized values

Resolution: separate_release. Schema: minutes,SEP forecasts,dot-plot version. Units: document/time; forecast percent.

Temporal availability: Original publication header and IANA America/New_York; scheduled time is not effective received time.

Source: https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm.

## ecb_decisions

Euro policy context; separate original release and correction times

Resolution: policy_release. Schema: decision,rate levels,statement,time. Units: percent; Europe/Berlin to UTC.

Temporal availability: Original release time Europe/Berlin with DST; corrections separately versioned.

Source: https://www.ecb.europa.eu/press/govcdec/mopo/html/index.en.html.

## macro_vintages

Free API key unavailable here; vintage date is not an intraday availability guarantee

Resolution: vintage_date. Schema: series,value,realtime_start,realtime_end. Units: series units; daily real-time metadata.

Temporal availability: Vintage dates preserve revisions; day-level real-time metadata is not an intraday publication timestamp.

Source: https://fred.stlouisfed.org/docs/api/fred/realtime_period.html.

## financial_crypto_news_metadata

DOC search short retention is not full archive limit; archive can cover window; scoped filter/storage pilot needed

Resolution: 15m_archive. Schema: URL,first-seen,source,language,themes,mentions. Units: UTC crawl/mention times.

Temporal availability: Discovery/first-seen time differs from original article publication; article edits and missing coverage explicit.

Source: https://www.gdeltproject.org/data.html.

## news_original_text

GDELT URL discovery does not grant republication rights to every publisher article

Resolution: article_release. Schema: original article publication and content revisions. Units: source time/text.

Temporal availability: Discovery/first-seen time differs from original article publication; article edits and missing coverage explicit.

Source: https://www.gdeltproject.org/data.html.

## regulatory_events

SEC is one regulator; coverage scope explicit, no universal global-event completeness claim

Resolution: announcement_event. Schema: release URL,published time,topic,correction history. Units: UTC; document hash.

Temporal availability: Original publication metadata plus received/revision timestamps; no retrospective edit substitution.

Source: https://www.sec.gov/newsroom/press-releases.

## binance_announcements

Support announcements/terms and API change logs investigated separately; machine export not established

Resolution: announcement_event. Schema: original notice URL,time,contract/rule/incident changes. Units: publication UTC; original text hash.

Temporal availability: Keep exchange timestamp and received timestamp; no historical availability inference.

Source: https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data.

## market_incidents

Use official notices plus observed connection/error logs; absence of notice is not proof of uptime

Resolution: incident_event. Schema: status,maintenance notices,event times,affected symbols. Units: UTC intervals.

Temporal availability: Keep exchange timestamp and received timestamp; no historical availability inference.

Source: https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data.

## vix_daily

Daily public history useful context; redistribution rights and original publication timing require review

Resolution: 1d. Schema: date,open,high,low,close. Units: volatility index points.

Temporal availability: End-of-day observations are unavailable at day's open; precise publication timing unproven.

Source: https://www.cboe.com/tradable-products/vix/vix-historical-data.

## historical_l2_tardis

Historical L2 is commercially recoverable, not impossible; full authorized dates/coverage/rights require quote

Resolution: tick_L2. Schema: incremental_L2,snapshots,quotes,trades,funding. Units: exchange and provider receive timestamps.

Temporal availability: Exchange plus provider receive time; vendor gaps remain possible.

Source: https://docs.tardis.dev/faq/general.

## historical_l2_kaiko

Snapshot product is not necessarily every depth event; venue coverage and redistribution license required

Resolution: provider_snapshots. Schema: L1/L2 snapshots,trades,derivative metrics. Units: price/qty/provider times.

Temporal availability: Vendor snapshots/trades with data-version metadata; not guaranteed gap-free event-level L2.

Source: https://docs.kaiko.com/explore-our-data/data-dictionary.

## execution_contract_filters

Current exchangeInfo is not two-year historical filters; dated announcements and forward snapshots needed

Resolution: change_and_poll. Schema: tickSize,stepSize,minQty,minNotional,contractType,status. Units: USDT; base units; contract identifiers.

Temporal availability: Keep exchange timestamp and received timestamp; no historical availability inference.

Source: https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data.

## execution_fees_public

Current fee table is not historical account-specific effective rate

Resolution: change_event. Schema: public maker/taker fee tiers,effective dates,promotions. Units: decimal fee rates; qualification rules.

Temporal availability: Keep exchange timestamp and received timestamp; no historical availability inference.

Source: https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data.

## execution_fees_account

Public-market foundation has no private account permission or Binance credentials; never invent account fees

Resolution: private_account. Schema: user commissionRate,income/filled orders. Units: fee rate; asset amounts.

Temporal availability: Keep exchange timestamp and received timestamp; no historical availability inference.

Source: https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data.

## execution_latency_observed

Receive times exist; calibrated clock and kernel receipt monitoring remain unimplemented

Resolution: receive_event. Schema: exchange T/E,receive_ns,clock offset,processing delay. Units: ms/ns; uncertainty bounds.

Temporal availability: Exchange ms and local receive ns; local clock calibration still required.

Source: https://developers.binance.com/en/docs/products/derivatives-trading-usds-futures/websocket-market-streams/Important-WebSocket-Change-Notice.

## full_l3_participant_orders

Public Binance feed is market-by-price; private user orders do not reveal all participants; no deanonymization

Resolution: order_event. Schema: market-wide individual order identities/queue events. Units: order-level identifiers.

Temporal availability: Exchange ms and local receive ns; local clock calibration still required.

Source: https://developers.binance.com/en/docs/products/derivatives-trading-usds-futures/websocket-market-streams/Important-WebSocket-Change-Notice.

## insurance_adl_context

Not public individual ADL executions; no proof that archive ID gaps correspond to these exclusions

Resolution: snapshot. Schema: insuranceBalance,ADL risk where public. Units: asset amounts/risk metrics.

Temporal availability: Keep exchange timestamp and received timestamp; no historical availability inference.

Source: https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data.

## continuous_contract_klines

Perpetual pair already selected; extra delivery contracts excluded pending cost/utility assessment

Resolution: 1m_or_coarser. Schema: pair,contractType,OHLCV. Units: USDT/base; UTC ms.

Temporal availability: Keep exchange timestamp and received timestamp; no historical availability inference.

Source: https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data.

## trade_aggressor_side

Do not infer participant identity or hidden intention

Resolution: declared transformation windows. Schema: versioned feature schema pending. Units: inherited and explicitly documented per transform.

Temporal availability: Each output available no earlier than latest contributing input; missing availability blocks strict replay.

Source: um_trades.

Transformation contract: buyer_maker=true => seller aggressor; false => buyer aggressor.

## buy_sell_volume_delta

Base and quote units kept separately; trade-count coverage required

Resolution: declared transformation windows. Schema: versioned feature schema pending. Units: inherited and explicitly documented per transform.

Temporal availability: Each output available no earlier than latest contributing input; missing availability blocks strict replay.

Source: um_trades.

Transformation contract: buy=sum(qty for buyer aggressor); sell=sum(qty for seller aggressor); delta=buy-sell.

## cvd

Anchor/reset and missing intervals explicit; gap is not zero delta

Resolution: declared transformation windows. Schema: versioned feature schema pending. Units: inherited and explicitly documented per transform.

Temporal availability: Each output available no earlier than latest contributing input; missing availability blocks strict replay.

Source: um_trades.

Transformation contract: cumulative sum of signed aggressor quantity from explicit anchor.

## vwap

Undefined at zero volume; daily/rolling/anchored variants versioned

Resolution: declared transformation windows. Schema: versioned feature schema pending. Units: inherited and explicitly documented per transform.

Temporal availability: Each output available no earlier than latest contributing input; missing availability blocks strict replay.

Source: um_trades.

Transformation contract: sum(price*qty)/sum(qty), exact decimals and explicit UTC/session/rolling anchor.

## volume_at_price_profile

Volume-at-price and profile bin rules require time-valid contract filters

Resolution: declared transformation windows. Schema: versioned feature schema pending. Units: inherited and explicitly documented per transform.

Temporal availability: Each output available no earlier than latest contributing input; missing availability blocks strict replay.

Source: um_trades.

Transformation contract: sum(qty) by declared exact price or tick-size bins.

## temporal_aggregations

Empty intervals and incomplete tape explicit; compare official bars

Resolution: declared transformation windows. Schema: versioned feature schema pending. Units: inherited and explicitly documented per transform.

Temporal availability: Each output available no earlier than latest contributing input; missing availability blocks strict replay.

Source: um_trades.

Transformation contract: OHLCV/count/taker volume from ordered executions in half-open UTC intervals.

## best_quote_spread

Observed quotes only; no synthetic historical quote inferred from trades

Resolution: declared transformation windows. Schema: versioned feature schema pending. Units: inherited and explicitly documented per transform.

Temporal availability: Each output available no earlier than latest contributing input; missing availability blocks strict replay.

Source: um_bookTicker_live.

Transformation contract: ask-bid; relative spread=(ask-bid)/mid.

## book_liquidity_imbalance

Require valid snapshot bridge and every intervening sequence; hidden liquidity excluded

Resolution: declared transformation windows. Schema: versioned feature schema pending. Units: inherited and explicitly documented per transform.

Temporal availability: Each output available no earlier than latest contributing input; missing availability blocks strict replay.

Source: um_depth_updates_live, um_depth_snapshot_live.

Transformation contract: (sum(bid_qty)-sum(ask_qty))/(sum(bid_qty)+sum(ask_qty)) on declared levels.

## order_flow_imbalance

No OFI from executions alone; no valid output across an unsynchronized book

Resolution: declared transformation windows. Schema: versioned feature schema pending. Units: inherited and explicitly documented per transform.

Temporal availability: Each output available no earlier than latest contributing input; missing availability blocks strict replay.

Source: um_depth_updates_live, um_depth_snapshot_live.

Transformation contract: Sum signed changes in displayed best bid/ask price and quantity under versioned OFI convention.

## liquidity_walls

Rule-dependent estimate; cannot identify spoofing or participant intent

Resolution: declared transformation windows. Schema: versioned feature schema pending. Units: inherited and explicitly documented per transform.

Temporal availability: Each output available no earlier than latest contributing input; missing availability blocks strict replay.

Source: um_depth_updates_live, um_depth_snapshot_live.

Transformation contract: Threshold/persistence rules on observed displayed depth.

## absorption_pressure

Hypothesis proxy, not direct observation of hidden orders; no strategy optimization

Resolution: declared transformation windows. Schema: versioned feature schema pending. Units: inherited and explicitly documented per transform.

Temporal availability: Each output available no earlier than latest contributing input; missing availability blocks strict replay.

Source: um_trades, um_bookTicker_live.

Transformation contract: Declared aggressive-flow/price-response statistic over synchronized windows.

## oi_changes

Time-valid unit/specification mapping; missing samples not zero changes

Resolution: declared transformation windows. Schema: versioned feature schema pending. Units: inherited and explicitly documented per transform.

Temporal availability: Each output available no earlier than latest contributing input; missing availability blocks strict replay.

Source: um_metrics.

Transformation contract: difference in OI levels between consecutive admitted observations.

## perpetual_basis

One-minute OHLC-derived basis is a sampled proxy, not simultaneous intrabar execution basis

Resolution: declared transformation windows. Schema: versioned feature schema pending. Units: inherited and explicitly documented per transform.

Temporal availability: Each output available no earlier than latest contributing input; missing availability blocks strict replay.

Source: um_mark_price, um_index_price.

Transformation contract: mark-index and (mark-index)/index at matching observed timestamps.

## futures_spot_spread

Clock/interval/quote-currency alignment; not an executable arbitrage signal

Resolution: declared transformation windows. Schema: versioned feature schema pending. Units: inherited and explicitly documented per transform.

Temporal availability: Each output available no earlier than latest contributing input; missing availability blocks strict replay.

Source: um_klines_1m, spot_klines_1m.

Transformation contract: matching-close difference and relative difference.

## cross_asset_volatility_correlation

No future returns, revised context or forward-filled missing inputs

Resolution: declared transformation windows. Schema: versioned feature schema pending. Units: inherited and explicitly documented per transform.

Temporal availability: Each output available no earlier than latest contributing input; missing availability blocks strict replay.

Source: um_klines_1m.

Transformation contract: causal returns, rolling realized volatility/correlation with explicit sample window.

## regime_descriptors

No predictive model or optimized trading regime in this phase

Resolution: declared transformation windows. Schema: versioned feature schema pending. Units: inherited and explicitly documented per transform.

Temporal availability: Each output available no earlier than latest contributing input; missing availability blocks strict replay.

Source: um_klines_1m, um_metrics.

Transformation contract: Versioned descriptive volatility/volume/OI transformations.

## execution_cost_scenarios

Assumptions never relabeled as observed fills or measured latency; no trading simulation here

Resolution: declared transformation windows. Schema: versioned feature schema pending. Units: inherited and explicitly documented per transform.

Temporal availability: Each output available no earlier than latest contributing input; missing availability blocks strict replay.

Source: um_bookTicker_live, execution_contract_filters, execution_fees_public, um_funding_settled.

Transformation contract: Explicit fee/funding/spread/slippage scenario assumptions.

## Acquisition priority and acceptance

Priority 0: bounded live public streams plus snapshot/OI/specification recovery where official access permits. Priority 1: preserve current futures campaign, investigate individual-trade gaps, admit bookDepth only after QA, acquire original macro releases and dated contract/funding notices. Priority 2: spot individual trades and 1m verification, scoped event metadata and reproducible microstructure transforms. Priority 3: optional venue/index expansion after storage and licensing evidence.

C16–C22 do not collide with existing C01–C15. C16 is an evidence checkpoint, acceptance pending complete per-source bounds/costs and executable acquisition contracts. C17 requires all selected recoverable coverage or exact justifications. C18 requires recomputation. C19 requires temporal provenance. C20 requires operational evidence. C21 requires independent restoration. C22 remains blocked until all acceptance conditions hold.

No book, OFI, queue events or historical bid/ask can be reconstructed from trades alone. Source events, transformations and rule-dependent estimates are separate. Missing publication time blocks strict causal replay.
