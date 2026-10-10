# Current data coverage

Generated: 2026-10-10T05:52:14.912781+00:00

QA days count observed passing dates. Remote days require matching RAW and Parquet readback receipts. Monthly funding coverage counts observed dates, not one day per archive.

| Symbol | Dataset | First | Last | QA days / expected | Remote days | Rows | QA partitions | Remote partitions |
|---|---|---|---|---:|---:|---:|---:|---:|
| BTCUSDT | trades | None | None | 0 / 731 | 0 | 0 | 0 | 0 |
| BTCUSDT | aggTrades | 2024-10-07 | 2025-01-23 | 109 / 731 | 109 | 184,846,201 | 109 | 109 |
| BTCUSDT | klines | 2024-10-07 | 2025-01-23 | 109 / 731 | 109 | 156,960 | 109 | 109 |
| BTCUSDT | markPriceKlines | 2024-10-07 | 2025-01-23 | 109 / 731 | 109 | 156,960 | 109 | 109 |
| BTCUSDT | indexPriceKlines | 2024-10-07 | 2025-01-23 | 109 / 731 | 109 | 156,960 | 109 | 109 |
| BTCUSDT | premiumIndexKlines | 2024-10-07 | 2025-01-23 | 109 / 731 | 109 | 156,960 | 109 | 109 |
| BTCUSDT | metrics | 2024-10-07 | 2025-01-22 | 108 / 731 | 108 | 31,102 | 108 | 108 |
| BTCUSDT | fundingRate | 2024-11-01 | 2026-09-30 | 699 / 731 | 699 | 2,097 | 23 | 23 |
| ETHUSDT | trades | None | None | 0 / 731 | 0 | 0 | 0 | 0 |
| ETHUSDT | aggTrades | 2024-10-07 | 2025-01-22 | 108 / 731 | 108 | 195,124,465 | 108 | 108 |
| ETHUSDT | klines | 2024-10-07 | 2025-01-22 | 108 / 731 | 108 | 155,520 | 108 | 108 |
| ETHUSDT | markPriceKlines | 2024-10-07 | 2025-01-22 | 108 / 731 | 108 | 155,520 | 108 | 108 |
| ETHUSDT | indexPriceKlines | 2024-10-07 | 2025-01-22 | 108 / 731 | 108 | 155,520 | 108 | 108 |
| ETHUSDT | premiumIndexKlines | 2024-10-07 | 2025-01-22 | 108 / 731 | 108 | 155,520 | 108 | 108 |
| ETHUSDT | metrics | 2024-10-07 | 2025-01-22 | 108 / 731 | 108 | 31,102 | 108 | 108 |
| ETHUSDT | fundingRate | 2024-11-01 | 2026-09-30 | 699 / 731 | 699 | 2,097 | 23 | 23 |
| SOLUSDT | trades | None | None | 0 / 731 | 0 | 0 | 0 | 0 |
| SOLUSDT | aggTrades | 2024-10-07 | 2025-01-22 | 108 / 731 | 108 | 50,142,775 | 108 | 108 |
| SOLUSDT | klines | 2024-10-07 | 2025-01-22 | 108 / 731 | 108 | 155,520 | 108 | 108 |
| SOLUSDT | markPriceKlines | 2024-10-07 | 2025-01-22 | 108 / 731 | 108 | 155,520 | 108 | 108 |
| SOLUSDT | indexPriceKlines | 2024-10-07 | 2025-01-22 | 108 / 731 | 108 | 155,520 | 108 | 108 |
| SOLUSDT | premiumIndexKlines | 2024-10-07 | 2025-01-22 | 108 / 731 | 108 | 155,520 | 108 | 108 |
| SOLUSDT | metrics | 2024-10-07 | 2025-01-22 | 108 / 731 | 108 | 31,102 | 108 | 108 |
| SOLUSDT | fundingRate | 2024-11-01 | 2026-09-30 | 699 / 731 | 699 | 2,097 | 23 | 23 |

Missing-date lists, failed partitions and remote URLs are in data_catalog.json. Unacquired dates do not imply Binance lacks those dates.

Funding archives are restricted to complete months inside the window. October 2024 and October 2026 need another permitted source for their in-window dates. No outside-window records were downloaded.
