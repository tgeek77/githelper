#!/usr/bin/env bash
# Create or reuse a virtualenv for PyInstaller build dependencies.
# Avoids PEP 668 "externally-managed-environment" errors on modern Debian/Ubuntu.
set -euo pipefail

: "${ROOT:?ROOT must be set before sourcing setup-build-venv.sh}"

VENV_DIR="$ROOT/packaging/.venv"

if [[ ! -d "$VENV_DIR" ]]; then
    echo "==> Creating build virtualenv at packaging/.venv"
    if ! python3 -m venv "$VENV_DIR" 2>/dev/null; then
        echo "error: python3-venv is required; install with: sudo apt-get install python3-venv" >&2
        exit 1
    fi
fi

# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"
python -m pip install -q --upgrade pip
python -m pip install -q -r "$ROOT/packaging/requirements-build.txt"
