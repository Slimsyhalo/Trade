# Current data coverage

Generated: 2026-10-08T20:37:42.305140+00:00

QA days count observed passing dates. Remote days require matching RAW and Parquet readback receipts. Monthly funding coverage counts observed dates, not one day per archive.

| Symbol | Dataset | First | Last | QA days / expected | Remote days | Rows | QA partitions | Remote partitions |
|---|---|---|---|---:|---:|---:|---:|---:|
| BTCUSDT | trades | None | None | 0 / 731 | 0 | 0 | 0 | 0 |
| BTCUSDT | aggTrades | 2024-10-07 | 2025-01-06 | 92 / 731 | 92 | 147,851,504 | 92 | 92 |
| BTCUSDT | klines | 2024-10-07 | 2025-01-06 | 92 / 731 | 92 | 132,480 | 92 | 92 |
| BTCUSDT | markPriceKlines | 2024-10-07 | 2025-01-06 | 92 / 731 | 92 | 132,480 | 92 | 92 |
| BTCUSDT | indexPriceKlines | 2024-10-07 | 2025-01-06 | 92 / 731 | 92 | 132,480 | 92 | 92 |
| BTCUSDT | premiumIndexKlines | 2024-10-07 | 2025-01-06 | 92 / 731 | 92 | 132,480 | 92 | 92 |
| BTCUSDT | metrics | 2024-10-07 | 2025-01-06 | 92 / 731 | 92 | 26,494 | 92 | 92 |
| BTCUSDT | fundingRate | 2024-11-01 | 2026-09-30 | 699 / 731 | 699 | 2,097 | 23 | 23 |
| ETHUSDT | trades | None | None | 0 / 731 | 0 | 0 | 0 | 0 |
| ETHUSDT | aggTrades | 2024-10-07 | 2025-01-06 | 92 / 731 | 92 | 161,357,945 | 92 | 92 |
| ETHUSDT | klines | 2024-10-07 | 2025-01-06 | 92 / 731 | 92 | 132,480 | 92 | 92 |
| ETHUSDT | markPriceKlines | 2024-10-07 | 2025-01-06 | 92 / 731 | 92 | 132,480 | 92 | 92 |
| ETHUSDT | indexPriceKlines | 2024-10-07 | 2025-01-06 | 92 / 731 | 92 | 132,480 | 92 | 92 |
| ETHUSDT | premiumIndexKlines | 2024-10-07 | 2025-01-06 | 92 / 731 | 92 | 132,480 | 92 | 92 |
| ETHUSDT | metrics | 2024-10-07 | 2025-01-06 | 92 / 731 | 92 | 26,494 | 92 | 92 |
| ETHUSDT | fundingRate | 2024-11-01 | 2026-09-30 | 699 / 731 | 699 | 2,097 | 23 | 23 |
| SOLUSDT | trades | None | None | 0 / 731 | 0 | 0 | 0 | 0 |
| SOLUSDT | aggTrades | 2024-10-07 | 2025-01-06 | 92 / 731 | 92 | 37,925,885 | 92 | 92 |
| SOLUSDT | klines | 2024-10-07 | 2025-01-06 | 92 / 731 | 92 | 132,480 | 92 | 92 |
| SOLUSDT | markPriceKlines | 2024-10-07 | 2025-01-05 | 91 / 731 | 91 | 131,040 | 91 | 91 |
| SOLUSDT | indexPriceKlines | 2024-10-07 | 2025-01-05 | 91 / 731 | 91 | 131,040 | 91 | 91 |
| SOLUSDT | premiumIndexKlines | 2024-10-07 | 2025-01-05 | 91 / 731 | 91 | 131,040 | 91 | 91 |
| SOLUSDT | metrics | 2024-10-07 | 2025-01-05 | 91 / 731 | 91 | 26,206 | 91 | 91 |
| SOLUSDT | fundingRate | 2024-11-01 | 2026-09-30 | 699 / 731 | 699 | 2,097 | 23 | 23 |

Missing-date lists, failed partitions and remote URLs are in data_catalog.json. Unacquired dates do not imply Binance lacks those dates.

Funding archives are restricted to complete months inside the window. October 2024 and October 2026 need another permitted source for their in-window dates. No outside-window records were downloaded.
