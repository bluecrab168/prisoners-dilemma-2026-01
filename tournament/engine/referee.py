"""Referee utilities to run matches between two Axelrod players."""
from __future__ import annotations

from typing import Tuple, Type, Optional

try:
    import axelrod as axl
except Exception:  # pragma: no cover
    axl = None  # type: ignore


def play_match(
    player_a_cls: Type,
    player_b_cls: Type,
    *,
    turns: int = 200,
    seed: Optional[int] = None,
) -> Tuple[int, int]:
    """Play a single match between two player classes.

    Returns a tuple of cumulative scores (score_a, score_b).
    """
    if axl is None:  # pragma: no cover - dependency guard
        raise RuntimeError("Axelrod is not available. Install it to run matches.")

    if seed is not None:
        axl.seed(seed)

    # Instantiate players and run a match
    p1 = player_a_cls()
    p2 = player_b_cls()
    match = axl.Match((p1, p2), turns=turns)
    result = match.play()

    game = axl.Game()
    score_a = 0
    score_b = 0
    for a_move, b_move in result:
        a_s, b_s = game.score((a_move, b_move))
        score_a += a_s
        score_b += b_s

    return score_a, score_b
