> Publication update 2026-10-07: the former GitHub 403 is resolved. The code and 18 passing pilot partitions (36 Release assets) are published; full readback and an isolated restoration passed. See reports/remote_execution.json. The original pilot findings below remain historical evidence; full-window extraction and C15 are still incomplete.

# Remote execution

GitHub connector write access was verified on 2026-10-07 by commit 8182005568a5502449324ccbdeb4ca9a0681141a. Earlier audit documents describe the original local pilot and its previous 403 blocker. Their data QA findings remain applicable.

The shell has no GitHub token and cannot push. Code is published through the authenticated connector. The proposed GitHub Actions job uses the repository-scoped GITHUB_TOKEN to reconstruct the passing pilot partitions from original Binance archives, upload RAW and Parquet as Releases, read them back fully, restore one isolated Parquet and check its row count, and commit manifests before deleting any local partition. No Binance credentials or trading operations.

The first run is bounded to the existing pilot's 18 passing partitions. Quarantined trade partitions remain excluded. No scheduled job or unbounded download is enabled. Full historical expansion requires successful remote evidence and improved estimates.

Actual results will appear in reports/remote_execution.json. Until that file records success, the remote dataset and restore gates remain pending.
