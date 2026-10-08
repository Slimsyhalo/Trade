# Research foundation resumption — 2026-10-08

Phase 1 and global C16–C22 acceptance remain open. This checkpoint integrates previously tested foundation modules into main while retaining its exact current acquisition manifest. Original development/evidence branches remain intact. No strategy, orders or paid backend is introduced.

## Immutable starting evidence

Main `61b571698c36a128fc366bc0ca2dadec416e7a06`: 1,346 complete hash/size-matching remotely verified archive pairs, 268,015,878 aggTrades rows, roughly 71 dates of most daily sources, and 69 monthly funding archives (699 observed days per symbol; 32 boundary dates remain outside those monthly archives). One QA-passing partition has an incomplete remote pair. Three original strict individual-tape quarantines are preserved. Expansion remains in its own ledger with 47 remote partitions: 41 validated, six quarantined.

All prior workflows were completed at the initial read-only audit; historical, expansion and live continuation had failed. Nothing running was cancelled. Main failed on a GitHub asset GET HTTP500. Expansion attempted to publish a verification-bar ZIP that had correctly been pruned after an earlier checkpoint but was omitted from re-materialization. The two-hour live capture preserved 227 valid segments, published 212, then stopped with a 15-segment backlog. The actual diagnostic artifact was downloaded and all 227 segment identities matched their immutable Git ledger. Recovery publication still requires hosted execution evidence.

## Correctness and resumption

Existing source-market individual-tape admission remains gated by complete 1,440-minute agreement with official OHLCV, execution counts and both taker-volume fields. The original strict QA and global ID gaps remain in its certificate; the precise cause of the skipped IDs is unknown. Resumption now restores the exact hash-identified bar evidence along with original and normalized tapes. Corrupt evidence is rejected; missing verification receipts prevent a skip. No silent ID-continuity relaxation was introduced.

Historical skip decisions now require both receipts to match source SHA-256 and byte count. Read-only transport and HTTP5xx retries are inherited from the tested C22 source; ambiguous mutations are reconciled by immutable asset name rather than blindly repeated. Hash failures and permission failures still stop the affected writer. Null receipts no longer crash an observational audit, and monthly funding coverage counts observed settlement dates.

## Hosted runtime and ownership

`foundation-resume.yml` starts tested historical resumption, isolated expansion resumption and one-time failed-live artifact recovery. History owns `main` metadata and the shared `quantlab-data-writer` lock. Expansion owns `codex/c17-archive-expansion` and the original expansion lock. Artifact recovery owns `codex/live-artifact-recovery`; its ledger retains the original capture failure as historical evidence. `live-observation.yml` owns `codex/live-observations` under the original live writer lock. `foundation-observability.yml` owns only `codex/foundation-ops`. Foreground development must avoid concurrent writes to those ledgers.

Historical and expansion scans resume every four hours within their runtime budget. Live observations are two-hour sessions scheduled every three hours, with up to one hour of publication drain and sample restoration. These schedules can be delayed or dropped by GitHub; there are known gaps between sessions, no 24/7 claim, and no process assumed to survive its runner. A supervised always-on host with an approved object backend remains the target for continuous capture. REST451 continues to block observed synchronized L2 snapshots and OI polling; public updates are retained without full-book certification.

Hosted standard runner minutes are free for this public repository according to current GitHub documentation. No paid service was contracted. Successful live jobs retain small receipt artifacts; failed raw artifact retention is bounded to one day and remote publication is prioritized. Release objects and hash receipts remain the durable data store, rather than temporary Actions artifacts.

## Capacity and acceptance

The 70-source inventory and existing scientific/document recovery modules are retained. The capacity model now uses measured spot/depth Parquet ratios, small futures partitions and actual whole-month funding volumes. Known selected historical components project approximately 408.1 GB, or 530.6 GB with a 30% planning margin. This is a sample extrapolation, not a certified total; future live duration, external context, derived outputs and redundant recovery copies remain additional or unmeasured. The 2 GB limit applies to temporary work.

176 local tests pass, including regression checks for exact bar restoration, tampered evidence, incomplete receipts, live artifact provenance and monthly funding coverage. Hosted acquisition/restore/live results must be recorded before declaring those actions successful. See `reports/checkpoints/C16_C22_resume_recovery_20261008.json`.
