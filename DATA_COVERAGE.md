# Current data coverage

Generated: 2026-10-08T19:43:54.030031+00:00

QA days count observed passing dates. Remote days require matching RAW and Parquet readback receipts. Monthly funding coverage counts observed dates, not one day per archive.

| Symbol | Dataset | First | Last | QA days / expected | Remote days | Rows | QA partitions | Remote partitions |
|---|---|---|---|---:|---:|---:|---:|---:|
| BTCUSDT | trades | None | None | 0 / 731 | 0 | 0 | 0 | 0 |
| BTCUSDT | aggTrades | 2024-10-07 | 2024-12-28 | 83 / 731 | 83 | 137,548,527 | 83 | 83 |
| BTCUSDT | klines | 2024-10-07 | 2024-12-27 | 82 / 731 | 82 | 118,080 | 82 | 82 |
| BTCUSDT | markPriceKlines | 2024-10-07 | 2024-12-27 | 82 / 731 | 82 | 118,080 | 82 | 82 |
| BTCUSDT | indexPriceKlines | 2024-10-07 | 2024-12-27 | 82 / 731 | 82 | 118,080 | 82 | 82 |
| BTCUSDT | premiumIndexKlines | 2024-10-07 | 2024-12-27 | 82 / 731 | 82 | 118,080 | 82 | 82 |
| BTCUSDT | metrics | 2024-10-07 | 2024-12-27 | 82 / 731 | 82 | 23,614 | 82 | 82 |
| BTCUSDT | fundingRate | 2024-11-01 | 2026-09-30 | 699 / 731 | 699 | 2,097 | 23 | 23 |
| ETHUSDT | trades | None | None | 0 / 731 | 0 | 0 | 0 | 0 |
| ETHUSDT | aggTrades | 2024-10-07 | 2024-12-27 | 82 / 731 | 82 | 149,705,637 | 82 | 82 |
| ETHUSDT | klines | 2024-10-07 | 2024-12-27 | 82 / 731 | 82 | 118,080 | 82 | 82 |
| ETHUSDT | markPriceKlines | 2024-10-07 | 2024-12-27 | 82 / 731 | 82 | 118,080 | 82 | 82 |
| ETHUSDT | indexPriceKlines | 2024-10-07 | 2024-12-27 | 82 / 731 | 82 | 118,080 | 82 | 82 |
| ETHUSDT | premiumIndexKlines | 2024-10-07 | 2024-12-27 | 82 / 731 | 82 | 118,080 | 82 | 82 |
| ETHUSDT | metrics | 2024-10-07 | 2024-12-27 | 82 / 731 | 82 | 23,614 | 82 | 82 |
| ETHUSDT | fundingRate | 2024-11-01 | 2026-09-30 | 699 / 731 | 699 | 2,097 | 23 | 23 |
| SOLUSDT | trades | None | None | 0 / 731 | 0 | 0 | 0 | 0 |
| SOLUSDT | aggTrades | 2024-10-07 | 2024-12-27 | 82 / 731 | 82 | 35,226,115 | 82 | 82 |
| SOLUSDT | klines | 2024-10-07 | 2024-12-27 | 82 / 731 | 82 | 118,080 | 82 | 82 |
| SOLUSDT | markPriceKlines | 2024-10-07 | 2024-12-27 | 82 / 731 | 82 | 118,080 | 82 | 82 |
| SOLUSDT | indexPriceKlines | 2024-10-07 | 2024-12-27 | 82 / 731 | 82 | 118,080 | 82 | 82 |
| SOLUSDT | premiumIndexKlines | 2024-10-07 | 2024-12-27 | 82 / 731 | 82 | 118,080 | 82 | 82 |
| SOLUSDT | metrics | 2024-10-07 | 2024-12-27 | 82 / 731 | 82 | 23,614 | 82 | 82 |
| SOLUSDT | fundingRate | 2024-11-01 | 2026-09-30 | 699 / 731 | 699 | 2,097 | 23 | 23 |

Missing-date lists, failed partitions and remote URLs are in data_catalog.json. Unacquired dates do not imply Binance lacks those dates.

Funding archives are restricted to complete months inside the window. October 2024 and October 2026 need another permitted source for their in-window dates. No outside-window records were downloaded.
