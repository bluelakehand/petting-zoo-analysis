from __future__ import annotations

from petting_zoo_analysis.experiments.tournament import run_policy_tournament


def run_smoke_batch(game_count: int = 100, player_count: int = 3) -> dict[str, int]:
    return {result.policy_name: result.wins for result in run_policy_tournament(game_count=game_count, player_count=player_count)}


if __name__ == "__main__":
    for result in run_policy_tournament():
        print(
            f"{result.policy_name:16} wins={result.wins:3d}/{result.games:<3d} "
            f"win_rate={result.win_rate:.3f} +/- {result.ci95:.3f} "
            f"vp_cards={result.mean_vp_cards:.2f} coins={result.mean_coins:.1f} cards={result.mean_cards:.1f}"
        )
