# Current data coverage

Generated: 2026-10-08T19:29:10.072623+00:00

QA days count observed passing dates. Remote days require matching RAW and Parquet readback receipts. Monthly funding coverage counts observed dates, not one day per archive.

| Symbol | Dataset | First | Last | QA days / expected | Remote days | Rows | QA partitions | Remote partitions |
|---|---|---|---|---:|---:|---:|---:|---:|
| BTCUSDT | trades | None | None | 0 / 731 | 0 | 0 | 0 | 0 |
| BTCUSDT | aggTrades | 2024-10-07 | 2024-12-25 | 80 / 731 | 80 | 133,430,681 | 80 | 80 |
| BTCUSDT | klines | 2024-10-07 | 2024-12-25 | 80 / 731 | 80 | 115,200 | 80 | 80 |
| BTCUSDT | markPriceKlines | 2024-10-07 | 2024-12-25 | 80 / 731 | 80 | 115,200 | 80 | 80 |
| BTCUSDT | indexPriceKlines | 2024-10-07 | 2024-12-25 | 80 / 731 | 80 | 115,200 | 80 | 80 |
| BTCUSDT | premiumIndexKlines | 2024-10-07 | 2024-12-25 | 80 / 731 | 80 | 115,200 | 80 | 80 |
| BTCUSDT | metrics | 2024-10-07 | 2024-12-24 | 79 / 731 | 79 | 22,750 | 79 | 79 |
| BTCUSDT | fundingRate | 2024-11-01 | 2026-09-30 | 699 / 731 | 699 | 2,097 | 23 | 23 |
| ETHUSDT | trades | None | None | 0 / 731 | 0 | 0 | 0 | 0 |
| ETHUSDT | aggTrades | 2024-10-07 | 2024-12-24 | 79 / 731 | 79 | 144,922,842 | 79 | 79 |
| ETHUSDT | klines | 2024-10-07 | 2024-12-24 | 79 / 731 | 79 | 113,760 | 79 | 79 |
| ETHUSDT | markPriceKlines | 2024-10-07 | 2024-12-24 | 79 / 731 | 79 | 113,760 | 79 | 79 |
| ETHUSDT | indexPriceKlines | 2024-10-07 | 2024-12-24 | 79 / 731 | 79 | 113,760 | 79 | 79 |
| ETHUSDT | premiumIndexKlines | 2024-10-07 | 2024-12-24 | 79 / 731 | 79 | 113,760 | 79 | 79 |
| ETHUSDT | metrics | 2024-10-07 | 2024-12-24 | 79 / 731 | 79 | 22,750 | 79 | 79 |
| ETHUSDT | fundingRate | 2024-11-01 | 2026-09-30 | 699 / 731 | 699 | 2,097 | 23 | 23 |
| SOLUSDT | trades | None | None | 0 / 731 | 0 | 0 | 0 | 0 |
| SOLUSDT | aggTrades | 2024-10-07 | 2024-12-24 | 79 / 731 | 79 | 34,344,703 | 79 | 79 |
| SOLUSDT | klines | 2024-10-07 | 2024-12-24 | 79 / 731 | 79 | 113,760 | 79 | 79 |
| SOLUSDT | markPriceKlines | 2024-10-07 | 2024-12-24 | 79 / 731 | 79 | 113,760 | 79 | 79 |
| SOLUSDT | indexPriceKlines | 2024-10-07 | 2024-12-24 | 79 / 731 | 79 | 113,760 | 79 | 79 |
| SOLUSDT | premiumIndexKlines | 2024-10-07 | 2024-12-24 | 79 / 731 | 79 | 113,760 | 79 | 79 |
| SOLUSDT | metrics | 2024-10-07 | 2024-12-24 | 79 / 731 | 79 | 22,750 | 79 | 79 |
| SOLUSDT | fundingRate | 2024-11-01 | 2026-09-30 | 699 / 731 | 699 | 2,097 | 23 | 23 |

Missing-date lists, failed partitions and remote URLs are in data_catalog.json. Unacquired dates do not imply Binance lacks those dates.

Funding archives are restricted to complete months inside the window. October 2024 and October 2026 need another permitted source for their in-window dates. No outside-window records were downloaded.
