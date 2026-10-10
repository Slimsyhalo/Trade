# Current research foundation operations

Observed UTC: 2026-10-10T09:05:00.625565+00:00. Phase 1 remains incomplete.

| Component | Evidence head | State | Preserved / verified scope |
|---|---|---|---|
| Main archives | 0855a44ee437e109d975d8f72bd9fb64c49a91cc | Immutable observation | 2018 remotely verified partitions; 430113441 aggTrades rows |
| Expansion | bdca278b74d400ebd216367094574f1406931c79 | RUNNING | 1360 partitions; 1326 validated |
| Latest live capture | b06016bf4a771562952220a85ad8df2bdf1e8bf9 | BOUNDED_CAPTURE_RESTORED | 25 segments |
| Original live recovery | 455e0cc4880b42329169d7c569dffbe4adb9fb61 | ALL_CAPTURE_SEGMENTS_REMOTE_VERIFIED_WITH_SAMPLE_RESTORATION | 227 segments |

These are separate scopes. Bounded observations, partial historical coverage and sampled restoration do not certify final acceptance, historical full L2 or continuous live operation. Full counters, dates, errors and workflow URLs are in `reports/operations/current.json`.
