# Current data coverage

Generated: 2026-10-08T20:45:26.094414+00:00

QA days count observed passing dates. Remote days require matching RAW and Parquet readback receipts. Monthly funding coverage counts observed dates, not one day per archive.

| Symbol | Dataset | First | Last | QA days / expected | Remote days | Rows | QA partitions | Remote partitions |
|---|---|---|---|---:|---:|---:|---:|---:|
| BTCUSDT | trades | None | None | 0 / 731 | 0 | 0 | 0 | 0 |
| BTCUSDT | aggTrades | 2024-10-07 | 2025-01-08 | 94 / 731 | 94 | 151,938,410 | 94 | 94 |
| BTCUSDT | klines | 2024-10-07 | 2025-01-08 | 94 / 731 | 94 | 135,360 | 94 | 94 |
| BTCUSDT | markPriceKlines | 2024-10-07 | 2025-01-08 | 94 / 731 | 94 | 135,360 | 94 | 94 |
| BTCUSDT | indexPriceKlines | 2024-10-07 | 2025-01-07 | 93 / 731 | 93 | 133,920 | 93 | 93 |
| BTCUSDT | premiumIndexKlines | 2024-10-07 | 2025-01-07 | 93 / 731 | 93 | 133,920 | 93 | 93 |
| BTCUSDT | metrics | 2024-10-07 | 2025-01-07 | 93 / 731 | 93 | 26,782 | 93 | 93 |
| BTCUSDT | fundingRate | 2024-11-01 | 2026-09-30 | 699 / 731 | 699 | 2,097 | 23 | 23 |
| ETHUSDT | trades | None | None | 0 / 731 | 0 | 0 | 0 | 0 |
| ETHUSDT | aggTrades | 2024-10-07 | 2025-01-07 | 93 / 731 | 93 | 163,357,040 | 93 | 93 |
| ETHUSDT | klines | 2024-10-07 | 2025-01-07 | 93 / 731 | 93 | 133,920 | 93 | 93 |
| ETHUSDT | markPriceKlines | 2024-10-07 | 2025-01-07 | 93 / 731 | 93 | 133,920 | 93 | 93 |
| ETHUSDT | indexPriceKlines | 2024-10-07 | 2025-01-07 | 93 / 731 | 93 | 133,920 | 93 | 93 |
| ETHUSDT | premiumIndexKlines | 2024-10-07 | 2025-01-07 | 93 / 731 | 93 | 133,920 | 93 | 93 |
| ETHUSDT | metrics | 2024-10-07 | 2025-01-07 | 93 / 731 | 93 | 26,782 | 93 | 93 |
| ETHUSDT | fundingRate | 2024-11-01 | 2026-09-30 | 699 / 731 | 699 | 2,097 | 23 | 23 |
| SOLUSDT | trades | None | None | 0 / 731 | 0 | 0 | 0 | 0 |
| SOLUSDT | aggTrades | 2024-10-07 | 2025-01-07 | 93 / 731 | 93 | 38,300,894 | 93 | 93 |
| SOLUSDT | klines | 2024-10-07 | 2025-01-07 | 93 / 731 | 93 | 133,920 | 93 | 93 |
| SOLUSDT | markPriceKlines | 2024-10-07 | 2025-01-07 | 93 / 731 | 93 | 133,920 | 93 | 93 |
| SOLUSDT | indexPriceKlines | 2024-10-07 | 2025-01-07 | 93 / 731 | 93 | 133,920 | 93 | 93 |
| SOLUSDT | premiumIndexKlines | 2024-10-07 | 2025-01-07 | 93 / 731 | 93 | 133,920 | 93 | 93 |
| SOLUSDT | metrics | 2024-10-07 | 2025-01-07 | 93 / 731 | 93 | 26,782 | 93 | 93 |
| SOLUSDT | fundingRate | 2024-11-01 | 2026-09-30 | 699 / 731 | 699 | 2,097 | 23 | 23 |

Missing-date lists, failed partitions and remote URLs are in data_catalog.json. Unacquired dates do not imply Binance lacks those dates.

Funding archives are restricted to complete months inside the window. October 2024 and October 2026 need another permitted source for their in-window dates. No outside-window records were downloaded.
