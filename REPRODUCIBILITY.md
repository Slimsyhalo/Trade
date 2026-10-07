# Reproduce the pilot

Python 3.12, exact dependency versions in requirements.lock. Work in the repository root.

```bash
python bootstrap.py
# Linux/macOS; Windows uses .venv\Scripts\python.exe
.venv/bin/python -m pytest -q
.venv/bin/python probe_sources.py
.venv/bin/python estimate.py
.venv/bin/python quantlab.py sync --dataset klines --start 2024-10-07 --end 2024-10-07 --limit 3
.venv/bin/python quantlab.py sync --dataset aggTrades --start 2024-10-07 --end 2024-10-07 --limit 3
.venv/bin/python quantlab.py validate
.venv/bin/python quantlab.py status
.venv/bin/python audit_bars.py
```

Repeat sync for each configured dataset. The default cap is one partition/invocation. This safety cap is not a reduced historical window. Do not launch all-history sync before storage estimate and real remote tests pass.

With properly authorized GitHub environment (token is never required by Binance):

```bash
.venv/bin/python quantlab.py upload
.venv/bin/python quantlab.py restore --key BTCUSDT/klines/2024-10-07
.venv/bin/python quantlab.py sync --remote --prune --max-local-storage-gb 2 --limit 3
```

Restore uses a separate absent `data/restored/` destination, verifies full SHA256/bytes and Parquet rows. It intentionally refuses to overwrite existing files. At current checkpoint this command has NOT succeeded against GitHub; no remote URLs exist in the catalog.

Live smoke: `.venv/bin/python -m live_collector.collector --seconds 20`. Never run historical sync and live capture concurrently in the same workspace. Captures include disconnect/gap records. Runtime ends after the requested duration and is not a background service. REST access may be region-blocked independently of archive and WebSocket access.

Exact compressed output hashes require the locked PyArrow version; logical equality alone is not byte equality. A synthetic reproducibility test checks deterministic Parquet output under the pinned environment.
