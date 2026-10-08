# Current data coverage

Generated: 2026-10-08T21:07:39.544788+00:00

QA days count observed passing dates. Remote days require matching RAW and Parquet readback receipts. Monthly funding coverage counts observed dates, not one day per archive.

| Symbol | Dataset | First | Last | QA days / expected | Remote days | Rows | QA partitions | Remote partitions |
|---|---|---|---|---:|---:|---:|---:|---:|
| BTCUSDT | trades | None | None | 0 / 731 | 0 | 0 | 0 | 0 |
| BTCUSDT | aggTrades | 2024-10-07 | 2025-01-12 | 98 / 731 | 98 | 157,495,397 | 98 | 98 |
| BTCUSDT | klines | 2024-10-07 | 2025-01-12 | 98 / 731 | 98 | 141,120 | 98 | 98 |
| BTCUSDT | markPriceKlines | 2024-10-07 | 2025-01-12 | 98 / 731 | 98 | 141,120 | 98 | 98 |
| BTCUSDT | indexPriceKlines | 2024-10-07 | 2025-01-12 | 98 / 731 | 98 | 141,120 | 98 | 98 |
| BTCUSDT | premiumIndexKlines | 2024-10-07 | 2025-01-12 | 98 / 731 | 98 | 141,120 | 98 | 98 |
| BTCUSDT | metrics | 2024-10-07 | 2025-01-12 | 98 / 731 | 98 | 28,222 | 98 | 98 |
| BTCUSDT | fundingRate | 2024-11-01 | 2026-09-30 | 699 / 731 | 699 | 2,097 | 23 | 23 |
| ETHUSDT | trades | None | None | 0 / 731 | 0 | 0 | 0 | 0 |
| ETHUSDT | aggTrades | 2024-10-07 | 2025-01-11 | 97 / 731 | 97 | 170,423,190 | 97 | 97 |
| ETHUSDT | klines | 2024-10-07 | 2025-01-11 | 97 / 731 | 97 | 139,680 | 97 | 97 |
| ETHUSDT | markPriceKlines | 2024-10-07 | 2025-01-11 | 97 / 731 | 97 | 139,680 | 97 | 97 |
| ETHUSDT | indexPriceKlines | 2024-10-07 | 2025-01-11 | 97 / 731 | 97 | 139,680 | 97 | 97 |
| ETHUSDT | premiumIndexKlines | 2024-10-07 | 2025-01-11 | 97 / 731 | 97 | 139,680 | 97 | 97 |
| ETHUSDT | metrics | 2024-10-07 | 2025-01-11 | 97 / 731 | 97 | 27,934 | 97 | 97 |
| ETHUSDT | fundingRate | 2024-11-01 | 2026-09-30 | 699 / 731 | 699 | 2,097 | 23 | 23 |
| SOLUSDT | trades | None | None | 0 / 731 | 0 | 0 | 0 | 0 |
| SOLUSDT | aggTrades | 2024-10-07 | 2025-01-11 | 97 / 731 | 97 | 39,719,972 | 97 | 97 |
| SOLUSDT | klines | 2024-10-07 | 2025-01-11 | 97 / 731 | 97 | 139,680 | 97 | 97 |
| SOLUSDT | markPriceKlines | 2024-10-07 | 2025-01-11 | 97 / 731 | 97 | 139,680 | 97 | 97 |
| SOLUSDT | indexPriceKlines | 2024-10-07 | 2025-01-11 | 97 / 731 | 97 | 139,680 | 97 | 97 |
| SOLUSDT | premiumIndexKlines | 2024-10-07 | 2025-01-11 | 97 / 731 | 97 | 139,680 | 97 | 97 |
| SOLUSDT | metrics | 2024-10-07 | 2025-01-11 | 97 / 731 | 97 | 27,934 | 97 | 97 |
| SOLUSDT | fundingRate | 2024-11-01 | 2026-09-30 | 699 / 731 | 699 | 2,097 | 23 | 23 |

Missing-date lists, failed partitions and remote URLs are in data_catalog.json. Unacquired dates do not imply Binance lacks those dates.

Funding archives are restricted to complete months inside the window. October 2024 and October 2026 need another permitted source for their in-window dates. No outside-window records were downloaded.
