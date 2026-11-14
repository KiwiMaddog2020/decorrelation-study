#!/usr/bin/env bash
# Local check, replaces CI. Override the interpreter with PYTHON=/path/to/python.
# Runs the pytest suite (needs pytest), then make verify. Writes nothing new.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
PYTHON="${PYTHON:-python3}"
PYTHONDONTWRITEBYTECODE=1 "$PYTHON" -m pytest tests -q -p no:cacheprovider
make verify PY="$PYTHON"
