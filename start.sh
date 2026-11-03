#!/usr/bin/env bash
# EcoServe AI launcher for macOS / Linux. Usage: ./start.sh   (first run installs, later runs just start)
set -e
cd "$(dirname "$0")/backend"
VENV=".venv"
if ! "$VENV/bin/python" -c "import flask, flask_sqlalchemy, flask_jwt_extended, flask_bcrypt, flask_cors, waitress" 2>/dev/null; then
  echo "First run: setting up EcoServe AI (one time only)..."
  rm -rf "$VENV"
  PY=""
  for c in python3.12 python3.11 python3.13 python3.10 python3.9 python3; do
    if command -v "$c" >/dev/null && "$c" -c "import sys; sys.exit(0 if (3,9) <= sys.version_info[:2] <= (3,13) else 1)"; then PY="$c"; break; fi
  done
  [ -z "$PY" ] && { echo "Python 3.9-3.13 not found. Install Python 3.12 from python.org."; exit 1; }
  "$PY" -m venv "$VENV"
  "$VENV/bin/python" -m pip install --disable-pip-version-check -q -r requirements.txt
fi
exec "$VENV/bin/python" run.py "$@"
