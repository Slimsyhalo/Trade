# Current data coverage

Generated: 2026-10-08T19:06:46.740268+00:00

QA days count observed passing dates. Remote days require matching RAW and Parquet readback receipts. Monthly funding coverage counts observed dates, not one day per archive.

| Symbol | Dataset | First | Last | QA days / expected | Remote days | Rows | QA partitions | Remote partitions |
|---|---|---|---|---:|---:|---:|---:|---:|
| BTCUSDT | trades | None | None | 0 / 731 | 0 | 0 | 0 | 0 |
| BTCUSDT | aggTrades | 2024-10-07 | 2024-12-21 | 76 / 731 | 76 | 126,973,972 | 76 | 76 |
| BTCUSDT | klines | 2024-10-07 | 2024-12-21 | 76 / 731 | 76 | 109,440 | 76 | 76 |
| BTCUSDT | markPriceKlines | 2024-10-07 | 2024-12-20 | 75 / 731 | 75 | 108,000 | 75 | 75 |
| BTCUSDT | indexPriceKlines | 2024-10-07 | 2024-12-20 | 75 / 731 | 75 | 108,000 | 75 | 75 |
| BTCUSDT | premiumIndexKlines | 2024-10-07 | 2024-12-20 | 75 / 731 | 75 | 108,000 | 75 | 75 |
| BTCUSDT | metrics | 2024-10-07 | 2024-12-20 | 75 / 731 | 75 | 21,598 | 75 | 75 |
| BTCUSDT | fundingRate | 2024-11-01 | 2026-09-30 | 699 / 731 | 699 | 2,097 | 23 | 23 |
| ETHUSDT | trades | None | None | 0 / 731 | 0 | 0 | 0 | 0 |
| ETHUSDT | aggTrades | 2024-10-07 | 2024-12-20 | 75 / 731 | 75 | 136,515,365 | 75 | 75 |
| ETHUSDT | klines | 2024-10-07 | 2024-12-20 | 75 / 731 | 75 | 108,000 | 75 | 75 |
| ETHUSDT | markPriceKlines | 2024-10-07 | 2024-12-20 | 75 / 731 | 75 | 108,000 | 75 | 75 |
| ETHUSDT | indexPriceKlines | 2024-10-07 | 2024-12-20 | 75 / 731 | 75 | 108,000 | 75 | 75 |
| ETHUSDT | premiumIndexKlines | 2024-10-07 | 2024-12-20 | 75 / 731 | 75 | 108,000 | 75 | 75 |
| ETHUSDT | metrics | 2024-10-07 | 2024-12-20 | 75 / 731 | 75 | 21,598 | 75 | 75 |
| ETHUSDT | fundingRate | 2024-11-01 | 2026-09-30 | 699 / 731 | 699 | 2,097 | 23 | 23 |
| SOLUSDT | trades | None | None | 0 / 731 | 0 | 0 | 0 | 0 |
| SOLUSDT | aggTrades | 2024-10-07 | 2024-12-20 | 75 / 731 | 75 | 32,565,421 | 75 | 75 |
| SOLUSDT | klines | 2024-10-07 | 2024-12-20 | 75 / 731 | 75 | 108,000 | 75 | 75 |
| SOLUSDT | markPriceKlines | 2024-10-07 | 2024-12-20 | 75 / 731 | 75 | 108,000 | 75 | 75 |
| SOLUSDT | indexPriceKlines | 2024-10-07 | 2024-12-20 | 75 / 731 | 75 | 108,000 | 75 | 75 |
| SOLUSDT | premiumIndexKlines | 2024-10-07 | 2024-12-20 | 75 / 731 | 75 | 108,000 | 75 | 75 |
| SOLUSDT | metrics | 2024-10-07 | 2024-12-20 | 75 / 731 | 75 | 21,598 | 75 | 75 |
| SOLUSDT | fundingRate | 2024-11-01 | 2026-09-30 | 699 / 731 | 699 | 2,097 | 23 | 23 |

Missing-date lists, failed partitions and remote URLs are in data_catalog.json. Unacquired dates do not imply Binance lacks those dates.

Funding archives are restricted to complete months inside the window. October 2024 and October 2026 need another permitted source for their in-window dates. No outside-window records were downloaded.
