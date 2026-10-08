# Current data coverage

Generated: 2026-10-08T18:58:28.533929+00:00

QA days count observed passing dates. Remote days require matching RAW and Parquet readback receipts. Monthly funding coverage counts observed dates, not one day per archive.

| Symbol | Dataset | First | Last | QA days / expected | Remote days | Rows | QA partitions | Remote partitions |
|---|---|---|---|---:|---:|---:|---:|---:|
| BTCUSDT | trades | None | None | 0 / 731 | 0 | 0 | 0 | 0 |
| BTCUSDT | aggTrades | 2024-10-07 | 2024-12-19 | 74 / 731 | 74 | 121,855,253 | 74 | 74 |
| BTCUSDT | klines | 2024-10-07 | 2024-12-19 | 74 / 731 | 74 | 106,560 | 74 | 74 |
| BTCUSDT | markPriceKlines | 2024-10-07 | 2024-12-19 | 74 / 731 | 74 | 106,560 | 74 | 74 |
| BTCUSDT | indexPriceKlines | 2024-10-07 | 2024-12-19 | 74 / 731 | 74 | 106,560 | 74 | 74 |
| BTCUSDT | premiumIndexKlines | 2024-10-07 | 2024-12-19 | 74 / 731 | 74 | 106,560 | 74 | 74 |
| BTCUSDT | metrics | 2024-10-07 | 2024-12-19 | 74 / 731 | 74 | 21,310 | 74 | 74 |
| BTCUSDT | fundingRate | 2024-11-01 | 2026-09-30 | 699 / 731 | 699 | 2,097 | 23 | 23 |
| ETHUSDT | trades | None | None | 0 / 731 | 0 | 0 | 0 | 0 |
| ETHUSDT | aggTrades | 2024-10-07 | 2024-12-19 | 74 / 731 | 74 | 131,921,317 | 74 | 74 |
| ETHUSDT | klines | 2024-10-07 | 2024-12-19 | 74 / 731 | 74 | 106,560 | 74 | 74 |
| ETHUSDT | markPriceKlines | 2024-10-07 | 2024-12-19 | 74 / 731 | 74 | 106,560 | 74 | 74 |
| ETHUSDT | indexPriceKlines | 2024-10-07 | 2024-12-19 | 74 / 731 | 74 | 106,560 | 74 | 74 |
| ETHUSDT | premiumIndexKlines | 2024-10-07 | 2024-12-19 | 74 / 731 | 74 | 106,560 | 74 | 74 |
| ETHUSDT | metrics | 2024-10-07 | 2024-12-19 | 74 / 731 | 74 | 21,310 | 74 | 74 |
| ETHUSDT | fundingRate | 2024-11-01 | 2026-09-30 | 699 / 731 | 699 | 2,097 | 23 | 23 |
| SOLUSDT | trades | None | None | 0 / 731 | 0 | 0 | 0 | 0 |
| SOLUSDT | aggTrades | 2024-10-07 | 2024-12-19 | 74 / 731 | 74 | 31,684,792 | 74 | 74 |
| SOLUSDT | klines | 2024-10-07 | 2024-12-18 | 73 / 731 | 73 | 105,120 | 73 | 73 |
| SOLUSDT | markPriceKlines | 2024-10-07 | 2024-12-18 | 73 / 731 | 73 | 105,120 | 73 | 73 |
| SOLUSDT | indexPriceKlines | 2024-10-07 | 2024-12-18 | 73 / 731 | 73 | 105,120 | 73 | 73 |
| SOLUSDT | premiumIndexKlines | 2024-10-07 | 2024-12-18 | 73 / 731 | 73 | 105,120 | 73 | 73 |
| SOLUSDT | metrics | 2024-10-07 | 2024-12-18 | 73 / 731 | 73 | 21,022 | 73 | 73 |
| SOLUSDT | fundingRate | 2024-11-01 | 2026-09-30 | 699 / 731 | 699 | 2,097 | 23 | 23 |

Missing-date lists, failed partitions and remote URLs are in data_catalog.json. Unacquired dates do not imply Binance lacks those dates.

Funding archives are restricted to complete months inside the window. October 2024 and October 2026 need another permitted source for their in-window dates. No outside-window records were downloaded.
