# Current data coverage

Generated: 2026-10-08T21:51:48.337765+00:00

QA days count observed passing dates. Remote days require matching RAW and Parquet readback receipts. Monthly funding coverage counts observed dates, not one day per archive.

| Symbol | Dataset | First | Last | QA days / expected | Remote days | Rows | QA partitions | Remote partitions |
|---|---|---|---|---:|---:|---:|---:|---:|
| BTCUSDT | trades | None | None | 0 / 731 | 0 | 0 | 0 | 0 |
| BTCUSDT | aggTrades | 2024-10-07 | 2025-01-20 | 106 / 731 | 106 | 176,200,501 | 106 | 106 |
| BTCUSDT | klines | 2024-10-07 | 2025-01-19 | 105 / 731 | 105 | 151,200 | 105 | 105 |
| BTCUSDT | markPriceKlines | 2024-10-07 | 2025-01-19 | 105 / 731 | 105 | 151,200 | 105 | 105 |
| BTCUSDT | indexPriceKlines | 2024-10-07 | 2025-01-19 | 105 / 731 | 105 | 151,200 | 105 | 105 |
| BTCUSDT | premiumIndexKlines | 2024-10-07 | 2025-01-19 | 105 / 731 | 105 | 151,200 | 105 | 105 |
| BTCUSDT | metrics | 2024-10-07 | 2025-01-19 | 105 / 731 | 105 | 30,238 | 105 | 105 |
| BTCUSDT | fundingRate | 2024-11-01 | 2026-09-30 | 699 / 731 | 699 | 2,097 | 23 | 23 |
| ETHUSDT | trades | None | None | 0 / 731 | 0 | 0 | 0 | 0 |
| ETHUSDT | aggTrades | 2024-10-07 | 2025-01-19 | 105 / 731 | 105 | 186,623,808 | 105 | 105 |
| ETHUSDT | klines | 2024-10-07 | 2025-01-19 | 105 / 731 | 105 | 151,200 | 105 | 105 |
| ETHUSDT | markPriceKlines | 2024-10-07 | 2025-01-19 | 105 / 731 | 105 | 151,200 | 105 | 105 |
| ETHUSDT | indexPriceKlines | 2024-10-07 | 2025-01-19 | 105 / 731 | 105 | 151,200 | 105 | 105 |
| ETHUSDT | premiumIndexKlines | 2024-10-07 | 2025-01-19 | 105 / 731 | 105 | 151,200 | 105 | 105 |
| ETHUSDT | metrics | 2024-10-07 | 2025-01-19 | 105 / 731 | 105 | 30,238 | 105 | 105 |
| ETHUSDT | fundingRate | 2024-11-01 | 2026-09-30 | 699 / 731 | 699 | 2,097 | 23 | 23 |
| SOLUSDT | trades | None | None | 0 / 731 | 0 | 0 | 0 | 0 |
| SOLUSDT | aggTrades | 2024-10-07 | 2025-01-19 | 105 / 731 | 105 | 46,403,798 | 105 | 105 |
| SOLUSDT | klines | 2024-10-07 | 2025-01-19 | 105 / 731 | 105 | 151,200 | 105 | 105 |
| SOLUSDT | markPriceKlines | 2024-10-07 | 2025-01-19 | 105 / 731 | 105 | 151,200 | 105 | 105 |
| SOLUSDT | indexPriceKlines | 2024-10-07 | 2025-01-19 | 105 / 731 | 105 | 151,200 | 105 | 105 |
| SOLUSDT | premiumIndexKlines | 2024-10-07 | 2025-01-19 | 105 / 731 | 105 | 151,200 | 105 | 105 |
| SOLUSDT | metrics | 2024-10-07 | 2025-01-19 | 105 / 731 | 105 | 30,238 | 105 | 105 |
| SOLUSDT | fundingRate | 2024-11-01 | 2026-09-30 | 699 / 731 | 699 | 2,097 | 23 | 23 |

Missing-date lists, failed partitions and remote URLs are in data_catalog.json. Unacquired dates do not imply Binance lacks those dates.

Funding archives are restricted to complete months inside the window. October 2024 and October 2026 need another permitted source for their in-window dates. No outside-window records were downloaded.
