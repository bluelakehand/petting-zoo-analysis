from dataclasses import replace

from petting_zoo_analysis.engine.simulate import legal_moves, new_game
from petting_zoo_analysis.engine.state import GameConfig, PlacedCard


def _state_with_zoo(*cards: PlacedCard, pawn=(0, 0)):
    state = new_game(config=GameConfig(player_count=3), seed=1)
    player = replace(state.players[0], zoo=cards, pawn=pawn)
    return replace(state, players=(player, *state.players[1:]))


def test_gift_shop_makes_entrance_valid_on_five() -> None:
    state = _state_with_zoo(
        PlacedCard("entrance", (0, 0)),
        PlacedCard("gift_shop", (1, 0)),
        pawn=(1, 0),
    )

    moves = legal_moves(state, roll=5, first_roll=True)

    assert [move.card_id for move in moves] == ["entrance"]


def test_entrance_cannot_be_reentered_after_first_move() -> None:
    state = _state_with_zoo(
        PlacedCard("entrance", (0, 0)),
        PlacedCard("gift_shop", (1, 0)),
    )
    player = replace(state.players[0], pawn=(1, 0))
    state = replace(state, players=(player, *state.players[1:]))

    moves = legal_moves(state, roll=5, first_roll=False)

    assert all(move.card_id != "entrance" for move in moves)


def test_llama_ride_can_jump_to_any_other_llama_ride_on_one_or_two() -> None:
    state = _state_with_zoo(
        PlacedCard("entrance", (0, 0)),
        PlacedCard("llama_ride", (1, 0)),
        PlacedCard("llama_ride", (-2, 2)),
        PlacedCard("llama_ride", (3, -1)),
        pawn=(1, 0),
    )

    moves = legal_moves(state, roll=2, first_roll=False)

    assert {move.destination for move in moves} == {(-2, 2), (3, -1)}
    assert {move.reason for move in moves} == {"llama_ride_jump"}


def test_sheep_can_be_entered_diagonally_from_a_normal_card() -> None:
    state = _state_with_zoo(
        PlacedCard("entrance", (0, 0)),
        PlacedCard("sheep", (1, 1)),
        pawn=(0, 0),
    )

    moves = legal_moves(state, roll=4, first_roll=False)

    assert [(move.card_id, move.destination, move.reason) for move in moves] == [
        ("sheep", (1, 1), "sheep_diagonal_allowed")
    ]


def test_pony_range_high_value_is_adjacent_paw_count() -> None:
    state = _state_with_zoo(
        PlacedCard("entrance", (0, 0)),
        PlacedCard("pony", (1, 0)),
        PlacedCard("sheep", (1, 1)),
        PlacedCard("llama_ride", (2, 0)),
        pawn=(0, 0),
    )

    assert legal_moves(state, roll=2, first_roll=False)
    assert not legal_moves(state, roll=3, first_roll=False)


def test_picnic_table_low_value_is_seven_minus_adjacent_utensils() -> None:
    state = _state_with_zoo(
        PlacedCard("entrance", (0, 0)),
        PlacedCard("picnic_table", (1, 0)),
        PlacedCard("snow_cone_stand", (1, 1)),
        PlacedCard("ice_cream_shop", (2, 0)),
        pawn=(0, 0),
    )

    assert legal_moves(state, roll=5, first_roll=False)
    assert not legal_moves(state, roll=4, first_roll=False)
