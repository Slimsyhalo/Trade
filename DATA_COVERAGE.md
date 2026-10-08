# Current data coverage

Generated: 2026-10-08T21:23:01.316839+00:00

QA days count observed passing dates. Remote days require matching RAW and Parquet readback receipts. Monthly funding coverage counts observed dates, not one day per archive.

| Symbol | Dataset | First | Last | QA days / expected | Remote days | Rows | QA partitions | Remote partitions |
|---|---|---|---|---:|---:|---:|---:|---:|
| BTCUSDT | trades | None | None | 0 / 731 | 0 | 0 | 0 | 0 |
| BTCUSDT | aggTrades | 2024-10-07 | 2025-01-15 | 101 / 731 | 101 | 163,655,453 | 101 | 101 |
| BTCUSDT | klines | 2024-10-07 | 2025-01-15 | 101 / 731 | 101 | 145,440 | 101 | 101 |
| BTCUSDT | markPriceKlines | 2024-10-07 | 2025-01-14 | 100 / 731 | 100 | 144,000 | 100 | 100 |
| BTCUSDT | indexPriceKlines | 2024-10-07 | 2025-01-14 | 100 / 731 | 100 | 144,000 | 100 | 100 |
| BTCUSDT | premiumIndexKlines | 2024-10-07 | 2025-01-14 | 100 / 731 | 100 | 144,000 | 100 | 100 |
| BTCUSDT | metrics | 2024-10-07 | 2025-01-14 | 100 / 731 | 100 | 28,798 | 100 | 100 |
| BTCUSDT | fundingRate | 2024-11-01 | 2026-09-30 | 699 / 731 | 699 | 2,097 | 23 | 23 |
| ETHUSDT | trades | None | None | 0 / 731 | 0 | 0 | 0 | 0 |
| ETHUSDT | aggTrades | 2024-10-07 | 2025-01-14 | 100 / 731 | 100 | 175,500,165 | 100 | 100 |
| ETHUSDT | klines | 2024-10-07 | 2025-01-14 | 100 / 731 | 100 | 144,000 | 100 | 100 |
| ETHUSDT | markPriceKlines | 2024-10-07 | 2025-01-14 | 100 / 731 | 100 | 144,000 | 100 | 100 |
| ETHUSDT | indexPriceKlines | 2024-10-07 | 2025-01-14 | 100 / 731 | 100 | 144,000 | 100 | 100 |
| ETHUSDT | premiumIndexKlines | 2024-10-07 | 2025-01-14 | 100 / 731 | 100 | 144,000 | 100 | 100 |
| ETHUSDT | metrics | 2024-10-07 | 2025-01-14 | 100 / 731 | 100 | 28,798 | 100 | 100 |
| ETHUSDT | fundingRate | 2024-11-01 | 2026-09-30 | 699 / 731 | 699 | 2,097 | 23 | 23 |
| SOLUSDT | trades | None | None | 0 / 731 | 0 | 0 | 0 | 0 |
| SOLUSDT | aggTrades | 2024-10-07 | 2025-01-14 | 100 / 731 | 100 | 40,729,133 | 100 | 100 |
| SOLUSDT | klines | 2024-10-07 | 2025-01-14 | 100 / 731 | 100 | 144,000 | 100 | 100 |
| SOLUSDT | markPriceKlines | 2024-10-07 | 2025-01-14 | 100 / 731 | 100 | 144,000 | 100 | 100 |
| SOLUSDT | indexPriceKlines | 2024-10-07 | 2025-01-14 | 100 / 731 | 100 | 144,000 | 100 | 100 |
| SOLUSDT | premiumIndexKlines | 2024-10-07 | 2025-01-14 | 100 / 731 | 100 | 144,000 | 100 | 100 |
| SOLUSDT | metrics | 2024-10-07 | 2025-01-14 | 100 / 731 | 100 | 28,798 | 100 | 100 |
| SOLUSDT | fundingRate | 2024-11-01 | 2026-09-30 | 699 / 731 | 699 | 2,097 | 23 | 23 |

Missing-date lists, failed partitions and remote URLs are in data_catalog.json. Unacquired dates do not imply Binance lacks those dates.

Funding archives are restricted to complete months inside the window. October 2024 and October 2026 need another permitted source for their in-window dates. No outside-window records were downloaded.
