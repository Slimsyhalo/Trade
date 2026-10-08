# Current data coverage

Generated: 2026-10-08T20:23:22.809242+00:00

QA days count observed passing dates. Remote days require matching RAW and Parquet readback receipts. Monthly funding coverage counts observed dates, not one day per archive.

| Symbol | Dataset | First | Last | QA days / expected | Remote days | Rows | QA partitions | Remote partitions |
|---|---|---|---|---:|---:|---:|---:|---:|
| BTCUSDT | trades | None | None | 0 / 731 | 0 | 0 | 0 | 0 |
| BTCUSDT | aggTrades | 2024-10-07 | 2025-01-03 | 89 / 731 | 89 | 145,079,241 | 89 | 89 |
| BTCUSDT | klines | 2024-10-07 | 2025-01-03 | 89 / 731 | 89 | 128,160 | 89 | 89 |
| BTCUSDT | markPriceKlines | 2024-10-07 | 2025-01-03 | 89 / 731 | 89 | 128,160 | 89 | 89 |
| BTCUSDT | indexPriceKlines | 2024-10-07 | 2025-01-03 | 89 / 731 | 89 | 128,160 | 89 | 89 |
| BTCUSDT | premiumIndexKlines | 2024-10-07 | 2025-01-03 | 89 / 731 | 89 | 128,160 | 89 | 89 |
| BTCUSDT | metrics | 2024-10-07 | 2025-01-03 | 89 / 731 | 89 | 25,630 | 89 | 89 |
| BTCUSDT | fundingRate | 2024-11-01 | 2026-09-30 | 699 / 731 | 699 | 2,097 | 23 | 23 |
| ETHUSDT | trades | None | None | 0 / 731 | 0 | 0 | 0 | 0 |
| ETHUSDT | aggTrades | 2024-10-07 | 2025-01-03 | 89 / 731 | 89 | 158,222,206 | 89 | 89 |
| ETHUSDT | klines | 2024-10-07 | 2025-01-03 | 89 / 731 | 89 | 128,160 | 89 | 89 |
| ETHUSDT | markPriceKlines | 2024-10-07 | 2025-01-03 | 89 / 731 | 89 | 128,160 | 89 | 89 |
| ETHUSDT | indexPriceKlines | 2024-10-07 | 2025-01-03 | 89 / 731 | 89 | 128,160 | 89 | 89 |
| ETHUSDT | premiumIndexKlines | 2024-10-07 | 2025-01-03 | 89 / 731 | 89 | 128,160 | 89 | 89 |
| ETHUSDT | metrics | 2024-10-07 | 2025-01-03 | 89 / 731 | 89 | 25,630 | 89 | 89 |
| ETHUSDT | fundingRate | 2024-11-01 | 2026-09-30 | 699 / 731 | 699 | 2,097 | 23 | 23 |
| SOLUSDT | trades | None | None | 0 / 731 | 0 | 0 | 0 | 0 |
| SOLUSDT | aggTrades | 2024-10-07 | 2025-01-03 | 89 / 731 | 89 | 37,216,438 | 89 | 89 |
| SOLUSDT | klines | 2024-10-07 | 2025-01-03 | 89 / 731 | 89 | 128,160 | 89 | 89 |
| SOLUSDT | markPriceKlines | 2024-10-07 | 2025-01-03 | 89 / 731 | 89 | 128,160 | 89 | 89 |
| SOLUSDT | indexPriceKlines | 2024-10-07 | 2025-01-03 | 89 / 731 | 89 | 128,160 | 89 | 89 |
| SOLUSDT | premiumIndexKlines | 2024-10-07 | 2025-01-03 | 89 / 731 | 89 | 128,160 | 89 | 89 |
| SOLUSDT | metrics | 2024-10-07 | 2025-01-03 | 89 / 731 | 89 | 25,630 | 89 | 89 |
| SOLUSDT | fundingRate | 2024-11-01 | 2026-09-30 | 699 / 731 | 699 | 2,097 | 23 | 23 |

Missing-date lists, failed partitions and remote URLs are in data_catalog.json. Unacquired dates do not imply Binance lacks those dates.

Funding archives are restricted to complete months inside the window. October 2024 and October 2026 need another permitted source for their in-window dates. No outside-window records were downloaded.
