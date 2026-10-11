# Current research foundation operations

Observed UTC: 2026-10-11T09:20:05.603903+00:00. Phase 1 remains incomplete.

| Component | Evidence head | State | Preserved / verified scope |
|---|---|---|---|
| Main archives | 39eaff5e04ebb38678e34b085021477ee02c4150 | Immutable observation | 2018 remotely verified partitions; 430113441 aggTrades rows |
| Expansion | 881725f94a34efafbf88c43bf118585851462b91 | RUNNING | 2349 partitions; 2262 validated |
| Latest live capture | ba38f2b8e6546463d3ee75cc4e98562a8ec6b097 | BOUNDED_CAPTURE_RESTORED | 25 segments |
| Original live recovery | 455e0cc4880b42329169d7c569dffbe4adb9fb61 | ALL_CAPTURE_SEGMENTS_REMOTE_VERIFIED_WITH_SAMPLE_RESTORATION | 227 segments |

These are separate scopes. Bounded observations, partial historical coverage and sampled restoration do not certify final acceptance, historical full L2 or continuous live operation. Full counters, dates, errors and workflow URLs are in `reports/operations/current.json`.
