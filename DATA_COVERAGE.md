# Current data coverage

Generated: 2026-10-08T22:04:04.865182+00:00

QA days count observed passing dates. Remote days require matching RAW and Parquet readback receipts. Monthly funding coverage counts observed dates, not one day per archive.

| Symbol | Dataset | First | Last | QA days / expected | Remote days | Rows | QA partitions | Remote partitions |
|---|---|---|---|---:|---:|---:|---:|---:|
| BTCUSDT | trades | None | None | 0 / 731 | 0 | 0 | 0 | 0 |
| BTCUSDT | aggTrades | 2024-10-07 | 2025-01-22 | 108 / 731 | 108 | 180,854,468 | 108 | 108 |
| BTCUSDT | klines | 2024-10-07 | 2025-01-21 | 107 / 731 | 107 | 154,080 | 107 | 107 |
| BTCUSDT | markPriceKlines | 2024-10-07 | 2025-01-21 | 107 / 731 | 107 | 154,080 | 107 | 107 |
| BTCUSDT | indexPriceKlines | 2024-10-07 | 2025-01-21 | 107 / 731 | 107 | 154,080 | 107 | 107 |
| BTCUSDT | premiumIndexKlines | 2024-10-07 | 2025-01-21 | 107 / 731 | 107 | 154,080 | 107 | 107 |
| BTCUSDT | metrics | 2024-10-07 | 2025-01-21 | 107 / 731 | 107 | 30,814 | 107 | 107 |
| BTCUSDT | fundingRate | 2024-11-01 | 2026-09-30 | 699 / 731 | 699 | 2,097 | 23 | 23 |
| ETHUSDT | trades | None | None | 0 / 731 | 0 | 0 | 0 | 0 |
| ETHUSDT | aggTrades | 2024-10-07 | 2025-01-21 | 107 / 731 | 107 | 193,817,830 | 107 | 107 |
| ETHUSDT | klines | 2024-10-07 | 2025-01-21 | 107 / 731 | 107 | 154,080 | 107 | 107 |
| ETHUSDT | markPriceKlines | 2024-10-07 | 2025-01-21 | 107 / 731 | 107 | 154,080 | 107 | 107 |
| ETHUSDT | indexPriceKlines | 2024-10-07 | 2025-01-21 | 107 / 731 | 107 | 154,080 | 107 | 107 |
| ETHUSDT | premiumIndexKlines | 2024-10-07 | 2025-01-21 | 107 / 731 | 107 | 154,080 | 107 | 107 |
| ETHUSDT | metrics | 2024-10-07 | 2025-01-21 | 107 / 731 | 107 | 30,814 | 107 | 107 |
| ETHUSDT | fundingRate | 2024-11-01 | 2026-09-30 | 699 / 731 | 699 | 2,097 | 23 | 23 |
| SOLUSDT | trades | None | None | 0 / 731 | 0 | 0 | 0 | 0 |
| SOLUSDT | aggTrades | 2024-10-07 | 2025-01-21 | 107 / 731 | 107 | 49,376,319 | 107 | 107 |
| SOLUSDT | klines | 2024-10-07 | 2025-01-21 | 107 / 731 | 107 | 154,080 | 107 | 107 |
| SOLUSDT | markPriceKlines | 2024-10-07 | 2025-01-21 | 107 / 731 | 107 | 154,080 | 107 | 107 |
| SOLUSDT | indexPriceKlines | 2024-10-07 | 2025-01-21 | 107 / 731 | 107 | 154,080 | 107 | 107 |
| SOLUSDT | premiumIndexKlines | 2024-10-07 | 2025-01-21 | 107 / 731 | 107 | 154,080 | 107 | 107 |
| SOLUSDT | metrics | 2024-10-07 | 2025-01-21 | 107 / 731 | 107 | 30,814 | 107 | 107 |
| SOLUSDT | fundingRate | 2024-11-01 | 2026-09-30 | 699 / 731 | 699 | 2,097 | 23 | 23 |

Missing-date lists, failed partitions and remote URLs are in data_catalog.json. Unacquired dates do not imply Binance lacks those dates.

Funding archives are restricted to complete months inside the window. October 2024 and October 2026 need another permitted source for their in-window dates. No outside-window records were downloaded.
