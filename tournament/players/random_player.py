"""Example player implementation for the class tournament.

This is a simple random strategy implemented using Axelrod's Player API.
Students should use this as a reference for their own submissions.
"""
from __future__ import annotations

import random
from axelrod import Player, Action


class Random(Player):
    name = "So Unpredictable"

    def strategy(self, opponent):
        """Disregard whatever happened before, just do something random."""
        return random.choice(tuple(Action))
