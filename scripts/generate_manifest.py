#!/usr/bin/env python3
"""Generate a deterministic SHA-256 manifest for the public package."""

from __future__ import annotations

import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "MANIFEST.sha256"
EXCLUDED_DIRS = {".git", "__pycache__", ".venv", "venv", "reproduced"}


def release_files():
    """Exclude local analysis outputs and caches, including after reproduction."""
    for path in sorted(ROOT.rglob("*"), key=lambda item: item.as_posix()):
        relative = path.relative_to(ROOT)
        if (not path.is_file() or path == MANIFEST
                or EXCLUDED_DIRS.intersection(relative.parts)
                or path.suffix in {".pyc", ".pyo"}):
            continue
        yield path


def main() -> None:
    lines: list[str] = []
    for path in release_files():
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        relative = path.relative_to(ROOT).as_posix()
        lines.append(f"{digest}  {relative}")
    MANIFEST.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"Wrote {len(lines)} checksums to {MANIFEST.name}")


if __name__ == "__main__":
    main()
