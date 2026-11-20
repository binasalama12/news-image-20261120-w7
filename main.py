#!/usr/bin/env python3
"""Publisher for the Numbers XL front-page entry.

Design: "Friday 20 November 2026 - one day of world news, by the numbers."
The artwork (entry.png, 1024x1024) ships pre-rendered inside this
repository; this program only validates it and copies it to the output
directory, using nothing beyond the Python standard library.
"""

import os
import shutil
import sys
from pathlib import Path

TITLE = "Friday 20 November 2026 - one day of world news, by the numbers."
MAX_BYTES = 1048576  # competition cap: 1 MiB
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
JPEG_MAGIC = b"\xff\xd8\xff"


def find_artwork() -> Path:
    return Path(__file__).resolve().parent / "entry.png"


def check_artwork(path: Path) -> int:
    if not path.is_file():
        print(f"error: artwork not found: {path}", file=sys.stderr)
        raise SystemExit(1)
    size = path.stat().st_size
    with path.open("rb") as handle:
        head = handle.read(len(PNG_MAGIC))
    if head != PNG_MAGIC and not head.startswith(JPEG_MAGIC):
        print("error: entry.png is neither PNG nor JPEG data", file=sys.stderr)
        raise SystemExit(1)
    if size > MAX_BYTES:
        print(f"error: entry.png is {size} bytes, over the {MAX_BYTES} cap",
              file=sys.stderr)
        raise SystemExit(1)
    return size


def publish(source: Path) -> Path:
    out_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output")
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / "entry.png"
    shutil.copyfile(source, target)
    return target


def main() -> int:
    artwork = find_artwork()
    size = check_artwork(artwork)
    target = publish(artwork)
    print(f"Design: {TITLE}")
    print(f"Artwork: entry.png ({size} bytes, 1024x1024)")
    print(f"Published entry.png to {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
