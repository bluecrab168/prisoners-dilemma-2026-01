"""Watch the players directory for changes and re-run validation.

Simple polling-based watcher to avoid external dependencies. Intended for
classroom convenience, not production reliability.

Usage:
    python -m tournament.scripts.watch_players [--interval SECONDS]
"""
from __future__ import annotations

import argparse
import os
import time
from pathlib import Path
from typing import Dict, List

from tournament.players import __path__ as players_pkg_paths  # type: ignore
from tournament.scripts.validate_player import main as validate_main


def snapshot_players(dir_path: Path) -> Dict[str, float]:
    """Return a mapping from file path (str) to mtime for .py files."""
    mtimes: Dict[str, float] = {}
    for p in dir_path.glob("*.py"):
        if p.name.startswith("_"):
            # include _registry.py to catch rebuilds, but skip others
            if p.name != "_registry.py":
                continue
        mtimes[str(p)] = p.stat().st_mtime
    return mtimes


essential_files = {"_registry.py", "__init__.py"}


def detect_changes(prev: Dict[str, float], curr: Dict[str, float]) -> List[str]:
    changes: List[str] = []
    # new or modified
    for path, mtime in curr.items():
        if path not in prev or prev[path] != mtime:
            changes.append(path)
    # deleted
    for path in prev.keys() - curr.keys():
        changes.append(path + " (deleted)")
    return sorted(changes)


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Watch players for changes and re-validate")
    parser.add_argument("--interval", type=float, default=1.0, help="Polling interval in seconds")
    args = parser.parse_args(argv)

    # Resolve the first path of the players package
    players_dir = Path(list(players_pkg_paths)[0])
    print(f"Watching: {players_dir}")

    prev = snapshot_players(players_dir)
    print("Initial validation...")
    validate_rc = validate_main([])
    print(f"Initial validation exit code: {validate_rc}")

    try:
        while True:
            time.sleep(args.interval)
            curr = snapshot_players(players_dir)
            changes = detect_changes(prev, curr)
            if changes:
                print("\nDetected changes:")
                for c in changes:
                    print(f" - {c}")
                prev = curr
                print("Re-validating...")
                rc = validate_main([])
                print(f"Validation exit code: {rc}")
    except KeyboardInterrupt:
        print("\nStopping watcher.")
        return 0


if __name__ == "__main__":  # pragma: no cover
    import sys
    raise SystemExit(main(sys.argv[1:]))
