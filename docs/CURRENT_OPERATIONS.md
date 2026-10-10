# Current research foundation operations

Observed UTC: 2026-10-10T01:56:12.118696+00:00. Phase 1 remains incomplete.

| Component | Evidence head | State | Preserved / verified scope |
|---|---|---|---|
| Main archives | 7e20fab4563c4ee3f6cf594107030762fd8b29ff | Immutable observation | 2018 remotely verified partitions; 430113441 aggTrades rows |
| Expansion | e39bfb35ee2724501123bd85b2d916533ead52ff | RUNNING | 1054 partitions; 1026 validated |
| Latest live capture | da3c3e74c2bfedd2ba3d94e5905b4eb92b55eb8e | BOUNDED_CAPTURE_RESTORED | 25 segments |
| Original live recovery | 455e0cc4880b42329169d7c569dffbe4adb9fb61 | ALL_CAPTURE_SEGMENTS_REMOTE_VERIFIED_WITH_SAMPLE_RESTORATION | 227 segments |

These are separate scopes. Bounded observations, partial historical coverage and sampled restoration do not certify final acceptance, historical full L2 or continuous live operation. Full counters, dates, errors and workflow URLs are in `reports/operations/current.json`.
