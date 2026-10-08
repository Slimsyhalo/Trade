# Current data coverage

Generated: 2026-10-08T19:14:18.763617+00:00

QA days count observed passing dates. Remote days require matching RAW and Parquet readback receipts. Monthly funding coverage counts observed dates, not one day per archive.

| Symbol | Dataset | First | Last | QA days / expected | Remote days | Rows | QA partitions | Remote partitions |
|---|---|---|---|---:|---:|---:|---:|---:|
| BTCUSDT | trades | None | None | 0 / 731 | 0 | 0 | 0 | 0 |
| BTCUSDT | aggTrades | 2024-10-07 | 2024-12-22 | 77 / 731 | 77 | 128,315,160 | 77 | 77 |
| BTCUSDT | klines | 2024-10-07 | 2024-12-22 | 77 / 731 | 77 | 110,880 | 77 | 77 |
| BTCUSDT | markPriceKlines | 2024-10-07 | 2024-12-22 | 77 / 731 | 77 | 110,880 | 77 | 77 |
| BTCUSDT | indexPriceKlines | 2024-10-07 | 2024-12-22 | 77 / 731 | 77 | 110,880 | 77 | 77 |
| BTCUSDT | premiumIndexKlines | 2024-10-07 | 2024-12-22 | 77 / 731 | 77 | 110,880 | 77 | 77 |
| BTCUSDT | metrics | 2024-10-07 | 2024-12-22 | 77 / 731 | 77 | 22,174 | 77 | 77 |
| BTCUSDT | fundingRate | 2024-11-01 | 2026-09-30 | 699 / 731 | 699 | 2,097 | 23 | 23 |
| ETHUSDT | trades | None | None | 0 / 731 | 0 | 0 | 0 | 0 |
| ETHUSDT | aggTrades | 2024-10-07 | 2024-12-22 | 77 / 731 | 77 | 140,652,811 | 77 | 77 |
| ETHUSDT | klines | 2024-10-07 | 2024-12-22 | 77 / 731 | 77 | 110,880 | 77 | 77 |
| ETHUSDT | markPriceKlines | 2024-10-07 | 2024-12-22 | 77 / 731 | 77 | 110,880 | 77 | 77 |
| ETHUSDT | indexPriceKlines | 2024-10-07 | 2024-12-21 | 76 / 731 | 76 | 109,440 | 76 | 76 |
| ETHUSDT | premiumIndexKlines | 2024-10-07 | 2024-12-21 | 76 / 731 | 76 | 109,440 | 76 | 76 |
| ETHUSDT | metrics | 2024-10-07 | 2024-12-21 | 76 / 731 | 76 | 21,886 | 76 | 76 |
| ETHUSDT | fundingRate | 2024-11-01 | 2026-09-30 | 699 / 731 | 699 | 2,097 | 23 | 23 |
| SOLUSDT | trades | None | None | 0 / 731 | 0 | 0 | 0 | 0 |
| SOLUSDT | aggTrades | 2024-10-07 | 2024-12-21 | 76 / 731 | 76 | 33,079,117 | 76 | 76 |
| SOLUSDT | klines | 2024-10-07 | 2024-12-21 | 76 / 731 | 76 | 109,440 | 76 | 76 |
| SOLUSDT | markPriceKlines | 2024-10-07 | 2024-12-21 | 76 / 731 | 76 | 109,440 | 76 | 76 |
| SOLUSDT | indexPriceKlines | 2024-10-07 | 2024-12-21 | 76 / 731 | 76 | 109,440 | 76 | 76 |
| SOLUSDT | premiumIndexKlines | 2024-10-07 | 2024-12-21 | 76 / 731 | 76 | 109,440 | 76 | 76 |
| SOLUSDT | metrics | 2024-10-07 | 2024-12-21 | 76 / 731 | 76 | 21,886 | 76 | 76 |
| SOLUSDT | fundingRate | 2024-11-01 | 2026-09-30 | 699 / 731 | 699 | 2,097 | 23 | 23 |

Missing-date lists, failed partitions and remote URLs are in data_catalog.json. Unacquired dates do not imply Binance lacks those dates.

Funding archives are restricted to complete months inside the window. October 2024 and October 2026 need another permitted source for their in-window dates. No outside-window records were downloaded.
