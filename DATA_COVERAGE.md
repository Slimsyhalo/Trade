# Current data coverage

Generated: 2026-10-08T18:50:07.850417+00:00

QA days count observed passing dates. Remote days require matching RAW and Parquet readback receipts. Monthly funding coverage counts observed dates, not one day per archive.

| Symbol | Dataset | First | Last | QA days / expected | Remote days | Rows | QA partitions | Remote partitions |
|---|---|---|---|---:|---:|---:|---:|---:|
| BTCUSDT | trades | None | None | 0 / 731 | 0 | 0 | 0 | 0 |
| BTCUSDT | aggTrades | 2024-10-07 | 2024-12-18 | 73 / 731 | 73 | 118,508,733 | 73 | 73 |
| BTCUSDT | klines | 2024-10-07 | 2024-12-18 | 73 / 731 | 73 | 105,120 | 73 | 73 |
| BTCUSDT | markPriceKlines | 2024-10-07 | 2024-12-18 | 73 / 731 | 73 | 105,120 | 73 | 73 |
| BTCUSDT | indexPriceKlines | 2024-10-07 | 2024-12-18 | 73 / 731 | 73 | 105,120 | 73 | 73 |
| BTCUSDT | premiumIndexKlines | 2024-10-07 | 2024-12-18 | 73 / 731 | 73 | 105,120 | 73 | 73 |
| BTCUSDT | metrics | 2024-10-07 | 2024-12-18 | 73 / 731 | 73 | 21,022 | 73 | 73 |
| BTCUSDT | fundingRate | 2024-11-01 | 2026-09-30 | 699 / 731 | 699 | 2,097 | 23 | 23 |
| ETHUSDT | trades | None | None | 0 / 731 | 0 | 0 | 0 | 0 |
| ETHUSDT | aggTrades | 2024-10-07 | 2024-12-17 | 72 / 731 | 72 | 125,781,448 | 72 | 72 |
| ETHUSDT | klines | 2024-10-07 | 2024-12-17 | 72 / 731 | 72 | 103,680 | 72 | 72 |
| ETHUSDT | markPriceKlines | 2024-10-07 | 2024-12-17 | 72 / 731 | 72 | 103,680 | 72 | 72 |
| ETHUSDT | indexPriceKlines | 2024-10-07 | 2024-12-17 | 72 / 731 | 72 | 103,680 | 72 | 72 |
| ETHUSDT | premiumIndexKlines | 2024-10-07 | 2024-12-17 | 72 / 731 | 72 | 103,680 | 72 | 72 |
| ETHUSDT | metrics | 2024-10-07 | 2024-12-17 | 72 / 731 | 72 | 20,734 | 72 | 72 |
| ETHUSDT | fundingRate | 2024-11-01 | 2026-09-30 | 699 / 731 | 699 | 2,097 | 23 | 23 |
| SOLUSDT | trades | None | None | 0 / 731 | 0 | 0 | 0 | 0 |
| SOLUSDT | aggTrades | 2024-10-07 | 2024-12-17 | 72 / 731 | 72 | 30,393,392 | 72 | 72 |
| SOLUSDT | klines | 2024-10-07 | 2024-12-17 | 72 / 731 | 72 | 103,680 | 72 | 72 |
| SOLUSDT | markPriceKlines | 2024-10-07 | 2024-12-17 | 72 / 731 | 72 | 103,680 | 72 | 72 |
| SOLUSDT | indexPriceKlines | 2024-10-07 | 2024-12-17 | 72 / 731 | 72 | 103,680 | 72 | 72 |
| SOLUSDT | premiumIndexKlines | 2024-10-07 | 2024-12-17 | 72 / 731 | 72 | 103,680 | 72 | 72 |
| SOLUSDT | metrics | 2024-10-07 | 2024-12-17 | 72 / 731 | 72 | 20,734 | 72 | 72 |
| SOLUSDT | fundingRate | 2024-11-01 | 2026-09-30 | 699 / 731 | 699 | 2,097 | 23 | 23 |

Missing-date lists, failed partitions and remote URLs are in data_catalog.json. Unacquired dates do not imply Binance lacks those dates.

Funding archives are restricted to complete months inside the window. October 2024 and October 2026 need another permitted source for their in-window dates. No outside-window records were downloaded.
