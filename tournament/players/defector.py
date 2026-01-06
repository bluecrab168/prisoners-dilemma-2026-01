"""Example player implementation for the class tournament.

This is a simple pure defection strategy implemented using Axelrod's Player API.
Students should use this as a reference for their own submissions.
"""
from __future__ import annotations

from axelrod import Player, Action


class Defector(Player):
    name = "Ms. Bad Apple"

    def strategy(self, opponent):
        """Disregard whatever happened before, always be mean."""
        return Action.D
