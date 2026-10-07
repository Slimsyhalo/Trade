"""Cross-platform advisory single-writer lock; OS releases it after a crash."""
import os
from contextlib import contextmanager
@contextmanager
def writer_lock(path):
    f=open(path,'a+b')
    try:
        if os.name=='nt':
            import msvcrt
            f.seek(0); f.write(b'0'); f.flush(); f.seek(0)
            msvcrt.locking(f.fileno(),msvcrt.LK_NBLCK,1)
        else:
            import fcntl
            fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
        yield
    finally: f.close()
