# C12 recovery source checkpoint — 2026-10-08

This source checkpoint extends the live collector with durable local spooling,
single-worker publication and sequence recovery. C12 remains PARTIAL. No continuous
deployment, valid full L2 book, new live remote upload or long-duration recovery
approval is claimed.

## What changed

Previously `Sink.close()` called GitHub synchronously on the receive loop, before
recording the segment in the manifest. A slow upload stopped ingestion; an upload
failure could leave a closed file without a manifest record. Duplicate/old IDs were
discarded and sequence state reset on each connection.

Now gzip segments remain `.part` while open. Closing writes the footer, flushes and
fsyncs the file, renames it, then saves/fsyncs the route manifest before publication.
A startup inspection verifies SHA256, bytes, JSONL/gzip integrity and rows. A closed
orphan after rename-before-manifest is recovered with unknown continuity. Interrupted
open segments and damaged inputs remain quarantined, without repair, overwrite,
deletion or remote promotion. Missing inputs remain explicit.

One publisher runs remote operations in an I/O thread. Capture continues while
GitHub waits. Every attempted upload gets a persisted `uploading` state; only a
matching SHA256/bytes/readback receipt becomes `remote_verified`. A failed or cancelled
attempt retains its input and diagnostic state. The same session stops publishing
after an ambiguous failure. A new process revalidates local files and uses the
existing GitHub adapter's immutable asset-name reconciliation before resuming.
Stored verified receipts are reused on startup; they are not fresh remote readbacks.

Release tags are route/hour-specific to limit assets per Release. After capture
stops, a configurable drain deadline limits starting further uploads. An in-flight
remote call finishes according to its own timeout and rate-limit policy, so the
capture duration is not a hard total process-duration guarantee. A pending backlog
or publication/integrity failure writes FAILED session evidence and exits nonzero.

All raw messages are retained, including duplicate/old IDs. Separate diagnostics
classify duplicate/old, trade gaps, depth `pu` gaps and malformed envelopes. Closed
segments carry the last observed sequence IDs. Reconnects and restarts always get
an unverified connection marker. Contiguous observed IDs do not establish a valid
book or prove zero losses. The collector does not reconstruct a book without a
snapshot bridge. The OrderBook helper now invalidates its bridge after a gap and
requires a new snapshot before it can become valid again. A blocked REST response (403/451) disables further polling for the
session; access restrictions are not bypassed.

Local segment write/flush, hashing, ledger operations and budget checks still run
on the receive loop. This change removes synchronous remote waits; it does not
claim a benchmarked zero-stall ingest path. Open-segment durability is weaker than
closed-segment durability: a hard crash can leave an incomplete compressed tail.
That tail is preserved and flagged rather than asserted recoverable.

No local files are pruned, even after verified upload. Remote manifest publication
and restoration gates must precede any future retention/pruning implementation.
The existing disk budget fails without deleting unverified data.

## Running and inspecting

```bash
python -m live_collector.collector --seconds 60
python -m live_collector.collector --seconds 60 --remote --drain-seconds 30
```

The remote mode requires an existing GitHub write environment. This checkpoint
does not configure credentials, start a persistent deployment or add another
queued data-writer workflow. Route manifests and `data/live/session-report.json`
contain local integrity/publication states. A writer lock protects the CLI.

For an existing original pilot, inspection is read-only:

```bash
python validate_live_spool.py --root EXISTING_DATA_ROOT/live \
  --inventory reports/live_inventory.json --output reports/live_pilot_integrity.json
```

## Verification

The full suite passed **111 tests**, including 29 new live recovery cases.
Fault tests exercise slow upload with ongoing capture, serialized remote calls,
failure/cancellation recovery, invalid receipts, pre-upload mutation, corrupt and
missing files, open-tail quarantine, rename-before-manifest crash, disk exhaustion,
cursor persistence across reconnects, raw duplicate retention and blocked REST.
Publication calls in these new fault tests use controlled test doubles; they do
not constitute a new real GitHub live-data upload/restore.

`reports/live_pilot_integrity.json` validates the actual original 20-second smoke:
3 segments, **3,990 retained rows**, 223,920 compressed bytes, matching inventory
SHA256 and row counts. The new diagnostics found no gaps in the retained messages.
The old collector may have discarded duplicates; this inspection cannot recover
them. The pilot includes 6 snapshot-error records and does not validate a full book.

`reports/live_recovery_tests.txt` is the full suite evidence.
`reports/work_sessions/C12_live_recovery_2026-10-08.json` records the measured work
window and validation durations, with unmeasured active time explicitly null.
Main acquisition is independent; consult its current report rather than this
branch's earlier data catalog. The code is preserved on `codex/live-recovery` for
integration at a safe writer boundary.

## Primary references checked

- Binance routed public/market streams:
  https://developers.binance.com/en/docs/products/derivatives-trading-usds-futures/websocket-market-streams/Important-WebSocket-Change-Notice
- Binance snapshot bridge and `pu` continuity:
  https://developers.binance.com/en/docs/products/derivatives-trading-usds-futures/websocket-market-streams/How-to-manage-a-local-order-book-correctly
- Python 3.12 `asyncio.to_thread`, timeout and task cancellation:
  https://docs.python.org/3.12/library/asyncio-task.html
