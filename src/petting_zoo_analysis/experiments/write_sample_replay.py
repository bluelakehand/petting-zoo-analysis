from __future__ import annotations

from pathlib import Path

from petting_zoo_analysis.engine.replay import write_replay
from petting_zoo_analysis.engine.simulate import play_game
from petting_zoo_analysis.engine.state import GameConfig
from petting_zoo_analysis.policies.random_policy import RandomPolicy


def main() -> None:
    seed = 1
    config = GameConfig(player_count=3, max_turns=5)
    policies = (RandomPolicy(), RandomPolicy(), RandomPolicy())
    state = play_game(policies, seed=seed, config=config)
    output_path = Path("sample-replay.json")
    write_replay(state, output_path, seed=seed, policies=tuple(policy.__class__.__name__ for policy in policies))
    print(output_path)


if __name__ == "__main__":
    main()

