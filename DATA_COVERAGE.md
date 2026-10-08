# Current data coverage

Generated: 2026-10-08T12:29:45.152823+00:00

QA days count observed passing dates. Remote days require matching RAW and Parquet readback receipts. Monthly funding coverage counts observed dates, not one day per archive.

| Symbol | Dataset | First | Last | QA days / expected | Remote days | Rows | QA partitions | Remote partitions |
|---|---|---|---|---:|---:|---:|---:|---:|
| BTCUSDT | trades | None | None | 0 / 731 | 0 | 0 | 0 | 0 |
| BTCUSDT | aggTrades | 2024-10-07 | 2024-10-28 | 22 / 731 | 22 | 25,252,653 | 22 | 22 |
| BTCUSDT | klines | 2024-10-07 | 2024-11-09 | 34 / 731 | 34 | 48,960 | 34 | 34 |
| BTCUSDT | markPriceKlines | 2024-10-07 | 2024-11-09 | 34 / 731 | 34 | 48,960 | 34 | 34 |
| BTCUSDT | indexPriceKlines | 2024-10-07 | 2024-11-09 | 34 / 731 | 34 | 48,960 | 34 | 34 |
| BTCUSDT | premiumIndexKlines | 2024-10-07 | 2024-11-09 | 34 / 731 | 34 | 48,960 | 34 | 34 |
| BTCUSDT | metrics | 2024-10-07 | 2024-11-09 | 34 / 731 | 33 | 9,790 | 34 | 33 |
| BTCUSDT | fundingRate | None | None | 0 / 731 | 0 | 0 | 0 | 0 |
| ETHUSDT | trades | None | None | 0 / 731 | 0 | 0 | 0 | 0 |
| ETHUSDT | aggTrades | 2024-10-07 | 2024-10-27 | 21 / 731 | 21 | 20,725,266 | 21 | 21 |
| ETHUSDT | klines | 2024-10-07 | 2024-11-08 | 33 / 731 | 33 | 47,520 | 33 | 33 |
| ETHUSDT | markPriceKlines | 2024-10-07 | 2024-11-08 | 33 / 731 | 33 | 47,520 | 33 | 33 |
| ETHUSDT | indexPriceKlines | 2024-10-07 | 2024-11-08 | 33 / 731 | 33 | 47,520 | 33 | 33 |
| ETHUSDT | premiumIndexKlines | 2024-10-07 | 2024-11-08 | 33 / 731 | 33 | 47,520 | 33 | 33 |
| ETHUSDT | metrics | 2024-10-07 | 2024-11-08 | 33 / 731 | 33 | 9,502 | 33 | 33 |
| ETHUSDT | fundingRate | None | None | 0 / 731 | 0 | 0 | 0 | 0 |
| SOLUSDT | trades | None | None | 0 / 731 | 0 | 0 | 0 | 0 |
| SOLUSDT | aggTrades | 2024-10-07 | 2024-10-27 | 21 / 731 | 21 | 7,636,409 | 21 | 21 |
| SOLUSDT | klines | 2024-10-07 | 2024-11-08 | 33 / 731 | 33 | 47,520 | 33 | 33 |
| SOLUSDT | markPriceKlines | 2024-10-07 | 2024-11-08 | 33 / 731 | 33 | 47,520 | 33 | 33 |
| SOLUSDT | indexPriceKlines | 2024-10-07 | 2024-11-08 | 33 / 731 | 33 | 47,520 | 33 | 33 |
| SOLUSDT | premiumIndexKlines | 2024-10-07 | 2024-11-08 | 33 / 731 | 33 | 47,520 | 33 | 33 |
| SOLUSDT | metrics | 2024-10-07 | 2024-11-08 | 33 / 731 | 33 | 9,502 | 33 | 33 |
| SOLUSDT | fundingRate | None | None | 0 / 731 | 0 | 0 | 0 | 0 |

Missing-date lists, failed partitions and remote URLs are in data_catalog.json. Unacquired dates do not imply Binance lacks those dates.

Funding archives are restricted to complete months inside the window. October 2024 and October 2026 need another permitted source for their in-window dates. No outside-window records were downloaded.
