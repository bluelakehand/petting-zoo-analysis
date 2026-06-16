from __future__ import annotations

import random
from dataclasses import replace

from petting_zoo_analysis.engine.actions import LegalBuy, LegalMove
from petting_zoo_analysis.engine.grid import adjacent_positions, diagonal_positions, surrounding_positions
from petting_zoo_analysis.engine.state import Event, GameConfig, GameState, PlacedCard, PlayerState, Position
from petting_zoo_analysis.policies.base import Policy
from petting_zoo_analysis.rules.cards import CARD_DEFS, VICTORY_CARD_IDS, build_deck
from petting_zoo_analysis.rules.scoring import has_winning_victory_set


def new_game(config: GameConfig | None = None, seed: int = 0, player_count: int | None = None, starting_coins: int | None = None) -> GameState:
    if config is None:
        config = GameConfig(
            player_count=player_count or GameConfig.player_count,
            starting_coins=starting_coins if starting_coins is not None else GameConfig.starting_coins,
        )
    rng = random.Random(seed)
    deck = [card_id for card_id in build_deck() if card_id != "entrance"]
    rng.shuffle(deck)
    market, deck = tuple(deck[: config.market_size]), tuple(deck[config.market_size :])
    players = tuple(PlayerState(player_id=i, coins=config.starting_coins) for i in range(config.player_count))
    return GameState(players=players, config=config, market=market, deck=deck)


def card_at(player: PlayerState, position: Position) -> PlacedCard | None:
    return next((card for card in player.zoo if card.position == position), None)


def occupied_positions(player: PlayerState) -> frozenset[Position]:
    return frozenset(card.position for card in player.zoo)


def empty_adjacent_positions(player: PlayerState) -> tuple[Position, ...]:
    occupied = occupied_positions(player)
    positions = {position for card in player.zoo for position in adjacent_positions(card.position)}
    return tuple(sorted(positions - occupied))


def legal_buys(state: GameState) -> tuple[LegalBuy, ...]:
    player = state.players[state.active_player]
    positions = empty_adjacent_positions(player)
    buys: list[LegalBuy] = []
    owned_vp = player.owned_victory_card_ids
    for card_id in state.market:
        card = CARD_DEFS[card_id]
        if card.cost > player.coins:
            continue
        if card_id in VICTORY_CARD_IDS and card_id in owned_vp:
            continue
        buys.extend(LegalBuy(card_id, position) for position in positions)
    return tuple(buys)


def legal_moves(state: GameState, roll: int, first_roll: bool) -> tuple[LegalMove, ...]:
    player = state.players[state.active_player]
    source = None if first_roll else card_at(player, player.pawn)
    destinations = _candidate_destinations(player, source, first_roll, roll)
    moves: list[LegalMove] = []
    for placed in destinations:
        if _card_matches_roll(player, placed, roll):
            moves.append(LegalMove(placed.position, placed.card_id, _move_reason(source, placed, first_roll)))
    return tuple(moves)


def apply_turn(state: GameState, policy: Policy, rng: random.Random) -> GameState:
    turn_earned = 0
    first_roll = True
    state = _append_event(state, "turn_start", f"Player {state.active_player} starts turn {state.turn_number}.")

    while True:
        roll = rng.randint(1, 6)
        moves = legal_moves(state, roll, first_roll)
        state = _append_event(
            state,
            "roll",
            f"Player {state.active_player} rolled {roll}; {len(moves)} legal move(s).",
            {"roll": roll, "legal_moves": [_move_details(move) for move in moves]},
        )
        chosen_move = policy.choose_move(state, roll, moves, rng)
        if chosen_move is None:
            state = _append_event(state, "move_failed", f"Player {state.active_player} cannot move on {roll}.", {"roll": roll})
            break
        player = state.players[state.active_player]
        placed = card_at(player, chosen_move.destination)
        if placed is None:
            raise ValueError(f"No card at chosen destination {chosen_move.destination}.")
        player = replace(player, pawn=chosen_move.destination)
        state = _replace_active_player(state, player)
        state = _append_event(
            state,
            "move",
            f"Player {player.player_id} moved to {CARD_DEFS[placed.card_id].name} at {placed.position}.",
            {"card_id": placed.card_id, "position": list(placed.position), "roll": roll, "reason": chosen_move.reason},
        )
        state, earned = activate_card(state, placed, turn_earned=turn_earned, policy=policy, rng=rng)
        turn_earned += earned
        first_roll = False

    buys = legal_buys(state)
    chosen_buy = policy.choose_buy(state, buys, rng)
    if chosen_buy is not None:
        state = apply_buy(state, chosen_buy)

    state = _append_event(state, "turn_end", f"Player {state.active_player} earned {turn_earned} coin(s) this turn.")
    winner = _winner_after_active_turn(state)
    next_player = (state.active_player + 1) % len(state.players)
    next_turn = state.turn_number + (1 if next_player == 0 else 0)
    return replace(state, active_player=next_player, turn_number=next_turn, winner=winner)


