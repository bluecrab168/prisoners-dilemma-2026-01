"""Run a round-robin tournament among registered players.

Usage:
    python -m tournament.scripts.run_tournament [--turns N] [--seed S]
"""
from __future__ import annotations

import argparse
from typing import List

from tournament.engine.tournament import run_round_robin
from tournament.players._registry import get_registered_players


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run a round-robin tournament")
    parser.add_argument("--turns", type=int, default=200, help="Number of turns per match")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility")
    args = parser.parse_args(argv)

    players = get_registered_players()
    print(f"Running tournament for {len(players)} players...")

    result = run_round_robin(players, turns=args.turns, seed=args.seed)

    print("\nTotals:")
    for name, total in result.totals.items():
        print(f" - {name}: {total}")

    print("\nRanking:")
    for i, (name, total) in enumerate(result.ranking(), start=1):
        print(f" {i:>2}. {name:20} {total}")

    print("\nMatch results:")
    for m in result.matches:
        print(f" {m.a} vs {m.b}: {m.score_a} - {m.score_b}")

    return 0


if __name__ == "__main__":  # pragma: no cover
    import sys
    raise SystemExit(main(sys.argv[1:]))
