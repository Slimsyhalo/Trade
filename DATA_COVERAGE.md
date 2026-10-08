# Current data coverage

Generated: 2026-10-08T21:30:34.727674+00:00

QA days count observed passing dates. Remote days require matching RAW and Parquet readback receipts. Monthly funding coverage counts observed dates, not one day per archive.

| Symbol | Dataset | First | Last | QA days / expected | Remote days | Rows | QA partitions | Remote partitions |
|---|---|---|---|---:|---:|---:|---:|---:|
| BTCUSDT | trades | None | None | 0 / 731 | 0 | 0 | 0 | 0 |
| BTCUSDT | aggTrades | 2024-10-07 | 2025-01-16 | 102 / 731 | 102 | 165,301,406 | 102 | 102 |
| BTCUSDT | klines | 2024-10-07 | 2025-01-16 | 102 / 731 | 102 | 146,880 | 102 | 102 |
| BTCUSDT | markPriceKlines | 2024-10-07 | 2025-01-16 | 102 / 731 | 102 | 146,880 | 102 | 102 |
| BTCUSDT | indexPriceKlines | 2024-10-07 | 2025-01-16 | 102 / 731 | 102 | 146,880 | 102 | 102 |
| BTCUSDT | premiumIndexKlines | 2024-10-07 | 2025-01-16 | 102 / 731 | 102 | 146,880 | 102 | 102 |
| BTCUSDT | metrics | 2024-10-07 | 2025-01-16 | 102 / 731 | 102 | 29,374 | 102 | 102 |
| BTCUSDT | fundingRate | 2024-11-01 | 2026-09-30 | 699 / 731 | 699 | 2,097 | 23 | 23 |
| ETHUSDT | trades | None | None | 0 / 731 | 0 | 0 | 0 | 0 |
| ETHUSDT | aggTrades | 2024-10-07 | 2025-01-16 | 102 / 731 | 102 | 178,986,122 | 102 | 102 |
| ETHUSDT | klines | 2024-10-07 | 2025-01-16 | 102 / 731 | 102 | 146,880 | 102 | 102 |
| ETHUSDT | markPriceKlines | 2024-10-07 | 2025-01-16 | 102 / 731 | 102 | 146,880 | 102 | 102 |
| ETHUSDT | indexPriceKlines | 2024-10-07 | 2025-01-15 | 101 / 731 | 101 | 145,440 | 101 | 101 |
| ETHUSDT | premiumIndexKlines | 2024-10-07 | 2025-01-15 | 101 / 731 | 101 | 145,440 | 101 | 101 |
| ETHUSDT | metrics | 2024-10-07 | 2025-01-15 | 101 / 731 | 101 | 29,086 | 101 | 101 |
| ETHUSDT | fundingRate | 2024-11-01 | 2026-09-30 | 699 / 731 | 699 | 2,097 | 23 | 23 |
| SOLUSDT | trades | None | None | 0 / 731 | 0 | 0 | 0 | 0 |
| SOLUSDT | aggTrades | 2024-10-07 | 2025-01-15 | 101 / 731 | 101 | 41,086,911 | 101 | 101 |
| SOLUSDT | klines | 2024-10-07 | 2025-01-15 | 101 / 731 | 101 | 145,440 | 101 | 101 |
| SOLUSDT | markPriceKlines | 2024-10-07 | 2025-01-15 | 101 / 731 | 101 | 145,440 | 101 | 101 |
| SOLUSDT | indexPriceKlines | 2024-10-07 | 2025-01-15 | 101 / 731 | 101 | 145,440 | 101 | 101 |
| SOLUSDT | premiumIndexKlines | 2024-10-07 | 2025-01-15 | 101 / 731 | 101 | 145,440 | 101 | 101 |
| SOLUSDT | metrics | 2024-10-07 | 2025-01-15 | 101 / 731 | 101 | 29,086 | 101 | 101 |
| SOLUSDT | fundingRate | 2024-11-01 | 2026-09-30 | 699 / 731 | 699 | 2,097 | 23 | 23 |

Missing-date lists, failed partitions and remote URLs are in data_catalog.json. Unacquired dates do not imply Binance lacks those dates.

Funding archives are restricted to complete months inside the window. October 2024 and October 2026 need another permitted source for their in-window dates. No outside-window records were downloaded.
