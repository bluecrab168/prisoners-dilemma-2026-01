"""Validate player classes for the tournament.

Usage:
    python -m tournament.scripts.validate_player [optional.module:Class]

If an argument is provided, attempts to import and validate that specific class.
Otherwise, validates all registered players from `tournament.players._registry`.
"""
from __future__ import annotations

import importlib
import sys
from typing import List, Type

from tournament.engine.validation import validate_player_class, validate_registered_players
from tournament.players._registry import get_registered_players


def _import_target(spec: str) -> Type:
    """Import a class from a spec like 'module.submodule:ClassName'."""
    if ":" not in spec:
        raise ValueError("Target must be in format 'module.path:ClassName'")
    module_name, cls_name = spec.split(":", 1)
    module = importlib.import_module(module_name)
    cls = getattr(module, cls_name)
    if not isinstance(cls, type):
        raise TypeError(f"{spec} does not resolve to a class")
    return cls


def main(argv: List[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv:
        try:
            target = _import_target(argv[0])
        except Exception as e:
            print(f"Error importing target: {e}")
            return 2
        errors = validate_player_class(target)
        if errors:
            print("Validation errors:")
            for e in errors:
                print(f" - {e}")
            return 1
        print("Validation passed for:", target.__name__)
        return 0

    # No argument: validate registry
    players = get_registered_players()
    messages = validate_registered_players(players)
    if messages:
        print("Validation errors found:")
        for m in messages:
            print(f" - {m}")
        return 1
    print(f"All {len(players)} registered players are valid.")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
