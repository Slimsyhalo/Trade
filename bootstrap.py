"""Install pinned dependencies into .venv without altering system Python."""
import subprocess, sys, venv
from pathlib import Path
root = Path(__file__).resolve().parent
venv.EnvBuilder(with_pip=True).create(root / '.venv')
python = root / '.venv' / ('Scripts/python.exe' if sys.platform == 'win32' else 'bin/python')
subprocess.run([str(python), '-m', 'pip', 'install', '-r', str(root / 'requirements.lock')], check=True)
