# Source version surveillance

The provider archive checksum can change after acquisition. audit_source_versions.py requests only advertised official CHECKSUM metadata for the latest admitted date of each core symbol/dataset group and the three original individually admitted tapes, bound to immutable ledger SHAs. Original manifests, market archives and Releases remain unchanged.

The exact filename, SHA-256 syntax, single entry, official host, no redirects and bounded metadata are required. SOURCE_REVISION_DETECTED records a new candidate version for independent acquisition and QA. OBSERVATION_BLOCKED retains the stored version. The historical effective time of a revision remains unknown. Current checksum equality does not certify all past versions.

The local real probe observed 21 unchanged checksums across 18 core groups and the three original tapes in 18.586 seconds; its source commits were 5b748611f319bb55ea278d8ac9792e13bc0b6168 and 5156dc7e8f1fbfe6f207b62202fd94a16f5f5d41. 158 tests passed locally before the execution environment disconnected. The hosted workflow repeats the probe against explicitly recorded immutable commits and persists full metadata/hash evidence.

remote_schema_audit.py restores a previously certified derived Parquet from Releases and records actual Arrow types, metadata, units and storage nullability alongside source-specific scientific policies. Runtime evidence is generated only after remote restore, SHA/size checks and schema/row inspection pass. Arrow storage nullability does not authorize missing source observations.

The shell service returned environment_offline during this source checkpoint. GitHub Actions and connector access remained available; no process inside the disconnected environment is claimed to continue. Changes are isolated on codex/c21-source-version-audit. Hosted publication and validation must be inspected before reporting operational success. Main, funding, expansion and live ledgers remain owned by their existing workflows.

Before future integration, inspect main and all active jobs. Reconcile later live capture-ID namespaces with checkpoint retry changes; do not replace the newer live source with an older inherited collector. The separate branches contain explicit state and checkpoints, not a forced update to an active main writer.
