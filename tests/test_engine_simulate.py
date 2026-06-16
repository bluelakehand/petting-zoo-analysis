from dataclasses import replace

from petting_zoo_analysis.engine.actions import LegalBuy
from petting_zoo_analysis.engine.simulate import activate_card, apply_buy, apply_turn, legal_buys, legal_moves, new_game
from petting_zoo_analysis.engine.state import GameConfig, PlacedCard
from petting_zoo_analysis.policies.random_policy import RandomPolicy


def test_new_game_seeds_market_and_deck_deterministically() -> None:
    config = GameConfig(player_count=3, market_size=6)

    state_a = new_game(config=config, seed=7)
    state_b = new_game(config=config, seed=7)

    assert state_a.market == state_b.market
    assert state_a.deck == state_b.deck
    assert len(state_a.market) == 6
    assert len(state_a.deck) == 76


def test_first_roll_can_enter_on_entrance() -> None:
    state = new_game(config=GameConfig(player_count=3), seed=1)

    moves = legal_moves(state, roll=3, first_roll=True)

    assert [(move.card_id, move.destination) for move in moves] == [("entrance", (0, 0))]


def test_buy_places_card_adjacent_and_refills_market() -> None:
    state = new_game(config=GameConfig(player_count=3, market_size=1), seed=1)
    player = replace(state.players[0], coins=100)
    state = replace(state, players=(player, *state.players[1:]), market=("sheep",), deck=("cow",))

    buy = LegalBuy("sheep", (1, 0))
    state = apply_buy(state, buy)

    assert state.players[0].coins == 99
    assert PlacedCard("sheep", (1, 0)) in state.players[0].zoo
    assert state.market == ("cow",)
    assert state.deck == ()


def test_duplicate_vp_cards_are_not_legal_buys() -> None:
    state = new_game(config=GameConfig(player_count=3, market_size=1), seed=1)
    player = replace(
        state.players[0],
        coins=100,
        zoo=(*state.players[0].zoo, PlacedCard("gift_shop", (1, 0))),
    )
    state = replace(state, players=(player, *state.players[1:]), market=("gift_shop",), deck=())

    assert legal_buys(state) == ()


def test_garden_doubles_coins_already_earned_this_turn() -> None:
    state = new_game(config=GameConfig(player_count=3), seed=1)
    player = replace(state.players[0], coins=4, zoo=(*state.players[0].zoo, PlacedCard("garden", (1, 0))))
    state = replace(state, players=(player, *state.players[1:]))

    state, earned = activate_card(state, PlacedCard("garden", (1, 0)), turn_earned=7)

    assert earned == 7
    assert state.players[0].coins == 11


def test_apple_picking_can_bank_coin_as_token() -> None:
    state = new_game(config=GameConfig(player_count=3), seed=1)
    apple = PlacedCard("apple_picking_1_6", (1, 0))
    player = replace(state.players[0], coins=4, zoo=(*state.players[0].zoo, apple))
    state = replace(state, players=(player, *state.players[1:]))

    state, earned = activate_card(state, apple, policy=RandomPolicy(), turn_earned=0)

    placed = next(card for card in state.players[0].zoo if card.card_id == "apple_picking_1_6")
    assert earned == 0
    assert placed.tokens == 1
    assert state.players[0].coins == 3


def test_cow_adds_bonus_to_diagonal_paw_cards() -> None:
    state = new_game(config=GameConfig(player_count=3), seed=1)
    sheep = PlacedCard("sheep", (1, 1))
    cow = PlacedCard("cow", (0, 0))
    player = replace(state.players[0], coins=4, zoo=(cow, sheep))
    state = replace(state, players=(player, *state.players[1:]))

    state, earned = activate_card(state, sheep)

    assert earned == 3
    assert state.players[0].coins == 7


def test_move_events_include_visited_card_details() -> None:
    state = new_game(config=GameConfig(player_count=3), seed=4)

    state = apply_turn(state, RandomPolicy(), __import__("random").Random(1))

    move_events = [event for event in state.events if event.kind == "move"]
    assert move_events
    assert "card_id" in move_events[0].details
    assert "position" in move_events[0].details
