# Current data coverage

Generated: 2026-10-08T21:00:41.239051+00:00

QA days count observed passing dates. Remote days require matching RAW and Parquet readback receipts. Monthly funding coverage counts observed dates, not one day per archive.

| Symbol | Dataset | First | Last | QA days / expected | Remote days | Rows | QA partitions | Remote partitions |
|---|---|---|---|---:|---:|---:|---:|---:|
| BTCUSDT | trades | None | None | 0 / 731 | 0 | 0 | 0 | 0 |
| BTCUSDT | aggTrades | 2024-10-07 | 2025-01-10 | 96 / 731 | 96 | 156,293,694 | 96 | 96 |
| BTCUSDT | klines | 2024-10-07 | 2025-01-10 | 96 / 731 | 96 | 138,240 | 96 | 96 |
| BTCUSDT | markPriceKlines | 2024-10-07 | 2025-01-10 | 96 / 731 | 96 | 138,240 | 96 | 96 |
| BTCUSDT | indexPriceKlines | 2024-10-07 | 2025-01-10 | 96 / 731 | 96 | 138,240 | 96 | 96 |
| BTCUSDT | premiumIndexKlines | 2024-10-07 | 2025-01-10 | 96 / 731 | 96 | 138,240 | 96 | 96 |
| BTCUSDT | metrics | 2024-10-07 | 2025-01-10 | 96 / 731 | 96 | 27,646 | 96 | 96 |
| BTCUSDT | fundingRate | 2024-11-01 | 2026-09-30 | 699 / 731 | 699 | 2,097 | 23 | 23 |
| ETHUSDT | trades | None | None | 0 / 731 | 0 | 0 | 0 | 0 |
| ETHUSDT | aggTrades | 2024-10-07 | 2025-01-10 | 96 / 731 | 96 | 169,642,533 | 96 | 96 |
| ETHUSDT | klines | 2024-10-07 | 2025-01-10 | 96 / 731 | 96 | 138,240 | 96 | 96 |
| ETHUSDT | markPriceKlines | 2024-10-07 | 2025-01-10 | 96 / 731 | 96 | 138,240 | 96 | 96 |
| ETHUSDT | indexPriceKlines | 2024-10-07 | 2025-01-10 | 96 / 731 | 96 | 138,240 | 96 | 96 |
| ETHUSDT | premiumIndexKlines | 2024-10-07 | 2025-01-10 | 96 / 731 | 96 | 138,240 | 96 | 96 |
| ETHUSDT | metrics | 2024-10-07 | 2025-01-10 | 96 / 731 | 96 | 27,646 | 96 | 96 |
| ETHUSDT | fundingRate | 2024-11-01 | 2026-09-30 | 699 / 731 | 699 | 2,097 | 23 | 23 |
| SOLUSDT | trades | None | None | 0 / 731 | 0 | 0 | 0 | 0 |
| SOLUSDT | aggTrades | 2024-10-07 | 2025-01-10 | 96 / 731 | 96 | 39,507,833 | 96 | 96 |
| SOLUSDT | klines | 2024-10-07 | 2025-01-10 | 96 / 731 | 96 | 138,240 | 96 | 96 |
| SOLUSDT | markPriceKlines | 2024-10-07 | 2025-01-10 | 96 / 731 | 96 | 138,240 | 96 | 96 |
| SOLUSDT | indexPriceKlines | 2024-10-07 | 2025-01-10 | 96 / 731 | 96 | 138,240 | 96 | 96 |
| SOLUSDT | premiumIndexKlines | 2024-10-07 | 2025-01-10 | 96 / 731 | 96 | 138,240 | 96 | 96 |
| SOLUSDT | metrics | 2024-10-07 | 2025-01-09 | 95 / 731 | 95 | 27,358 | 95 | 95 |
| SOLUSDT | fundingRate | 2024-11-01 | 2026-09-30 | 699 / 731 | 699 | 2,097 | 23 | 23 |

Missing-date lists, failed partitions and remote URLs are in data_catalog.json. Unacquired dates do not imply Binance lacks those dates.

Funding archives are restricted to complete months inside the window. October 2024 and October 2026 need another permitted source for their in-window dates. No outside-window records were downloaded.
