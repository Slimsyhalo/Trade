> Publication update 2026-10-07: the former GitHub 403 is resolved. The code and 18 passing pilot partitions (36 Release assets) are published; full readback and an isolated restoration passed. See reports/remote_execution.json. The original pilot findings below remain historical evidence; full-window extraction and C15 are still incomplete.

# Storage decision

Selected: normal Git for source/config/catalog/QA; GitHub Releases for immutable original ZIP and normalized Parquet assets. Current execution is BLOCKED on GitHub integration HTTP 403; no release or remote verification has occurred.

GitHub documentation checked 2026-10-07:
- Normal Git warns above 50 MiB and rejects files above 100 MiB; repositories should remain small (ideally under 1 GB, under 5 GB strongly recommended): https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github
- Releases: <2 GiB/file, <=1000 assets/release; documented no total release size or bandwidth limit: https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases
- LFS per-file: Free/Pro 2 GB, Team 4 GB, Enterprise Cloud 5 GB: https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-git-large-file-storage
- LFS storage/download are plan-dependent metered resources: https://docs.github.com/en/billing/concepts/product-billing/git-lfs . Account-specific quota and billing authorization have NOT been inspected. Do not assume paid capacity.
- REST normally 60 unauthenticated requests/hour and 5000 authenticated requests/hour; installation/secondary limits can differ: https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api

Use release tag per symbol/dataset/month; two assets/day => at most 62 for normal daily partitions. Asset names include full content hash. Release assets can still be deleted by repository owners; this is not WORM backup. Keep manifests in Git and protect published releases as operational policy.

Each successful upload is downloaded in full into a streaming hash before it is called verified. Only after both RAW and normalized copies are verified and their locations committed to durable manifest may prune delete local data. No credentials in config; external GITHUB_TOKEN only. This token needs repository Contents write, not Binance access.

The pipeline refuses >=2 GiB assets instead of uploading blindly. Automatic splitting for unusually large daily partitions is NOT yet implemented. Do not approve bulk production until tested. GitHub upload integration is implemented but not integration-tested against a real authorized repository. A mock restore test cannot approve the remote acceptance gate.

Disk budget applies to `data/`, including temporary, quarantined, live and restored payloads; installed environment/source/log metadata are outside the stated data budget. CLI single writer is mandatory; do not run collector and historical sync simultaneously under the same budget until coordinated reservations are added. Raw revisions get hash-versioned paths; never overwrite a different archive version.
