#!/usr/bin/env bash
# Quick packaging checks without building AppImages (no FUSE/appimagetool needed).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT"

echo "==> Import checks"
python3 -c "from githelper.cli_app import main; print('cli_app ok')"
python3 cli/githelper.py --help >/dev/null
python3 cli/githelper.py config path >/dev/null

if ! python3 -m pip --version >/dev/null 2>&1; then
    echo "pip not available; skipping PyInstaller checks"
    exit 0
fi

python3 -m pip install -q -r "$ROOT/packaging/requirements-build.txt"
python3 -m PyInstaller "$ROOT/packaging/pyinstaller/githelper-cli.spec" --clean --noconfirm

echo "==> PyInstaller CLI binary"
"$ROOT/dist/githelper" --help >/dev/null
"$ROOT/dist/githelper" config path >/dev/null
echo "Packaging checks passed."