def activate_card(
    state: GameState,
    placed: PlacedCard,
    turn_earned: int = 0,
    policy: Policy | None = None,
    rng: random.Random | None = None,
) -> tuple[GameState, int]:
    card = CARD_DEFS[placed.card_id]
    state, earned = _activate_card_base(state, placed, turn_earned=turn_earned, policy=policy, rng=rng)
    bonus = _cow_diagonal_bonus(state.players[state.active_player], placed)
    if bonus:
        state = _gain_active(state, bonus, "Cow diagonal bonus")
        earned += bonus
    return state, earned


def _activate_card_base(
    state: GameState,
    placed: PlacedCard,
    turn_earned: int = 0,
    policy: Policy | None = None,
    rng: random.Random | None = None,
) -> tuple[GameState, int]:
    card = CARD_DEFS[placed.card_id]
    if card.ability_id == "entrance":
        return _gain_active(state, 2, "Entrance"), 2
    if card.ability_id == "aviary":
        return _gain_active(state, 1, "Aviary"), 1
    if card.ability_id == "flat_5":
        return _gain_active(state, 5, card.name), 5
    if card.ability_id == "flat_10":
        return _gain_active(state, 10, card.name), 10
    if card.ability_id == "gift_shop":
        return _gain_active(state, 3, "Gift Shop"), 3
    if card.ability_id == "bunny_count":
        amount = _count_owned_by_name(state.players[state.active_player], "Bunny")
        return _gain_active(state, amount, "Bunny"), amount
    if card.ability_id == "llama_ride":
        return _gain_active(state, 2, "Llama Ride"), 2
    if card.ability_id == "sheep_diagonal":
        return _gain_active(state, 2, "Sheep"), 2
    if card.ability_id == "apple_picking":
        token_total = _apple_token_total(state.players[state.active_player])
        should_place = policy.choose_apple_picking_token(state, placed, token_total, rng or random.Random(0)) if policy else token_total < 3
        if should_place and state.players[state.active_player].coins > 0:
            state = _place_apple_token(state, placed)
            return state, 0
        return _gain_active(state, token_total, "Apple Picking"), token_total
    if card.ability_id == "take_7_from_others":
        return _take_from_others(state, 7, "Dolphin")
    if card.ability_id == "tax_vp_cards":
        return _tax_others_by_vp_cards(state, 2, "Burger Stand")
    if card.ability_id == "snow_cone":
        player = state.players[state.active_player]
        utensils = _count_kind_at(player, adjacent_positions(placed.position), "utensils")
        return _take_from_others(state, utensils, "Snow Cone Stand")
    if card.ability_id == "feed_dispenser":
        player = state.players[state.active_player]
        amount = _count_kinds_at(player, surrounding_positions(placed.position), {"paw", "utensils"})
        return _gain_active(state, amount, "Feed Dispenser"), amount
    if card.ability_id == "ice_cream_shop":
        player = state.players[state.active_player]
        amount = 2 * _count_names_at(player, surrounding_positions(placed.position), {"Cow"})
        return _gain_active(state, amount, "Ice Cream Shop"), amount
    if card.ability_id == "double_turn_coins":
        return _gain_active(state, turn_earned, "Garden"), turn_earned
    if card.ability_id == "cow_diagonal_animals":
        return _gain_active(state, 2, "Cow"), 2
    if card.ability_id == "pony":
        return _gain_active(state, 3, "Pony"), 3
    if card.ability_id == "picnic_table":
        player = state.players[state.active_player]
        amount = _count_kind_at(player, diagonal_positions(placed.position), "flower")
        return _gain_active(state, amount, "Picnic Table"), amount
    if card.ability_id == "distance_from_entrance":
        distance = abs(placed.position[0]) + abs(placed.position[1])
        amount = 2 * distance
        return _gain_active(state, amount, "Smoothie Shack"), amount
    raise NotImplementedError(f"Unhandled ability: {card.ability_id}")


