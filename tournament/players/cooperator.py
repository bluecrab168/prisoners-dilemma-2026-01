"""Example player implementation for the class tournament.

This is a simple pure cooperation strategy implemented using Axelrod's Player API.
Students should use this as a reference for their own submissions.
"""
from __future__ import annotations

from axelrod import Player, Action


class Cooperator(Player):
    name = "Mr. Nice Guy"

    def strategy(self, opponent):
        """Disregard whatever happened before, always be nice and cooperate."""
        return Action.C
