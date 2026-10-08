# Current QA report

........................................................................ [ 40%]
........................................................................ [ 81%]
................................                                         [100%]
176 passed in 1.67s

Manifest: 1496 QA-passing, 3 quarantined, 1496 verified remote partitions.

Absent local files after verified pruning are REMOTE_NOT_RECHECKED, never a fresh validation PASS. SHA-256/size/readback times remain in the manifest. Real restoration evidence is in reports/remote_execution.json and reports/funding_execution.json when available.

Funding schedule checks use one-second QA resolution for observed millisecond jitter. Original calc_time is unchanged; variable intervals use source funding_interval_hours. Publication timestamps remain null and fail strict replay.

Reconstruction evidence remains in reports/bar_comparison_*.json. Individual-trade bars matched pilot candles but ID-gap QA failed; aggregate bars differed. Archive integrity does not erase either limitation.
