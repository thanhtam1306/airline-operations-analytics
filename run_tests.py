"""
Test runner: runs pytest in the virtual environment.
Usage:
    python run_tests.py [pytest options]
"""
import os
from pathlib import Path
import subprocess
import sys

project_root = Path(__file__).resolve().parent
venv_py = project_root / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")

if venv_py.exists():
    cmd = [str(venv_py), "-m", "pytest"] + sys.argv[1:]
else:
    cmd = [sys.executable, "-m", "pytest"] + sys.argv[1:]

res = subprocess.run(cmd)
sys.exit(res.returncode)
