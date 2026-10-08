# Exact original-document preservation decision

The hosted runner observes HTTP 403 from BLS archive indexes. Fed HTML fetched
there also differs from the response bytes legally acquired in this workspace.
The existing workflow records these restrictions/version differences and does
not silently replace the original versions or claim original historical values.

The 109 release documents, their 109 normalized metadata records and five
original discovery pages occupy a 9,074,316-byte immutable bundle. Losing this
workspace would make those exact source versions costly or impossible to recover.
A one-off Git handoff of nineteen small binary parts is justified for this
bounded document corpus. It does not put market tapes into Git or change the
large-volume Releases storage backend; no new provider, subscription or paid
capacity is created. Transfer blobs have individual hashes and a combined hash.

A fresh hosted checkout assembles and verifies the bundle, checks all 223 member
hashes/bytes/CRCs and all 109 original HTML hashes/publication headers, uploads the
container to Releases with full streaming readback, and commits its receipt.
It then restores the container from that remote asset into an absent path and
repeats every member/provenance test before retiring the working-tree transfer
parts. The small original transfer remains immutable in Git history. Original
local payloads are pruned only after verified Release storage and durable ledger.

The runner does not request restricted provider endpoints or use a proxy. It
preserves data already obtained through permitted public access. The catalog
references container member paths explicitly; a container receipt is never
misrepresented as a direct individual-file receipt. Historical effective
availability and unchanged historical vintage remain uncertified. C21 acceptance
for the entire market foundation is separate from this full document restoration.
