#!/usr/bin/python3
"""Launch the githelper CLI (development entry point)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from githelper.cli_app import main

if __name__ == "__main__":
    main()
