from petting_zoo_analysis.engine.replay import replay_payload
from petting_zoo_analysis.engine.simulate import play_game
from petting_zoo_analysis.engine.state import GameConfig
from petting_zoo_analysis.policies.random_policy import RandomPolicy


def test_replay_payload_contains_visualizer_required_sections() -> None:
    policies = (RandomPolicy(), RandomPolicy(), RandomPolicy())
    state = play_game(policies, seed=5, config=GameConfig(player_count=3, max_turns=1))

    payload = replay_payload(state, seed=5, policies=("RandomPolicy",) * 3)

    assert payload["schema_version"] == 1
    assert payload["seed"] == 5
    assert payload["card_catalog"]
    assert payload["card_catalog"]["entrance"]["image"] == "assets/cards/entrance.jpg"
    assert payload["players"]
    assert payload["market"]
    assert payload["events"]
    assert payload["events"][0]["snapshot"]["players"]
    assert "deck_count" in payload
