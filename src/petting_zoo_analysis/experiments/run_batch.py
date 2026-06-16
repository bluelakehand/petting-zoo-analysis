from __future__ import annotations

from petting_zoo_analysis.engine.simulate import play_game
from petting_zoo_analysis.policies.random_policy import RandomPolicy


def run_smoke_batch(game_count: int = 100, player_count: int = 3) -> list[int]:
    policies = tuple(RandomPolicy() for _ in range(player_count))
    winners: list[int] = []
    for seed in range(game_count):
        final_state = play_game(policies, seed=seed)
        winner = max(final_state.players, key=lambda player: (player.victory_points, player.coins))
        winners.append(winner.player_id)
    return winners


if __name__ == "__main__":
    winners = run_smoke_batch()
    print({player_id: winners.count(player_id) for player_id in sorted(set(winners))})

