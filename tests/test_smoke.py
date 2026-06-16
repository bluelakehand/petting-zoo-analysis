from petting_zoo_analysis.engine.simulate import new_game, play_game
from petting_zoo_analysis.policies.random_policy import RandomPolicy


def test_new_game_starts_each_player_at_entrance() -> None:
    state = new_game(player_count=3)

    assert len(state.players) == 3
    assert {player.pawn for player in state.players} == {(0, 0)}
    assert all(player.zoo[0].card_id == "entrance" for player in state.players)


def test_placeholder_game_is_seeded_and_terminates() -> None:
    policies = (RandomPolicy(), RandomPolicy(), RandomPolicy())

    final_a = play_game(policies, seed=123, max_turns=5)
    final_b = play_game(policies, seed=123, max_turns=5)

    assert final_a == final_b
    assert final_a.turn_number == 6
    assert final_a.events
