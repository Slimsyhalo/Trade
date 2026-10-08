# Live research capture: operation and limits

`live-foundation.yml` runs a bounded ten-minute observation on an independent
branch ledger. It leaves the main historical writer and queued funding job
untouched. Raw combined WebSocket messages, receipt times, connection markers
and detected sequence gaps are preserved. Segments rotate at 300 seconds or
32 MB compressed. One publisher owns remote mutations, paced at 15 seconds;
the repository API quota is shared with historical jobs and rate waits remain
observable. Full SHA-256/size readback precedes verified receipts. Git ledger
checkpoints occur each minute. Raw inputs are not pruned by this runner.

Separate routes preserve depth/best quotes, aggregate trades, mark/funding
observations and liquidation notifications. REST depth/OI failure is explicit;
451/403 ends polling without bypass. Raw depth deltas without an admitted
snapshot bridge are not a valid reconstructed book. Liquidation snapshots are
not certified as every liquidation. Application receipt times require clock
calibration before latency interpretation.

At completion one segment per available route is downloaded from its remote
asset into an absent isolated path, checked for hash/size/gzip/schema/row count,
and inspected for actual event types. Machine evidence lives under
`reports/live_execution/<run_id>.json` and `catalog/live/<run_id>/`. A successful
bounded run is operational evidence, never proof of continuous service. Partial
remote failure retains local data and diagnostic artifacts for fourteen days;
those artifacts are temporary recovery aids, not certified permanent storage.

GitHub-hosted Actions jobs have a six-hour platform maximum and scheduled jobs
can be delayed. Chaining jobs introduces unobserved intervals. Reliable future
capture requires an authorized continuously running host (for example a
self-hosted runner or systemd service), persistent spool, clock monitoring,
backlog alerts and a recovery ledger. No paid host was created. Until such a
host is supplied, permanent collection and C20 final acceptance remain open.
Official limit: https://docs.github.com/en/actions/reference/limits .

Recovery procedure: stop the affected writer; retrieve its ledger and retained
spool; reconcile immutable hash-named assets by readback; restore absent inputs
before constructing Sink; quarantine incomplete tails; start a new connection
with an explicit continuity break; fetch and synchronize a new official
snapshot before admitting any book metric. Never infer uninterrupted coverage
from the last sequence number alone.
