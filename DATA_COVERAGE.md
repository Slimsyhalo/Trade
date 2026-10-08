# Current data coverage

Generated: 2026-10-08T19:58:12.207062+00:00

QA days count observed passing dates. Remote days require matching RAW and Parquet readback receipts. Monthly funding coverage counts observed dates, not one day per archive.

| Symbol | Dataset | First | Last | QA days / expected | Remote days | Rows | QA partitions | Remote partitions |
|---|---|---|---|---:|---:|---:|---:|---:|
| BTCUSDT | trades | None | None | 0 / 731 | 0 | 0 | 0 | 0 |
| BTCUSDT | aggTrades | 2024-10-07 | 2024-12-30 | 85 / 731 | 85 | 140,281,055 | 85 | 85 |
| BTCUSDT | klines | 2024-10-07 | 2024-12-30 | 85 / 731 | 85 | 122,400 | 85 | 85 |
| BTCUSDT | markPriceKlines | 2024-10-07 | 2024-12-30 | 85 / 731 | 85 | 122,400 | 85 | 85 |
| BTCUSDT | indexPriceKlines | 2024-10-07 | 2024-12-30 | 85 / 731 | 85 | 122,400 | 85 | 85 |
| BTCUSDT | premiumIndexKlines | 2024-10-07 | 2024-12-30 | 85 / 731 | 85 | 122,400 | 85 | 85 |
| BTCUSDT | metrics | 2024-10-07 | 2024-12-30 | 85 / 731 | 85 | 24,478 | 85 | 85 |
| BTCUSDT | fundingRate | 2024-11-01 | 2026-09-30 | 699 / 731 | 699 | 2,097 | 23 | 23 |
| ETHUSDT | trades | None | None | 0 / 731 | 0 | 0 | 0 | 0 |
| ETHUSDT | aggTrades | 2024-10-07 | 2024-12-30 | 85 / 731 | 85 | 153,309,996 | 85 | 85 |
| ETHUSDT | klines | 2024-10-07 | 2024-12-30 | 85 / 731 | 85 | 122,400 | 85 | 85 |
| ETHUSDT | markPriceKlines | 2024-10-07 | 2024-12-30 | 85 / 731 | 85 | 122,400 | 85 | 85 |
| ETHUSDT | indexPriceKlines | 2024-10-07 | 2024-12-30 | 85 / 731 | 85 | 122,400 | 85 | 85 |
| ETHUSDT | premiumIndexKlines | 2024-10-07 | 2024-12-30 | 85 / 731 | 85 | 122,400 | 85 | 85 |
| ETHUSDT | metrics | 2024-10-07 | 2024-12-30 | 85 / 731 | 85 | 24,478 | 85 | 85 |
| ETHUSDT | fundingRate | 2024-11-01 | 2026-09-30 | 699 / 731 | 699 | 2,097 | 23 | 23 |
| SOLUSDT | trades | None | None | 0 / 731 | 0 | 0 | 0 | 0 |
| SOLUSDT | aggTrades | 2024-10-07 | 2024-12-30 | 85 / 731 | 85 | 36,018,087 | 85 | 85 |
| SOLUSDT | klines | 2024-10-07 | 2024-12-30 | 85 / 731 | 85 | 122,400 | 85 | 85 |
| SOLUSDT | markPriceKlines | 2024-10-07 | 2024-12-30 | 85 / 731 | 85 | 122,400 | 85 | 85 |
| SOLUSDT | indexPriceKlines | 2024-10-07 | 2024-12-29 | 84 / 731 | 84 | 120,960 | 84 | 84 |
| SOLUSDT | premiumIndexKlines | 2024-10-07 | 2024-12-29 | 84 / 731 | 84 | 120,960 | 84 | 84 |
| SOLUSDT | metrics | 2024-10-07 | 2024-12-29 | 84 / 731 | 84 | 24,190 | 84 | 84 |
| SOLUSDT | fundingRate | 2024-11-01 | 2026-09-30 | 699 / 731 | 699 | 2,097 | 23 | 23 |

Missing-date lists, failed partitions and remote URLs are in data_catalog.json. Unacquired dates do not imply Binance lacks those dates.

Funding archives are restricted to complete months inside the window. October 2024 and October 2026 need another permitted source for their in-window dates. No outside-window records were downloaded.
