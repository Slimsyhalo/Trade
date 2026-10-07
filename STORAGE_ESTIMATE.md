# Storage estimate

Pre-bulk estimate based on streamed Content-Length probes of 2024-10-07 only. This is a one-day extrapolation, NOT a capacity guarantee. Downloading all history is blocked until remote storage works. Plan 3x this baseline for activity variation; obtain at least 12 stratified monthly samples before production bulk approval.

731 inclusive calendar dates are requested. The end date is still in progress at this audit. Exact endpoints are authoritative; no earlier history is requested.

| Symbol | Dataset | Sample ZIP bytes | RAW ZIP baseline GB (731d) | Normalized uncompressed | Parquet ZSTD | Remote |
|---|---|---:|---:|---|---|---|
| BTCUSDT | aggTrades | 18674460 | 13.651 | unmeasured | unmeasured | RAW + Parquet; unmeasured |
| BTCUSDT | trades | 31854063 | 23.285 | unmeasured | unmeasured | RAW + Parquet; unmeasured |
| BTCUSDT | klines | 62633 | 0.046 | unmeasured | unmeasured | RAW + Parquet; unmeasured |
| BTCUSDT | markPriceKlines | 34464 | 0.025 | unmeasured | unmeasured | RAW + Parquet; unmeasured |
| BTCUSDT | indexPriceKlines | 35940 | 0.026 | unmeasured | unmeasured | RAW + Parquet; unmeasured |
| BTCUSDT | premiumIndexKlines | 28557 | 0.021 | unmeasured | unmeasured | RAW + Parquet; unmeasured |
| BTCUSDT | metrics | 11237 | 0.008 | unmeasured | unmeasured | RAW + Parquet; unmeasured |
| BTCUSDT | bookDepth | 466314 | 0.341 | unmeasured | unmeasured | RAW + Parquet; unmeasured |
| BTCUSDT | bookTicker | unavailable at sample date | unknown | unmeasured | unmeasured | RAW + Parquet; unmeasured |
| BTCUSDT | liquidationSnapshot | unavailable at sample date | unknown | unmeasured | unmeasured | RAW + Parquet; unmeasured |
| ETHUSDT | aggTrades | 16478397 | 12.046 | unmeasured | unmeasured | RAW + Parquet; unmeasured |
| ETHUSDT | trades | 36227290 | 26.482 | unmeasured | unmeasured | RAW + Parquet; unmeasured |
| ETHUSDT | klines | 63539 | 0.046 | unmeasured | unmeasured | RAW + Parquet; unmeasured |
| ETHUSDT | markPriceKlines | 32430 | 0.024 | unmeasured | unmeasured | RAW + Parquet; unmeasured |
| ETHUSDT | indexPriceKlines | 31470 | 0.023 | unmeasured | unmeasured | RAW + Parquet; unmeasured |
| ETHUSDT | premiumIndexKlines | 28757 | 0.021 | unmeasured | unmeasured | RAW + Parquet; unmeasured |
| ETHUSDT | metrics | 11692 | 0.009 | unmeasured | unmeasured | RAW + Parquet; unmeasured |
| ETHUSDT | bookDepth | 492669 | 0.360 | unmeasured | unmeasured | RAW + Parquet; unmeasured |
| ETHUSDT | bookTicker | unavailable at sample date | unknown | unmeasured | unmeasured | RAW + Parquet; unmeasured |
| ETHUSDT | liquidationSnapshot | unavailable at sample date | unknown | unmeasured | unmeasured | RAW + Parquet; unmeasured |
| SOLUSDT | aggTrades | 9495931 | 6.942 | unmeasured | unmeasured | RAW + Parquet; unmeasured |
| SOLUSDT | trades | 13856642 | 10.129 | unmeasured | unmeasured | RAW + Parquet; unmeasured |
| SOLUSDT | klines | 55008 | 0.040 | unmeasured | unmeasured | RAW + Parquet; unmeasured |
| SOLUSDT | markPriceKlines | 32045 | 0.023 | unmeasured | unmeasured | RAW + Parquet; unmeasured |
| SOLUSDT | indexPriceKlines | 38848 | 0.028 | unmeasured | unmeasured | RAW + Parquet; unmeasured |
| SOLUSDT | premiumIndexKlines | 29044 | 0.021 | unmeasured | unmeasured | RAW + Parquet; unmeasured |
| SOLUSDT | metrics | 10909 | 0.008 | unmeasured | unmeasured | RAW + Parquet; unmeasured |
| SOLUSDT | bookDepth | 410028 | 0.300 | unmeasured | unmeasured | RAW + Parquet; unmeasured |
| SOLUSDT | bookTicker | unavailable at sample date | unknown | unmeasured | unmeasured | RAW + Parquet; unmeasured |
| SOLUSDT | liquidationSnapshot | unavailable at sample date | unknown | unmeasured | unmeasured | RAW + Parquet; unmeasured |

No invented compression ratios. Pilot measurements will be appended. aggTrades are prioritized; individual trades retain finer event timing and are not exactly reconstructible from aggTrades. Do not silently label them redundant. bookDepth is a coarse summary and must not be used as full L2 history.

## Measured pilot

| Symbol | Dataset | Raw CSV bytes | Original ZIP bytes | Uncompressed Arrow bytes | Parquet ZSTD bytes | Remote needed ZIP+Parquet |
|---|---|---:|---:|---:|---:|---:|
| BTCUSDT | aggTrades | 96878806 | 18674460 | 176219401 | 25192970 | 43867430 |
| BTCUSDT | indexPriceKlines | 145554 | 35940 | 261540 | 66430 | 102370 |
| BTCUSDT | klines | 164273 | 62633 | 277639 | 95457 | 158090 |
| BTCUSDT | markPriceKlines | 140037 | 34464 | 256023 | 64978 | 99442 |
| BTCUSDT | metrics | 35603 | 11237 | 56808 | 16040 | 27277 |
| BTCUSDT | premiumIndexKlines | 128214 | 28557 | 244200 | 55210 | 83767 |
| BTCUSDT | trades | 198884806 | 31854063 | 434398779 | 46689550 | 78543613 |
| ETHUSDT | aggTrades | 80904871 | 16478397 | 147304541 | 21879928 | 38358325 |
| ETHUSDT | indexPriceKlines | 139794 | 31470 | 255780 | 61174 | 92644 |
| ETHUSDT | klines | 160594 | 63539 | 273865 | 97330 | 160869 |
| ETHUSDT | markPriceKlines | 138588 | 32430 | 254574 | 61745 | 94175 |
| ETHUSDT | metrics | 35891 | 11692 | 57096 | 16532 | 28224 |
| ETHUSDT | premiumIndexKlines | 128101 | 28757 | 244087 | 55379 | 84136 |
| ETHUSDT | trades | 205307023 | 36227290 | 448918162 | 48946493 | 85173783 |
| SOLUSDT | aggTrades | 47755246 | 9495931 | 89186080 | 12739391 | 22235322 |
| SOLUSDT | indexPriceKlines | 134034 | 38848 | 250020 | 67893 | 106741 |
| SOLUSDT | klines | 152371 | 55008 | 266303 | 85937 | 140945 |
| SOLUSDT | markPriceKlines | 133926 | 32045 | 249912 | 60618 | 92663 |
| SOLUSDT | metrics | 35891 | 10909 | 57096 | 15723 | 26632 |
| SOLUSDT | premiumIndexKlines | 128113 | 29044 | 244099 | 55531 | 84575 |
| SOLUSDT | trades | 92947729 | 13856642 | 208796391 | 20034007 | 33890649 |
