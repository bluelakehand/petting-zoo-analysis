from __future__ import annotations

import random

from petting_zoo_analysis.engine.actions import LegalBuy, LegalMove
from petting_zoo_analysis.engine.state import GameState
from petting_zoo_analysis.policies.base import Policy


class RandomPolicy(Policy):
    def choose_move(self, state: GameState, roll: int, legal_moves: tuple[LegalMove, ...], rng: random.Random) -> LegalMove | None:
        _ = state
        _ = roll
        if not legal_moves:
            return None
        return rng.choice(legal_moves)

    def choose_buy(self, state: GameState, legal_buys: tuple[LegalBuy, ...], rng: random.Random) -> LegalBuy | None:
        _ = state
        if not legal_buys:
            return None
        return rng.choice((None, *legal_buys))
