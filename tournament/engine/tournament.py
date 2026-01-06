"""Round-robin tournament harness for Axelrod player classes."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Sequence, Tuple, Type, Optional

from .referee import play_match


@dataclass
class MatchResult:
    a: str
    b: str
    score_a: int
    score_b: int


@dataclass
class TournamentResult:
    players: List[str]
    totals: Dict[str, int]
    matches: List[MatchResult]

    def ranking(self) -> List[Tuple[str, int]]:
        return sorted(self.totals.items(), key=lambda kv: kv[1], reverse=True)


def run_round_robin(
    player_classes: Sequence[Type],
    *,
    turns: int = 200,
    seed: Optional[int] = None,
) -> TournamentResult:
    """Run a simple round-robin tournament among the given player classes.

    Each pair plays once. Scores from the Axelrod game are summed.
    """
    names = [cls.__name__ for cls in player_classes]
    totals: Dict[str, int] = {name: 0 for name in names}
    matches: List[MatchResult] = []

    n = len(player_classes)
    for i in range(n):
        for j in range(i + 1, n):
            a_cls = player_classes[i]
            b_cls = player_classes[j]
            score_a, score_b = play_match(a_cls, b_cls, turns=turns, seed=seed)
            name_a = a_cls.__name__
            name_b = b_cls.__name__
            totals[name_a] += score_a
            totals[name_b] += score_b
            matches.append(MatchResult(name_a, name_b, score_a, score_b))

    return TournamentResult(players=names, totals=totals, matches=matches)
