from __future__ import annotations

import argparse

from petting_zoo_analysis.experiments.reporting import write_tournament_outputs
from petting_zoo_analysis.experiments.tournament import run_policy_tournament


def run_smoke_batch(game_count: int = 100, player_count: int = 3) -> dict[str, int]:
    return {result.policy_name: result.wins for result in run_policy_tournament(game_count=game_count, player_count=player_count)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Petting Zoo baseline policy tournaments.")
    parser.add_argument("--games", type=int, default=100)
    parser.add_argument("--players", type=int, default=3)
    parser.add_argument("--max-turns", type=int, default=80)
    parser.add_argument("--output-dir", default="")
    args = parser.parse_args()

    results = run_policy_tournament(game_count=args.games, player_count=args.players, max_turns=args.max_turns)
    for result in results:
        print(
            f"{result.policy_name:16} wins={result.wins:3d}/{result.games:<3d} "
            f"win_rate={result.win_rate:.3f} +/- {result.ci95:.3f} "
            f"vp_cards={result.mean_vp_cards:.2f} coins={result.mean_coins:.1f} cards={result.mean_cards:.1f}"
        )
    if args.output_dir:
        write_tournament_outputs(results, args.output_dir)