def apply_buy(state: GameState, buy: LegalBuy) -> GameState:
    player = state.players[state.active_player]
    card = CARD_DEFS[buy.card_id]
    if card.cost > player.coins:
        raise ValueError("Cannot buy a card the player cannot afford.")
    if buy.position not in empty_adjacent_positions(player):
        raise ValueError("Bought cards must be placed orthogonally adjacent to the zoo.")
    player = replace(
        player,
        coins=player.coins - card.cost,
        zoo=(*player.zoo, PlacedCard(buy.card_id, buy.position)),
    )
    market = list(state.market)
    market.remove(buy.card_id)
    deck = list(state.deck)
    if deck:
        market.append(deck.pop(0))
    state = replace(state, market=tuple(market), deck=tuple(deck))
    state = _replace_active_player(state, player)
    return _append_event(
        state,
        "buy",
        f"Player {player.player_id} bought {card.name} at {buy.position} for {card.cost}.",
        {"card_id": buy.card_id, "position": list(buy.position), "cost": card.cost},
    )


def play_game(policies: tuple[Policy, ...], seed: int, config: GameConfig | None = None, max_turns: int | None = None) -> GameState:
    if config is None:
        config = GameConfig(player_count=len(policies), max_turns=max_turns or GameConfig.max_turns)
    rng = random.Random(seed)
    state = new_game(config=config, seed=seed)
    while not state.is_complete:
        policy = policies[state.active_player]
        state = apply_turn(state, policy, rng)
    return state


def _candidate_destinations(player: PlayerState, source: PlacedCard | None, first_roll: bool, roll: int) -> tuple[PlacedCard, ...]:
    if first_roll:
        candidates = [placed for placed in player.zoo if placed.card_id == "entrance"]
        candidates.extend(placed for placed in player.zoo if placed.card_id == "aviary" and roll == 6)
        return tuple(candidates)

    assert source is not None
    source_card = CARD_DEFS[source.card_id]
    allowed_positions: set[Position]
    if source.card_id == "llama_ride" and roll in {1, 2}:
        return tuple(placed for placed in player.zoo if placed.card_id == "llama_ride" and placed.position != source.position)
    if source_card.ability_id in {"pony", "picnic_table"}:
        allowed_positions = set(diagonal_positions(source.position))
    else:
        allowed_positions = set(adjacent_positions(source.position))
        allowed_positions.update(pos for pos in diagonal_positions(source.position) if (card_at(player, pos) or PlacedCard("", pos)).card_id == "sheep")
    return tuple(placed for placed in player.zoo if placed.position in allowed_positions)


def _card_matches_roll(player: PlayerState, placed: PlacedCard, roll: int) -> bool:
    card = CARD_DEFS[placed.card_id]
    if placed.card_id == "entrance" and "gift_shop" in player.owned_card_ids:
        return 1 <= roll <= 5
    if card.ability_id == "pony":
        high = _count_kind_at(player, adjacent_positions(placed.position), "paw")
        return card.roll.contains(roll, dynamic_high=high)
    if card.ability_id == "picnic_table":
        low = 7 - _count_kind_at(player, adjacent_positions(placed.position), "utensils")
        return card.roll.contains(roll, dynamic_low=low)
    return card.roll.contains(roll)


def _move_reason(source: PlacedCard | None, destination: PlacedCard, first_roll: bool) -> str:
    if first_roll:
        return "first_roll_entry"
    if destination.card_id == "sheep":
        return "sheep_diagonal_allowed"
    if source and source.card_id == "llama_ride" and destination.card_id == "llama_ride":
        return "llama_ride_jump"
    return "standard"


def _move_details(move: LegalMove) -> dict[str, object]:
    return {"card_id": move.card_id, "position": list(move.destination), "reason": move.reason}


def _replace_active_player(state: GameState, player: PlayerState) -> GameState:
    players = list(state.players)
    players[state.active_player] = player
    return replace(state, players=tuple(players))


def _append_event(state: GameState, kind: str, message: str, details: dict[str, object] | None = None) -> GameState:
    return replace(
        state,
        events=(*state.events, Event(state.turn_number, state.active_player, kind, message, details or {}, _snapshot(state))),
    )


