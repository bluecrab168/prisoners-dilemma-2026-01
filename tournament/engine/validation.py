"""Validation utilities for participant player classes.

A valid player is expected to be a subclass of `axelrod.Player` and implement
at least the `strategy` method.
"""
from __future__ import annotations

from typing import List, Type

try:
    import axelrod as axl
except Exception:  # pragma: no cover - present as dependency
    axl = None  # type: ignore


def validate_player_class(cls: Type) -> List[str]:
    """Validate a player class and return a list of error messages.

    Rules (initial scaffolding):
    - Axelrod must be available.
    - `cls` must be a subclass of `axelrod.Player`.
    - `cls` must implement `strategy(self, opponent)`.
    """
    errors: List[str] = []
    if axl is None:
        errors.append("Axelrod library is not available. Ensure it is installed.")
        return errors

    if not isinstance(cls, type):
        errors.append("Provided object is not a class.")
        return errors

    if not issubclass(cls, axl.Player):
        errors.append(
            "Player must inherit from axelrod.Player to be compatible with the engine."
        )

    if "strategy" not in cls.__dict__:
        # Ensure the class overrides the base method
        errors.append("Player class must implement a 'strategy(self, opponent)' method.")

    return errors


def validate_registered_players(classes: List[Type]) -> List[str]:
    """Validate a list of player classes, aggregate errors with context."""
    messages: List[str] = []
    for cls in classes:
        errs = validate_player_class(cls)
        for e in errs:
            messages.append(f"{cls.__name__}: {e}")
    return messages
