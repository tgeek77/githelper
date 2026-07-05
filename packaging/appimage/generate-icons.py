#!/usr/bin/env python3
"""Generate 256x256 PNG icons for AppImage packaging (stdlib only)."""

import struct
import sys
import zlib
from pathlib import Path

PALETTES = {
    "githelper": ((35, 120, 70), (50, 160, 95)),
    "githelper-gui": ((30, 90, 160), (55, 130, 210)),
}


def _chunk(tag: bytes, data: bytes) -> bytes:
    crc = zlib.crc32(tag + data) & 0xFFFFFFFF
    return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", crc)


def write_icon(path: Path, icon_id: str) -> None:
    """Write a simple checkerboard-style 256x256 RGB PNG."""
    base, accent = PALETTES.get(icon_id, ((60, 60, 60), (100, 100, 100)))
    size = 256
    raw_rows = []

    for y in range(size):
        row = b"\x00"  # PNG filter type 0
        for x in range(size):
            margin = 12
            if x < margin or y < margin or x >= size - margin or y >= size - margin:
                row += bytes((30, 30, 30))
                continue
            cell = ((x // 32) + (y // 32)) % 2
            color = accent if cell else base
            row += bytes(color)
        raw_rows.append(row)

    ihdr = struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0)
    png = bytearray(b"\x89PNG\r\n\x1a\n")
    png += _chunk(b"IHDR", ihdr)
    png += _chunk(b"IDAT", zlib.compress(b"".join(raw_rows), 9))
    png += _chunk(b"IEND", b"")
    path.write_bytes(png)


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(f"usage: {argv[0]} ICON_ID OUTPUT_DIR", file=sys.stderr)
        return 1
    icon_id = argv[1]
    out_dir = Path(argv[2])
    out_dir.mkdir(parents=True, exist_ok=True)
    write_icon(out_dir / f"{icon_id}.png", icon_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
