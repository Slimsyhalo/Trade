# Resumption — demonstrated operational evidence

Phase 1 and global C16–C22 remain incomplete. This checkpoint records actual execution after source publication; it is not final certification.

Observed UTC: 2026-10-08T19:00:21.236981+00:00. Exact immutable source heads, per-source dates, hashes, errors and runtime measurements are in `reports/checkpoints/RESUME_OPERATIONAL_EVIDENCE_20261008.json`.

| Component | Observed result |
|---|---|
| Primary history | 1390 verified partitions; 284742492 aggTrades rows; resumed RUNNING |
| Expansion | 62 verified partitions, 56 admitted, 6 quarantined; original failure crossed safely |
| Failed live recovery | 15 pending segments published; all 227 verified; 6,578,897 source records and 291,127,111 bytes; public/market/snapshot samples restored |
| New bounded live session | 765871 remotely verified observations; session still RUNNING |
| New derivative products | 2 published products; 1 daily set; both families independently restored; continuing other available days |
| Hosted derivative tests | 190 passing tests |

History and expansion keep their original ledgers and resume from existing records. Main source/inventory/recovery changes: `0edc1bc1bc5b9830487c060c78778c1d323e8954`. New C18 code: `36205fcdddb10a6cc63f51c08e15b2b7f1e70e52`. Active writers remain untouched by this independent evidence branch.

Primary/expanded originals and scheduled bounded live sessions continue in GitHub-hosted jobs, with separate ownership, runtime limits, durable checkpoints and raw/normalized readbacks. Source derivatives operate on an immutable main snapshot and do not reacquire official archives. Their non-default-branch schedule must be integrated at a safe historical-writer boundary before it can run periodically.

Missing full historical coverage, continuous live operation, synchronized full L2, temporal context completeness, further derived families and global restoration acceptance remain open. Original strict individual-tape ID QA is retained; admitted market tapes require exact official-minute consistency evidence. No profitability or final acceptance is claimed.