def _snapshot(state: GameState) -> dict[str, object]:
    return {
        "active_player": state.active_player,
        "turn_number": state.turn_number,
        "winner": state.winner,
        "market": list(state.market),
        "deck_count": len(state.deck),
        "discard_count": len(state.discard),
        "players": [
            {
                "player_id": player.player_id,
                "coins": player.coins,
                "victory_points": player.victory_points,
                "pawn": list(player.pawn),
                "zoo": [
                    {
                        "card_id": placed.card_id,
                        "position": list(placed.position),
                        "tokens": placed.tokens,
                    }
                    for placed in player.zoo
                ],
            }
            for player in state.players
        ],
    }


def _gain_active(state: GameState, amount: int, source: str) -> GameState:
    if amount <= 0:
        return _append_event(state, "ability", f"{source} earned 0 coin(s).", {"source": source, "coins": 0})
    player = state.players[state.active_player]
    player = replace(player, coins=player.coins + amount)
    state = _replace_active_player(state, player)
    return _append_event(state, "ability", f"{source} earned {amount} coin(s).", {"source": source, "coins": amount})


def _place_apple_token(state: GameState, placed: PlacedCard) -> GameState:
    player = state.players[state.active_player]
    updated_zoo = tuple(
        replace(card, tokens=card.tokens + 1) if card.position == placed.position and card.card_id == placed.card_id else card
        for card in player.zoo
    )
    player = replace(player, coins=player.coins - 1, zoo=updated_zoo)
    state = _replace_active_player(state, player)
    return _append_event(
        state,
        "ability",
        "Apple Picking banked 1 coin on the card.",
        {"source": "Apple Picking", "coins": -1, "token_position": list(placed.position)},
    )


def _take_from_others(state: GameState, amount_each: int, source: str) -> tuple[GameState, int]:
    if amount_each <= 0:
        return _append_event(state, "ability", f"{source} took 0 coin(s)."), 0
    players = list(state.players)
    active = players[state.active_player]
    total = 0
    for idx, player in enumerate(players):
        if idx == state.active_player:
            continue
        paid = min(amount_each, player.coins)
        total += paid
        players[idx] = replace(player, coins=player.coins - paid)
    players[state.active_player] = replace(active, coins=active.coins + total)
    state = replace(state, players=tuple(players))
    return _append_event(state, "ability", f"{source} took {total} total coin(s) from other players."), total


def _tax_others_by_vp_cards(state: GameState, amount_each: int, source: str) -> tuple[GameState, int]:
    players = list(state.players)
    active = players[state.active_player]
    total = 0
    for idx, player in enumerate(players):
        if idx == state.active_player:
            continue
        owed = amount_each * len(player.owned_victory_card_ids)
        paid = min(owed, player.coins)
        total += paid
        players[idx] = replace(player, coins=player.coins - paid)
    players[state.active_player] = replace(active, coins=active.coins + total)
    state = replace(state, players=tuple(players))
    return _append_event(state, "ability", f"{source} took {total} total coin(s) for opponents' VP cards."), total


def _count_owned_by_name(player: PlayerState, name: str) -> int:
    return sum(1 for placed in player.zoo if CARD_DEFS[placed.card_id].name == name)


def _apple_token_total(player: PlayerState) -> int:
    return sum(placed.tokens for placed in player.zoo if CARD_DEFS[placed.card_id].name == "Apple Picking")


def _count_kind_at(player: PlayerState, positions: tuple[Position, ...], kind: str) -> int:
    return _count_kinds_at(player, positions, {kind})


def _count_kinds_at(player: PlayerState, positions: tuple[Position, ...], kinds: set[str]) -> int:
    position_set = set(positions)
    return sum(1 for placed in player.zoo if placed.position in position_set and CARD_DEFS[placed.card_id].kind.value in kinds)


def _count_names_at(player: PlayerState, positions: tuple[Position, ...], names: set[str]) -> int:
    position_set = set(positions)
    return sum(1 for placed in player.zoo if placed.position in position_set and CARD_DEFS[placed.card_id].name in names)


def _cow_diagonal_bonus(player: PlayerState, placed: PlacedCard) -> int:
    card = CARD_DEFS[placed.card_id]
    if card.kind.value != "paw" or placed.card_id == "cow":
        return 0
    return _count_names_at(player, diagonal_positions(placed.position), {"Cow"})


def _winner_after_active_turn(state: GameState) -> int | None:
    player = state.players[state.active_player]
    if has_winning_victory_set(player.owned_card_ids):
        return player.player_id
    return state.winner
