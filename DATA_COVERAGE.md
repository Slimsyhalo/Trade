# Current data coverage

Generated: 2026-10-08T16:11:16.121139+00:00

QA days count observed passing dates. Remote days require matching RAW and Parquet readback receipts. Monthly funding coverage counts observed dates, not one day per archive.

| Symbol | Dataset | First | Last | QA days / expected | Remote days | Rows | QA partitions | Remote partitions |
|---|---|---|---|---:|---:|---:|---:|---:|
| BTCUSDT | trades | None | None | 0 / 731 | 0 | 0 | 0 | 0 |
| BTCUSDT | aggTrades | 2024-10-07 | 2024-12-16 | 71 / 731 | 71 | 114,153,483 | 71 | 71 |
| BTCUSDT | klines | 2024-10-07 | 2024-12-16 | 71 / 731 | 71 | 102,240 | 71 | 71 |
| BTCUSDT | markPriceKlines | 2024-10-07 | 2024-12-16 | 71 / 731 | 71 | 102,240 | 71 | 71 |
| BTCUSDT | indexPriceKlines | 2024-10-07 | 2024-12-16 | 71 / 731 | 71 | 102,240 | 71 | 71 |
| BTCUSDT | premiumIndexKlines | 2024-10-07 | 2024-12-16 | 71 / 731 | 71 | 102,240 | 71 | 71 |
| BTCUSDT | metrics | 2024-10-07 | 2024-12-16 | 71 / 731 | 71 | 20,446 | 71 | 71 |
| BTCUSDT | fundingRate | 2024-11-01 | 2026-01-31 | 457 / 731 | 457 | 1,371 | 15 | 15 |
| ETHUSDT | trades | None | None | 0 / 731 | 0 | 0 | 0 | 0 |
| ETHUSDT | aggTrades | 2024-10-07 | 2024-12-16 | 71 / 731 | 71 | 123,950,165 | 71 | 71 |
| ETHUSDT | klines | 2024-10-07 | 2024-12-16 | 71 / 731 | 71 | 102,240 | 71 | 71 |
| ETHUSDT | markPriceKlines | 2024-10-07 | 2024-12-16 | 71 / 731 | 71 | 102,240 | 71 | 71 |
| ETHUSDT | indexPriceKlines | 2024-10-07 | 2024-12-15 | 70 / 731 | 70 | 100,800 | 70 | 70 |
| ETHUSDT | premiumIndexKlines | 2024-10-07 | 2024-12-15 | 70 / 731 | 70 | 100,800 | 70 | 70 |
| ETHUSDT | metrics | 2024-10-07 | 2024-12-15 | 70 / 731 | 70 | 20,158 | 70 | 70 |
| ETHUSDT | fundingRate | None | None | 0 / 731 | 0 | 0 | 0 | 0 |
| SOLUSDT | trades | None | None | 0 / 731 | 0 | 0 | 0 | 0 |
| SOLUSDT | aggTrades | 2024-10-07 | 2024-12-15 | 70 / 731 | 70 | 29,546,563 | 70 | 70 |
| SOLUSDT | klines | 2024-10-07 | 2024-12-15 | 70 / 731 | 70 | 100,800 | 70 | 70 |
| SOLUSDT | markPriceKlines | 2024-10-07 | 2024-12-15 | 70 / 731 | 70 | 100,800 | 70 | 70 |
| SOLUSDT | indexPriceKlines | 2024-10-07 | 2024-12-15 | 70 / 731 | 70 | 100,800 | 70 | 70 |
| SOLUSDT | premiumIndexKlines | 2024-10-07 | 2024-12-15 | 70 / 731 | 70 | 100,800 | 70 | 70 |
| SOLUSDT | metrics | 2024-10-07 | 2024-12-15 | 70 / 731 | 70 | 20,158 | 70 | 70 |
| SOLUSDT | fundingRate | None | None | 0 / 731 | 0 | 0 | 0 | 0 |

Missing-date lists, failed partitions and remote URLs are in data_catalog.json. Unacquired dates do not imply Binance lacks those dates.

Funding archives are restricted to complete months inside the window. October 2024 and October 2026 need another permitted source for their in-window dates. No outside-window records were downloaded.
