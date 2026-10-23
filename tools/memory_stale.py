#!/usr/bin/env python3
"""Detect stale project memory: compare docs/ai/manifest.json checksums with the
files listed in autoRefreshTriggers. Agent-neutral (any agent or script can call it).

Exit 0 = fresh, 1 = stale or manifest unusable. `--update` records current checksums.
"""
import argparse
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path

MANIFEST = Path("docs") / "ai" / "manifest.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def current_checksums(root: Path, triggers) -> dict:
    """Checksums of existing trigger files that stay inside root."""
    out = {}
    root = root.resolve()
    for rel in triggers:
        path = (root / rel).resolve()
        if root not in path.parents or not path.is_file():
            continue
        out[rel] = sha256(path)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Project root (contains docs/ai/manifest.json)")
    parser.add_argument("--update", action="store_true", help="Record current checksums and lastScanned")
    args = parser.parse_args()

    root = Path(args.root)
    manifest_path = root / MANIFEST
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        triggers = list(manifest.get("autoRefreshTriggers", []))
        recorded = dict(manifest.get("checksums", {}))
    except (OSError, json.JSONDecodeError, AttributeError, TypeError) as exc:
        print(f"memory_stale: manifest unusable at {manifest_path}: {exc}")
        return 1

    current = current_checksums(root, triggers)

    if args.update:
        manifest["checksums"] = current
        manifest["lastScanned"] = datetime.now().astimezone().isoformat(timespec="seconds")
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        print(f"memory_stale: recorded {len(current)} checksum(s) in {manifest_path}")
        return 0

    stale = sorted(rel for rel, digest in current.items() if recorded.get(rel) != digest)
    if stale:
        print("memory_stale: project memory is stale, refresh docs/ai (/init-memory). Changed:")
        for rel in stale:
            print(f"  - {rel}")
        return 1
    print("memory_stale: fresh")
    return 0


if __name__ == "__main__":
    sys.exit(main())
