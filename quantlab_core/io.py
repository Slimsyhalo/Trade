"""Atomic files, hard disk budget, bounded read-only HTTP and integrity."""
import hashlib, json, os, random, time
from pathlib import Path
import requests


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''): h.update(block)
    return h.hexdigest()


def atomic_json(path, value):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + '.part')
    with temp.open('w') as f:
        json.dump(value, f, indent=2); f.flush(); os.fsync(f.fileno())
    os.replace(temp, path)


class Budget:
    def __init__(self, root, gb):
        self.root, self.limit = Path(root), int(gb * 1_000_000_000)
        if self.limit <= 0: raise ValueError('Budget must be positive')
    def used(self):
        return sum(p.stat().st_size for p in self.root.rglob('*') if p.is_file())
    def check(self, extra=0):
        if self.used() + extra > self.limit: raise RuntimeError('Local storage budget exhausted; no unverified data deleted')


class HTTP:
    def __init__(self, interval=1, attempts=5):
        self.session = requests.Session(); self.interval = interval; self.attempts = attempts; self.last = 0
    def get(self, url, **kwargs):
        for attempt in range(self.attempts):
            time.sleep(max(0, self.interval - (time.monotonic() - self.last)))
            self.last = time.monotonic()
            try:
                r = self.session.get(url, timeout=(15, 90), **kwargs)
            except requests.RequestException:
                if attempt + 1 == self.attempts: raise
                time.sleep(min(30, 2 ** attempt) + random.random()); continue
            if r.status_code == 418:
                r.close(); raise RuntimeError('Binance IP ban: stop, do not retry')
            if r.status_code == 429 or r.status_code >= 500:
                delay = max(float(r.headers.get('Retry-After', 0)), min(30, 2 ** attempt) + random.random())
                r.close()
                if delay > 60: raise RuntimeError(f'Rate limited; resume after {delay} seconds')
                time.sleep(delay); continue
            r.raise_for_status(); return r
        raise RuntimeError('Retry limit exhausted')
    def download(self, url, path, budget, expected=None):
        path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            if expected and sha256(path) == expected: return
            raise RuntimeError('Immutable path already exists with unknown/different content')
        temp = path.with_suffix(path.suffix + '.part')
        try:
            with self.get(url, stream=True) as r:
                budget.check(int(r.headers.get('Content-Length', 0)))
                with temp.open('wb') as f:
                    for block in r.iter_content(1024 * 1024):
                        budget.check(len(block)); f.write(block); f.flush()
                    os.fsync(f.fileno())
            if expected and sha256(temp) != expected: raise ValueError('Source checksum mismatch')
            os.replace(temp, path)
        finally:
            if temp.exists(): temp.unlink()
