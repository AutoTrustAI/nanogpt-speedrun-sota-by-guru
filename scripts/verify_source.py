#!/usr/bin/env python3
"""Verify the 33 archived model files without importing the training stack."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify(source=None, manifest=None):
    source = ROOT / "model" if source is None else Path(source)
    manifest = (json.loads((ROOT / "provenance/source-files.json").read_text())
                if manifest is None else manifest)
    expected = manifest["sha256"]
    if len(expected) != 33:
        raise ValueError("Expected the complete 33-file archived source inventory")
    checked = {}
    for name, wanted in expected.items():
        relative = Path(name)
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError(f"Unsafe source path: {name}")
        path = source / relative
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"Missing or non-regular source file: {name}")
        checked[name] = sha256(path)
        if checked[name] != wanted:
            raise ValueError(f"Source SHA-256 mismatch: {name}")
    return checked


if __name__ == "__main__":
    print(json.dumps({"status": "verified", "files": len(verify())}, indent=2))
