# Checkpoints — evidence-driven, none approved remotely

| Checkpoint | Local evidence / state | Acceptance |
|---|---|---|
| C01 Repository/bootstrap | Empty public Trade discovered; dependency lock, bootstrap, README and tests created | BLOCKED: integration 403, not pushed |
| C02 Official discovery | Current official docs, archive probes and actual REST/WS observations | PARTIAL: broad date discovery pending |
| C03 Storage | Sample sizes and conservative policy; Releases chosen | PARTIAL: stratified estimate and remote capacity verification pending |
| C04 Historical downloader | Daily streaming ZIP, checksums, retry, resume | LOCAL TESTED; bulk not approved |
| C05 Integrity | SHA256, byte counts, rows, manifest and validation | LOCAL TESTED; remote missing |
| C06 Normalization | Versioned typed schemas and ZSTD for pilot | LOCAL TESTED |
| C07 QA | Unit, fault/mocked integration, actual source QA | PARTIAL: cross-day/fault-duration gates pending |
| C08 BTC extraction | Single-day pilot only | INCOMPLETE |
| C09 ETH extraction | Single-day pilot only | INCOMPLETE |
| C10 SOL extraction | Single-day pilot only | INCOMPLETE |
| C11 Derivatives | Mark/index/premium/metrics samples; funding blocked via REST | INCOMPLETE |
| C12 Live | 20-second observed capture, routed streams, gap markers | PARTIAL; book snapshot blocked, no deployment |
| C13 GitHub storage | Adapter and mocked verification; no real upload | BLOCKED |
| C14 Replay | Availability guards and exact comparison reports | PARTIAL; aggregate reconstruction discrepancy |
| C15 Audit/handoff | Honest pilot audit and handoff delivered | NOT APPROVED; full foundation incomplete |

Each future approval requires tests PASS + dataset QA PASS + source/checksums valid + documentation + verified remote state. A local source snapshot commit is not a checkpoint approval. Never label a blocked checkpoint approved because its unit tests pass.
