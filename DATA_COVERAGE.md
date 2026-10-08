# Current data coverage

Generated: 2026-10-08T20:30:29.744806+00:00

QA days count observed passing dates. Remote days require matching RAW and Parquet readback receipts. Monthly funding coverage counts observed dates, not one day per archive.

| Symbol | Dataset | First | Last | QA days / expected | Remote days | Rows | QA partitions | Remote partitions |
|---|---|---|---|---:|---:|---:|---:|---:|
| BTCUSDT | trades | None | None | 0 / 731 | 0 | 0 | 0 | 0 |
| BTCUSDT | aggTrades | 2024-10-07 | 2025-01-05 | 91 / 731 | 91 | 146,250,643 | 91 | 91 |
| BTCUSDT | klines | 2024-10-07 | 2025-01-05 | 91 / 731 | 91 | 131,040 | 91 | 91 |
| BTCUSDT | markPriceKlines | 2024-10-07 | 2025-01-05 | 91 / 731 | 91 | 131,040 | 91 | 91 |
| BTCUSDT | indexPriceKlines | 2024-10-07 | 2025-01-05 | 91 / 731 | 91 | 131,040 | 91 | 91 |
| BTCUSDT | premiumIndexKlines | 2024-10-07 | 2025-01-05 | 91 / 731 | 91 | 131,040 | 91 | 91 |
| BTCUSDT | metrics | 2024-10-07 | 2025-01-05 | 91 / 731 | 91 | 26,206 | 91 | 91 |
| BTCUSDT | fundingRate | 2024-11-01 | 2026-09-30 | 699 / 731 | 699 | 2,097 | 23 | 23 |
| ETHUSDT | trades | None | None | 0 / 731 | 0 | 0 | 0 | 0 |
| ETHUSDT | aggTrades | 2024-10-07 | 2025-01-05 | 91 / 731 | 91 | 159,922,556 | 91 | 91 |
| ETHUSDT | klines | 2024-10-07 | 2025-01-04 | 90 / 731 | 90 | 129,600 | 90 | 90 |
| ETHUSDT | markPriceKlines | 2024-10-07 | 2025-01-04 | 90 / 731 | 90 | 129,600 | 90 | 90 |
| ETHUSDT | indexPriceKlines | 2024-10-07 | 2025-01-04 | 90 / 731 | 90 | 129,600 | 90 | 90 |
| ETHUSDT | premiumIndexKlines | 2024-10-07 | 2025-01-04 | 90 / 731 | 90 | 129,600 | 90 | 90 |
| ETHUSDT | metrics | 2024-10-07 | 2025-01-04 | 90 / 731 | 90 | 25,918 | 90 | 90 |
| ETHUSDT | fundingRate | 2024-11-01 | 2026-09-30 | 699 / 731 | 699 | 2,097 | 23 | 23 |
| SOLUSDT | trades | None | None | 0 / 731 | 0 | 0 | 0 | 0 |
| SOLUSDT | aggTrades | 2024-10-07 | 2025-01-04 | 90 / 731 | 90 | 37,412,058 | 90 | 90 |
| SOLUSDT | klines | 2024-10-07 | 2025-01-04 | 90 / 731 | 90 | 129,600 | 90 | 90 |
| SOLUSDT | markPriceKlines | 2024-10-07 | 2025-01-04 | 90 / 731 | 90 | 129,600 | 90 | 90 |
| SOLUSDT | indexPriceKlines | 2024-10-07 | 2025-01-04 | 90 / 731 | 90 | 129,600 | 90 | 90 |
| SOLUSDT | premiumIndexKlines | 2024-10-07 | 2025-01-04 | 90 / 731 | 90 | 129,600 | 90 | 90 |
| SOLUSDT | metrics | 2024-10-07 | 2025-01-04 | 90 / 731 | 90 | 25,918 | 90 | 90 |
| SOLUSDT | fundingRate | 2024-11-01 | 2026-09-30 | 699 / 731 | 699 | 2,097 | 23 | 23 |

Missing-date lists, failed partitions and remote URLs are in data_catalog.json. Unacquired dates do not imply Binance lacks those dates.

Funding archives are restricted to complete months inside the window. October 2024 and October 2026 need another permitted source for their in-window dates. No outside-window records were downloaded.
