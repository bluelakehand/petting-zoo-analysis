from __future__ import annotations

import random
from dataclasses import replace

from petting_zoo_analysis.engine.actions import TurnAction
from petting_zoo_analysis.engine.state import GameState, PlayerState
from petting_zoo_analysis.policies.base import Policy


def new_game(player_count: int, starting_coins: int = 4) -> GameState:
    players = tuple(PlayerState(player_id=i, coins=starting_coins) for i in range(player_count))
    return GameState(players=players)


def apply_turn(state: GameState, action: TurnAction, rng: random.Random) -> GameState:
    """Placeholder transition until the full rule transcription is complete."""
    _ = action
    _ = rng
    next_player = (state.active_player + 1) % len(state.players)
    next_turn = state.turn_number + (1 if next_player == 0 else 0)
    return replace(state, active_player=next_player, turn_number=next_turn)


def play_game(policies: tuple[Policy, ...], seed: int, max_turns: int = 200) -> GameState:
    rng = random.Random(seed)
    state = new_game(len(policies))
    while state.turn_number <= max_turns:
        policy = policies[state.active_player]
        action = policy.choose_action(state, rng)
        state = apply_turn(state, action, rng)
    return state

