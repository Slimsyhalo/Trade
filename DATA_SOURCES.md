# Official source discovery — 2026-10-07

Research verified against official Binance and GitHub documentation. Actual download observations are in `reports/source_probes.json`; a successful probe is NOT a downloaded partition. A 404 on one date is NOT proof that a dataset never exists.

| Dataset | Official source | Frequency / schema | Units / time | Limits and observed availability |
|---|---|---|---|---|
| aggTrades | `data.binance.vision/data/futures/um/daily/aggTrades/{symbol}/` | CSV aggregate ID, price, quantity, first/last ID, transact time, maker flag | Exact decimal strings; base units; USDT; UTC ms | Daily ZIP + SHA256 CHECKSUM; sampled in-window files exist. REST `/fapi/v1/aggTrades` currently limited to past 48h, weight 20, up to 1000, time spans <1h. RPI inclusion and exclusions mean aggregates are not a lossless substitute for all executions. |
| trades | Same archive, `trades` | ID, price, qty, quote qty, time, maker | UTC ms; base and quote units | Available at sampled date; larger than aggregates; not downloaded in pilot. |
| klines | Same archive, `klines/{symbol}/1m/`; `/fapi/v1/klines` | 12 CSV fields in dictionary | UTC ms, OHLC USDT, volume base/USDT | 1m minimum documented USD-M interval; do not import Spot's 1s support. Reconstruct 1s under explicit trade/aggregate semantics. |
| markPriceKlines | Same archive; `/fapi/v1/markPriceKlines` | OHLC with 12-column archive envelope | UTC ms; USDT | Preserve placeholders; do not interpret zero placeholder volume as traded volume. |
| indexPriceKlines | Same archive; `/fapi/v1/indexPriceKlines` | OHLC with 12-column envelope | UTC ms; USDT | REST uses pair; archive uses symbol paths. |
| premiumIndexKlines | Same archive; `/fapi/v1/premiumIndexKlines` | OHLC of premium | UTC ms; dimensionless, signed | Negative values valid; not a USD price. |
| metrics / open interest | Same archive, `metrics`; `/futures/data/openInterestHist` | 5m metrics with OI levels, values and ratios | UTC text timestamp; base units / USDT; ratios | Historical archive sample exists beyond REST retention. REST latest 1 month, max 500, 1000 requests/5min. Historical publication latency unknown: excluded from strict replay. |
| funding | Official monthly `data/futures/um/monthly/fundingRate/{symbol}/`; `/fapi/v1/fundingRate` | fundingTime, rate, symbol, markPrice when supplied | UTC ms; dimensionless rate | Max 1000; 500 calls/5min shared with fundingInfo. Cursor last timestamp +1; never assume fixed funding interval. REST returned HTTP 451 here. Boundary-period REST extraction remains blocked. Full-month official archives are now supported; archive fields are calc_time, funding_interval_hours, last_funding_rate, with no mark price. |
| basis | `/futures/data/basis` | futures/index prices, basis, basis rate | UTC ms; USDT / ratio | Latest 30 days. Historical mark/index candles enable close-boundary divergence, not tick-synchronous executable basis. |
| bookDepth | Official daily archive | Coarse percentage depth summaries | UTC; percentage, depth/notional | File exists in pilot; not a sequenced L2 reconstruction. Parser pending. |
| bookTicker | Official archive path probe; public WS | bid/ask prices and sizes, update IDs | UTC event/transaction/receive timestamps | Sample archive date 404; interval-wide availability unverified. WS observed. |
| liquidations | Market WS `symbol@forceOrder` | Raw payload retained | Exchange event + receive ns | One historical liquidationSnapshot probe returned 404; no complete market-wide historical coverage claim. Delivery/completeness must be verified from current stream schema before liquidation intensity research. A user's forceOrders endpoint is not global market history. |
| live aggTrade / mark / funding | `wss://fstream.binance.com/market/stream?streams=...` | Original JSON including new `nq` field retained | Exchange ms + local receive ns | Actual smoke capture succeeded. `nq` does not exist in the older 7-field archive schema. |
| live depth / ticker | `wss://fstream.binance.com/public/stream?streams=...` | Original U/u/pu sequences and levels | Exchange ms + local receive ns | Actual capture succeeded; REST snapshot HTTP 451 means complete book initialization unavailable here. Never mark those deltas as a valid full book. |

Source references:
- https://github.com/binance/binance-public-data
- https://data.binance.vision/?prefix=data/futures/um/daily/
- https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data
- https://developers.binance.com/en/docs/products/derivatives-trading-usds-futures/websocket-market-streams/Connect
- https://developers.binance.com/en/docs/products/derivatives-trading-usds-futures/websocket-market-streams/Important-WebSocket-Change-Notice
- https://developers.binance.com/en/docs/products/derivatives-trading-usds-futures/websocket-market-streams/How-to-manage-a-local-order-book-correctly

Archive pacing: one request/second by default; no official fixed archive quota assumed. Respect 429, Retry-After; stop on 418/451. WebSocket: 24h connection lifetime, 10 inbound messages/s, maximum 1024 streams. Separate routing is required after the 2026 migration. Rate values are a documentation snapshot, not a perpetual promise.

## Funding archive discovery — 2026-10-08

Observed an official monthly BTCUSDT November 2024 ZIP and CHECKSUM, plus September 2026 files for BTC/ETH/SOL. Monthly ZIP schema: calc_time (UTC ms), funding_interval_hours (integer hours), last_funding_rate (exact signed decimal string). Daily fundingRate probe for 2024-10-07 returned 404. For this window, only November 2024 through September 2026 whole-month archives may be downloaded; October boundary archives include unauthorized dates and are never requested. Their in-window days remain missing until an allowed bounded source is available. Publication latency is unknown; funding is excluded from strict replay. Archive snapshots have no historical markPrice field. Source: https://data.binance.vision/?prefix=data/futures/um/monthly/fundingRate/ .
